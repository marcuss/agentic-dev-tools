#!/usr/bin/env python3

import json
import os
from datetime import datetime

# Using urllib to avoid dependency issues
import urllib.request
import urllib.parse

class StatsigExporter:
    def __init__(self, console_api_key):
        self.api_key = console_api_key
        self.base_url = "https://statsigapi.net/console/v1"
        self.headers = {
            "STATSIG-API-KEY": console_api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint):
        """Make authenticated request to Statsig Console API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    return json.loads(response.read().decode())
                else:
                    print(f"Error: HTTP {response.status} for {endpoint}")
                    print(f"Response: {response.read().decode()}")
                    return None
        except Exception as e:
            print(f"Request failed for {endpoint}: {e}")
            return None

    def get_experiments(self):
        """Get all experiments from Statsig"""
        print("Fetching experiments from Statsig...")
        data = self._make_request("experiments")
        if data:
            experiments = data.get("data", [])
            print(f"✓ Found {len(experiments)} experiments")
            return experiments
        return []

    def get_feature_gates(self):
        """Get all feature gates from Statsig"""
        print("Fetching feature gates from Statsig...")
        data = self._make_request("gates")
        if data:
            gates = data.get("data", [])
            print(f"✓ Found {len(gates)} feature gates")
            return gates
        return []

    def get_dynamic_configs(self):
        """Get all dynamic configs from Statsig"""
        print("Fetching dynamic configs from Statsig...")
        data = self._make_request("dynamic_configs")
        if data:
            configs = data.get("data", [])
            print(f"✓ Found {len(configs)} dynamic configs")
            return configs
        return []

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

def compare_mpu_experiments(amplitude_data, statsig_data, target_experiments):
    """Compare specific MPU experiments between Amplitude and Statsig"""
    print("\n🔍 MPU EXPERIMENTS COMPARISON")
    print("="*50)
    
    # Load amplitude experiments
    if isinstance(amplitude_data, str):
        with open(amplitude_data, 'r') as f:
            amp_data = json.load(f)
            # Handle both old and new format
            if isinstance(amp_data, dict) and 'experiments' in amp_data:
                amplitude_experiments = amp_data.get('experiments', [])
            else:
                amplitude_experiments = amp_data
    else:
        amplitude_experiments = amplitude_data

    # Create lookup dictionaries
    amp_exp_dict = {exp.get('key'): exp for exp in amplitude_experiments}
    statsig_exp_dict = {exp.get('name', exp.get('id', '')): exp for exp in statsig_data}
    
    comparison_results = []
    
    for exp_key in target_experiments:
        print(f"\n📊 Comparing: {exp_key}")
        print("-" * 30)
        
        # Find in Amplitude
        amp_exp = amp_exp_dict.get(exp_key)
        # Find in Statsig (try exact match first, then partial)
        statsig_exp = statsig_exp_dict.get(exp_key)
        if not statsig_exp:
            # Try to find by partial match
            for name, exp in statsig_exp_dict.items():
                if exp_key.lower() in name.lower() or name.lower() in exp_key.lower():
                    statsig_exp = exp
                    break
        
        result = {
            'experiment_key': exp_key,
            'found_in_amplitude': amp_exp is not None,
            'found_in_statsig': statsig_exp is not None,
            'amplitude_data': amp_exp,
            'statsig_data': statsig_exp,
            'comparison': {}
        }
        
        if amp_exp and statsig_exp:
            print("✅ Found in both platforms")
            
            # Compare key attributes
            comparison = {}
            
            # Compare basic info
            comparison['name_match'] = amp_exp.get('name') == statsig_exp.get('name')
            comparison['description_match'] = amp_exp.get('description', '') == statsig_exp.get('description', '')
            
            # Compare state/status
            amp_state = amp_exp.get('state', 'unknown')
            statsig_status = statsig_exp.get('status', 'unknown')
            comparison['status_comparison'] = {
                'amplitude_state': amp_state,
                'statsig_status': statsig_status,
                'equivalent': amp_state == statsig_status or (amp_state == 'running' and statsig_status == 'active')
            }
            
            # Compare variants
            amp_variants = amp_exp.get('variants', [])
            statsig_groups = statsig_exp.get('groups', [])
            
            amp_variant_keys = [v.get('key') for v in amp_variants]
            statsig_group_names = [g.get('name') for g in statsig_groups]
            
            comparison['variants'] = {
                'amplitude_variants': amp_variant_keys,
                'statsig_groups': statsig_group_names,
                'variants_match': set(amp_variant_keys) == set(statsig_group_names)
            }
            
            # Compare rollout
            amp_rollout = amp_exp.get('rolloutWeights', {})
            statsig_allocation = statsig_exp.get('allocation', {})
            
            comparison['rollout'] = {
                'amplitude_weights': amp_rollout,
                'statsig_allocation': statsig_allocation
            }
            
            result['comparison'] = comparison
            
            print(f"   Name: {'✅' if comparison['name_match'] else '❌'}")
            print(f"   Status: {amp_state} → {statsig_status} {'✅' if comparison['status_comparison']['equivalent'] else '❌'}")
            print(f"   Variants: {amp_variant_keys} → {statsig_group_names} {'✅' if comparison['variants']['variants_match'] else '❌'}")
            
        elif amp_exp:
            print("⚠️  Found only in Amplitude")
            print(f"   State: {amp_exp.get('state')}")
            print(f"   Variants: {[v.get('key') for v in amp_exp.get('variants', [])]}")
        elif statsig_exp:
            print("⚠️  Found only in Statsig")
            print(f"   Status: {statsig_exp.get('status')}")
            print(f"   Groups: {[g.get('name') for g in statsig_exp.get('groups', [])]}")
        else:
            print("❌ Not found in either platform")
            
        comparison_results.append(result)
    
    return comparison_results

def main():
    print("🔄 Statsig Configuration Exporter & Comparator")
    print("="*50)
    
    # Get API key from environment
    api_key = os.getenv('STATSIG_CONSOLE_API_KEY')
    if not api_key:
        print("❌ Error: Please set STATSIG_CONSOLE_API_KEY environment variable")
        print("\nTo get your Statsig Console API key:")
        print("1. Go to your Statsig console")
        print("2. Navigate to Settings → Keys & Environments")  
        print("3. Create or copy a Console API key")
        print("\nThen run:")
        print("export STATSIG_CONSOLE_API_KEY='console-your-key-here'")
        print("python3 statsig_export.py")
        return
    
    exporter = StatsigExporter(api_key)
    
    # Export Statsig data
    experiments = exporter.get_experiments()
    feature_gates = exporter.get_feature_gates()
    dynamic_configs = exporter.get_dynamic_configs()
    
    # Define output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build", "statsig")
    
    # Save individual files
    if experiments:
        save_json(experiments, 'statsig_experiments.json', output_dir)
    if feature_gates:
        save_json(feature_gates, 'statsig_feature_gates.json', output_dir)
    if dynamic_configs:
        save_json(dynamic_configs, 'statsig_dynamic_configs.json', output_dir)
    
    # Save combined export
    combined_data = {
        'exported_at': datetime.now().isoformat(),
        'experiments': experiments,
        'feature_gates': feature_gates,
        'dynamic_configs': dynamic_configs,
        'summary': {
            'total_experiments': len(experiments),
            'total_feature_gates': len(feature_gates),
            'total_dynamic_configs': len(dynamic_configs)
        }
    }
    save_json(combined_data, 'statsig_complete_export.json', output_dir)
    
    # Compare specific MPU experiments
    target_experiments = [
        "mpu-heuristics-v1",
        "mpu-rest-of-world", 
        "mpu-optimize-for-views-asia-south-america-africa",
        "mpu-heuristic-algorithm-optimizations-q125",
        "expand-mpu-heuristics"
    ]
    
    # Define amplitude data path
    amplitude_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build", "amplitude")
    amplitude_file = os.path.join(amplitude_dir, 'amplitude_experiments.json')
    
    if os.path.exists(amplitude_file):
        print(f"\n🔍 Comparing {len(target_experiments)} MPU experiments...")
        comparison_results = compare_mpu_experiments(amplitude_file, experiments, target_experiments)
        save_json(comparison_results, 'mpu_experiments_comparison.json', output_dir)
        
        # Summary
        print(f"\n📋 COMPARISON SUMMARY")
        print("="*30)
        found_both = sum(1 for r in comparison_results if r['found_in_amplitude'] and r['found_in_statsig'])
        found_amp_only = sum(1 for r in comparison_results if r['found_in_amplitude'] and not r['found_in_statsig'])
        found_statsig_only = sum(1 for r in comparison_results if not r['found_in_amplitude'] and r['found_in_statsig'])
        found_neither = sum(1 for r in comparison_results if not r['found_in_amplitude'] and not r['found_in_statsig'])
        
        print(f"✅ Found in both: {found_both}")
        print(f"⚠️  Amplitude only: {found_amp_only}")
        print(f"⚠️  Statsig only: {found_statsig_only}")
        print(f"❌ Found in neither: {found_neither}")
        
    else:
        print("⚠️  amplitude_experiments.json not found. Run amplitude_export.py first.")
    
    print(f"\n✅ Export and comparison completed!")
    print(f"📁 Files created:")
    print(f"   - statsig_experiments.json")
    print(f"   - statsig_feature_gates.json")
    print(f"   - statsig_dynamic_configs.json")
    print(f"   - statsig_complete_export.json")
    print(f"   - mpu_experiments_comparison.json")

if __name__ == "__main__":
    main()