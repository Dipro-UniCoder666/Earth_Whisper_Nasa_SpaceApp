"""Pure metric and label validation functions for Phase 7B human references."""
from __future__ import annotations
import numpy as np
LABELS={'water','non_water','uncertain','invalid'}
CONFIDENCE={'high','medium','low'}
def validate_reference_rows(rows):
 errors=[];counts={k:0 for k in LABELS};complete=0
 for r in rows:
  for side in ('pre','post'):
   label=r.get(f'{side}_label');confidence=r.get(f'{side}_confidence')
   if label not in (None,''):
    if label not in LABELS:errors.append(f"{r.get('sample_id')} {side}: invalid label {label!r}")
    else:
     counts[label]+=1
     if label in ('water','non_water'):complete+=1
   if confidence not in (None,'') and confidence not in CONFIDENCE:errors.append(f"{r.get('sample_id')} {side}: invalid confidence {confidence!r}")
 return {'errors':errors,'counts':counts,'binary_reference_count':complete,'label_slots':len(rows)*2,'blank_slots':len(rows)*2-sum(counts.values())}
def _arrays(y_true,probability,weights):
 y=np.asarray(y_true);p=np.asarray(probability,dtype=np.float64);w=np.asarray(weights,dtype=np.float64)
 if y.ndim!=1 or p.shape!=y.shape or w.shape!=y.shape:raise ValueError('Labels, probabilities and weights must be aligned one-dimensional arrays')
 if not np.isin(y,[0,1]).all():raise ValueError('Primary metrics accept only binary water/non-water labels')
 if not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Probabilities must be finite in [0,1]')
 if not np.isfinite(w).all() or np.any(w<=0):raise ValueError('Sampling weights must be finite and positive')
 return y.astype(np.uint8),p,w
def weighted_average_precision(y,p,w):
 order=np.argsort(-p,kind='mergesort');ys=y[order];ps=p[order];ws=w[order];total=float(ws[ys==1].sum())
 if total<=0:return None
 tp=fp=ap=0.0;i=0
 while i<len(ys):
  j=i+1
  while j<len(ys) and ps[j]==ps[i]:j+=1
  gw=float(ws[i:j][ys[i:j]==1].sum());tp+=gw;fp+=float(ws[i:j][ys[i:j]==0].sum());ap+=(gw/total)*(tp/(tp+fp));i=j
 return float(ap)
def weighted_metrics(y_true,probability,weights,threshold=.5):
 y,p,w=_arrays(y_true,probability,weights)
 if not np.isfinite(threshold) or not 0<=threshold<=1:raise ValueError('Threshold must be in [0,1]')
 pred=p>=threshold;tn=float(w[(y==0)&~pred].sum());fp=float(w[(y==0)&pred].sum());fn=float(w[(y==1)&~pred].sum());tp=float(w[(y==1)&pred].sum())
 precision=tp/max(tp+fp,1e-15);recall=tp/max(tp+fn,1e-15);f1=2*precision*recall/max(precision+recall,1e-15);iou=tp/max(tp+fp+fn,1e-15)
 return {'threshold':float(threshold),'weighted_confusion_rows_true_0_1_cols_pred_0_1':[[tn,fp],[fn,tp]],'weighted_precision':precision,'weighted_recall':recall,'weighted_f1':f1,'weighted_iou':iou,'weighted_pr_auc_average_precision':weighted_average_precision(y,p,w),'evaluated_sample_count':int(len(y)),'sum_sampling_weights':float(w.sum())}
def choose_threshold(y_true,probability,weights,candidates=None):
 y,p,w=_arrays(y_true,probability,weights)
 if candidates is None:candidates=np.round(np.arange(.05,1,.05),2)
 rows=[weighted_metrics(y,p,w,float(t)) for t in candidates]
 return min(rows,key=lambda m:(-m['weighted_f1'],abs(m['threshold']-.5),m['threshold']))
