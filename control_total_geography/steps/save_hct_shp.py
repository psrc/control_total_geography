from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from util import Pipeline
from control_total_geography.util.elmer_helpers import read_from_elmer_geo

def dissolve_parcels_to_hct(pipeline):
    p = pipeline
    # read parcels from elmer geo directly (too large to save to pipeline)
    print("Reading parcels from Elmer Geo")
    parcels_gdf = read_from_elmer_geo('PARCELS_URBANSIM_2023',['parcel_id'])
    print(f"Read {len(parcels_gdf)} parcels from Elmer Geo")
    # get parcel points already tagged with control_hct_id
    gdf = p.get_geodataframe('parcels_hct')[['parcel_id', 'control_id','control_hct_id']]
    # merge to get parcel polygons with control_hct_id, then dissolve to get hct polygons
    gdf = parcels_gdf.merge(gdf, on='parcel_id', how='left')
    diss_gdf = gdf.dissolve(by=['control_id','control_hct_id'])
    diss_gdf = diss_gdf.reset_index()[['control_id','control_hct_id','geometry']]
    # get control areas and merge to get control names for hct polygons
    control_areas = p.get_geodataframe('control')[['control_id','control_name']]
    # control_id is kept so plot_hct can assign counties; it is dropped before saving
    diss_gdf = (diss_gdf.merge(control_areas, on='control_id', how='left')
                .rename(columns={'control_name':'chct_name','control_hct_id':'chct_id'}))
    return diss_gdf

COUNTY_NAMES = {33: 'King', 35: 'Kitsap', 53: 'Pierce', 61: 'Snohomish'}

def plot_hct(pipeline, gdf, output_dir):
    """Save one PNG map of the HCT polygons per county to output_dir."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xwalk = (
        pipeline.get_table('control_target_xwalk')[['control_id','county_id']]
        .drop_duplicates('control_id')
        .set_index('control_id')['county_id']
    )
    gdf = gdf.copy()
    # keep only HCT polygons (chct_id >= 1000)
    is_hct = gdf['chct_id'] >= 1000
    gdf = gdf[is_hct]
    # xwalk county_id is the full FIPS (e.g. 53033); reduce to the 2-digit county code
    gdf['county_id'] = gdf['control_id'].map(xwalk).astype('Int64') % 1000

    counties = pipeline.get_geodataframe('county')[['county_fip','geometry']].to_crs(gdf.crs)
    counties['county_id'] = counties['county_fip'].astype(int)

    for county_id, county_hct in gdf.dropna(subset=['county_id']).groupby('county_id'):
        county_name = COUNTY_NAMES.get(int(county_id), f'county_{county_id}')
        fig, ax = plt.subplots(figsize=(10, 10))
        counties[counties['county_id'] == county_id].plot(
            ax=ax, facecolor='whitesmoke', edgecolor='black', linewidth=0.8)
        county_hct.plot(ax=ax, facecolor='tab:blue', edgecolor='navy', alpha=0.6, linewidth=0.3)
        ax.set_title(f'{county_name} County High Capacity Transit Areas')
        ax.set_axis_off()
        out_path = output_dir / f'hct_{county_name.lower()}.png'
        fig.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved {out_path}")


def run_step(context):
    print("Running save_hct_shp step")
    p = Pipeline(settings_path=context["configs_dir"])
    hct_gdf = dissolve_parcels_to_hct(p)
    plot_hct(p, hct_gdf, p.get_output_path())
    p.save_geodataframe('control_hct', hct_gdf.drop(columns='control_id'))
    return context