from control_total_geography.util import Pipeline

def run_step(context):
    # pypyr step
    p = Pipeline(settings_path=context['configs_dir'])
    print("Saving outputs from HDF5 to disk...")
    output_dir = p.get_output_path()
    output_layers = p.settings.get('output_layers', [])
    output_geodatabase = p.settings.get('output_geodatabase', 'control.gdb')
    for layer in output_layers:
        gdf = p.get_geodataframe(layer)
        if gdf is not None:
            print(f"Saving {layer} to {output_dir / output_geodatabase}...")
            gdf.to_file(output_dir / output_geodatabase, layer=layer, driver='OpenFileGDB', promote_to_multi=True)
        else:
            print(f"Warning: No geospatial data found for layer '{layer}' in HDF5 store.")
    return context