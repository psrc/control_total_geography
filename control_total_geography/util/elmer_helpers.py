import pandas as pd
from shapely import wkt
import sqlalchemy
import geopandas as gpd
import pyodbc

def _get_sql_server_driver():
        """Returns the newest installed SQL Server ODBC driver name, preferring 18 then 17."""
        installed = pyodbc.drivers()
        for version in ('18', '17'):
                driver = f'ODBC Driver {version} for SQL Server'
                if driver in installed:
                        return driver
        raise RuntimeError(
                'No supported SQL Server ODBC driver found. Install "ODBC Driver 17 for SQL Server" '
                'or "ODBC Driver 18 for SQL Server".'
        )

def patch_psrcelmerpy_trust_server_certificate():
        """Patch psrcelmerpy.Connection to trust the server certificate.

        ODBC Driver 18 enforces certificate validation by default, which
        psrcelmerpy's connection string does not account for, causing an
        SSL Provider error against PSRC's SQL Server. This appends
        TrustServerCertificate=yes to the connection string it builds.
        """
        import urllib
        import psrcelmerpy.conn.connection as connection

        def _create_engine(self):
                conn_string = "DRIVER={}; SERVER={}; DATABASE={}; trusted_connection=yes; TrustServerCertificate=yes".format(
                        _get_sql_server_driver(),
                        self.server_name,
                        self.database_name
                        )
                params = urllib.parse.quote_plus(conn_string)
                self.engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

        connection.Connection._create_engine = _create_engine

def read_from_elmer_geo(feature_class_name, cols, crs='epsg:2285'):
        """
        Returns the specified feature class as a geodataframe from ElmerGeo.

        Parameters
        ----------
        feature_class_name: the name of the featureclass in PSRC's ElmerGeo 
                        Geodatabase

        cols: list of columns to be read from the feature class

        crs: coordinate reference system
        """
        driver = _get_sql_server_driver().replace(' ', '+')
        conn_str = f'mssql+pyodbc://SQLserver/ElmerGeo?driver={driver}&TrustServerCertificate=yes'
        engine = sqlalchemy.create_engine(conn_str)
        con=engine.connect()
        # converts cols list to string for sql query
        cols_str = ', '.join(cols)

        df=pd.read_sql('select %s, Shape.STAsText() as geometry from %s' % 
                        (cols_str, feature_class_name), con=con)
        con.close()
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf=gpd.GeoDataFrame(df, geometry='geometry', crs=crs)
        cols = [col for col in gdf.columns if col not in 
                ['Shape', 'GDB_GEOMATTR_DATA', 'SDE_STATE_ID']]
    
        return gdf[cols]

def read_from_elmer(table_name, columns):
        driver = _get_sql_server_driver().replace(' ', '+')
        conn_str = f'mssql+pyodbc://SQLserver/Elmer?driver={driver}&TrustServerCertificate=yes'
        engine = sqlalchemy.create_engine(conn_str)
        with engine.connect() as con:
                cols_str = ', '.join(columns)
                sql_query = f'select {cols_str} from {table_name}'
                df = pd.read_sql(sql=sql_query, con=con)
        return df