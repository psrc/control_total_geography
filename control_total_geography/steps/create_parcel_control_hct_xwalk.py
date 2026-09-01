from control_total_geography.util import Pipeline


def county_id_2_digit(df):
    return df['county_id'].astype(str).str[3:5].astype(int)
    

def run_step(context):
    print("Creating parcels_control_hct_xwalk table...")
    p = Pipeline(settings_path=context['configs_dir'])
    parcels_hct = p.get_geodataframe('parcels_control_hct').drop(columns=['geometry'])
    control = p.get_geodataframe('control')[['control_id','target_id','county_id']]
    control['county_id'] = county_id_2_digit(control)
    parcels_xwalk = parcels_hct.merge(control, how='left', on='control_id')
    p.save_table('parcels_control_hct_xwalk',parcels_xwalk)
    return context