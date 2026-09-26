import xml.etree.ElementTree as ET
import numpy as np
from osgeo import gdal
import sys

def read_calibration_xml(xml_file):
    root = ET.parse(xml_file).getroot()
    vectors = []

    for cv in root.iter("calibrationVector"):
        line = int(cv.find("line").text)

        pixels = np.fromstring(
            cv.find("pixel").text, sep=" ", dtype=np.float64
        )
        sigma = np.fromstring(
            cv.find("sigmaNought").text, sep=" ", dtype=np.float64
        )

        if len(pixels) != len(sigma):
            raise ValueError(f"Pixel/sigma mismatch at line {line}")

        vectors.append((line, pixels, sigma))

    vectors.sort(key=lambda x: x[0])

    if not vectors:
        raise ValueError("No calibration vectors found")

    lines = np.array([v[0] for v in vectors], dtype=np.float64)
    pixels = vectors[0][1]
    sigma_lut = np.vstack([v[2] for v in vectors])

    return lines, pixels, sigma_lut


def calibrate(measurement_tif, calibration_xml, output_tif):

    print("Reading:", measurement_tif)
    print("Calibration:", calibration_xml)

    ds = gdal.Open(measurement_tif, gdal.GA_ReadOnly)

    if ds is None:
        raise RuntimeError("Could not open measurement TIFF")

    width = ds.RasterXSize
    height = ds.RasterYSize

    print(f"Raster: {width} x {height}")

    lines, pixels, sigma_lut = read_calibration_xml(calibration_xml)

    print("Calibration vectors:", len(lines))
    print("Calibration pixels:", len(pixels))
    print("Line range:", lines[0], "to", lines[-1])
    print("Pixel range:", pixels[0], "to", pixels[-1])

    # Interpolate calibration LUT across image columns.
    image_pixels = np.arange(width, dtype=np.float64)

    sigma_at_vectors = np.empty(
        (len(lines), width),
        dtype=np.float32
    )

    for i in range(len(lines)):
        sigma_at_vectors[i] = np.interp(
            image_pixels,
            pixels,
            sigma_lut[i]
        ).astype(np.float32)

    print("Range interpolation complete.")

    driver = gdal.GetDriverByName("GTiff")

    out = driver.Create(
        output_tif,
        width,
        height,
        1,
        gdal.GDT_Float32,
        options=[
            "COMPRESS=DEFLATE",
            "PREDICTOR=2",
            "TILED=YES",
            "BIGTIFF=YES"
        ]
    )

    if out is None:
        raise RuntimeError("Could not create output TIFF")

    out.SetGeoTransform(ds.GetGeoTransform())
    out.SetProjection(ds.GetProjection())

    out_band = out.GetRasterBand(1)
    out_band.SetNoDataValue(0)

    band = ds.GetRasterBand(1)

    block_rows = 128

    global_min = np.inf
    global_max = -np.inf
    global_sum = 0.0
    global_count = 0

    for row0 in range(0, height, block_rows):

        rows = min(block_rows, height - row0)

        dn = band.ReadAsArray(
            0, row0, width, rows
        ).astype(np.float32)

        row_numbers = np.arange(
            row0,
            row0 + rows,
            dtype=np.float64
        )

        upper = np.searchsorted(
            lines,
            row_numbers,
            side="right"
        )

        upper = np.clip(
            upper,
            1,
            len(lines) - 1
        )

        lower = upper - 1

        l0 = lines[lower]
        l1 = lines[upper]

        fraction = (
            (row_numbers - l0) /
            (l1 - l0)
        )

        sigma_lower = sigma_at_vectors[lower]
        sigma_upper = sigma_at_vectors[upper]

        sigma_block = (
            sigma_lower +
            fraction[:, None] *
            (sigma_upper - sigma_lower)
        ).astype(np.float32)

        valid = (
            (dn > 0) &
            np.isfinite(dn) &
            (sigma_block > 0) &
            np.isfinite(sigma_block)
        )

        sigma0 = np.zeros(
            (rows, width),
            dtype=np.float32
        )

        # Sentinel-1 calibration:
        # sigma0 = DN^2 / sigmaNought^2
        sigma0[valid] = (
            dn[valid].astype(np.float64) ** 2 /
            sigma_block[valid].astype(np.float64) ** 2
        ).astype(np.float32)

        out_band.WriteArray(
            sigma0,
            0,
            row0
        )

        if np.any(valid):
            vals = sigma0[valid].astype(np.float64)

            global_min = min(global_min, float(vals.min()))
            global_max = max(global_max, float(vals.max()))
            global_sum += float(vals.sum())
            global_count += vals.size

        if row0 % (block_rows * 10) == 0:
            print(f"Processed rows {row0} / {height}")

    out_band.FlushCache()
    out.FlushCache()

    out = None
    ds = None

    print()
    print("CALIBRATION COMPLETE")
    print("Output:", output_tif)

    if global_count:
        print("Valid calibrated pixels:", global_count)
        print("Sigma0 min:", global_min)
        print("Sigma0 max:", global_max)
        print("Sigma0 mean:", global_sum / global_count)


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(
            "Usage: python calibrate_s1.py "
            "<measurement.tif> <calibration.xml> <output.tif>"
        )
        sys.exit(1)

    calibrate(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]
    )
