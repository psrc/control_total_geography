import pandas as pd
import yaml
from pathlib import Path
import os
import geopandas as gpd
from shapely.wkt import loads

# pandas 3.0 defaults to pyarrow-backed string dtypes ("future.infer_string").
# Parquet round-trips then hand geopandas ArrowDtype-backed string columns,
# which triggers a memory-blowup bug in geopandas.sjoin's reindexing step.
# Force classic numpy object-dtype strings to avoid that.
pd.set_option('future.infer_string', False)

class Pipeline:
    def __init__(self, settings_path='configs'):
        """
        Initialize Pipeline with settings loaded from a YAML file.
        """
        self.settings_path = Path(settings_path).resolve()
        self.base_dir = self.settings_path.parent

        with open(self.settings_path / 'settings.yaml', 'r') as file:
            self.settings = yaml.safe_load(file)

        # create data and output directories if they don't exist
        self.create_directory(path=self.get_data_path())
        self.create_directory(path=self.get_output_path())
        self.create_directory(path=self.get_pipeline_path())

    def create_directory(self, path_parts: list=None, path: str=None) -> Path:
        """Create a directory if it doesn't exist."""
        if path_parts:
            path = Path(os.path.join(*path_parts))
        else:
            path_parts = path

        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory {path} created.")

    def _resolve_workspace_path(self, configured_path, default_name):
        path = Path(configured_path or default_name)
        if not path.is_absolute():
            path = self.base_dir / path
        return path

    def get_settings_path(self):
        # Returns the path to the settings directory
        return str(self.settings_path)
    
    def get_data_path(self, *path_parts):
        return self._resolve_workspace_path(self.settings.get('data_dir'), 'data').joinpath(*path_parts)

    def get_pipeline_path(self, *path_parts):
        return self._resolve_workspace_path(self.settings.get('pipeline_dir'), 'pipeline').joinpath(*path_parts)

    def get_output_path(self, *path_parts):
        return self._resolve_workspace_path(self.settings.get('output_dir'), 'output').joinpath(*path_parts)
    
    def get_table_path(self, table_name):
        return self.get_pipeline_path(f'{table_name}.parquet')

    def save_table(self, table_name, df):
        print(f"Saving table {table_name} to pipeline...")
        df.to_parquet(self.get_table_path(table_name))

    def get_table(self, table_name):
        return pd.read_parquet(self.get_table_path(table_name))

    def save_geodataframe(self, name, gdf):
        gdf['geometry_wkt'] = gdf.geometry.to_wkt()
        gdf_to_save = gdf.drop(columns=['geometry'])
        self.save_table(name, gdf_to_save)

    def get_geodataframe(self, name,crs='epsg:2285'):
        df = self.get_table(name)
        df['geometry'] = df['geometry_wkt'].apply(loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=crs)
        gdf = gdf.drop(columns=['geometry_wkt'])
        return gdf
    
    def convert_id_to_int64(self, table, df):
        if 'id_col' in table:
            id_col = table['id_col']
            df[id_col] = df[id_col].astype('int64')
            return df
        else:
            return df