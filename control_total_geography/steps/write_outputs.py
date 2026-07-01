from control_total_geography.util import Pipeline

def run_step(context):
    # pypyr step
    p = Pipeline(settings_path=context['configs_dir'])
    print("Saving outputs from HDF5 to disk...")
    output_dir = p.get_output_path()
    output_layers = p.settings.get('output_layers', [])
    output_geodatabase = p.settings.get('output_geodatabase', 'control.gdb')
    layer_year_suffix = str(p.settings.get('control_areas_year', 2026))[-2:]  # Get last two digits of the year for layer naming
    if not output_layers:
        print("Warning: No output layers specified in settings.yaml. Skipping geodatabase export.")
    else:
        for layer in output_layers:
            gdf = p.get_geodataframe(layer)
            if gdf is not None:
                layer_name = f"{layer}{layer_year_suffix}"
                print(f"Saving {layer_name} to {output_dir / output_geodatabase}...")
                gdf.to_file(output_dir / output_geodatabase, layer=layer_name, driver='OpenFileGDB', promote_to_multi=True)
            else:
                print(f"Warning: No geospatial data found for layer '{layer}' in HDF5 store.")
    for table in p.settings.get('output_tables', []):
        df = p.get_table(table)
        if df is not None:
            print(f"Saving {table} to {output_dir / (table + '.csv')}...")
            df.to_csv(output_dir / (table + '.csv'), index=False)
        else:
            print(f"Warning: No tabular data found for table '{table}' in HDF5 store.")
    return context