"""Pure NumPy input contract shared by Phase 7 preprocessing and tests."""
from __future__ import annotations
import numpy as np

INPUT_BANDS=('VV','VH')
NODATA=-32768.0
DB_CLIP=(-60.0,20.0)

def linear_gamma0_to_db(values, *, band_names, representation, nodata=NODATA):
    """Convert two-channel linear gamma0 intensity to dB exactly once.

    Returns (dB[2,H,W], per_band_valid[2,H,W], common_valid[H,W]).
    ``representation`` is deliberately explicit so dB cannot accidentally be
    passed through another logarithm in a caller.
    """
    if tuple(band_names)!=INPUT_BANDS:
        raise ValueError(f'Expected input channel order {INPUT_BANDS}, received {tuple(band_names)}')
    if representation!='linear_gamma0':
        raise ValueError('Expected linear_gamma0 input; refusing to apply logarithm to another representation')
    x=np.asarray(values,dtype=np.float32)
    if x.ndim!=3 or x.shape[0]!=2:
        raise ValueError('Input must have shape [2, height, width] for VV,VH')
    valid=np.isfinite(x)&(x>0)&(x!=nodata)
    db=np.full(x.shape,nodata,dtype=np.float32)
    with np.errstate(divide='ignore',invalid='ignore'):
        db[valid]=10.0*np.log10(x[valid])
    valid &= np.isfinite(db)
    db[~valid]=nodata
    return db,valid,np.all(valid,axis=0)

def normalize_db(db, valid_mask, mean, std, *, band_names, clip=DB_CLIP):
    """Apply the project's training clip and checkpoint-specific z-score.

    Invalid spatial pixels follow the actual training loader: normalized
    channels are set to zero and the original validity mask is returned.
    """
    if tuple(band_names)!=INPUT_BANDS:
        raise ValueError(f'Expected input channel order {INPUT_BANDS}, received {tuple(band_names)}')
    x=np.asarray(db,dtype=np.float32)
    m=np.asarray(valid_mask,dtype=bool)
    mu=np.asarray(mean,dtype=np.float32); sigma=np.asarray(std,dtype=np.float32)
    if x.ndim!=3 or x.shape[0]!=2 or m.shape!=x.shape[1:]:
        raise ValueError('Expected dB shape [2,H,W] and validity mask [H,W]')
    if mu.shape!=(2,) or sigma.shape!=(2,) or not np.isfinite(mu).all() or not np.isfinite(sigma).all() or np.any(sigma<=0):
        raise ValueError('Checkpoint normalization must contain two finite means and positive standard deviations')
    if np.any(~np.isfinite(x[:,m])):
        raise ValueError('Valid input pixels contain NaN or infinity')
    lo,hi=map(float,clip)
    if not np.isfinite([lo,hi]).all() or lo>=hi:
        raise ValueError('Invalid dB clip range')
    y=np.zeros(x.shape,dtype=np.float32)
    clipped=np.clip(x[:,m],lo,hi)
    y[:,m]=(clipped-mu[:,None])/sigma[:,None]
    if not np.isfinite(y).all():
        raise ValueError('Normalization produced NaN or infinity')
    return y,m.copy()

def tile_starts(length, patch=256, overlap=64):
    """Return deterministic tile starts that cover a 1-D image dimension."""
    if length<=0 or patch<=0 or overlap<0 or overlap>=patch:
        raise ValueError('Invalid dimension, patch, or overlap')
    if length<=patch: return [0]
    stride=patch-overlap
    starts=list(range(0,max(1,length-patch+1),stride))
    final=length-patch
    if starts[-1]!=final: starts.append(final)
    return starts
