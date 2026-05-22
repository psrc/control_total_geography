# Control Total Geography
Control Total Geography uses spatial layers from Elmer to create "control" and "control_hct" layers that are used for creating control totals for Urbansim.

## Installation
1. Install UV package manager 

    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` 

2. Connect to PSRC VPN before running so the pipeline can load data from Elmer and network drives

3. Create a new example project by copying project/summer_2026 or just make modifications to settings in projects/summer_2026/configs/settings.yaml

4. Run the control total geography pipeline using -c "<configs_dir>" cmd line arg
    
    `uv run control_totals\run.py -c projects\summer_2026\configs`
