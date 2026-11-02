# Setup phase report — laptop GPU environment, staged data, tools, core modules

## Summary
The project now runs on the laptop's RTX 3050 (DECISIONS D15, user decision); the HPC `kut` stays prepared as an
optional backup. Every dependency and every Phase 0–5 dataset we chose (except Gen1, postponed) is downloaded and
verified (20 GB). The core spiking modules and all Section 6.1 unit tests exist; **57/57 tests pass on GPU and
CPU**, and the GPU gives identical spike times to the CPU. The GPU runs our current pipeline ~6× faster than the
laptop CPU. Gate S status: **all criteria pass → waiting for user approval**.

## Setup
- Laptop: Windows 11, Ryzen 7 5800HS, 16 GB RAM, RTX 3050 Laptop 4 GB (compute 8.6, driver 617.42).
- Environment: `biovision-snn/.venv`, Python 3.12, torch 2.14.1 + torchvision 0.29.1 (CUDA 12.6), CuPy 14.2
  (custom kernels via NVRTC); other packages pinned to the HPC set — `env/requirements-lock-laptop.txt` (D14).
- Data: raw in `download/datasets/` (read-only), outputs in `work/{proc,cache,runs}` (`biovision/paths.py`).
- Code: commit `5a3a4d1`; tests `.venv/Scripts/python -m pytest -q`. Persian version: `REPORT_fa.md`.

## Results
| Check | Result |
|---|---|
| Unit tests (Section 6.1 + device tests) | **57 passed** in 7.4 s (CPU + CUDA) |
| CPU vs GPU equality (retina, latency/rank code, IF + WTA, k-WTA, STDP) | identical spike times, winners; weights equal to 1e-12 |
| CuPy first-crossing kernel vs PyTorch | identical |
| Throughput, retina + S1 on the 3-level pyramid, 1 image at a time | GPU 28–30 img/s (23–24 with an STDP step); laptop CPU 4.7 img/s |
| `download/verify_all.py` | ALL OK: 77 HPC + 81 laptop wheels sha256; MNIST md5 = torchvision; every zip/tgz CRC; 11,787/11,787 COCO JPEGs; MVSEC 7/7 files = server size |
| Detached job runner | `tools/run_local.sh` smoke run finished (exit 0) with cmd, commit, device.json, log; keep-awake released |
| Disk | work/ 0 GB of 10 GB cap; A: 16 GB free |

## Data staged (D13)
MNIST · Caltech-101 · ETH-80 (cropped-close128 + cropped256) · Penn-Fudan · COCO 2017 subset (person/car/bird:
8,829 train + 2,958 val images with masks) · MVSEC indoor_flying 1–3 data + gt + calibration (14 GB) ·
psee_loader (Gen1 loader) · v2e source (optional, not installable here). Gen1 itself: Phase 5, needs the user's form.

## Verification checklist (Gate S, adapted by D15)
- Environment installed and locked: PASS (`env/requirements-lock-laptop.txt`)
- Tests pass on the machine that runs the experiments: PASS (57/57, GPU + CPU)
- All required data present and verified: PASS (`verify_all.py` ALL OK)
- Disk within budget: PASS (work/ 0 GB / 10 GB)
- Tools working (health, detached run, status): PASS
- Original HPC criteria: `ssh hpc` without password PASS; pytest on the HPC not run (HPC no longer the main
  runner; its venv has no packages yet); HPC disk 0.7 GB (< 10 GB) PASS

## Red flags observed and how they were handled
- Slow / changing internet (2 KB/s – 3 MB/s): parallel range downloads with resume, overnight supervisor.
- pip on Windows skipped Linux-only dependencies (pexpect): found by a marker-aware closure check (D12).
- Laptop slept for 18 h mid-download (lid / manual sleep): downloads resumed on wake, no data lost.
- Two torch dependencies came at versions other than the HPC pins: fetched the pinned versions.

## Deviations from CLAUDE.md
D1–D2 (HPC specs, disk), D4 (Git Bash), D6/D8 (Miniforge, Python 3.14 on the HPC), D9 (repo in `biovision-snn/`),
D11 (data staged on the laptop), D12–D13 (package set, datasets, MVSEC subset, Gen1 later),
**D14–D15 (laptop GPU is the main compute; laptop Python 3.12)**.

## Gate S: criteria and status → waiting for user approval

## Next steps (Phase 0 — reproduce Kheradpisheh et al. 2018)
1. Extract MNIST, Caltech-101 (face/motorbike) and ETH-80 into `work/proc/`.
2. Run SpykeTorch's own `KheradpishehDeep.py` (MNIST) unchanged on the GPU; record the result.
3. Re-implement the Kheradpisheh SDNN with our modules (grey DoG → S1/C1/S2/C2/S3/C3, flat STDP,
   SVM probe), convergence curves and feature grids; targets taken from the paper PDF in the project folder.
