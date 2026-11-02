"""Automatic experiment campaigns for Phase 0 (reports/phase0/plan_fa.md, Section 5).

    python tools/campaign.py campaigns/<name>.yaml [--dry]

A campaign is a list of stages run in order. A stage is a list of run groups; each group is one configuration
(``config`` + ``set`` overrides) run for several ``seeds`` (and ``folds`` for leave-one-out protocols). Inside a
stage up to ``slots`` runs execute at once, and a run starts only while fewer than ``max_jobs`` Phase 0 processes
(ours or others) are alive on the machine. Finished runs (``metrics.json`` present) are skipped, so a campaign
resumes after a crash or a reboot.

Selection: a stage with ``from: <stage>`` builds its groups from the ``top`` best groups of an earlier stage (pooled
with the stages in ``pool``), ranked by the mean validation accuracy over seeds of the best readout variant. The
selected readout variant is passed on (``readout.variants=[spec]``); ``drop`` removes overrides by prefix (e.g. the
validation split for the final test), ``exclude`` removes groups from the candidates by name and ``set`` adds more. ``{seed}`` and ``{fold}`` in overrides are replaced.

Everything is logged to ``<work>/campaigns/<name>/campaign.log`` and every finished run is collected in
``results.csv`` there (the source of the final report's tables).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def log(path: Path, msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def phase0_jobs() -> int:
    """Phase 0 python processes alive on this machine (the venv launcher stub is not counted)."""
    if os.name != "nt":
        out = subprocess.run(["pgrep", "-fc", "biovision.experiments.phase0"], capture_output=True, text=True)
        return int(out.stdout.strip() or 0)
    ps = ("(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like "
          "'*biovision.experiments.phase0*' -and $_.WorkingSetSize -gt 150MB }).Count")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    try:
        return int(out.stdout.strip() or 0)
    except ValueError:
        return 0


def best_variant(metrics: dict) -> tuple[str, float]:
    v = metrics.get("variants") or {}
    if not v:
        return "", float(metrics["test_acc"])
    name = max(v, key=lambda k: v[k]["svm"])
    return name, float(v[name]["svm"])


class Campaign:
    def __init__(self, path: Path, dry: bool):
        self.spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.name = self.spec["name"]
        work = Path(self.spec.get("work", REPO.parent / "work"))
        self.dir = work / "campaigns" / self.name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.logf = self.dir / "campaign.log"
        self.dry = dry
        self.slots = int(self.spec.get("slots", 1))
        self.max_jobs = int(self.spec.get("max_jobs", 3))
        self.groups: dict[str, list[dict]] = {}  # stage -> groups

    # ---- runs -------------------------------------------------------------------------------------------
    def stage_dir(self, stage: str) -> Path:
        """``stage`` of this campaign, or ``<campaign>/<stage>`` of another one."""
        return self.dir.parent / stage if "/" in stage else self.dir / stage

    def stage_groups(self, stage: str) -> list[dict]:
        if "/" not in stage:
            return self.groups.get(stage, [])
        camp, st = stage.split("/", 1)
        f = self.dir.parent / camp / f"stage_{st}.yaml"
        return yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else []

    def runs_of(self, stage: str, group: dict) -> list[dict]:
        folds = group.get("folds") or [None]
        out = []
        for seed in group.get("seeds", [0]):
            for fold in folds:
                tag = f"s{seed}" + (f"_f{fold}" if fold is not None else "")
                sets = [s.replace("{seed}", str(seed)).replace("{fold}", str(fold)) for s in group.get("set", [])]
                out.append({"stage": stage, "group": group["name"], "seed": seed, "fold": fold, "sets": sets,
                            "config": group["config"], "args": list(group.get("args", [])),
                            "dir": self.stage_dir(stage) / group["name"] / tag})
        return out

    @staticmethod
    def busy_elsewhere(run: dict) -> bool:
        """A run whose log was written in the last 15 minutes but has no metrics is being executed by a process
        this runner did not start (e.g. after the campaign runner itself was restarted)."""
        log_f = run["dir"] / "log.txt"
        return (not (run["dir"] / "metrics.json").exists() and log_f.exists()
                and time.time() - log_f.stat().st_mtime < 900)

    def start(self, run: dict) -> subprocess.Popen | None:
        run["dir"].mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-m", "biovision.experiments.phase0", "--config", run["config"],
               "--seed", str(run["seed"])]
        for s in run["sets"]:
            cmd += ["--set", s]
        cmd += run.get("args", [])  # e.g. --load-weights of an STDP run (R-STDP search on fixed features)
        (run["dir"] / "cmd.json").write_text(json.dumps(cmd, indent=1), encoding="utf-8")
        log(self.logf, f"start {run['stage']}/{run['group']}/{run['dir'].name}")
        if self.dry:
            return None
        env = {**os.environ, "RUN_DIR": str(run["dir"]), "PYTHONIOENCODING": "utf-8"}
        out = open(run["dir"] / "log.txt", "a", encoding="utf-8")
        return subprocess.Popen(cmd, cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)

    def run_stage(self, stage: str, groups: list[dict]) -> None:
        todo = [r for g in groups for r in self.runs_of(stage, g) if not (r["dir"] / "metrics.json").exists()]
        log(self.logf, f"stage {stage}: {len(groups)} groups, {len(todo)} runs to do")
        alive: list[tuple[dict, subprocess.Popen]] = []
        while todo or alive:
            if todo and not alive and all(self.busy_elsewhere(r) for r in todo):
                time.sleep(30)  # only runs that another process is finishing are left
                todo = [r for r in todo if not (r["dir"] / "metrics.json").exists()]
                continue
            for run, proc in list(alive):
                if proc.poll() is not None:
                    alive.remove((run, proc))
                    m = run["dir"] / "metrics.json"
                    if m.exists():
                        met = json.loads(m.read_text(encoding="utf-8"))
                        name, acc = best_variant(met)
                        log(self.logf, f"done  {run['stage']}/{run['group']}/{run['dir'].name}: "
                                       f"{met['eval_split']} acc {met['test_acc']:.4f}; best variant {name} {acc:.4f}")
                    else:
                        (run["dir"] / "failed.txt").write_text(f"exit code {proc.returncode}\n", encoding="utf-8")
                        log(self.logf, f"FAILED {run['stage']}/{run['group']}/{run['dir'].name} (exit {proc.returncode})")
                    self.collect()
            todo = [r for r in todo if not (r["dir"] / "metrics.json").exists()]
            ready = [r for r in todo if not self.busy_elsewhere(r)]
            while ready and len(alive) < self.slots and (self.dry or phase0_jobs() < self.max_jobs):
                run = ready.pop(0)
                todo.remove(run)
                proc = self.start(run)
                if proc is not None:
                    alive.append((run, proc))
                    time.sleep(20)  # let the new process show up before counting jobs again
            if self.dry:
                break
            time.sleep(30)

    # ---- selection ----------------------------------------------------------------------------------------
    def scores(self, stages: list[str]) -> dict[str, dict]:
        """group -> {variant: [acc per finished run]}, pooled over ``stages``; plus the group's spec."""
        out: dict[str, dict] = {}
        for st in stages:
            for g in self.stage_groups(st):
                rec = out.setdefault(g["name"], {"group": g, "acc": {}, "specs": {}})
                for r in self.runs_of(st, g):
                    m = r["dir"] / "metrics.json"
                    if not m.exists():
                        continue
                    met = json.loads(m.read_text(encoding="utf-8"))
                    vs = met.get("variants") or {"": {"svm": met["test_acc"], "spec": None}}
                    for vn, v in vs.items():
                        rec["acc"].setdefault(vn, []).append(float(v["svm"]))
                        rec["specs"][vn] = v.get("spec")
        return out

    def select(self, stage: dict) -> list[dict]:
        frm = stage["from"] if isinstance(stage["from"], list) else [stage["from"]]
        src = frm + list(stage.get("pool", []))
        sc = self.scores(src)
        candidates = {g["name"] for st in frm for g in self.stage_groups(st)} - set(stage.get("exclude", []))
        ranked = []
        for name, rec in sc.items():
            if name not in candidates or not rec["acc"]:
                continue
            n_max = max(len(a) for a in rec["acc"].values())
            vn, accs = max(((vn, a) for vn, a in rec["acc"].items() if len(a) == n_max),
                           key=lambda t: sum(t[1]) / len(t[1]))
            ranked.append((sum(accs) / len(accs), len(accs), name, vn, rec))
        ranked.sort(key=lambda t: (-t[0], -t[1]))
        lines = [f"{name} [{vn or 'single readout'}]: mean {m:.4f} over {n} runs" for m, n, name, vn, _ in ranked]
        log(self.logf, f"ranking for {stage['name']} (from {', '.join(src)}):\n    " + "\n    ".join(lines))
        groups = []
        for m, n, name, vn, rec in ranked[: stage.get("top", 1)]:
            g0 = rec["group"]
            drop = tuple(stage.get("drop", []))
            keep = stage.get("keep_variant", True)
            sets = [s for s in g0.get("set", []) if not s.startswith(drop)
                    and not (keep and s.startswith("readout.variants="))]
            spec = rec["specs"].get(vn)
            if spec and keep:
                spec = {k: v for k, v in spec.items() if v is not None}
                if "final_C" in stage:
                    spec["C"] = stage["final_C"]
                sets.append("readout.variants=" + yaml.safe_dump([spec], default_flow_style=True).strip())
            g = {"name": name, "config": g0["config"], "set": sets + list(stage.get("set", [])),
                 "args": list(stage.get("args", g0.get("args", []) if stage.get("keep_args", False) else [])),
                 "seeds": stage.get("seeds", g0.get("seeds", [0])), "folds": stage.get("folds"),
                 "selected_from": {"mean": m, "runs": n, "variant": vn}}
            groups.append(g)
        return groups

    # ---- results ------------------------------------------------------------------------------------------
    def collect(self) -> None:
        rows = []
        for m in sorted(self.dir.glob("*/*/*/metrics.json")):
            met = json.loads(m.read_text(encoding="utf-8"))
            stage, group, tag = m.parts[-4], m.parts[-3], m.parts[-2]
            vn, vacc = best_variant(met)
            rows.append({
                "stage": stage, "group": group, "run": tag, "dataset": met["dataset"], "seed": met["seed"],
                "eval_split": met["eval_split"], "acc": round(met["test_acc"], 6), "best_variant": vn,
                "best_variant_acc": round(vacc, 6), "knn": met.get("knn_test_acc", ""),
                "rstdp_best_test_optimistic": met.get("rstdp_best_test_acc_optimistic", ""),
                "rstdp_final": met.get("rstdp_final_test_acc", ""),
                "spikes_per_image": round(met["spikes_per_image_input_plus_conv"], 1),
                "weights": met["weights"], "images_per_s": round(met["feature_images_per_s"], 2),
                "train_time_s": round(sum(met["train_time_s"].values()), 1), "n_train": met["n_train"],
                "n_test": met["n_test"], "overrides": " ".join(met.get("overrides", [])), "path": str(m.parent),
            })
        if rows:
            with open(self.dir / "results.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)

    def run(self) -> None:
        log(self.logf, f"campaign {self.name}: {len(self.spec['stages'])} stages, slots {self.slots}, "
                       f"max jobs {self.max_jobs}")
        for st in self.spec["stages"]:
            waits = st.get("wait_for", [])  # other campaigns whose results this stage selects from
            if waits and not self.dry:
                log(self.logf, f"stage {st['name']}: waiting for {', '.join(waits)}")
                while not all("finished" in (self.dir.parent / c / "campaign.log").read_text(encoding="utf-8")
                              for c in waits if (self.dir.parent / c / "campaign.log").exists())                         or not all((self.dir.parent / c / "campaign.log").exists() for c in waits):
                    time.sleep(60)
            defaults = st.get("defaults", {})
            if "from" in st:
                groups = self.select(st)
            else:
                groups = [{**defaults, **g, "set": list(defaults.get("set", [])) + list(g.get("set", []))}
                          for g in st["runs"]]
            self.groups[st["name"]] = groups
            (self.dir / f"stage_{st['name']}.yaml").write_text(yaml.safe_dump(groups, sort_keys=False, allow_unicode=True),
                                                               encoding="utf-8")
            self.run_stage(st["name"], groups)
        self.collect()
        log(self.logf, f"campaign {self.name} finished")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign")
    ap.add_argument("--dry", action="store_true", help="print the runs of the first stages without running them")
    a = ap.parse_args()
    Campaign(Path(a.campaign), a.dry).run()


if __name__ == "__main__":
    main()
