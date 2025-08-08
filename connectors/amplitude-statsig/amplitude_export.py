#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

class AmplitudeExporter:
    def __init__(self, management_api_key):
        self.api_key = management_api_key
        self.base_url = "https://experiment.amplitude.com/api/1"
        self.headers = {
            "Authorization": f"Bearer {management_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def export_flags(self):
        """Export all feature flags from Amplitude"""
        try:
            print("Fetching feature flags...")
            response = requests.get(f"{self.base_url}/flags", headers=self.headers)
            
            if response.status_code == 200:
                flags = response.json()
                print(f"✓ Found {len(flags)} feature flags")
                return flags
            else:
                print(f"✗ Failed to fetch flags. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return []
        except Exception as e:
            print(f"✗ Error fetching flags: {e}")
            return []

    def export_experiments(self):
        """Export all experiments from Amplitude"""
        try:
            print("Fetching experiments...")
            response = requests.get(f"{self.base_url}/experiments", headers=self.headers)
            
            if response.status_code == 200:
                experiments = response.json()
                print(f"✓ Found {len(experiments)} experiments")
                return experiments
            else:
                print(f"✗ Failed to fetch experiments. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return []
        except Exception as e:
            print(f"✗ Error fetching experiments: {e}")
            return []

    def get_deployments(self):
        """Get available deployments"""
        try:
            print("Fetching deployments...")
            response = requests.get(f"{self.base_url}/deployments", headers=self.headers)
            
            if response.status_code == 200:
                deployments = response.json()
                print(f"✓ Found {len(deployments)} deployments")
                return deployments
            else:
                print(f"✗ Failed to fetch deployments. Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"✗ Error fetching deployments: {e}")
            return []

def save_json(data, filename):
    """Save data as pretty-printed JSON"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"💾 Saved to {filename}")

def print_summary(flags, experiments):
    """Print a summary of the exported data"""
    print("\n" + "="*50)
    print("AMPLITUDE EXPORT SUMMARY")
    print("="*50)
    
    print(f"\n📊 Feature Flags: {len(flags)}")
    if flags:
        enabled_flags = [f for f in flags if f.get('enabled', False)]
        print(f"   - Enabled: {len(enabled_flags)}")
        print(f"   - Disabled: {len(flags) - len(enabled_flags)}")
        
        print("\n   Key flags found:")
        for flag in flags[:10]:  # Show first 10
            status = "🟢" if flag.get('enabled', False) else "🔴"
            print(f"   {status} {flag.get('key', 'unknown')}: {flag.get('name', 'No name')}")
        if len(flags) > 10:
            print(f"   ... and {len(flags)-10} more")
    
    print(f"\n🧪 Experiments: {len(experiments)}")
    if experiments:
        running_experiments = [e for e in experiments if e.get('state') == 'running']
        print(f"   - Running: {len(running_experiments)}")
        print(f"   - Other states: {len(experiments) - len(running_experiments)}")
        
        print("\n   Key experiments found:")
        for exp in experiments[:10]:  # Show first 10
            state = exp.get('state', 'unknown')
            emoji = "🟢" if state == 'running' else "🟡" if state == 'draft' else "⚫"
            print(f"   {emoji} {exp.get('key', 'unknown')}: {exp.get('name', 'No name')} ({state})")
        if len(experiments) > 10:
            print(f"   ... and {len(experiments)-10} more")

def main():
    print("🔄 Amplitude Configuration Exporter")
    print("="*40)
    
    # Get API key from environment variable
    api_key = os.getenv('AMPLITUDE_MANAGEMENT_API_KEY')
    if not api_key:
        print("❌ Error: Please set AMPLITUDE_MANAGEMENT_API_KEY environment variable")
        print("\nTo get your Management API key:")
        print("1. Go to your Amplitude Experiment project")
        print("2. Click on 'Management API' in the sidebar")
        print("3. Create or copy an existing management API key")
        print("\nThen run:")
        print("export AMPLITUDE_MANAGEMENT_API_KEY='your-key-here'")
        print("python3 amplitude_export.py")
        return
    
    exporter = AmplitudeExporter(api_key)
    
    # Export data
    flags = exporter.export_flags()
    experiments = exporter.export_experiments()
    deployments = exporter.get_deployments()
    
    # Save individual files
    if flags:
        save_json(flags, 'amplitude_flags.json')
    if experiments:
        save_json(experiments, 'amplitude_experiments.json')
    if deployments:
        save_json(deployments, 'amplitude_deployments.json')
    
    # Save combined export
    combined_data = {
        'exported_at': datetime.now().isoformat(),
        'flags': flags,
        'experiments': experiments,
        'deployments': deployments,
        'summary': {
            'total_flags': len(flags),
            'total_experiments': len(experiments),
            'total_deployments': len(deployments),
            'enabled_flags': len([f for f in flags if f.get('enabled', False)]),
            'running_experiments': len([e for e in experiments if e.get('state') == 'running'])
        }
    }
    save_json(combined_data, 'amplitude_complete_export.json')
    
    # Print summary
    print_summary(flags, experiments)
    
    print(f"\n✅ Export completed!")
    print(f"📁 Files created:")
    print(f"   - amplitude_flags.json")
    print(f"   - amplitude_experiments.json") 
    print(f"   - amplitude_deployments.json")
    print(f"   - amplitude_complete_export.json")

if __name__ == "__main__":
    main()