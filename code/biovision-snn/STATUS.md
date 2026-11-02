# STATUS

**Phase:** 0 closed (Gate 0 closed by the user on 2026-10-20) → Phase 1 next
**Updated:** 2026-10-20

## Phase 0 (done)
- [x] SDNN, Kheradpisheh 2016 and Mozafari 2018 re-implemented with our modules; 100+ unit tests
- [x] Honest protocol: validation-only selection, each paper's own test protocol (D17)
- [x] Improvements: homeostasis, grid readouts, H-ASIZH threshold dynamics (D21), SDSP / R-SDSP (D20, D23),
      calcium per-neuron adaptive rates, shift-and-add hardware mode (D22), attention-gated R-STDP (D24)
- [x] Campaign runner + figures + Persian Word report (`reports/phase0/گزارش_نهایی_فاز_۰.docx`), `REPORT.md`
- [ ] ETH-80 classifier final test (3 seeds, `work/campaigns/eth80_final`) — running; the report is rebuilt when done

## Main results (test, %)
RL Caltech 98.65 ± 0.49 (best epoch 98.94 ± 0.37; paper 98.9 ± 0.4) · RL ETH-80 LOO 81.83 ± 5.58 (best epoch
84.36 ± 5.31; paper 89.5 ± 1.9) · SVM MNIST 98.52 ± 0.06 (paper 98.4) · SVM Caltech 98.96 ± 0.25 (paper 99.1 ± 0.2).

## Next step
Phase 1: three-channel retina (P, K, M + microsaccades, divisive normalisation, 3-level pyramid), LGN relay,
V1 S1/C1 → V2 → V4 → IT; shift-and-add mode by default; R-STDP readout with calcium rates (main) + SVM probe.
