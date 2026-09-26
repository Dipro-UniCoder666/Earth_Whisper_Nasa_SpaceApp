from osgeo import gdal
import numpy as np

f1 = "S1D_20260703_Sandhya_sigma0_VV.tif"
f2 = "S1D_20260715_Sandhya_sigma0_VV.tif"

ds1 = gdal.Open(f1, gdal.GA_ReadOnly)
ds2 = gdal.Open(f2, gdal.GA_ReadOnly)

print("July 3 opened:", ds1 is not None)
print("July 15 opened:", ds2 is not None)

if ds1 is None or ds2 is None:
    raise RuntimeError("Could not open one of the Sentinel-1 AOI rasters.")

print("July 3 size:", ds1.RasterXSize, ds1.RasterYSize)
print("July 15 size:", ds2.RasterXSize, ds2.RasterYSize)

a = ds1.GetRasterBand(1).ReadAsArray().astype(np.float32)
b = ds2.GetRasterBand(1).ReadAsArray().astype(np.float32)

valid = (
    (a > 0) &
    (b > 0) &
    np.isfinite(a) &
    np.isfinite(b)
)

diff = np.zeros_like(a, dtype=np.float32)
db = np.zeros_like(a, dtype=np.float32)

diff[valid] = b[valid] - a[valid]
db[valid] = 10.0 * np.log10(b[valid] / a[valid])

driver = gdal.GetDriverByName("GTiff")

out = driver.Create(
    "S1D_20260703_to_20260715_Sandhya_VV_diff.tif",
    a.shape[1],
    a.shape[0],
    1,
    gdal.GDT_Float32,
    options=["COMPRESS=DEFLATE", "PREDICTOR=2", "TILED=YES"]
)
out.SetGeoTransform(ds1.GetGeoTransform())
out.SetProjection(ds1.GetProjection())
band = out.GetRasterBand(1)
band.SetNoDataValue(0)
band.WriteArray(diff)
out.FlushCache()
out = None

out = driver.Create(
    "S1D_20260703_to_20260715_Sandhya_VV_dB_change.tif",
    a.shape[1],
    a.shape[0],
    1,
    gdal.GDT_Float32,
    options=["COMPRESS=DEFLATE", "PREDICTOR=2", "TILED=YES"]
)
out.SetGeoTransform(ds1.GetGeoTransform())
out.SetProjection(ds1.GetProjection())
band = out.GetRasterBand(1)
band.SetNoDataValue(0)
band.WriteArray(db)
out.FlushCache()
out = None

v = db[valid]

print()
print("CHANGE ANALYSIS COMPLETE")
print("Valid pixels:", v.size)
print("dB change min:", v.min())
print("dB change max:", v.max())
print("dB change mean:", v.mean())
print("dB change median:", np.median(v))
print("dB change P5/P25/P75/P95:", np.percentile(v, [5, 25, 75, 95]))

print("Decrease <= -1 dB:", np.mean(v <= -1) * 100, "%")
print("Decrease <= -2 dB:", np.mean(v <= -2) * 100, "%")
print("Decrease <= -3 dB:", np.mean(v <= -3) * 100, "%")

print("Increase >= +1 dB:", np.mean(v >= 1) * 100, "%")
print("Increase >= +2 dB:", np.mean(v >= 2) * 100, "%")
print("Increase >= +3 dB:", np.mean(v >= 3) * 100, "%")
