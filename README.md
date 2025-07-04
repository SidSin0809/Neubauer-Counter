# Neubauer-Counter
A Head-less Python Tool for Automated Cell Counting in Cropped Hemocytometer Frames

Neubauer-Counter is a single-file Python utility that detects and enumerates cells (or other roughly circular particles) in already-cropped images of a Neubauer or Improved Neubauer counting chamber. It is designed for quick batch processing on any machine that has OpenCV and NumPy—no GUI, no manual clicks, no external dependencies beyond standard wheels. The script can also compute cell concentrations (cells · mL⁻¹) when you supply the dilution factor and the frame’s physical volume.

# Features
| Feature                       | What it does                                                      |
| ----------------------------- | ----------------------------------------------------------------- |
| **Head-less workflow**        | No `cv2.imshow` / `selectROI`; runs on servers, CI, notebooks     |
| **Command-line configurable** | All blob-detection and I/O options exposed as flags               |
| **Overlay generation**        | Optionally writes JPEG overlays with red dots & indices           |
| **CSV summary**               | Saves a per-image report (cells and, if requested, concentration) |
| **Flexible blob filter**      | Area range, circularity gate can be tuned or disabled             |
| **Live preview (optional)**   | `--preview` pops real-time windows when you have a desktop        |

# Installation
# 1. Clone or download the repo
git clone https://github.com/SidSin0809/neubauer-counter.git
cd neubauer-counter

# 2. Install dependencies
pip install --upgrade pip
pip install opencv-python numpy

If you need head-less builds (no HighGUI), replace opencv-python with opencv-python-headless

# Quick Start
# Count and overlay every *.jpg in the folder
python count_cells_frame.py

# Count only PNGs, store outputs in ./results, skip overlay images
python count_cells_frame.py --glob "*.png" --out results --no-overlay

# Tighter area filter (50-1200 px²) and no circularity gate
python count_cells_frame.py --min-area 50 --max-area 1200 --no-circularity

# Also compute concentration (cells · mL⁻¹)
python count_cells_frame.py --dilution 2.0 --frame-vol 1e-4

# CLI Options
| Flag                                      | Purpose                    | Default      |
| ----------------------------------------- | -------------------------- | ------------ |
| `--glob "*.jpg"`                          | File pattern to scan       | `"*.jpg"`    |
| `--out results`                           | Output directory           | `results`    |
| `--min-area 30` / `--max-area 1500`       | Blob area filter (px²)     | `30–1500`    |
| `--circularity 0.40` / `--no-circularity` | Roundness threshold        | 0.40 (ON)    |
| `--no-overlay`                            | Don’t write overlay JPEGs  | Off (writes) |
| `--preview`                               | Show live windows          | Off          |
| `--dilution 2.0`                          | Sample dilution factor (×) | *None*       |
| `--frame-vol 1e-4`                        | Volume of one frame (mL)   | *None*       |


