from control_total_geography.util.elmer_helpers import read_from_elmer_geo, read_from_elmer, patch_psrcelmerpy_trust_server_certificate
from control_total_geography.util import Pipeline
import psrcelmerpy

#patch_psrcelmerpy_trust_server_certificate()


def copy_elmer_geo_to_hdf5(pipeline):
    """Copy geospatial feature classes from ElmerGeo into the pipeline HDF5 store.

    Iterates over the ``ElmerGeo`` list in settings, reads each feature class
    from the ElmerGeo SQL server, converts the ID column to int64, and saves
    the result as a GeoDataFrame.

    Args:
        pipeline (Pipeline): The data pipeline providing access to settings
            and the save interface.
    """
    # loop through ElmerGeo files specified in settings.yaml
    elmer_geo_list = pipeline.settings.get('ElmerGeo', [])
    eg_conn = psrcelmerpy.ElmerGeoConn()
    if elmer_geo_list:
        for file in elmer_geo_list:
            gdf = eg_conn.read_geolayer(file['sql_table'])
            gdf = gdf[file['columns'] + [gdf._geometry_column_name]]
            
            # convert id column to int64
            gdf = pipeline.convert_id_to_int64(file, gdf)

            # save to HDF5
            pipeline.save_geodataframe(file['name'], gdf)

def copy_elmer_to_hdf5(pipeline):
    """Copy tabular data from Elmer into the pipeline.

    Iterates over the ``Elmer`` table list in settings, reads each table
    from the Elmer SQL server, converts the ID column to int64, and saves
    the result.

    Args:
        pipeline (Pipeline): The data pipeline providing access to settings
            and the save interface.
    """
    # loop through Elmer tables specified in settings.yaml unless it's empty
    elmer_list = pipeline.settings.get('Elmer', [])
    e_conn = psrcelmerpy.ElmerConn()
    if elmer_list:
        for table in elmer_list:
            df = e_conn.read_table(table['sql_table'], ['*'])
            
            # convert id column to int64
            df = pipeline.convert_id_to_int64(table, df)
            
            # save to HDF5
            pipeline.save_table(table['name'], df)


def run_step(context):
    """Execute the Elmer data retrieval pipeline step.

    Copies ElmerGeo geospatial feature classes and Elmer tabular data into
    the pipeline HDF5 store.

    Args:
        context (dict): The pypyr context dictionary, expected to contain
            a ``'configs_dir'`` key.

    Returns:
        dict: The unchanged pypyr context dictionary.
    """
    # pypyr step
    p = Pipeline(settings_path=context['configs_dir'])
    print("Getting ElmerGeo data and saving to pipeline...")
    copy_elmer_geo_to_hdf5(p)
    return context
