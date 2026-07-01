import pandas as pd
import geopandas as gpd
import numpy as np
from control_total_geography.util import Pipeline

def run_step(context):
    p = Pipeline(settings_path=context['configs_dir'])
    print("Creating cities geography...")
    psrc = p.get_geodataframe('psrc_region')
    df = psrc.loc[psrc['feat_type'] == 'city'].copy()
    df = df.sort_values(by=['cnty_fips','juris'])
    df['city_id'] = range(1, len(df) + 1)
    p.save_geodataframe('cities', df)
    # create parcels-cities crosswalk table
    print("Creating parcels_cities crosswalk table...")
    parcels = p.get_geodataframe('parcel_pts_current')[['parcel_id', 'geometry']]
    parcels = parcels.sjoin(df)
    for col in ['rgeo_class', 'cnty_fips']:
        parcels[col] = parcels[col].astype('int')
    keep_cols = ['parcel_id', 'city_id', 'juris', 'rgeo_class', 'cnty_fips', 'cnty_name']
    p.save_table('parcels_cities',parcels[keep_cols])
    return context