"""
Test harness for selective_collar.py

Runs ground_truth.rttm + raw_prediction.rttm through clsSelectiveCollar
and reports the snapped hypothesis RTTM plus boundary-snap statistics.

Usage:
    python test_selective_collar.py
"""

from pathlib import Path
from selective_collar import clsSelectiveCollar

HERE = Path(__file__).parent
GT_PATH = HERE / "ground_truth.rttm"
PRED_PATH = HERE / "raw_prediction.rttm"
COLLAR_SIZE = 0.25
URI = "sample_meeting"


def main():
    assert GT_PATH.exists(), f"Missing {GT_PATH}"
    assert PRED_PATH.exists(), f"Missing {PRED_PATH}"

    print("=" * 72)
    print(f"Ground truth : {GT_PATH.name}")
    print(f"Prediction   : {PRED_PATH.name}")
    print(f"Collar size  : {COLLAR_SIZE}s")
    print("=" * 72)

    sc = clsSelectiveCollar(collar_size=COLLAR_SIZE, uri=URI)
    snapped_rttm = sc.return_selective_collar_rttm(str(GT_PATH), str(PRED_PATH))

    out_path = HERE / "selective_collar_output.rttm"
    out_path.write_text(snapped_rttm, encoding="utf-8")

    print("\n--- Snapped Hypothesis RTTM ---")
    print(snapped_rttm.strip())

    print("\n--- Boundary Snap Statistics ---")
    print(f"Altered starts : {sc.altered_starts} / {sc.traditional_start}")
    print(f"Altered ends   : {sc.altered_ends} / {sc.traditional_end}")
    print(f"\nSaved snapped RTTM to: {out_path.name}")

    assert sc.altered_starts + sc.altered_ends > 0, (
        "Expected at least one boundary to fall inside the collar zone"
    )
    print("\n[OK] Selective collar produced boundary snaps as expected.")


if __name__ == "__main__":
    main()
