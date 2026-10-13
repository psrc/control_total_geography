from control_total_geography.util import Pipeline


def run_step(context):
    print("Creating parcels_control_hct_xwalk table...")
    p = Pipeline(settings_path=context['configs_dir'])
    parcels_hct = p.get_table('parcels_control_hct')
    control = p.get_geodataframe('control')[['control_id','target_id','county_id']]
    parcels_xwalk = parcels_hct.merge(control, how='left', on='control_id')
    p.save_table('parcels_control_hct_xwalk',parcels_xwalk)
    return context