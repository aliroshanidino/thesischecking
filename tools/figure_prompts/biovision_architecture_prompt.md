# Prompt — BioVision-SNN architecture figure (IEEE quality)

ROLE
You are an expert scientific illustrator for IEEE Transactions papers (TCAS-I, TNNLS, TBioCAS). Redraw the architecture below as a publication-quality vector figure. Reproduce every block, number and connection exactly as specified — do not invent, drop or "simplify away" any label, value or arrow. If something does not fit, move it to the caption text (see OUTPUT), never delete it silently.

VISUAL LANGUAGE (style reference: Kheradpisheh et al., "STDP-based spiking deep convolutional neural networks", Neural Networks 2018, Fig. 1)
- Every spiking layer is a 3-D slab in oblique projection (front face + thin top and side faces), like a stack of feature maps. Slab THICKNESS encodes the number of maps n (log-scaled so 2 and 128 both stay readable); slab HEIGHT/WIDTH encodes spatial size (256², 128², 64², 32², 16²). Write n under each slab and the spatial size as "n × H²" in small text.
- Receptive fields: a small dashed square (pooling) or dashed cuboid/pyramid (convolution) on the source slab, with 3–4 thin grey lines converging to ONE dot on the target slab. Label the window size on the lines (5×5, 3×3, 2×2).
- Layer titles above each slab in the form "V1 · S1 (simple) · WTA". Area names (V1, V2 thin, V4, IT, MT, …) in bold, layer code (S1, C1, S2t …) in regular.
- Modules that are not feature-map stacks (readout, priority map, attention, PFC, depth fusion, outputs) are rounded rectangles with a 1-line title and up to 4 short lines of content.
- Flat pastel fills, 0.75 pt dark-grey outlines, no drop shadows, no gradients, no 3-D lighting, no clip-art. Generous white space; align everything to a grid.

COLOUR CODE (colour-blind safe, must stay distinguishable in grayscale — vary lightness, not only hue)
- Retina emulator (fixed, outside the proposed architecture): light grey #EEEEEE, outline #8A8A8A
- LGN relay (fixed): light green #DCEFD8, outline #5E9E4F
- Shared early vision V1/V2 and ventral stream (form, colour): light blue #DCE9F7, outline #2A6FB0
- Dorsal stream (motion, depth): light orange #FBE3C8, outline #C47A1E
- Selection, goal and memory (priority map, attention, PFC): light purple #E8DDF3, outline #7A5AA8
- Outputs (gist, object tokens): light yellow #FFF2C2, outline #B8920F
- Background panels per stage: very light tints of the same colours with dashed panel borders and the stage name in small caps at the panel's top-left.

