#!/usr/bin/env python3
"""
Flexible full-frame cell counter for Neubauer (or any cropped chamber image).

Runs head-less: no cv2.imshow / selectROI needed.
"""

import cv2
import glob
import os
import csv
import argparse
import numpy as np

# ───────────────────────────────────────────────── CLI ──────────────────────────────────────────
ap = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Count blobs (cells) in each cropped chamber image."
)
ap.add_argument("--glob", default="*.jpg", help="Filename pattern to process")
ap.add_argument("--out", default="results", help="Output folder")
ap.add_argument("--min-area", type=int, default=30, help="Min blob area (px²)")
ap.add_argument("--max-area", type=int, default=1500, help="Max blob area (px²)")
ap.add_argument("--circularity", type=float, default=0.40,
                help="Min circularity (0-1); disable with --no-circularity")
ap.add_argument("--no-circularity", action="store_true",
                help="Turn off the circularity filter")
ap.add_argument("--no-overlay", action="store_true",
                help="Skip writing overlay images")
ap.add_argument("--preview", action="store_true",
                help="Show overlay windows (requires desktop GUI)")
# concentration extras
ap.add_argument("--dilution", type=float, default=None,
                help="Sample dilution factor (×). If set with --frame-vol, "
                     "concentration (cells/mL) is reported.")
ap.add_argument("--frame-vol", type=float, default=None,
                help="Volume represented by ONE cropped frame in mL "
                     "(e.g. 1e-4 for 0.1 mm depth × 1 cm²).")

args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

# ────────────────────────────── blob detector factory ──────────────────────────────
def make_detector(min_a, max_a, circ, use_circ=True):
    p = cv2.SimpleBlobDetector_Params()
    p.filterByArea, p.minArea, p.maxArea = True, min_a, max_a
    p.filterByCircularity = use_circ
    if use_circ:
        p.minCircularity = circ
    # Disable filters we don’t use
    for flag in ("filterByConvexity", "filterByInertia", "filterByColor"):
        setattr(p, flag, False)
    p.minThreshold, p.maxThreshold, p.thresholdStep = 10, 220, 10
    return cv2.SimpleBlobDetector_create(p)

detector = make_detector(
    args.min_area,
    args.max_area,
    args.circularity,
    use_circ=not args.no_circularity
)

# ────────────────────────────── helper functions ──────────────────────────────
def detect_cells(gray):
    return [(int(k.pt[0]), int(k.pt[1])) for k in detector.detect(gray)]

def draw_overlay(img, centroids):
    out = img.copy()
    for i, (x, y) in enumerate(centroids, start=1):
        cv2.circle(out, (x, y), 3, (0, 0, 255), -1)
        cv2.putText(out, str(i), (x + 4, y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    return out

def concentration(n_cells, dilution, frame_vol):
    """cells per mL for this frame, or None if args not provided."""
    if dilution is None or frame_vol is None:
        return None
    return n_cells * dilution / frame_vol

# ────────────────────────────── main loop ──────────────────────────────
csv_rows = [["image", "cells", "concentration_cells_per_mL"]]
for path in sorted(glob.glob(args.glob)):
    img = cv2.imread(path)
    if img is None:
        print(f"⚠  Could not read {path}; skipped.")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    centroids = detect_cells(gray)
    n = len(centroids)

    # overlay image
    if not args.no_overlay:
        overlay = draw_overlay(img, centroids)
        base = os.path.splitext(os.path.basename(path))[0]
        cv2.imwrite(os.path.join(args.out, f"{base}_overlay.jpg"), overlay)
        if args.preview:
            cv2.imshow(base, overlay)
            cv2.waitKey(1)

    # optional concentration
    conc = concentration(n, args.dilution, args.frame_vol)
    csv_rows.append([os.path.basename(path), n, conc if conc is not None else ""])

    print(f"{os.path.basename(path):25s}  {n:4d} cells"
          + (f"  |  {conc:.3e} cells/mL" if conc is not None else ""))

if args.preview:
    print("\nPress any key in an image window to close all.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# write CSV
csv_path = os.path.join(args.out, "summary.csv")
with open(csv_path, "w", newline="") as fp:
    csv.writer(fp).writerows(csv_rows)
print(f"\n✔  Summary saved to {csv_path}")
