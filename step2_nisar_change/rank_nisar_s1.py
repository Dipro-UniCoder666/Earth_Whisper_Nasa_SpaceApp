import csv

src = "step2_nisar_s1_exact_overlap.csv"
out = "step2_nisar_s1_ranked.csv"

with open(src, newline="") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    r["nisar_pixels"] = int(r["nisar_pixels"])
    r["area_m2"] = float(r["area_m2"])
    r["s1_median_db"] = float(r["s1_median_db"])
    r["s1_mean_db"] = float(r["s1_mean_db"])
    r["s1_pct_le_minus2db"] = float(r["s1_pct_le_minus2db"])
    r["s1_pct_le_minus3db"] = float(r["s1_pct_le_minus3db"])

# Screening order only — NOT an event score.
rows.sort(key=lambda x: x["s1_median_db"])

# Preserve every column from the original file.
fields = list(rows[0].keys())

with open(out, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("Total candidates:", len(rows))
print("Output:", out)
print()
print("TOP 30 BY SENTINEL-1 MEDIAN ΔdB")
print()

for i, r in enumerate(rows[:30], 1):
    print(
        f"{i:02d} | "
        f"{r['comparison']:15s} | "
        f"Region {r['region_id']:4s} | "
        f"NISAR px {r['nisar_pixels']:3d} | "
        f"Area {r['area_m2']:7.0f} m2 | "
        f"Lon {float(r['lon']):.7f} | "
        f"Lat {float(r['lat']):.7f} | "
        f"S1 median {r['s1_median_db']:7.3f} dB | "
        f"S1 mean {r['s1_mean_db']:7.3f} dB | "
        f"<=-2 dB {r['s1_pct_le_minus2db']:6.2f}%"
    )

print()
print("COUNTS")
print("Median <= -2 dB:", sum(r["s1_median_db"] <= -2 for r in rows))
print("Median <= -3 dB:", sum(r["s1_median_db"] <= -3 for r in rows))
print("Median <= -5 dB:", sum(r["s1_median_db"] <= -5 for r in rows))
