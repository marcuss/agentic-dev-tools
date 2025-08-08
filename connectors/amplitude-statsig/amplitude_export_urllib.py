#!/usr/bin/env python3

import json
import os
import urllib.request
import urllib.error
import urllib.parse
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

    def _make_request(self, endpoint):
        """Make a GET request to the Amplitude API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    # Handle different response structures
                    if isinstance(data, dict) and 'flags' in data:
                        return data['flags']
                    elif isinstance(data, dict) and 'experiments' in data:
                        return data['experiments']
                    elif isinstance(data, dict) and 'deployments' in data:
                        return data['deployments']
                    return data
                else:
                    print(f"✗ Failed to fetch {endpoint}. Status: {response.status}")
                    print(f"Response: {response.read().decode()}")
                    return []
        except urllib.error.URLError as e:
            print(f"✗ Error fetching {endpoint}: {e}")
            return []
        except Exception as e:
            print(f"✗ Unexpected error fetching {endpoint}: {e}")
            return []

    def export_flags(self):
        """Export all feature flags from Amplitude"""
        print("Fetching feature flags...")
        flags = self._make_request("flags")
        if flags:
            print(f"✓ Found {len(flags)} feature flags")
        return flags

    def export_experiments(self):
        """Export all experiments from Amplitude"""
        print("Fetching experiments...")
        experiments = self._make_request("experiments")
        if experiments:
            print(f"✓ Found {len(experiments)} experiments")
        return experiments

    def get_deployments(self):
        """Get available deployments"""
        print("Fetching deployments...")
        deployments = self._make_request("deployments")
        if deployments:
            print(f"✓ Found {len(deployments)} deployments")
        return deployments

def save_json(data, filename, directory=""):
    """Save data as pretty-printed JSON"""
    # Create directory if it doesn't exist
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Construct the full path
    filepath = os.path.join(directory, filename) if directory else filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"💾 Saved to {filepath}")

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
    print("🔄 Amplitude Configuration Exporter (urllib version)")
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
        print("python3 amplitude_export_urllib.py")
        return
    
    exporter = AmplitudeExporter(api_key)
    
    # Export data
    flags = exporter.export_flags()
    experiments = exporter.export_experiments()
    deployments = exporter.get_deployments()
    
    # Define output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build", "amplitude")
    
    # Save individual files
    if flags:
        save_json(flags, 'amplitude_flags.json', output_dir)
    if experiments:
        save_json(experiments, 'amplitude_experiments.json', output_dir)
    if deployments:
        save_json(deployments, 'amplitude_deployments.json', output_dir)
    
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
    save_json(combined_data, 'amplitude_complete_export.json', output_dir)
    
    # Print summary
    print_summary(flags, experiments)
    
    print(f"\n✅ Export completed!")
    print(f"📁 Files created in {output_dir}:")
    print(f"   - amplitude_flags.json")
    print(f"   - amplitude_experiments.json") 
    print(f"   - amplitude_deployments.json")
    print(f"   - amplitude_complete_export.json")

if __name__ == "__main__":
    main()