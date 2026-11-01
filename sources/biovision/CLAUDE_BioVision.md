# BioVision-SNN — Project Brief and Operating Manual for Claude Code

> Put this file at the root of the project repository on the laptop as `CLAUDE.md`.
> It is the single source of truth for the project. Read it fully at the start of every
> session, then read `STATUS.md` and `DECISIONS.md` (Section 7.3) before doing anything.

---

## 0. How to use this file

1. **Session start protocol** (every session, no exceptions):
   1. Read this file, `STATUS.md`, `DECISIONS.md`.
   2. Run `tools/hpc_health.sh` (Section 3.8) and report free disk on the HPC.
   3. State in one paragraph: current phase, last completed task, next task.
2. **Never skip a gate.** Each phase ends with a gate (Section 8). At a gate you stop,
   write the phase report, and wait for the user's explicit approval.
3. **Ask the user** before: deleting any dataset or run directory, downloading anything
   larger than 5 GB, changing the architecture in Section 4, or changing a gate criterion.
4. **Record every non-trivial choice** in `DECISIONS.md` (date, decision, reason, alternatives).
5. **Placeholders** in angle brackets (`<HPC_HOST>`, `<HPC_USER>`, `<HPC_ROOT>`) must be
   asked from the user once and then stored in `tools/hpc.env` (not committed if it holds secrets).

---

## 1. Context and goal

### 1.1 What we are building

A **bio-inspired spiking visual system** that does what an object detector such as YOLO
does — *what is where in the scene* — but is built like the primate visual system and learns
with **local, biologically plausible rules** instead of backpropagation.

It is **not** a converted ANN ("spiking YOLO"). Every layer is a spiking layer with
time-to-first-spike (TTFS) coding, lateral inhibition, weight sharing and STDP-family learning.

### 1.2 Scientific goals (what the final paper must show)