ARROWS
- Solid dark-grey arrow (1 pt): module output (feed-forward).
- Thin grey line: spiking synapses (window → one target neuron) and auxiliary inputs.
- Red dashed arrow (#C0392B, 1 pt): feedback, applied in wave n+1.
- Green dashed arrow (#2E8B57, 1 pt): reward signal for R-STDP.
- Label every non-obvious arrow in small italic text placed beside (never on top of) the line. Use orthogonal routing; no arrow may cross a text label; minimise crossings.

TYPOGRAPHY AND MATH
- Sans-serif (Helvetica/Arial) for labels; math in LaTeX style (italic variables, upright operators and units, proper sub/superscripts: σ_c, θ_i, W_{S1}, D_c(u), ⌊·⌋₊).
- At final printed size: block titles 8–9 pt bold, contents 7–8 pt, nothing below 6.5 pt. Line widths ≥ 0.5 pt.

LAYOUT (left → right = processing order; three horizontal bands)
Columns from left: Input | Retina emulator | LGN | Shared early vision (V1, V2) | Ventral stream (top band) and Dorsal stream (bottom band) | Selection, goal and memory | Outputs.
Rows: P and K channels feed the TOP band (form/colour); M channel feeds the BOTTOM band (motion). The ventral stream occupies the upper right, the dorsal stream the lower right, selection/PFC the far right column.

GLOBAL PRINCIPLES (state once, in a slim header strip or in the caption)
Wave-based TTFS: each neuron fires at most one spike per wave; T = 15 time steps per stage; non-leaky IF neurons; lateral inhibition (feature-WTA) in every S layer; wave 1 = pure feed-forward (ultra-rapid); red dashed feedback is applied in wave n+1.

COMPLETE CONTENT

1) Input — "Input image / video frame": RGB pyramid 256² · 181² · 128² (each level ÷ √2); L ≈ R, M ≈ G, S ≈ B, Y = (L+M)/2. Draw as three nested frames.

2) Retina emulator (fixed, outside the proposed architecture) — three slabs:
 - Retina · Parvo (P), n = 4: L/M opponent DoG, σ_c = 1, σ_s = 3σ_c; L+/M− and M+/L− × ON/OFF; divisive normalisation r = ⌊D⌋₊ / (ε + G∗Y); latency t = T(1 − r/r_max), no spike if r < θ_in; out 4 × 256² per scale. Edge label from input: "DoG".
 - Retina · Konio (K), n = 2: S − Y, coextensive, σ_k = 2σ_c; ON/OFF; same latency code; out 2 × 256² per scale. Edge label: "DoG".
 - Retina · Magno (M), n = 2: events |log Y − log Y_ref| ≥ C, C = 0.15–0.3, + DoG σ = 3σ_c, ON/OFF; static input: microsaccade shifts of 1–2 px in 4 directions; out 2 × 256² per scale. Edge label: "events + DoG". Under the retina column: "Total: 8 maps × 3 scales = 24".

3) LGN (relay, no learning) — three thin slabs LGN · P (4), LGN · K (2), LGN · M (2), each fed 1:1 from its retina channel (label "1:1"). Shared note: 1:1 relay, w = 1; t_out = clip(t_in − δ·a(x), 0, T), δ = 3; a > 0 (attended) → earlier spikes; a < 0 → TRN suppression; the fine scale is gated outside a(x): virtual fovea.

4) Shared early vision (V1 and V2, stream-specific compartments)
 - V1 · S1 (simple) · WTA, n = 12, from LGN P ⊕ K (5×5 windows): 12 maps, kernel 5×5×6 (P4 ⊕ K2), stride 1, pad 2; W_{S1} = 12×6×5×5 = 1,800, shared over x and scales; non-leaky IF, threshold θ₁, ≤ 1 spike per wave; feature-WTA per position, k-WTA when learning; flat STDP (a⁺ ≈ 0.004, a⁻ ≈ 0.003) or a fixed Gabor baseline; out 12 × 256² per scale.
 - V1 · C1 (complex), n = 12 (2×2): max-pool 2×2, stride 2, + max over adjacent scales; t_C = min t_S (first spike wins); out 12 × 128².
 - V2 thin · S2t · WTA, n = 16 (5×5 on C1): W_{S2t} = 16×12×5×5 = 4,800; surface colour; flat STDP; out 16 × 128². → C2t, n = 16 (2×2): max-pool 2×2 → 16 × 64².
 - V2 pale · S2p · WTA, n = 16 (5×5 on C1): W_{S2p} = 16×12×5×5 = 4,800; corners, junctions; flat STDP; + border ownership B±(x, θ): 8 maps (phase 5), B± = E·⌊Φ± − Φ∓⌋₊. → C2p, n = 16 (2×2): max-pool 2×2 → 16 × 64².
 - V1 · motion (direction-selective), n = 24, from LGN M (label "2 taps + delay"): 8 directions × 3 speeds = 24 maps; V = w₁·e(x − d_θ, t − Δ) + w₂·e(x, t); coincidence: w₁, w₂ < θ < w₁ + w₂; |d| = 1 px, Δ ∈ {1, 2, 4} steps (speed v = |d|/Δ); delays fixed → exponential STDP (A±, τ±); out 24 × 256².
 - V1 · C1m, n = 24 (2×2): max-pool 2×2 → 24 × 128².
 - V2 thick · S2k · WTA, n = 16 (5×5 on C1m): W_{S2k} = 16×24×5×5 = 9,600; pooled motion; STDP; out 16 × 128². → C2k, n = 16 (2×2): max-pool 2×2 → 16 × 64².

