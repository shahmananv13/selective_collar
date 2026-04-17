# Selective Collar — Testing Data

Reference implementation for the **Selective Collar**
diarization evaluation method, which conditionally snaps predicted speaker
boundaries to ground-truth boundaries when they fall within a tolerance
window.

## Files

| File | Purpose |
| :--- | :--- |
| `selective_collar.py` | Core implementation (`clsSelectiveCollar`) |
| `ground_truth.rttm` | Sample GT (3 speakers, 8 segments) |
| `raw_prediction.rttm` | Sample perturbed prediction |
| `test_selective_collar.py` | Minimal test harness |
| `requirements.txt` | Python dependencies |

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

## Implementation

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
