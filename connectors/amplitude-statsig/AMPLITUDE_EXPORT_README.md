# Amplitude Configuration Export Tool

This tool connects to Amplitude's Management API to export experiment configurations and feature flags for comparison with Statsig during the migration.

## Prerequisites

1. **Python 3.6+** with `requests` library:
   ```bash
   pip install requests
   ```

2. **Amplitude Management API Key**: You need a management API key from your Amplitude Experiment project.

## Getting Your API Key

1. Log into your Amplitude Experiment project
2. Navigate to **Settings** → **Management API** in the sidebar
3. Create a new management API key or copy an existing one
4. The key should look like: `mgmt-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Usage

### 1. Set your API key as an environment variable:
```bash
export AMPLITUDE_MANAGEMENT_API_KEY="mgmt-your-actual-key-here"
```

### 2. Run the export script:
```bash
python3 amplitude_export.py
```

### 3. Alternative one-liner:
```bash
AMPLITUDE_MANAGEMENT_API_KEY="mgmt-your-key" python3 amplitude_export.py
```

## Output Files

The script will create the following JSON files:

- **`amplitude_flags.json`** - All feature flags with their configurations
- **`amplitude_experiments.json`** - All experiments with their settings  
- **`amplitude_deployments.json`** - Available deployment environments
- **`amplitude_complete_export.json`** - Combined export with metadata and summary

## What Gets Exported

### Feature Flags
- Flag keys, names, and descriptions
- Enabled/disabled status
- Evaluation mode and bucketing configuration
- Variants and their payloads
- Rollout percentages
- Target segments and conditions
- Deployment assignments

### Experiments  
- Experiment keys, names, and descriptions
- Current state (draft, running, decision-made, etc.)
- Start and end dates
- Variants and rollout weights
- Target segments and conditions
- Bucketing configuration

### Deployments
- Available deployment environments
- Deployment IDs and names

## Example Output

```bash
🔄 Amplitude Configuration Exporter
========================================
Fetching feature flags...
✓ Found 12 feature flags
Fetching experiments...
✓ Found 8 experiments  
Fetching deployments...
✓ Found 3 deployments

💾 Saved to amplitude_flags.json
💾 Saved to amplitude_experiments.json
💾 Saved to amplitude_deployments.json
💾 Saved to amplitude_complete_export.json

==================================================
AMPLITUDE EXPORT SUMMARY
==================================================

📊 Feature Flags: 12
   - Enabled: 8
   - Disabled: 4

   Key flags found:
   🟢 boost-pricing: Boost Pricing Test
   🟢 online-only-filter: Online Only Filter
   🔴 old-experiment: Deprecated Feature
   ...

🧪 Experiments: 8
   - Running: 3
   - Other states: 5

   Key experiments found:
   🟢 gender-filter-a-b-20230712: Gender Filter A/B Test (running)
   🟡 boost-price-test: Boost Price Test (draft)
   ⚫ old-test: Old Test (decision-made)
   ...

✅ Export completed!
```

## Configuration Comparison with Statsig

After exporting, you can compare the Amplitude configurations with your Statsig setup by:

1. **Feature Flags**: Compare `amplitude_flags.json` with Statsig feature gates
2. **Experiments**: Compare `amplitude_experiments.json` with Statsig experiments  
3. **Targeting**: Review segment conditions and rollout configurations
4. **Variants**: Ensure variant keys and payloads match between platforms

## From Current Codebase Context

Based on the assignment service codebase, these experiments are referenced in the configuration:

- Remote allowlist experiments (from `application-dev2.yml`):
  - `enable-mutual-taps-no-paywall`
  - `disable-remote-profile-distance` 
  - `gender-filter-a-b-20230712`
  - `project-everest-ios-20230207`
  - `boost-price-*` experiments for various regions
  - And many more...

## Troubleshooting

### Common Issues:

1. **"Failed to fetch" errors**: Check that your API key is valid and has the correct permissions
2. **Empty results**: Verify you're using the management API key (not deployment key)
3. **Authentication errors**: Ensure the API key format is correct (`mgmt-...`)

### API Endpoints Used:
- `GET https://experiment.amplitude.com/api/1/flags`
- `GET https://experiment.amplitude.com/api/1/experiments`  
- `GET https://experiment.amplitude.com/api/1/deployments`

For more details on the Amplitude Management API, see: https://amplitude.com/docs/apis/experiment/experiment-management-api