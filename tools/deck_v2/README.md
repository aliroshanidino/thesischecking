# Thesis deck v2 — generator (work in progress)

The v2 deck is rebuilt slide by slide with the author.
- **Figures:** each figure is an HTML/SVG page rendered by Chromium (Playwright): `fig_*.py` → `figs/*.png`.
- **Deck:** `build_v2.py` assembles it with python-pptx, using the design kit `dk2.py`.
- **Visual style:** seminar palette, with the paper-deck navigation (left nav bar, section dividers, pager).

| File | Role |
|---|---|
| `dk2.py` | Palette, fonts, shape helpers, `Deck` class (chrome, nav links, pager, divider). |
| `figkit.py` | MDI icons (`@mdi/svg` 7.4.47, Apache-2.0), Google Fonts CSS, HTML→PNG rendering. |
| `art.py` | Hand-drawn SVG objects (cloud, rack, building, MEC tower, street lamp, car, drone, eye implant). |
| `deckkit.py` | Slide cloning, and rendering via LibreOffice → PDF → PNG. |
| `fig_outline.py`, `fig_hero.py`, `fig_apps.py`, `fig_scene.py`, `fig_power.py`, `fig_vuln.py`, `fig_continuum.py` | One script per figure. |

**Before re-running:**
- Paths inside the scripts point to the session scratchpad; adjust them first.
- The base deck is `originals/seminar_H-ASIZH_Roshani.pptx`.

**Data rule:**
- Every number on a figure comes from Table 1.1 of Ch. 1, the TCAS-I paper, or the cited reference.
- The neuron traces in `fig_vuln.py` come from a behavioural Izhikevich RS simulation, and the figure says so.
