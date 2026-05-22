from pathlib import Path

from control_total_geography.util import Pipeline


def run_step(context):
	p = Pipeline(settings_path=context['configs_dir'])
	hdf5_path = Path(p.get_output_path()) / 'pipeline.h5'

	if hdf5_path.exists():
		print(f"Deleting existing HDF5 store: {hdf5_path}")
		hdf5_path.unlink()

	return context
