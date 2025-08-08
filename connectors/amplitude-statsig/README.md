# Amplitude-Statsig Connector

This connector provides tools for exporting and comparing configuration data between Amplitude Experiment and Statsig platforms.

## Overview

The connector includes scripts for:

1. Exporting feature flags, experiments, and deployments from Amplitude
2. Exporting experiments, feature gates, and dynamic configs from Statsig
3. Comparing MPU (Most Promising Users) experiments between the two platforms
4. Analyzing Amplitude configuration and generating migration checklists

## File Structure

All exported JSON files are now stored in dedicated build directories:

- `/build/amplitude/` - Contains all Amplitude export files
- `/build/statsig/` - Contains all Statsig export files and comparison results

## Scripts

### amplitude_export.py

Exports configuration data from Amplitude using the requests library.

```bash
AMPLITUDE_MANAGEMENT_API_KEY="your-key-here" python3 connectors/amplitude-statsig/amplitude_export.py
```

### amplitude_export_urllib.py

Alternative exporter that uses only built-in Python libraries (no external dependencies).

```bash
AMPLITUDE_MANAGEMENT_API_KEY="your-key-here" python3 connectors/amplitude-statsig/amplitude_export_urllib.py
```

### statsig_export.py

Exports configuration data from Statsig and compares MPU experiments with Amplitude data.

```bash
STATSIG_CONSOLE_API_KEY="your-key-here" python3 connectors/amplitude-statsig/statsig_export.py
```

### compare_configs.py

Analyzes Amplitude configuration and generates migration checklists.

```bash
python3 connectors/amplitude-statsig/compare_configs.py
```

### set_env_and_compare.sh

Helper script to set environment variables and run the comparison tools.

```bash
bash connectors/amplitude-statsig/set_env_and_compare.sh
```

## Output Files

### Amplitude Files

- `amplitude_flags.json` - All feature flags
- `amplitude_experiments.json` - All experiments
- `amplitude_deployments.json` - Available deployment environments
- `amplitude_complete_export.json` - Combined export with metadata

### Statsig Files

- `statsig_experiments.json` - All experiments
- `statsig_feature_gates.json` - All feature gates
- `statsig_dynamic_configs.json` - All dynamic configs
- `statsig_complete_export.json` - Combined export with metadata

### Comparison Files

- `mpu_experiments_comparison.json` - Comparison of MPU experiments between platforms
- `mpu_heuristics_v1_comparison.json` - Detailed comparison of the mpu-heuristics-v1 experiment

## Recent Changes

- Updated all scripts to store JSON responses in dedicated build directories
- Added directory creation if the build directories don't exist
- Updated file paths in all scripts to use the new locations
- Improved error handling and reporting