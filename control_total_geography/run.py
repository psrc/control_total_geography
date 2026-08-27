import argparse
import sys
from pathlib import Path
import yaml
from pypyr import pipelinerunner


def add_run_args(parser):
    parser.add_argument(
        "-c",
        "--configs_dir",
        type=str,
        metavar="PATH",
        default="configs",
        help="path to configs dir that contains settings.yaml (default: configs)",
    )
    parser.add_argument(
        "-r",
        "--resume_after",
        type=str,
        metavar="STEP",
        default=None,
        help="step name to resume after, e.g. 'create_control_geography' or "
             "'steps.create_control_geography' (skips all steps up to and "
             "including this one)",
    )

def _step_matches(step, resume_after):
    name = step['name'] if isinstance(step, dict) else step
    return name == resume_after or name.rsplit('.', 1)[-1] == resume_after

def _build_resumed_pipeline_path(settings_path, resume_after):
    """Writes a temp copy of settings.yaml with steps up to resume_after removed."""
    with open(settings_path) as f:
        pipeline = yaml.safe_load(f)

    steps = pipeline.get('steps', [])
    match_idx = next((i for i, step in enumerate(steps) if _step_matches(step, resume_after)), None)
    if match_idx is None:
        raise ValueError(f"resume_after step '{resume_after}' not found in steps: {steps}")

    pipeline['steps'] = steps[match_idx + 1:]
    print(f"Resuming after step '{resume_after}', running steps: {pipeline['steps']}")

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', dir=settings_path.parent, delete=False)
    yaml.safe_dump(pipeline, tmp)
    tmp.close()
    return Path(tmp.name)

def run(args):
    configs_dir = str(Path(args.configs_dir).resolve())
    print(f"Running control-totals pipeline with configs in: {configs_dir}")

    settings_path = Path(configs_dir) / 'settings.yaml'
    pipeline_path = settings_path
    if args.resume_after:
        pipeline_path = _build_resumed_pipeline_path(settings_path, args.resume_after)

    try:
        pipelinerunner.run(str(pipeline_path.with_suffix('')), dict_in={'configs_dir': configs_dir})
    finally:
        if pipeline_path != settings_path:
            pipeline_path.unlink(missing_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    add_run_args(parser)
    args = parser.parse_args()
    sys.exit(run(args))