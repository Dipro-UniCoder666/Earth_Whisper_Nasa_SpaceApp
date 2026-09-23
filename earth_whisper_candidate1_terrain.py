import math
from pathlib import Path
import numpy as np

# Earth Whisper — Candidate #1 terrain calculator
# Reads NASADEM 1-arcsecond HGT directly; no QGIS clicking required.

HGT = Path(r"D:\Earth_Whisper_Nasa\Earth_Whisper\AquaByte_NISAR\n31e077.hgt")
LON = 77.93722159661133
LAT = 31.11051824162363

N = 3601

if not HGT.exists():
    raise FileNotFoundError(f"DEM not found: {HGT}")

# NASADEM HGT is signed 16-bit big-endian, 3601 x 3601.
z = np.fromfile(HGT, dtype=">i2", count=N*N).reshape((N, N)).astype(np.float64)

# HGT row 0 = north edge (32N), row increases southward.
x = (LON - 77.0) * 3600.0
y_from_south = (LAT - 31.0) * 3600.0
col = int(round(x))
row = N - 1 - int(round(y_from_south))

# Small 3x3 neighborhood around the candidate.
r0, r1 = row - 1, row + 2
c0, c1 = col - 1, col + 2
win = z[r0:r1, c0:c1]

if win.shape != (3, 3):
    raise RuntimeError(f"Candidate is too close to tile edge: row={row}, col={col}")

# Missing/void values in HGT are usually -32768.
if np.any(win <= -32768):
    raise RuntimeError("DEM neighborhood contains a void value.")

elevation_m = z[row, col]

# 1 arc-second spacing. Use local metric distances.
lat_rad = math.radians(LAT)
dy = 111320.0 / 3600.0
dx = (111320.0 * math.cos(lat_rad)) / 3600.0

# Central differences.
dzdx = (z[row, col+1] - z[row, col-1]) / (2.0 * dx)
dzdy = (z[row-1, col] - z[row+1, col]) / (2.0 * dy)

slope_deg = math.degrees(math.atan(math.sqrt(dzdx*dzdx + dzdy*dzdy)))
slope_pct = 100.0 * math.tan(math.radians(slope_deg))

out = Path(r"D:\AquaByte_NISAR\candidate1_terrain_result.txt")
text = (
    "EARTH WHISPER — Candidate #1 terrain result\n"
    f"Latitude: {LAT:.8f}\n"
    f"Longitude: {LON:.8f}\n"
    f"Elevation: {elevation_m:.1f} m\n"
    f"Slope: {slope_deg:.3f} degrees\n"
    f"Slope: {slope_pct:.1f} percent\n"
    f"DEM: {HGT}\n"
)
out.write_text(text, encoding="utf-8")

print(text)
print(f"Saved: {out}")
