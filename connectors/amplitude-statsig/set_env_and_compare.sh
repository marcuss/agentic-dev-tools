#!/bin/bash

# Script to set environment variables and run the comparison tools
# This script helps with comparing the "mpu-heuristics-v1" experiment between Amplitude and Statsig

# Display header
echo "========================================================"
echo "MPU Experiments Comparison Tool"
echo "========================================================"
echo

# Check if .env file exists
ENV_FILE="/Users/marcuss/agentic-dev/.env/DEV.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: Environment file not found at $ENV_FILE"
    exit 1
fi

# Extract environment variables from DEV.env
echo "🔑 Loading environment variables from $ENV_FILE"
AMPLITUDE_KEY=$(grep -E "^AMPLITUDE_MANAGEMENT_API_KEY=" "$ENV_FILE" | cut -d'"' -f2)
STATSIG_KEY=$(grep -E "^STATSIG_CONSOLE_API_KEY=" "$ENV_FILE" | cut -d'"' -f2)

# Check if required environment variables are set
if [ -z "$AMPLITUDE_KEY" ]; then
    echo "❌ Error: AMPLITUDE_MANAGEMENT_API_KEY is not set in $ENV_FILE"
    exit 1
fi

if [ -z "$STATSIG_KEY" ]; then
    echo "❌ Error: STATSIG_CONSOLE_API_KEY is not set in $ENV_FILE"
    exit 1
fi

# Export the variables for use in the scripts
export AMPLITUDE_MANAGEMENT_API_KEY="$AMPLITUDE_KEY"
export STATSIG_CONSOLE_API_KEY="$STATSIG_KEY"

echo "🔑 AMPLITUDE_MANAGEMENT_API_KEY: ${AMPLITUDE_KEY:0:10}...${AMPLITUDE_KEY: -5}"
echo "🔑 STATSIG_CONSOLE_API_KEY: ${STATSIG_KEY:0:10}...${STATSIG_KEY: -5}"

echo "✅ Environment variables loaded successfully"
echo

# Change to the project directory
cd /Users/marcuss/agentic-dev || exit 1

# Clean up old files
echo "🧹 Cleaning up old export files..."
rm -f amplitude_*.json statsig_*.json mpu_*.json

# Run the Amplitude export
echo "🔄 Exporting data from Amplitude..."
python3 connectors/amplitude-statsig/amplitude_export_urllib.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to export data from Amplitude"
    exit 1
fi
echo

# Run the Statsig export and comparison
echo "🔄 Exporting data from Statsig and comparing experiments..."
python3 connectors/amplitude-statsig/statsig_export.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to export data from Statsig or compare experiments"
    exit 1
fi
echo

# Generate a detailed report for mpu-heuristics-v1
echo "📝 Generating detailed report for mpu-heuristics-v1..."

# Extract mpu-heuristics-v1 data from the comparison results
python3 -c "
import json
import os

# Load comparison results
with open('mpu_experiments_comparison.json', 'r') as f:
    comparisons = json.load(f)

# Find mpu-heuristics-v1 comparison
mpu_heuristics = None
for comp in comparisons:
    if comp['experiment_key'] == 'mpu-heuristics-v1':
        mpu_heuristics = comp
        break

if mpu_heuristics:
    # Save to a separate file for easier access
    with open('mpu_heuristics_v1_comparison.json', 'w') as f:
        json.dump(mpu_heuristics, f, indent=2)
    print('✅ Extracted mpu-heuristics-v1 data to mpu_heuristics_v1_comparison.json')
else:
    print('❌ Could not find mpu-heuristics-v1 in comparison results')
"

echo
echo "✅ Comparison completed!"
echo "📊 Results are available in the following files:"
echo "   - amplitude_complete_export.json: All Amplitude data"
echo "   - statsig_complete_export.json: All Statsig data"
echo "   - mpu_experiments_comparison.json: Comparison of all MPU experiments"
echo "   - mpu_heuristics_v1_comparison.json: Detailed data for mpu-heuristics-v1"
echo
echo "To run this comparison again, simply execute:"
echo "   bash connectors/amplitude-statsig/set_env_and_compare.sh"