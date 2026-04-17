# Selective Collar — Testing Data

Reference implementation and evaluation harness for the **Selective Collar**
diarization evaluation method, which conditionally snaps predicted speaker
boundaries to ground-truth boundaries when they fall within a small tolerance
window — an honest alternative to the industry-standard 0.25 s exclusion collar.

## Files

| File | Purpose |
| :--- | :--- |
| `selective_collar.py` | Core implementation (`clsSelectiveCollar`) |
| `ground_truth.rttm` | Sample GT (3 speakers, 8 segments) |
| `raw_prediction.rttm` | Sample perturbed prediction |
| `test_selective_collar.py` | Minimal test harness |
| `requirements.txt` | Python dependencies |
| `result_analysis.ipynb` | Statistical analysis notebook (Tasks 1–3) |
| `run_analysis.py` | Standalone analysis script |
| `metric_results_parallel/all_metrics.csv` | Per-file metric results across 720 files |
| `plot1_sota_metric_grid.png` | SOTA metric boxplot grid |
| `plot2_decomposed_stacked_bar.png` | DER component decomposition |

## Install

```bash
pip install -r requirements.txt
```

## Run the test

```bash
python test_selective_collar.py
```

Expected output — the prediction RTTM gets its boundaries conditionally
snapped to the GT where they fall inside the ±0.125 s zone around each GT
boundary. Snapped segments are written to `selective_collar_output.rttm`.

```
Altered starts : 5 / 8
Altered ends   : 6 / 8
```

## API

```python
from selective_collar import clsSelectiveCollar

sc = clsSelectiveCollar(collar_size=0.25, uri="my_meeting")
snapped_rttm_str = sc.return_selective_collar_rttm(
    gt_rttm="ground_truth.rttm",
    pred_rttm="raw_prediction.rttm",
)
# sc.altered_starts, sc.altered_ends — count of boundaries snapped
# sc.traditional_start, sc.traditional_end — total boundaries considered
```

## Reproduce the statistical analysis

The notebook evaluates 720 files (488 MSDWILD + 232 VoxConverse) across three
conditions (Pyannote / Selective / Traditional) and eight metrics (DER, JER,
CDER, SER, BER, MS, FA, SC).

```bash
jupyter notebook result_analysis.ipynb
# or as a script:
python run_analysis.py
```

Outputs:
- Table 1 — Mean ± SD per dataset × condition
- Table 2 — Paired Wilcoxon tests (Selective vs. Traditional)
- Figure 1 — 2×5 SOTA metric boxplot grid
- Figure 2 — Stacked DER decomposition with MS/FA error bars
