import pandas as pd

from control_total_geography.util import Pipeline

def load_data_tables_to_hdf5(pipeline):
    # load general data tables in the data_tables list in settings.yaml
    p = pipeline
    data_tables = p.settings.get('data_tables', [])
    for table in data_tables:
        table_name = table['name']
        file_path = f"{p.get_data_path()}/{table['file']}"
        print(f"Loading {file_path} into HDF5 as {table_name}...")
        df = pd.read_csv(file_path)
        # save to HDF5
        p.save_table(table_name, df)

def run_step(context):
    # pypyr step
    p = Pipeline(settings_path=context['configs_dir'])
    print("Loading data tables from CSV files into HDF5...")
    load_data_tables_to_hdf5(p)
    return context