# TriageLoop technical monograph

This directory contains the academic-style technical working paper for the TriageLoop Round-2 prototype.

## Contents

- `main.tex` - complete LaTeX source.
- `main.pdf` - compiled release-candidate paper.
- `generate_figures.py` - deterministic vector-chart generator using the versioned evaluation JSON.
- `figures/` - generated vector architecture, ML-pipeline, result, sensitivity, NBO, and review figures.

The paper also embeds direct working-product captures from `submission/visuals/product-surfaces/`.

## Rebuild

From the repository root:

```powershell
python paper/generate_figures.py
tectonic paper/main.tex
```

The chart generator requires ReportLab. The LaTeX source intentionally uses a compact package set compatible with Tectonic. Run the compiler from the `paper/` directory if relative image paths are not resolved by the local TeX frontend.

## Evidence boundary

All quantitative prototype results are generated from synthetic data and/or simulation unless explicitly labelled as external input plausibility. The document is not evidence of clinical effectiveness, patient benefit, safe staffing, legal compliance, or production readiness.
