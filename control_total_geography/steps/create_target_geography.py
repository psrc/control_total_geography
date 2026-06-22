import pandas as pd
import geopandas as gpd
import numpy as np
from control_total_geography.util import Pipeline

def run_step(context):
    p = Pipeline(settings_path=context['configs_dir'])
    print("Creating target geography...")
    control = p.get_geodataframe('control')
    df = (
        control.dissolve(by=['target_id','target_name'], as_index=False)
        .drop(columns=['exclude_from_target','control_id','control_name'], errors='ignore')
    )
    p.save_geodataframe('target', df)
    return context