5) VENTRAL STREAM — what (identity, location-preserving), upper band:
 - V4 · S3 · WTA, n = 64, from C2t ⊕ C2p (5×5): W_{S3} = 64×32×5×5 = 51,200; shape × colour; flat STDP; out 64 × 64².
 - V4 · C3, n = 64 (2×2): max-pool 2×2 → 64 × 32².
 - IT · S4 · WTA, n = 128 (3×3): W_{S4} = 128×64×3×3 = 73,728; STDP, then R-STDP fine-tuning; out 128 × 32².
 - IT · C4, n = 128 (2×2): max-pool 2×2 → 128 × 16²; retinotopic IT map — no global pooling, location is kept.
 - Location-wise readout D_c(u), n = N_c (3×3 on C4): N_c class maps, 3×3×128, shared over u; W_D = N_c × 128 × 3 × 3; the earliest spike per cell wins; silence = background; R-STDP reward per cell: +1 if u ∈ Ω_c, −1 if u ∈ Ω_c′, −λ_bg on background; a_r ∝ N_miss/N, a_p ∝ N_hit/N; dropout.
 - Output box (yellow) "Ultra-rapid gist (wave 1)": t_c^gist = min_u t(D_c(u)) — "is there a car in the scene?".

6) DORSAL STREAM — where / how (motion, depth), lower band:
 - MT · pattern cells · WTA, n = 24, from C2k (5×5, stride 2): 24 velocity maps (8 dirs × 3 speeds) at 32²; W_{MT} = 24×16×5×5 = 9,600; V_v = Σ[α s_{θ,v·n} − β s_{θ+π,v·n}] (intersection of constraints); exponential STDP; velocity WTA → v(u).
 - V3 (thin slab, n = 1), input v(u): motion contrast MC = ‖v − v̄_surr‖, centre 3×3, surround 9×9 → 32²; moving-object salience and mask.
 - MST (fixed templates), input v(u): expansion, contraction, rotation, translation; E(x₀) = Σ v·(x − x₀)/‖x − x₀‖ → heading; looming τ = φ/φ̇ per object.
 - Monocular depth fusion (orange rounded box): ① occlusion (border ownership, V2) → depth order; ② familiar size Z = f·H_c/h (class c from readout D); ③ height in field Z = f·h_cam/(y_b − y_h); ④ motion parallax Z = f·T⊥/‖v_trans‖ (MST); ⑤ time-to-contact τ; fused Ẑ_k = Σ_m c_{m,k} Z_{m,k} / Σ_m c_{m,k}.

7) SELECTION, GOAL AND MEMORY (purple column):
 - Priority map (LIP), thin slab 1 × 32²: P = α_b·S + α_t·F_g − α_r·R; S: colour/orientation contrast + motion contrast; F_g: goal-class readout; R: inhibition of return; k-WTA with inhibition radius r → up to K objects; replaces NMS (inside the network).
 - Attention map → LGN: a(x) = clip(Σ_k exp(−‖x − p_k‖² / 2ρ_k²) − γ, −1, 1).
 - PFC · goal + working memory: goal g → F_g (top-down bias); object files j: p_j, v_j, f_j (IT features), id_j; cost(k, j) = ‖p_k − (p_j + v_j Δt)‖ + λ(1 − sim(f_k, f_j)); unmatched slot: predicted and kept for N waves (object permanence); issues reward r for R-STDP.
 - Output box (yellow) "Object tokens (every wave)": o_k = (p_k, M_k, c_k, Ẑ_k, v_k, τ_k, id_k); mask M_k: grouping from p_k along B± (phase 5); box for mAP = min/max of M_k (never a training target).

