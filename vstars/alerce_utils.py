from __future__ import print_function
from __future__ import division
from . import C_

import numpy as np
import pandas as pd
from dask import dataframe as dd

###################################################################################################################################################

def get_valid_classes_objs(df, df_index_names, target_classes):
    new_df = df.reset_index()
    valid_objs = new_df.loc[new_df[df_index_names['label']].isin(target_classes)][df_index_names['oid']]
    return list(valid_objs.values)

def subset_df_columns(df, subset_cols):
	df_cols = list(df.columns)
	return df[[c for c in subset_cols if c in df_cols]]

def df_to_float32(df):
	for c in df.columns:
		if df[c].dtype=='float64':
			df[c] = df[c].astype(np.float32)
	return df

def delete_invalid_detections(df, index_name,
	uses_corr:True,
	npartitions=C_.N_DASK,
	):
	obs_index = 'magpsf_corr' if uses_corr else 'magpsf'
	obse_index = 'sigmapsf_corr' if uses_corr else 'sigmapsf'
	ddf = dd.from_pandas(df, npartitions=npartitions)
	if uses_corr:
		df = ddf[~(
			(ddf['isdiffpos']==-1) |
			(ddf[obse_index]==100) |
			(ddf[obs_index].isna()) | # delete nans
			(ddf[obse_index].isna()) # delete nans
		)].compute() # FAST
	else:
		df = ddf[~(
			(ddf['isdiffpos']==-1) |
			(ddf[obs_index].isna()) | # delete nans
			(ddf[obse_index].isna()) # delete nans
		)].compute() # FAST
	return df

def filter_by_valid_objs(df, valid_objs):
	return df[df.index.isin(valid_objs)]

###################################################################################################################################################

def process_df_detections(df, index_name, new_index_name, detections_cols,
	uses_corr=True,
	npartitions=C_.N_DASK,
	):
	assert df.index.name==index_name
	df.index.rename(new_index_name, inplace=True) # rename index
	df = df.reset_index()
	df = df_to_float32(df)
	df = delete_invalid_detections(df, new_index_name, uses_corr, npartitions)
	df = subset_df_columns(df, detections_cols+[new_index_name]) # sub sample columns
	df = df.set_index([new_index_name])
	objs = list(set(df.index))
	return df, objs

def process_df_labels(df, new_index_name, det_objs):
	df = df_to_float32(df)
	df = df.set_index([new_index_name])
	df = filter_by_valid_objs(df, det_objs) # clean labels dataframe
	objs = list(set(df.index))
	return df, objs