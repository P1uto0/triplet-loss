#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: mAP.py

# Copy from:
# https://github.com/huanghoujing/person-reid-triplet-loss-baseline/blob/master/tri_loss/utils/metric.py#L107

import sklearn
from sklearn.metrics import average_precision_score
import numpy as np

def mean_ap(
    distmat,
    query_ids=None,
    gallery_ids=None,
    query_cams=None,
    gallery_cams=None,
    average=True):
  """
  Copy from:
  https://github.com/huanghoujing/person-reid-triplet-loss-baseline/blob/master/tri_loss/utils/metric.py#L107

  Args:
    distmat: numpy array with shape [num_query, num_gallery], the 
      pairwise distance between query and gallery samples
    query_ids: numpy array with shape [num_query]
    gallery_ids: numpy array with shape [num_gallery]
    query_cams: numpy array with shape [num_query]
    gallery_cams: numpy array with shape [num_gallery]
    average: whether to average the results across queries
  Returns:
    If `average` is `False`:
      ret: numpy array with shape [num_query]
      is_valid_query: numpy array with shape [num_query], containing 0's and 
        1's, whether each query is valid or not
    If `average` is `True`:
      a scalar
  """

  # -------------------------------------------------------------------------
  # The behavior of method `sklearn.average_precision` has changed since version
  # 0.19.
  # Version 0.18.1 has same results as Matlab evaluation code by Zhun Zhong
  # (https://github.com/zhunzhong07/person-re-ranking/
  # blob/master/evaluation/utils/evaluation.m) and by Liang Zheng
  # (http://www.liangzheng.org/Project/project_reid.html).
  # My current awkward solution is sticking to this older version.
  
  cur_version = sklearn.__version__
  required_version = '0.18.1'
  if cur_version != required_version:
    print('User Warning: Version {} is required for package scikit-learn, '
          'your current version is {}. '
          'As a result, the mAP score may not be totally correct. '
          'You can try `pip uninstall scikit-learn` '
          'and then `pip install scikit-learn=={}`'.format(
      required_version, cur_version, required_version))
  # -------------------------------------------------------------------------

  # Ensure numpy array
  assert isinstance(distmat, np.ndarray)
  assert isinstance(query_ids, np.ndarray)
  assert isinstance(gallery_ids, np.ndarray)
  assert isinstance(query_cams, np.ndarray)
  assert isinstance(gallery_cams, np.ndarray)

  m, n = distmat.shape

  # Sort and find correct matches
  indices = np.argsort(distmat, axis=1)
  matches = (gallery_ids[indices] == query_ids[:, np.newaxis])
  # Compute AP for each query
  aps = np.zeros(m)
  is_valid_query = np.zeros(m)
  for i in range(m):
    # Filter out the same id and same camera
    valid = ((gallery_ids[indices[i]] != query_ids[i]) |
             (gallery_cams[indices[i]] != query_cams[i]))
    y_true = matches[i, valid]
    y_score = -distmat[i][indices[i]][valid]
    if not np.any(y_true): continue
    is_valid_query[i] = 1
    aps[i] = average_precision_score(y_true, y_score)
  if len(aps) == 0:
    raise RuntimeError("No valid query")
  if average:
    return float(np.sum(aps)) / np.sum(is_valid_query)
  return aps, is_valid_query
