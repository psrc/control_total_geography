import pandas as pd
import geopandas as gpd
import numpy as np
from control_total_geography.util import Pipeline

def run_step(context):
    p = Pipeline(settings_path=context['configs_dir'])
    print("Creating cities geography...")
    psrc = p.get_geodataframe('psrc_region')
    df = psrc.loc[psrc['feat_type'] == 'city'].copy()
    p.save_geodataframe('cities', df)
    return context