CONNECTIONS (draw all of them)
Feed-forward (solid): Input → retina P/K/M; retina → LGN (1:1); LGN P, K → V1 S1; LGN M → V1 motion; S1 → C1 → {S2t, S2p}; S2t → C2t; S2p → C2p; {C2t, C2p} → V4 S3 → C3 → IT S4 → C4 → readout D_c(u) → gist; V1 motion → C1m → S2k → C2k → MT; MT → V3 and MT → MST (label "v(u)"); readout → priority map ("class maps"); V3 → priority map ("motion salience"); priority map → attention map ("selected p_k"); priority map → PFC ("K objects"); IT → PFC ("IT features f_k"); MST → depth fusion ("heading, T⊥, τ"); V2 pale → depth fusion ("occlusion (B±)"); depth fusion → object tokens ("Ẑ_k"); PFC → object tokens ("tokens with id_k").
Feedback (red dashed, wave n+1): attention map → all three LGN sheets ("ATTENTION FEEDBACK a(x) → all three LGN sheets"); V4 → V2 pale ("border-ownership evidence Φ±"); PFC → priority map ("goal g").
Reward (green dashed): PFC → readout D_c(u) and IT ("reward r (R-STDP)").

LEGEND (compact box, bottom-left, one row if possible)
Slab = stack of n spiking feature maps (n below the slab) · dashed window = receptive field (conv kernel / pooling window) · thin lines = spiking synapses (window → one target neuron) · red dashed = feedback applied in wave n+1 · green dashed = R-STDP reward · solid arrow = module output · grey = auxiliary input. Colour key (retina, LGN, ventral, dorsal, selection, outputs). Learning key: flat STDP in S1–S4 and S2*, exponential STDP in the motion path, R-STDP for IT fine-tuning and the readout, fixed MST templates; adaptive threshold θ_i ← θ_i + η_θ (z_i − ρ) in every S layer.

OUTPUT
- Version A (IEEE double-column figure): 7.16 in (182 mm) wide, about 4.2 in high; keep all blocks, all slab labels (name, n, size), all connections and the legend; keep the key equations of LGN, S1, readout, priority map, attention and tokens; move remaining long equations into a numbered callout list placed in the caption text.
- Version B (thesis / slides, full detail): landscape 10 in × 5.6 in with every equation above in place.
- Deliver vector PDF and SVG with all fonts embedded or converted to outlines, plus a 600-dpi PNG. RGB for screen, CMYK-safe colours.
- No title inside the image (IEEE puts it in the caption). Provide this caption separately:
  "Fig. X. Anatomy of the proposed bio-inspired spiking visual system (BioVision-SNN). Wave-based time-to-first-spike coding with at most one spike per neuron per wave (T = 15 steps per stage), non-leaky IF neurons and feature-WTA lateral inhibition in every S layer. A fixed retina emulator produces Parvo, Konio and Magno channels that the LGN relays and gates by attention. Shared V1/V2 feed a location-preserving ventral stream (V4, IT, location-wise R-STDP readout) and a dorsal stream (MT, V3, MST, monocular depth fusion). A priority map with k-WTA replaces NMS, and PFC keeps object files and issues the reward. Red dashed: feedback applied in the next wave; green dashed: R-STDP reward."

QUALITY CHECKLIST (verify before delivering)
[ ] Every number above appears exactly once and is correct (e.g. 1,800; 4,800; 9,600; 51,200; 73,728; 12 × 256²; 128 × 16²).
[ ] Every arrow listed under CONNECTIONS exists, with the right style and label.
[ ] No text overlaps a line, a slab or another text; no label below 6.5 pt at final size.
[ ] Readable when printed in grayscale.
[ ] Slab sizes decrease monotonically along each stream; thickness tracks n.
[ ] Consistent spacing, alignment and line weights across the figure.