| # | Goal | How it is measured |
|---|------|--------------------|
| G1 | Ultra-rapid recognition: a class decision in the first feed-forward wave | decision time step; worst-case latency < 50 ms in the hardware time model (Section 4.12) |
| G2 | Localisation without boxes as a training target: "what" at each retinotopic location | mAP (box derived from the object mask), pointing accuracy |
| G3 | Invariance: scale, position, illumination | accuracy under rescaled, shifted and brightness/gamma-changed test images |
| G4 | Extreme sparsity and low energy | spikes per image, synaptic operations (SOPs), fraction of active neurons per layer |
| G5 | Motion: direction and speed per location; heading; time-to-contact | flow endpoint error on MVSEC; tuning curves |
| G6 | Monocular depth (order and metric with scale) | depth-order accuracy; abs-rel error after median scaling |
| G7 | Attention via feedback to LGN improves the second wave | wave-2 vs wave-1 accuracy on cluttered scenes (paired test) |
| G8 | Object permanence: identities kept through occlusion | ID switches, IDF1 on synthetic and real sequences |
| G9 | Robustness to hardware faults (link to the user's fault-tolerant accelerator work) | accuracy vs stuck-at fault rate per module |

**Realistic expectation:** accuracy on COCO will be below YOLO. The claim of the work is the
*combination*: acceptable accuracy + local learning + < 100 ms + very few spikes + outputs YOLO does
not produce (depth, motion, identity persistence) + fault tolerance. Never tune or report in a
way that hides this; always report energy/latency/spike metrics next to accuracy.

### 1.3 Non-negotiable design principles

1. **TTFS only.** Every neuron fires **at most one spike per wave**. No rate coding anywhere
   (rate coding appears only as an ablation baseline in Phase 5).
2. **Local learning only.** STDP, flat STDP, exponential STDP, R-STDP (and optionally SDSP).
   No backpropagation through the spiking network. (A linear SVM may be used *only* as an
   evaluation probe in Phases 0–1, clearly labelled as a probe.)
3. **Weight sharing** (convolution) in every simple-cell layer; **max-pooling = complex cells**
   (in TTFS, max-pool = earliest spike wins).
4. **Lateral inhibition / WTA** in every simple-cell layer (feature-wise WTA at each position;
   k-WTA with an inhibition radius during learning).
5. **Three retinal channels are kept**: Parvo (P), Konio (K), Magno (M).
6. **The retina emulator is outside the learned architecture** (we have no event camera for
   static images): fixed DoG filters, intensity-to-latency and rank-order coding.
7. **Feedback is applied in the next wave** (wave n+1). Wave 1 is purely feed-forward.
8. **Boxes are never a training target.** A box is computed from the object mask only for
   comparison with detectors (mAP).

---

## 2. Hard constraints

| Constraint | Value / rule |
|---|---|
| HPC | headless Linux, **no internet**, reachable **only via SSH** from the laptop; 10th-gen Xeon, 44 cores, 500 GB RAM, **no GPU** |
| HPC disk budget for this project | **100 GB hard cap** (stop and ask at 85 GB used) |
| Laptop | Windows 11, Ryzen 7 5800HS, RTX 3050, 16 GB RAM, 512 GB SSD, **very little free disk** |
| Where Claude Code runs | **on the laptop** (it needs internet); it operates the HPC through `ssh`/`scp` |
| Heavy compute | **only on the HPC**; the laptop never trains, never stores datasets |
| Downloads | done from the laptop and **streamed** to the HPC without being stored on the laptop (Section 3.6) |

---

## 3. Environment and HPC setup

### 3.1 Topology

```
 Internet ── Laptop (Claude Code, git, ssh, curl, python for `pip download`)
                │  ssh / scp / git over ssh
                ▼
            HPC (offline) : <HPC_ROOT>/
                 ├── miniforge/        Python distribution (offline-installed)
                 ├── venv/             project virtual env
                 ├── repo.git/         bare git repo (push target)
                 ├── src/              working tree (checked out by hook)
                 ├── data/raw/         downloaded archives (temporary)
                 ├── data/proc/        preprocessed datasets
                 ├── cache/            spike-time caches (uint8)
                 └── runs/             experiment outputs
```

### 3.2 Laptop prerequisites (keep tiny)

- **Preferred:** WSL2 + Ubuntu (gives `rsync`, `tmux`, SSH connection multiplexing). Use it if the
  user has ≥ 8 GB free on the laptop. Ask the user.
- **Fallback:** native Windows with Git for Windows (Git Bash) + built-in OpenSSH. Note: Windows
  OpenSSH does **not** support `ControlMaster`; every `ssh` call opens a new connection (slower).
- Python 3 on the laptop is needed only for `pip download` (no project env on the laptop).
- Do **not** install CUDA PyTorch on the laptop (≈ 2.5 GB). Unit tests run on the HPC.

### 3.3 SSH setup (one-time, with the user)

Claude Code cannot type passwords interactively, so **key-based authentication is required**.

```bash
# on the laptop
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_hpc -C "biovision"
# user appends ~/.ssh/id_ed25519_hpc.pub to <HPC_USER>@<HPC_HOST>:~/.ssh/authorized_keys
```

`~/.ssh/config` on the laptop:

```
Host hpc
    HostName <HPC_HOST>
    User <HPC_USER>
    IdentityFile ~/.ssh/id_ed25519_hpc
    ServerAliveInterval 60
    ServerAliveCountMax 5
    # WSL/Linux only (remove the next three lines on native Windows):
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 15m
```

Test: `ssh hpc 'hostname && nproc && free -g && df -h ~'`.

### 3.4 HPC inventory (run once, save output to `docs/hpc_inventory.txt`)

```bash
ssh hpc 'uname -a; ldd --version | head -1; python3 --version; which conda module tmux screen gcc;
         gcc --version | head -1; nproc; free -g; df -h <HPC_ROOT>; quota -s 2>/dev/null;
         which sbatch sinfo && sinfo'
```

Decisions that depend on it (record in `DECISIONS.md`):
- **glibc version** → which wheel platform tags are allowed (Section 3.5).
- **Slurm present?** → use `sbatch`; otherwise `tmux` (or `nohup setsid`) jobs.
- **Shared machine?** → if other users run jobs, cap at the core count the user allows.

### 3.5 Offline Python environment

**Step A — Python on the HPC.** If the HPC has Python ≥ 3.10 with `venv`, use it. Otherwise:

```bash
# laptop: stream the installer directly to the HPC (nothing stored on the laptop)
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
  | ssh hpc 'cat > <HPC_ROOT>/Miniforge3.sh'
ssh hpc 'bash <HPC_ROOT>/Miniforge3.sh -b -p <HPC_ROOT>/miniforge && rm <HPC_ROOT>/Miniforge3.sh
         && <HPC_ROOT>/miniforge/bin/python --version'
ssh hpc '<HPC_ROOT>/miniforge/bin/python -m venv <HPC_ROOT>/venv'
```

Write down the exact Python version (e.g. 3.12 → ABI tag `cp312`).

**Step B — wheels on the laptop** (`env/requirements.txt`, pin exact versions once resolved):

```
numpy  scipy  pandas  pyyaml  tqdm  matplotlib  pillow
scikit-learn  scikit-image  opencv-python-headless  h5py  hdf5plugin
pycocotools  numba  pytest  tensorboard
torch  torchvision        # CPU builds
```

```bash
PYV=312   # from Step A
mkdir -p wheels
# CPU PyTorch (its wheels may use the plain linux_x86_64 tag)
pip download torch torchvision --index-url https://download.pytorch.org/whl/cpu \
  --platform linux_x86_64 --platform manylinux_2_28_x86_64 --platform manylinux2014_x86_64 \
  --python-version $PYV --implementation cp --abi cp$PYV --only-binary=:all: -d wheels
# everything else
pip download -r env/requirements-nontorch.txt -d wheels \
  --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux_2_28_x86_64 \
  --platform linux_x86_64 --python-version $PYV --implementation cp --abi cp$PYV --only-binary=:all:
```

If a package has no wheel compatible with the HPC glibc, pick an older version and record it.

**Step C — pure-Python dependencies from source, vendored into the repo:**
- `third_party/SpykeTorch/` — clone `https://github.com/miladmozafari/SpykeTorch` on the laptop,
  commit it (its licence file included). It may need small patches for current PyTorch; keep
  patches as separate commits named `spyketorch: <fix>`.
- `third_party/psee_loader/` — Prophesee `.dat` loader from the Prophesee automotive dataset
  toolbox (Phase 5 only).
- `v2e` is **optional** (Phase 4). Our own event emulator (`retina/events.py`) is the default.

**Step D — transfer and install:**

```bash
tar czf - wheels | ssh hpc 'tar xzf - -C <HPC_ROOT>/'
ssh hpc 'source <HPC_ROOT>/venv/bin/activate &&
         pip install --no-index --find-links <HPC_ROOT>/wheels -r <HPC_ROOT>/src/env/requirements.txt &&
         pip install --no-deps -e <HPC_ROOT>/src/third_party/SpykeTorch &&
         pip freeze > <HPC_ROOT>/src/env/requirements-lock.txt && rm -rf <HPC_ROOT>/wheels'
rm -rf wheels   # laptop
```

Then copy `requirements-lock.txt` back and commit it.

### 3.6 Code sync (git over SSH; the HPC needs no internet)

```bash
ssh hpc 'git init --bare <HPC_ROOT>/repo.git && mkdir -p <HPC_ROOT>/src'
# post-receive hook: check out pushed branch into src/
ssh hpc 'cat > <HPC_ROOT>/repo.git/hooks/post-receive <<"EOF"
#!/bin/bash
while read old new ref; do
  git --work-tree=<HPC_ROOT>/src --git-dir=<HPC_ROOT>/repo.git checkout -f "${ref#refs/heads/}"
done
EOF
chmod +x <HPC_ROOT>/repo.git/hooks/post-receive'
git remote add hpc hpc:<HPC_ROOT>/repo.git
git push hpc <branch>
```

Rules: code changes are made on the laptop, committed, then pushed. **Never edit code on the HPC.**
Results come back with `tools/fetch.sh` (Section 3.8); only small files (JSON, CSV, PNG, MD)
travel back. Large outputs stay on the HPC.

### 3.7 Datasets: streaming download and storage budget

**Golden rule:** check the size first (`curl -sIL URL | grep -i content-length`), then stream:

```bash
curl -L <URL> | ssh hpc 'cat > <HPC_ROOT>/data/raw/<file>'                    # any file
curl -L <URL> | ssh hpc 'tar xzf - -C <HPC_ROOT>/data/raw/<name>'             # .tar.gz, extract on the fly
```

Verify checksums on the HPC when the source publishes them. Delete raw archives after
extraction and preprocessing (ask the user first the first time).

| Dataset | Phase | Source (verify) | Plan | Budget |
|---|---|---|---|---|
| MNIST | 0 (sanity) | torchvision mirrors | stream raw files | 0.1 GB |
| Caltech-101 | 0–1 | CaltechDATA (official) | full, colour | 0.3 GB |
| ETH-80 | 0–1 | official ETH-80 release (ask the user if unreachable) | full | 1 GB |
| Penn-Fudan Pedestrian | 2 | `https://www.cis.upenn.edu/~jshi/ped_html/PennFudanPed.zip` | full (170 images, masks) | 0.1 GB |
| COCO 2017 subset | 2, 4 | `annotations_trainval2017.zip` + per-image `coco_url` | classes person, car, bird; ≤ 3,000 train images per class; all val2017 images with these classes; letterboxed to 256² after download | 4 GB |
| MVSEC | 3–4 | `https://daniilidis-group.github.io/mvsec/` | indoor_flying1–3, outdoor_day1–2 (data + ground-truth files); check sizes first | ≤ 25 GB |
| Synthetic sequences (ours) | 3–5 | generated on the HPC | moving gratings/plaids, moving COCO cut-outs with occluders | ≤ 2 GB |
| Gen1 Automotive (Prophesee) | 5 | Prophesee official | **subset only**; convert chunk by chunk to compact tensors at labelled timestamps, delete raw | ≤ 25 GB |

COCO subset procedure (no full COCO download): stream the annotations zip to the HPC → a script
on the HPC selects image IDs and writes `coco_urls.txt` → copy that list to the laptop → the
laptop downloads images in batches of 500 into a temporary folder, streams each batch as a tar
to the HPC, and deletes it → the HPC letterboxes to 256² and stores PNG + a JSON index.

**Disk budget (100 GB):**

| Item | GB |
|---|---|
| miniforge + venv | 4 |
| repo + bare repo | < 1 |
| Phase 0–2 datasets | ~6 |
| MVSEC | ≤ 25 |
| Gen1 subset | ≤ 25 |
| synthetic data | ≤ 2 |
| spike-time caches | ≤ 10 |
| runs, logs, checkpoints | ≤ 5 |
| **headroom (never use)** | **≥ 15** |

**Cache format:** spike times as `uint8`, `NO_SPIKE = 255`, shape `[C, H, W]`, compressed
`.npz`. Example: C1 output 12×128² = 196 KB per image. Never cache full binary `[T, C, H, W]` tensors.
Caches are disposable and must be regenerable from config + seed.

### 3.8 Helper scripts (create these first, in `tools/`)

| Script | What it does |
|---|---|
| `hpc.env` | `HPC_ROOT=...`, thread defaults, Python path |
| `remote.sh <cmd>` | `ssh hpc "cd $HPC_ROOT/src && source $HPC_ROOT/venv/bin/activate && <cmd>"` |
| `submit.sh <name> <threads> <cmd>` | starts a detached job (`sbatch` if Slurm, else `tmux new -d -s <name>`), sets `OMP_NUM_THREADS`/`MKL_NUM_THREADS`, writes `runs/<phase>/<date>_<name>/{cmd.txt,log.txt,pid}` |
| `status.sh` | lists running jobs, last 20 log lines of each, CPU load |
| `fetch.sh <run_dir>` | copies `metrics.json`, `*.csv`, `figs/*.png`, `REPORT*.md` back to `results/<run_dir>` on the laptop |
| `hpc_health.sh` | `du -sh` per top-level folder, total vs 100 GB cap, free RAM, load; **exits non-zero above 85 GB** |
| `push.sh` | `git push hpc <current-branch>` |

Jobs must survive a dropped SSH connection (tmux/Slurm/nohup). Claude Code polls with `status.sh`
at sensible intervals (minutes, not seconds) and never keeps an SSH session open for a running job.

### 3.9 Using 44 cores well

- STDP learning is **sequential over samples** (batch size 1). Run it in one process with
  `torch.set_num_threads(8)`; more threads rarely help on 256² inputs.
- **Feature extraction / evaluation** with frozen layers is embarrassingly parallel:
  `multiprocessing.Pool(40)` with `torch.set_num_threads(1)` in each worker.
- Run **independent experiments in parallel** (seeds, ablations): e.g. 5 jobs × 8 threads.
- Always set `OMP_NUM_THREADS` explicitly; use `nice -n 10` if the machine is shared.
- Profile once per phase (`time`, `torch.profiler`) and record images/s in the report.

---

## 4. Architecture specification

The figure `docs/bio-spiking-visual-system.drawio` is the visual version of this section.
Notation: `C×H×W` = maps × height × width. All learned layers are **non-leaky integrate-and-fire
(IF)** neurons; potential `V_i(t) = Σ_{s≤t} Σ_j w_ij·x_j(s)`; neuron fires once when `V_i ≥ θ_i`,
then is silent for the rest of the wave.

### 4.1 Time model and waves

- A **wave** is one pass of the image (or one time window of video/events) through the network.
- Simulation (SpykeTorch convention): each wave uses a shared time axis of `T = 15` steps; input
  spikes are placed on it; each layer fires at the first step its accumulated potential crosses
  threshold (zero synaptic delay). Config option `stage_delay` (default 0) adds one step per stage.
- Hardware time model used for latency reporting: each stage may need up to `T_l = 15` steps,
  step `Δt = 0.5 ms` → worst-case wave latency `L_wave = Σ_l T_l·Δt` ≈ 46 ms for wave 1 and
  ≈ 91 ms for wave 2 (both within the 100 ms target). Report both the measured decision step and
  this worst case.
- Wave 1: feed-forward only (`a(x) = 0`). Wave n+1 receives the feedback computed at the end of
  wave n: attention map `a(x)`, goal `g`, border-ownership evidence `Φ±`.
- Video/events: one wave per time window (default 20 ms of events, configurable).

### 4.2 Input

- RGB image letterboxed to 256², pyramid of 3 levels: 256², 181², 128² (each ÷√2).
- Cone approximations: `L ≈ R`, `M ≈ G`, `S ≈ B`, luminance `Y = (L+M)/2`.
- Weights are **shared across scales** (scale invariance by construction).

### 4.3 Retina emulator (fixed, outside the learned network) — `retina/`

Per scale:

| Channel | Maps | Filter | Notes |
|---|---|---|---|
| P (Parvo) | 4 | L/M opponent DoG, centre σ_c = 1, surround σ_s = 3σ_c: L+/M− and M+/L−, each ON and OFF | fine detail, colour |
| K (Konio) | 2 | S − Y, coextensive (centre and surround same size), σ_k = 2σ_c, ON and OFF | blue–yellow |
| M (Magno) | 2 | log-intensity events + DoG with σ = 3σ_c, ON and OFF | motion, coarse |

Total: 8 maps per scale × 3 scales = 24 maps.

**Divisive normalisation (illumination invariance):** `r = ⌊D⌋₊ / (ε + G∗Y)`, where `D` is the DoG
response, `⌊·⌋₊` keeps the positive part (ON; OFF uses `−D`), `G∗Y` is the local mean luminance
(Gaussian blur of `Y`), and `ε` is a small constant.

**Intensity-to-latency / rank-order code:** `t = round((T−1)·(1 − r/r_max))`; `r_max` is the
largest response in that channel and scale; if `r < θ_in` there is no spike. Strong responses fire
first; multiplying the image brightness does not change the order. Option `coding: rank` uses the
pure rank instead (spike time from the sorted order, quantised to `T` steps).

**Magno events:** a pixel emits an event when `|log Y(t) − log Y_ref| ≥ C`, contrast threshold
`C ∈ [0.15, 0.3]`, then `Y_ref` is reset. ON for increase, OFF for decrease. Spike time = time
step of the first event in the wave window. For **static images**, generate events with
microsaccades: 4 shifts of 1–2 px (right, up, left, down) at steps 0, 3, 6, 9.
For MVSEC/Gen1, real events replace the emulator (first event per pixel and polarity per window).

### 4.4 LGN — `lgn/` (relay, no learning)

- Three sheets P, K, M, 1:1 relay (`w = 1`), same sizes as the retina maps.
- Attention gate: `t_out = clip(t_in − δ·a(x), 0, T)`, `δ = 3` steps. `a(x) > 0` (attended) →
  spikes earlier → they win the WTA races downstream. `a(x) < 0` → spikes later (TRN-like
  suppression); pushed beyond `T` means no spike.
- Virtual fovea (from wave 2): the finest pyramid level (256²) passes only where `a(x) > a_min`;
  coarser levels pass everywhere. Wave 1 passes all levels.

### 4.5 V1 — `v1/`

**S1 (simple cells), ventral input:**
- 12 maps, kernel 5×5×6 on P(4) ⊕ K(2), stride 1, padding 2.
- **W_S1: 12×6×5×5 = 1,800 weights**, shared across positions and scales.
- IF threshold `θ_1` (calibrated, Section 5.4). Feature-wise WTA at each position (only the
  earliest map may fire at a position); k-WTA with inhibition radius during learning.
- Learning: flat STDP (`a⁺ ≈ 0.004`, `a⁻ ≈ 0.003`), or fixed Gabor bank as baseline/ablation.
- Output: 12 × 256² (per scale).

**C1 (complex cells):** max-pool 2×2 stride 2 (earliest spike wins, `t_C = min t_S`) → resample all
three scales to a 128² grid → min over scales. Keep an `argmin_scale` map (needed for size and
depth cues). Output: 12 × 128².

**V1 motion (direction-selective), dorsal input (M sheet, 256² level):**
- 24 maps = 8 directions × 3 speeds.
- Coincidence detector: `V = w₁·e(x − d_θ, t − Δ) + w₂·e(x, t)`. `e(x, t)` is an event at pixel `x`
  and step `t`; `d_θ` is a 1-px displacement in direction `θ`; `Δ ∈ {1, 2, 4}` steps is the delay;
  speed `v = |d|/Δ`. Thresholds satisfy `w₁, w₂ < θ < w₁ + w₂`, so the neuron fires only when both
  inputs arrive together, i.e. when something moved by `d_θ` in `Δ` steps.
- Delays fixed; weights learned with exponential STDP (`A±`, `τ±`).
- Output 24 × 256². **C1m:** max-pool 2×2 → 24 × 128².

### 4.6 V2 — `v2/`

| Layer | Maps | Kernel / input | Weights | Role | Output |
|---|---|---|---|---|---|
| S2t (thin stripe) | 16 | 5×5×12 on C1 | 16×12×5×5 = 4,800 | surface colour | 16 × 128² |
| S2p (pale stripe) | 16 | 5×5×12 on C1 | 16×12×5×5 = 4,800 | corners, junctions, form | 16 × 128² |
| S2k (thick stripe) | 16 | 5×5×24 on C1m | 16×24×5×5 = 9,600 | pooled motion | 16 × 128² |
| C2t / C2p / C2k | 16 each | max-pool 2×2 | — | complex cells | 16 × 64² each |

All S2 layers: IF, feature WTA, flat STDP (S2k: STDP).
**Specialisation check:** if S2t and S2p learn redundant features (mean max cross-correlation of
their weight maps > 0.8), then (a) feed S2t from the colour-dominant S1 maps and S2p from the
orientation-dominant ones, or (b) add cross-inhibition between them. Record the choice.

**Border ownership (Phase 5), in the pale stripe:** 8 maps = 4 orientations × 2 sides.
`B± = E·⌊Φ± − Φ∓⌋₊`. `E` is edge strength at that orientation (from C1), `Φ+` and `Φ−` are the
evidence that the figure lies on side + or side − of the edge, fed back from V4 in wave n+1;
`⌊·⌋₊` keeps the positive part, so only the winning side gets a response.

### 4.7 Ventral stream — `ventral/`

| Layer | Maps | Kernel / input | Weights | Learning | Output |
|---|---|---|---|---|---|
| V4 S3 | 64 | 5×5×32 on C2t ⊕ C2p | 64×32×5×5 = 51,200 | flat STDP | 64 × 64² |
| V4 C3 | 64 | max-pool 2×2 | — | — | 64 × 32² |
| IT S4 | 128 | 3×3×64 | 128×64×3×3 = 73,728 | STDP, then R-STDP fine-tune | 128 × 32² |
| IT C4 | 128 | max-pool 2×2 | — | — | 128 × 16², **retinotopic, no global pooling** |

**Location-wise readout D_c(u)** (replaces the detection head):
- `N_c` class maps, kernel 3×3×128 on C4, shared over locations `u` (16² grid, one cell = 16 px).
- **W_D: N_c×128×3×3.**
- At each cell, the earliest class spike wins; **silence = background**.
- Cell label: class `c` if ≥ 50 % of the cell's pixels lie in a mask of class `c`; otherwise background.
- R-STDP reward per cell where map `c*` fired: `+1` if the label is `c*`; `−1` if the label is
  another class; `−λ_bg` if the label is background. `λ_bg` balances the many background cells.
- Adaptive rates (Mozafari 2018): reward rate `∝ N_miss/N`, punishment rate `∝ N_hit/N`;
  dropout on readout maps during training.
- Confidence of a detection: `1 − t/T` (earlier spike = more confident).

**Ultra-rapid gist (wave 1):** `t_c^gist = min_u t(D_c(u))`: "is class c anywhere in the scene?".

### 4.8 Dorsal stream — `dorsal/`

- **MT (pattern cells):** 24 velocity maps (8 directions × 3 speeds), kernel 5×5×16 on C2k, stride 2
  → 32². **W_MT: 24×16×5×5 = 9,600.** Intersection of constraints:
  `V_v = Σ [α·s_{θ, v·n} − β·s_{θ+π, v·n}]`. `s_{θ, v·n}` is the input from component cells whose
  direction `θ` and normal speed match the projection of velocity `v` on the edge normal `n`; the
  opposite direction `θ+π` inhibits; `α, β > 0` are weights. This solves the aperture problem.
  Exponential STDP; velocity WTA gives `v(u)` per location.
- **V3 (motion contrast):** `MC = ‖v − v̄_surr‖`, centre 3×3, surround 9×9 → 1 × 32²; salience
  and mask of independently moving objects.
- **MST (fixed templates):** expansion, contraction, rotation, translation.
  Expansion score `E(x₀) = Σ_x v(x)·(x − x₀)/‖x − x₀‖`; the focus of expansion
  `x₀* = argmax E` gives the heading. Looming per object: `τ = φ/φ̇` (`φ` = angular size,
  `φ̇` = its rate of change) = time-to-contact.

### 4.9 Monocular depth fusion — `depth/` (algorithmic module, Phase 4)

| Cue | Formula | Symbols |
|---|---|---|
| ① occlusion | depth order from border ownership B± | figure side is nearer |
| ② familiar size | `Z = f·H_c/h` | `f` focal length (px), `H_c` typical real height of class `c` (from the readout), `h` object height in image (px) |
| ③ height in field | `Z = f·h_cam/(y_b − y_h)` | `h_cam` camera height, `y_b` image row of the object's base, `y_h` horizon row |
| ④ motion parallax | `Z = f·T⊥/‖v_trans‖` | `T⊥` camera translation speed perpendicular to the ray, `v_trans` translational image velocity (rotation removed using MST) |
| ⑤ time-to-contact | `τ` from MST | approach without metric depth |

Fusion: `Ẑ_k = Σ_m c_{m,k}·Z_{m,k} / Σ_m c_{m,k}`, where `c_{m,k}` is the confidence of cue `m` for
object `k` (0 if the cue is unavailable). Monocular metric depth is only defined up to scale unless
`H_c`, `h_cam` or `T⊥` is known; report scale-aligned metrics.

### 4.10 Selection, goal, memory — `select/`

- **Attention map → LGN:** `a(x) = clip(Σ_k exp(−‖x − p_k‖²/2ρ_k²) − γ, −1, 1)`, where `p_k` is the
  position of selected object `k`, `ρ_k` its spatial extent, `γ` a baseline suppression of
  unattended regions.
- **Priority map (LIP), spiking, 1 × 32²:** `P = α_b·S + α_t·F_g − α_r·R`. `S` = bottom-up salience
  (colour/orientation contrast + motion contrast MC), `F_g` = readout map of the goal class `g`
  (upsampled 16²→32²), `R` = inhibition of return (positions already selected), `α` = weights.
  k-WTA with inhibition radius `r` selects up to `K` objects. **This replaces NMS inside the network.**
- **PFC (algorithmic module):** holds the goal `g` (top-down bias `F_g`) and object files
  `j = (p_j, v_j, f_j, id_j)` (`f_j` = IT feature vector). Matching cost
  `cost(k, j) = ‖p_k − (p_j + v_j·Δt)‖ + λ·(1 − sim(f_k, f_j))`, solved with the Hungarian
  algorithm (`scipy.optimize.linear_sum_assignment`). An unmatched file is kept for `N` waves at its
  predicted position (**object permanence**). PFC issues the reward `r` for R-STDP.
- PFC and depth fusion are **non-spiking algorithmic modules** in this project; mark them as such
  in the paper (future work: spiking versions).

### 4.11 Output

Object token per selected object, every wave: `o_k = (p_k, M_k, c_k, Ẑ_k, v_k, τ_k, id_k)`.
`M_k` = mask: before Phase 5, the connected component of class-`c_k` readout cells around `p_k`
(upsampled, refined with S2p edges); in Phase 5, grouping from `p_k` along border ownership.
Box for mAP = min/max of `M_k`.

### 4.12 Parameter count summary

| Layer | Weights |
|---|---|
| S1 | 1,800 |
| S2t, S2p | 4,800 each |
| S2k | 9,600 |
| S3 | 51,200 |
| S4 | 73,728 |
| MT | 9,600 |
| D | N_c × 1,152 |
| motion V1 | 24 × 2 taps (+ learned weights) |

Total ≈ 156k + 1,152·N_c. This is tiny compared with YOLO; mention it in every report.

---

## 5. Learning rules — `learning/`

| Rule | Where | Definition |
|---|---|---|
| Flat STDP (Kheradpisheh 2018) | S1, S2t, S2p, S3, S4 (pre-training) | if pre fired before or with post: `Δw = a⁺·w(1−w)`; else `Δw = −a⁻·w(1−w)`. Depends only on spike order; the factor `w(1−w)` keeps `w` in [0,1] and drives it to 0 or 1 |
| Exponential STDP | V1 motion, S2k, MT | `Δw = A⁺·exp(−Δt/τ⁺)` for `Δt = t_post − t_pre ≥ 0`, `−A⁻·exp(Δt/τ⁻)` otherwise; precise timing matters for motion |
| R-STDP (Mozafari 2018) | readout D, IT fine-tune | reward → apply STDP; punishment → apply anti-STDP; adaptive rates from hit/miss counts |
| Fixed templates | MST | no learning |
| SDSP (Brader, Senn & Fusi 2007) | optional, Phase 5 ablation | spike-driven, bistable synapses; a reward-modulated variant (R-SDSP) is a possible novel contribution — only if time allows |

### 5.1 Protocol
- **Layer-wise training:** train S1 → freeze → train S2* → freeze → S3 → S4 → readout.
- During learning: k-WTA (`k` winners per image with inhibition radius, so different maps learn
  different features); one STDP update per winner; batch size 1.
- **Convergence index** per layer: `C_l = (1/n_w)·Σ w(1−w)`. `n_w` is the number of weights. When
  `C_l < 0.01` almost every weight is near 0 or 1 → stop and freeze the layer.
- Learning-rate schedule: follow the SpykeTorch examples/paper; record it.

### 5.2 Homeostasis
Adaptive threshold per map: `θ_i ← θ_i + η_θ·(z_i − ρ)`, where `z_i = 1` if map `i` fired on this
sample (else 0), `ρ` is the target firing probability, `η_θ` a small rate. Prevents dead and
dominant maps.

### 5.3 Sparsity target
Fraction of neurons that fire per wave in each S layer should be in **[1 %, 10 %]**. Report it
per layer in every phase.

### 5.4 Threshold calibration
Before learning, set `θ_l` so that ~5 % of positions fire on 200 held-out images; then homeostasis.

---

## 6. Code structure and conventions

```
biovision/
  retina/      dog.py  latency.py  events.py  microsaccade.py
  lgn/         relay.py  attention_gate.py
  v1/          s1.py  c1.py  motion.py
  v2/          stripes.py  border_ownership.py
  ventral/     v4.py  it.py  readout.py
  dorsal/      mt.py  v3.py  mst.py
  depth/       cues.py  fusion.py
  select/      priority.py  pfc.py  tokens.py  masks.py
  learning/    flat_stdp.py  exp_stdp.py  rstdp.py  homeostasis.py  convergence.py
  engine/      spikes.py  wave.py  pipeline.py
  data/        caltech.py  eth80.py  pennfudan.py  coco_subset.py  mvsec.py  gen1.py  synthetic.py
  eval/        metrics.py  probes.py  ablation.py  fault_inject.py  energy.py  visualize.py
configs/       phase0_*.yaml ... phase5_*.yaml
tests/         one test file per module
tools/         Section 3.8
docs/          figure, hpc_inventory.txt, paper notes
reports/       phase0/ ... phase5/   (REPORT.md + figures; committed)
third_party/   SpykeTorch, psee_loader
CLAUDE.md  STATUS.md  DECISIONS.md
```

Conventions:
- **Spike-time tensor** (`engine/spikes.py`): `torch.uint8`, `[C, H, W]`, `NO_SPIKE = 255`.
  Converters `to_binary(t, T) -> [T, C, H, W]` (cumulative, SpykeTorch format) and back. One code path.
- **Wave engine** (`engine/wave.py`): loops over waves; holds `feedback = {a, g, phi}` from wave n
  and injects it in wave n+1. Every module has `forward(inputs, feedback) -> outputs`.
- Every module is configurable from YAML; no magic numbers in code.
- Seeds: `torch`, `numpy`, `random` from config; main results use seeds 0, 1, 2 (mean ± std).
- Every run directory contains `config.yaml`, `git_commit.txt`, `log.txt`, `metrics.json`, `figs/`.
- Global registry `results/registry.csv`: run, phase, config hash, seed, key metrics.
- Type hints, docstrings that cite the formula in Section 4, `pytest` for every module.
- Git: branch `phase-N`, tag `gate-N` when the user approves the gate.

### 6.1 Unit tests that must exist before Phase 1
- DoG kernel sums to ~0; uniform image → no spikes.
- Latency coding is monotonic; brightness ×0.25…×4 leaves spike order unchanged.
- k-WTA / feature WTA: at most one winner per position; winners respect the inhibition radius.
- STDP sign correct on a synthetic pre/post pair; `w` stays in [0,1].
- Wave engine: no neuron fires more than once per wave.
- Spike-time ↔ binary conversion is lossless.

---

## 7. Workflow (how the plan advances)

### 7.1 Loop for every task
1. Write/modify code + unit tests on the laptop → commit → `tools/push.sh`.
2. Run tests on the HPC (`tools/remote.sh pytest -q`).
3. Small smoke run (≤ 5 min, tiny subset) → check outputs → then the full run with `submit.sh`.
4. `fetch.sh` the results; **look at every figure** (read the PNGs); check against the phase's
   verification checklist; write findings into the run's `REPORT.md`.
5. Update `STATUS.md` (done / next / blockers) and `results/registry.csv`.

### 7.2 Gates
At the end of each phase: write `reports/phaseN/REPORT.md` (template, Section 11), list which
gate criteria passed, then **stop and ask the user**. If a criterion fails, propose 2–3 options
with a cost estimate; do not move on silently.

### 7.3 Living files
- `STATUS.md`: phase, task list with checkboxes, current runs, last result, next step.
- `DECISIONS.md`: dated decisions with reasons (environment, deviations from this spec, hyperparameters).

### 7.4 Time plan (estimates)
| Phase | Weeks |
|---|---|
| Setup (Section 3) | 1 |
| 0 | 2–3 |
| 1 | 4–6 |
| 2 | 6–8 (highest risk) |
| 3 | 6–8 (can run in parallel with Phase 2 if Phase 2 stalls) |
| 4 | 6–8 |
| 5 | 6–8 |

---

## 8. Phases

Each phase lists: goal, data, build tasks, experiments, required outputs, verification
checklist, red flags, gate.

### Setup phase (before Phase 0)
- **Tasks:** Sections 3.3–3.8; repo skeleton (Section 6); `STATUS.md`, `DECISIONS.md`;
  unit tests of Section 6.1 (those not depending on later modules).
- **Outputs:** `docs/hpc_inventory.txt`, `env/requirements-lock.txt`, working `tools/*`,
  disk report.
- **Gate S:** `ssh hpc` works without password; `pytest` passes on the HPC; disk < 10 GB used.

---

### Phase 0 — Reproduce Kheradpisheh et al. 2018 with SpykeTorch

**Goal:** prove the toolchain and our learning implementation are correct before changing anything.

**Data:** MNIST (sanity), Caltech-101 face/motorbike (and the 4-class variant used in our plan),
ETH-80.

**Tasks:**
1. Run SpykeTorch's own example scripts (if present) unchanged; record results.
2. Re-implement the Kheradpisheh SDNN (grey-scale DoG → S1/C1/S2/C2/S3/C3, flat STDP, global max
   pooling + linear SVM probe) using **our** modules (`retina/`, `learning/flat_stdp.py`,
   `engine/`) so the same code is reused later.
3. Implement the convergence index and the feature visualisation.

**Targets:** take the reported accuracies from the paper itself (ask the user for the PDF if
needed). From memory, to be verified: ≈ 99.1 % Caltech face/motorbike, ≈ 82.8 % ETH-80,
≈ 98.4 % MNIST. Do not hard-code these numbers in the report without checking them against the paper.

**Required outputs (`reports/phase0/`):**
- Table: dataset | reported | ours (mean ± std, 3 seeds) | spikes/image | images/s.
- Learned S1 and S2 features (grid images); convergence curve `C_l` vs iterations per layer.
- Confusion matrices; per-layer sparsity.

**Verification checklist:**
- S1 features look like oriented edges / DoG-like blobs; no two features identical.
- `C_l` decreases monotonically and falls below 0.01.
- Sparsity per S layer in [1 %, 10 %].
- Results within ~2 percentage points of the paper; otherwise explain why.

**Red flags:** all weights → 1 (threshold too low); silent layers (too high); all maps learn
the same feature (WTA/k-WTA broken); accuracy at chance (labels or pooling bug).

**Gate 0:** reproduction within tolerance (or user accepts the explained gap).

---

### Phase 1 — Three-channel retina and colour ventral stream up to IT

**Goal:** the full retina emulator (P, K, M with microsaccades), LGN relay without attention, V1
S1/C1, V2 S2t/S2p/C2, V4 S3/C3, IT S4/C4 — classification only.

**Data:** Caltech-101 (colour subset, 4 classes and then more), ETH-80 colour.

**Tasks:**
1. `retina/`: DoG banks (Section 4.3), divisive normalisation, latency and rank coding, magno
   events, microsaccades, 3-level pyramid.
2. `lgn/relay.py` (attention gate implemented but `a = 0`).
3. Layers S1→C4 with weight sharing across scales, scale pooling in C1 with `argmin_scale`.
4. Classification readouts: (a) linear SVM probe on globally min-pooled C4 spike times (for
   comparison with Phase 0), (b) R-STDP global readout with `N_c` neurons (the biological one).

**Experiments:**
- Grey (Phase 0 pipeline) vs P only vs P+K vs P+K+M(microsaccade-driven, through S2k only as a
  side check).
- Learned S1 vs fixed Gabor S1.
- **Invariance tests** on the test set: brightness ×{0.25, 0.5, 2, 4} and gamma {0.5, 2};
  rescale {0.7, 0.85, 1.2, 1.4}; translation ±{8, 16, 32} px.
- Latency vs rank coding.

**Required outputs (`reports/phase1/`):**
- Spike-latency maps for each retinal channel on 4 example images (colour-coded by time).
- Feature grids for S1 (colour shown via opponent → RGB mapping), S2t, S2p; back-projected
  preferred stimuli for S3/S4 (Kheradpisheh visualisation method).
- Tables: accuracy per channel configuration; invariance curves (accuracy vs perturbation).
- Sparsity per layer, spikes per image, SOPs per image, `C_l` curves, S2t/S2p redundancy score.

**Verification checklist:**
- Colour (P+K) ≥ grey with a consistent gain over 3 seeds; report the K contribution separately.
- Accuracy drop under brightness/gamma changes ≤ 1 percentage point (normalisation works).
- Scale and translation curves are flat around the training scale.
- No dead maps (every map fires on ≥ 1 % of images).

**Red flags:** colour hurts accuracy (opponent maps mis-signed); brightness changes the spike
order (normalisation bug); S2t ≈ S2p (apply Section 4.6 fix).

**Gate 1:** colour gain shown, invariance shown, all layers converged.

---

### Phase 2 — Location-wise R-STDP readout, priority map, detection outputs

**Goal:** turn recognition into "what is where" without box regression.

**Data:** Penn-Fudan (1 class: pedestrian; split 120 train / 50 test, flips and small scale
augmentation), then the COCO subset (person, car, bird).

**Tasks:**
1. `ventral/readout.py`: location-wise readout D (Section 4.7), cell labels from masks,
   R-STDP with `λ_bg`, adaptive rates, dropout.
2. `select/priority.py`: bottom-up salience S (colour/orientation contrast from C1/C2), `F_g`,
   k-WTA with inhibition radius, IOR inside a wave.
3. `select/masks.py` + `select/tokens.py`: approximate masks, tokens, boxes, confidences.
4. Evaluation: COCO-style mAP@0.5 and mAP@[0.5:0.95] with `pycocotools`; pointing accuracy
   (selected `p_k` inside an object of the right class); per-cell precision/recall;
   gist (image-level) accuracy; background-silence rate.

**Key points:**
- Start with **one class** (Penn-Fudan). Only when the readout fires on objects and stays silent on
  background, add classes.
- Background dominates the cells (most cells are background). If the network collapses to
  "always silent", raise reward on hits, lower `λ_bg`, balance sampling of object vs background
  cells; if it fires everywhere, raise `λ_bg`.
- Baselines for context: (a) centre-prior box, (b) salience-only (no readout) boxes. Optional: a tiny
  conventional detector on the same subset at 256², trained only for context (ask the user before
  installing extra packages).

**Required outputs (`reports/phase2/`):**
- Overlays on 12 test images: readout cells coloured by class and by spike time, selected `p_k`,
  masks, derived boxes, ground truth.
- Tables: mAP@0.5, mAP@[.5:.95], pointing accuracy, cell P/R, gist accuracy, background-silence
  rate; spikes/image; decision step; worst-case latency.
- Curves: readout hit/miss/false-alarm rates over training; effect of `λ_bg` (sweep).

**Verification checklist:**
- Background-silence rate between 70 % and 95 % (neither collapsed nor saturated).
- Pointing accuracy clearly above the centre-prior baseline.
- mAP above both baselines on Penn-Fudan.
- Earlier spikes ⇒ higher precision (confidence is calibrated in rank).

**Red flags:** readout silent everywhere; one class wins every cell; boxes all the same size (mask
step broken).

**Gate 2:** readout works on Penn-Fudan above baselines and is reported on the COCO subset.
(This phase alone can support a conference paper: location-wise reward-modulated readout in a
TTFS STDP network.)

---

### Phase 3 — Dorsal stream and consecutive waves (video/events)

**Goal:** direction and speed per location, motion contrast, heading, time-to-contact.

**Data:** synthetic stimuli first (drifting gratings, moving bars, plaids, expanding dots), then
MVSEC (real events; optical-flow ground truth from the MVSEC flow release, depth and odometry).

**Tasks:**
1. `v1/motion.py` coincidence detectors (Section 4.5), exponential STDP; C1m; S2k/C2k; MT with
   IOC; V3; MST templates.
2. `engine/wave.py`: consecutive waves over event windows (default 20 ms).
3. `data/mvsec.py`: read events, convert each window to first-event spike times per pixel and
   polarity, downsample to our grid; align ground truth flow to 32².

**Experiments and metrics:**
- Direction tuning (polar plots) and speed tuning per V1 motion map and MT map; direction
  selectivity index `DSI = (R_pref − R_null)/(R_pref + R_null)` (`R` = response, e.g. fraction of
  cells firing / inverse latency).
- Plaids: pattern vs component classification of MT cells (partial-correlation method of
  Movshon et al. 1985).
- MVSEC: average endpoint error (AEE) and % outliers on pixels with events, at 32²; compare as
  context with published spiking optical-flow results (numbers taken from the papers).
- Heading error (MST focus of expansion vs odometry); TTC on approaching objects.

**Required outputs (`reports/phase3/`):** tuning plots, plaid scatter (Zp vs Zc), flow fields
overlaid on event frames, error maps, tables of AEE/outliers/heading error, spikes per window.

**Verification checklist:** majority of motion maps have DSI > 0.5; MT contains pattern cells on
plaids; AEE reported per sequence; static images with microsaccades do not produce spurious
coherent motion in MT.

**Gate 3:** motion selectivity emerges and MVSEC flow is measured.

---

### Phase 4 — Attention feedback, working memory, monocular depth

**Goal:** close the loop: priority → `a(x)` → LGN in wave n+1; PFC goal and object files; depth.

**Data:** COCO subset (cluttered images, static, several waves with microsaccades); MVSEC (depth
ground truth, odometry); our synthetic "moving COCO cut-outs with occluders" (exact identities,
occlusion and depth order); optional v2e videos.

**Tasks:**
1. `lgn/attention_gate.py` live; virtual fovea; `select/pfc.py` (goal, object files, Hungarian
   matching, permanence for `N` waves, reward signal); `depth/` cues and fusion.
2. `data/synthetic.py`: generator for occlusion/permanence sequences with ground truth.

**Experiments and metrics:**
- **Wave 2 vs wave 1** on cluttered COCO images (images with ≥ 3 objects): mAP, pointing accuracy;
  paired test across images (Wilcoxon).
- Goal-directed search: with goal `g`, how many waves until the goal object is selected.
- Permanence on synthetic sequences: ID switches, IDF1, recovery after occlusion of 1…N waves.
- Depth: pairwise depth-order accuracy; abs-rel and RMSE-log after median scaling on MVSEC; per-cue
  ablation (drop each cue).

**Required outputs (`reports/phase4/`):** wave-1 vs wave-2 overlays (attention map, priority
map, selections); search-time histogram; ID timelines through occlusion; depth maps vs ground
truth; tables for all metrics above.

**Verification checklist:** wave 2 significantly better than wave 1 in clutter; IOR yields `K`
distinct objects (no repeats); IDs survive short occlusions; depth order clearly above chance
(50 %).

**Gate 4:** attention benefit shown (main result of the journal paper), permanence and depth reported.

---

### Phase 5 — Border ownership, masks, final comparison, ablations, faults

**Goal:** finish the model and produce the paper's full evidence.

**Data:** synthetic figure-ground stimuli (squares, overlapping shapes); COCO subset; Gen1 subset
(events, cars and pedestrians).

**Tasks:**
1. `v2/border_ownership.py` with V4 feedback `Φ±` (wave n+1); mask grouping along B±.
2. `data/gen1.py` with chunked conversion (Section 3.7).
3. `eval/ablation.py`, `eval/fault_inject.py`, `eval/energy.py`.

**Ablations (all with 3 seeds):**
1. TTFS vs rate coding (accuracy, spikes, latency).
2. All three channels vs removing each of P, K, M.
3. With vs without attention feedback (clutter subset).
4. Learned STDP V1 vs fixed Gabor V1.
5. Illumination invariance (brightness/gamma sweep).
6. Stuck-at faults (stuck-at-0 / stuck-at-1 on weights; dead / always-firing neurons) at rates
   0.1 %, 0.5 %, 1 %, 2 %, 5 %, 10 %, injected **per module**; sensitivity curves.
7. Optional: SDSP / R-SDSP vs STDP / R-STDP.

**Final metrics:** mAP on Gen1 subset and COCO subset; spikes per inference; SOPs; energy proxy
(SOPs × energy per synaptic operation, constant cited from literature, stated explicitly);
decision step and worst-case latency; parameter count; context table of published spiking
detectors on Gen1 (numbers copied from their papers with citations — the user verifies).

**Required outputs (`reports/phase5/`):** border-ownership maps on synthetic stimuli; masks vs
ground truth (IoU); full ablation tables; fault-sensitivity plots per module; final comparison
table; `reports/final/PAPER_FIGURES.md` listing every figure/table with its source run.

**Gate 5:** all tables complete, every number traceable to a run directory.

---

## 9. Metric definitions (`eval/metrics.py`)

| Metric | Definition |
|---|---|
| Accuracy | top-1 on the test split, mean ± std over 3 seeds |
| mAP@0.5, mAP@[.5:.95] | COCO protocol via `pycocotools`, boxes from masks, score `1 − t/T` |
| Pointing accuracy | fraction of selected positions `p_k` inside a ground-truth object of class `c_k` |
| Background-silence rate | fraction of background cells where no readout map fires |
| Sparsity | fraction of neurons that fire per wave, per layer |
| Spikes / image | total spikes over all layers in one wave |
| SOPs | Σ over spikes of the neuron's fan-out |
| Decision step | earliest readout spike time (steps) |
| Worst-case latency | `Σ_l T_l·Δt`, `Δt = 0.5 ms` |
| AEE | mean ‖flow_pred − flow_gt‖ over valid pixels |
| DSI | `(R_pref − R_null)/(R_pref + R_null)` |
| Depth order | fraction of object pairs with correct nearer/farther order |
| abs-rel | mean `|Z − Z_gt|/Z_gt` after median scaling |
| IDF1, ID switches | standard multi-object tracking definitions |

---

## 10. Risks and mitigations

| Risk | Effect | Mitigation |
|---|---|---|
| STDP quality drops in deep layers / real images | low COCO accuracy | layer-wise training, homeostasis, few classes first |
| Background dominates the readout | network always silent | `λ_bg`, balanced cell sampling, adaptive rates |
| Border ownership / masks complex | schedule slip | postponed to Phase 5; approximate masks before |
| 3-level pyramid × several waves is slow on CPU | long training | start at 128² with one scale; parallel feature extraction |
| Disk budget (MVSEC, Gen1) | exceeds 100 GB | subsets, chunked conversion, uint8 caches, `hpc_health.sh` |
| SpykeTorch incompatible with current PyTorch | blocked Phase 0 | vendored copy with small, documented patches |
| Unfair comparison with YOLO | reviewers attack mAP | always report accuracy + energy + latency + robustness + extra outputs |

---

## 11. Report template (`reports/phaseN/REPORT.md`)

```
# Phase N report — <title>
## Summary (3–5 sentences: what was built, main numbers, gate status)
## Setup (data splits, configs, commit, seeds, runtime, threads)
## Results (tables with mean ± std; every number links to its run directory)
## Figures (with one-line interpretation each)
## Verification checklist (each item: PASS / FAIL + evidence)
## Red flags observed and how they were handled
## Deviations from CLAUDE.md (link to DECISIONS.md entries)
## Gate N: criteria and status → waiting for user approval
## Next steps
```

---

## 12. Do / Don't

**Do**
- Keep everything reproducible: config + commit + seed for every number.
- Look at the figures yourself before writing conclusions.
- Prefer small smoke runs before long runs; estimate runtime from the smoke run.
- Keep the laptop clean: no datasets, no large wheels left behind.
- Report negative results honestly.

**Don't**
- Don't use backpropagation inside the spiking network or rate coding outside the ablation.
- Don't let any neuron fire twice in one wave.
- Don't train on boxes.
- Don't download directly on the HPC (it is offline) and don't store datasets on the laptop.
- Don't exceed 85 GB on the HPC without asking; never touch files outside `<HPC_ROOT>`.
- Don't change Section 4 without a `DECISIONS.md` entry and user approval.
- Don't invent published numbers; every external number needs a citation the user can check.

---

## 13. References (verify bibliographic details before citing)

- Kheradpisheh, Ganjtabesh, Thorpe, Masquelier (2018). STDP-based spiking deep convolutional neural networks for object recognition. *Neural Networks*.
- Mozafari, Kheradpisheh, Masquelier, Nowzari-Dalini, Ganjtabesh (2018). First-spike-based visual categorization using reward-modulated STDP. *IEEE TNNLS*.
- Mozafari, Ganjtabesh, Nowzari-Dalini, Masquelier (2019). SpykeTorch: efficient simulation of convolutional spiking neural networks with at most one spike per neuron. *Frontiers in Neuroscience*.
- Masquelier & Thorpe (2007). Unsupervised learning of visual features through spike timing dependent plasticity. *PLoS Computational Biology*.
- Thorpe, Fize, Marlot (1996). Speed of processing in the human visual system. *Nature*.
- Brader, Senn, Fusi (2007). Learning real-world stimuli in a neural network with spike-driven synaptic dynamics. *Neural Computation*.
- Paredes-Vallés, Scheper, de Croon (2019). Unsupervised learning of a hierarchical spiking neural network for optical flow estimation. *IEEE TPAMI*.
- Zhu et al. (2018). The Multivehicle Stereo Event Camera Dataset (MVSEC). *IEEE RA-L*.
- de Tournemire et al. (2020). A large scale event-based detection dataset for automotive (Gen1).
- Hu, Liu, Delbruck (2021). v2e: from video frames to realistic DVS events. *CVPR Workshops*.
- Zhou, Friedman, von der Heydt (2000). Coding of border ownership in monkey visual cortex. *J. Neuroscience*.
- Movshon, Adelson, Gizzi, Newsome (1985). The analysis of moving visual patterns.
- Itti & Koch (2001). Computational modelling of visual attention. *Nature Reviews Neuroscience*.
- Lennie (2003). The cost of cortical computation. *Current Biology*.
