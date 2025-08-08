#!/usr/bin/env python3

import json
import os
from typing import Dict, List, Set

class ConfigComparator:
    def __init__(self, amplitude_file: str, statsig_file: str = None):
        self.amplitude_data = self.load_json(amplitude_file)
        self.statsig_data = self.load_json(statsig_file) if statsig_file else None
        
    def load_json(self, filename: str) -> Dict:
        """Load JSON data from file"""
        if not os.path.exists(filename):
            print(f"⚠️  File not found: {filename}")
            return {}
        
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return {}

    def analyze_amplitude_config(self):
        """Analyze the Amplitude configuration export"""
        print("🔍 AMPLITUDE CONFIGURATION ANALYSIS")
        print("="*50)
        
        flags = self.amplitude_data.get('flags', [])
        experiments = self.amplitude_data.get('experiments', [])
        
        # Analyze flags
        print(f"\n📊 Feature Flags Analysis ({len(flags)} total):")
        if flags:
            enabled_flags = [f for f in flags if f.get('enabled', False)]
            print(f"   ✅ Enabled: {len(enabled_flags)}")
            print(f"   ❌ Disabled: {len(flags) - len(enabled_flags)}")
            
            # Group by evaluation mode
            eval_modes = {}
            for flag in flags:
                mode = flag.get('evaluationMode', 'unknown')
                eval_modes[mode] = eval_modes.get(mode, 0) + 1
            
            print(f"\n   📋 Evaluation Modes:")
            for mode, count in eval_modes.items():
                print(f"      - {mode}: {count}")
            
            # Check for variants
            flags_with_variants = [f for f in flags if f.get('variants', [])]
            print(f"\n   🎛️  Flags with variants: {len(flags_with_variants)}")
            
            # Print flag details
            print(f"\n   🏷️  Flag Details:")
            for flag in flags[:10]:  # Show first 10
                variants = flag.get('variants', [])
                variant_keys = [v.get('key', 'unknown') for v in variants]
                status = "🟢" if flag.get('enabled', False) else "🔴"
                print(f"      {status} {flag.get('key', 'unknown')}")
                print(f"         Name: {flag.get('name', 'No name')}")
                print(f"         Variants: {variant_keys}")
                print(f"         Rollout: {flag.get('rolloutPercentage', 0)}%")
                print()
            
            if len(flags) > 10:
                print(f"      ... and {len(flags)-10} more flags")
        
        # Analyze experiments  
        print(f"\n🧪 Experiments Analysis ({len(experiments)} total):")
        if experiments:
            # Group by state
            states = {}
            for exp in experiments:
                state = exp.get('state', 'unknown')
                states[state] = states.get(state, 0) + 1
            
            print(f"   📊 States:")
            for state, count in states.items():
                emoji = "🟢" if state == 'running' else "🟡" if state == 'draft' else "⚫"
                print(f"      {emoji} {state}: {count}")
            
            # Group by evaluation mode
            eval_modes = {}
            for exp in experiments:
                mode = exp.get('evaluationMode', 'unknown')
                eval_modes[mode] = eval_modes.get(mode, 0) + 1
            
            print(f"\n   📋 Evaluation Modes:")
            for mode, count in eval_modes.items():
                print(f"      - {mode}: {count}")
            
            # Print experiment details
            print(f"\n   🧪 Experiment Details:")
            for exp in experiments[:10]:  # Show first 10
                variants = exp.get('variants', [])
                variant_keys = [v.get('key', 'unknown') for v in variants]
                state = exp.get('state', 'unknown')
                emoji = "🟢" if state == 'running' else "🟡" if state == 'draft' else "⚫"
                print(f"      {emoji} {exp.get('key', 'unknown')}")
                print(f"         Name: {exp.get('name', 'No name')}")
                print(f"         State: {state}")
                print(f"         Variants: {variant_keys}")
                if exp.get('rolloutWeights'):
                    print(f"         Rollout Weights: {exp.get('rolloutWeights')}")
                print()
            
            if len(experiments) > 10:
                print(f"      ... and {len(experiments)-10} more experiments")

    def extract_amplitude_keys(self) -> Dict[str, Set[str]]:
        """Extract all keys from Amplitude configuration"""
        flags = self.amplitude_data.get('flags', [])
        experiments = self.amplitude_data.get('experiments', [])
        
        flag_keys = {f.get('key', '') for f in flags if f.get('key')}
        experiment_keys = {e.get('key', '') for e in experiments if e.get('key')}
        
        return {
            'flags': flag_keys,
            'experiments': experiment_keys,
            'all': flag_keys.union(experiment_keys)
        }

    def compare_with_codebase_config(self):
        """Compare with the configurations found in the codebase"""
        print("\n🔗 COMPARISON WITH CODEBASE CONFIGURATION")
        print("="*50)
        
        # Known experiment keys from the codebase remote-allowlist
        codebase_experiments = {
            "enable-mutual-taps-no-paywall",
            "disable-remote-profile-distance", 
            "test-backend-experiment-20230106",
            "gender-filter-a-b-20230712",
            "gender-filter",
            "project-everest-ios-20230207",
            "project-everest-android-20230207",
            "xtra-day-pass-ios-20230207",
            "xtra-day-pass-android-20230207",
            "server-driven-cascade",
            "approximate-distance",
            "unified-cascade-filters-20221019",
            "taps-paywall-ios-20230308",
            "taps-paywall-android-20230308",
            "boost-price-retest-us-ios-202302",
            "boost-price-retest-us-android-202302",
            "boost-price-retest-gb-ios-202302",
            "boost-price-test-gb-android-202302",
            "boost-price-retest-br-ios-202302",
            "boost-price-retest-br-android-202302",
            "boost-price-test-fr-ios-202302",
            "boost-price-test-fr-android-202302",
            "boost-price-test-au-ios-202302",
            "boost-price-test-au-android-202302",
            "boost-price-test-ca-ios-202302",
            "boost-price-test-ca-android-202302",
            "boost-price-test-es-ios-202302",
            "boost-price-test-es-android-202302",
            "boost-price-test-de-ios-202302",
            "boost-price-test-de-android-202302",
            "boost-price-test-mx-ios-202302",
            "boost-price-test-mx-android-202302",
            "boost-price-test-cl-ios-202302",
            "boost-price-test-cl-android-202302",
            "boost-price-test-row-ios-202302",
            "boost-price-test-row-android-202302",
            "inaccessible-profile-preview-ios",
            "inaccessible-profile-preview-android"
        }
        
        amplitude_keys = self.extract_amplitude_keys()
        
        print(f"📋 Codebase remote-allowlist: {len(codebase_experiments)} experiments")
        print(f"📋 Amplitude export: {len(amplitude_keys['all'])} total configurations")
        
        # Find matches and mismatches
        amplitude_all = amplitude_keys['all']
        found_in_amplitude = codebase_experiments.intersection(amplitude_all)
        missing_from_amplitude = codebase_experiments - amplitude_all
        extra_in_amplitude = amplitude_all - codebase_experiments
        
        print(f"\n✅ Found in both: {len(found_in_amplitude)}")
        if found_in_amplitude:
            for key in sorted(found_in_amplitude):
                print(f"   ✓ {key}")
        
        print(f"\n❌ In codebase but missing from Amplitude: {len(missing_from_amplitude)}")
        if missing_from_amplitude:
            for key in sorted(missing_from_amplitude):
                print(f"   ⚠️  {key}")
        
        print(f"\n➕ In Amplitude but not in codebase allowlist: {len(extra_in_amplitude)}")
        if extra_in_amplitude:
            for key in sorted(extra_in_amplitude):
                print(f"   📝 {key}")

    def generate_migration_checklist(self):
        """Generate a migration checklist for Statsig"""
        print("\n📝 MIGRATION CHECKLIST FOR STATSIG")
        print("="*50)
        
        flags = self.amplitude_data.get('flags', [])
        experiments = self.amplitude_data.get('experiments', [])
        
        print("## Feature Flags to Migrate:")
        enabled_flags = [f for f in flags if f.get('enabled', False)]
        for flag in enabled_flags:
            variants = flag.get('variants', [])
            variant_info = f" ({len(variants)} variants)" if len(variants) > 1 else ""
            print(f"- [ ] {flag.get('key', 'unknown')}: {flag.get('name', 'No name')}{variant_info}")
        
        print(f"\n## Experiments to Migrate:")
        running_experiments = [e for e in experiments if e.get('state') == 'running']
        for exp in running_experiments:
            variants = exp.get('variants', [])
            variant_info = f" ({len(variants)} variants)" if len(variants) > 1 else ""
            print(f"- [ ] {exp.get('key', 'unknown')}: {exp.get('name', 'No name')}{variant_info}")
        
        print(f"\n## Configuration Items to Review:")
        print("- [ ] Verify all variant keys match between platforms")
        print("- [ ] Check rollout percentages are correctly configured")
        print("- [ ] Review targeting rules and segments")
        print("- [ ] Validate experiment start/end dates")
        print("- [ ] Test payload structures match expected format")
        print("- [ ] Update application configuration allowlists")
        print("- [ ] Remove deprecated/unused experiments")

def main():
    import sys
    
    print("🔄 Amplitude to Statsig Configuration Comparator")
    print("="*50)
    
    # Check if amplitude export file exists
    amplitude_file = "amplitude_complete_export.json"
    if not os.path.exists(amplitude_file):
        print(f"❌ Amplitude export file not found: {amplitude_file}")
        print("\nFirst run: python3 amplitude_export.py")
        return
    
    # Initialize comparator
    comparator = ConfigComparator(amplitude_file)
    
    # Run analysis
    comparator.analyze_amplitude_config()
    comparator.compare_with_codebase_config()
    comparator.generate_migration_checklist()
    
    print(f"\n✅ Analysis completed!")
    print(f"💡 Next steps:")
    print(f"   1. Review the migration checklist above")
    print(f"   2. Export similar data from Statsig for comparison")
    print(f"   3. Use the checklist to ensure complete migration coverage")

if __name__ == "__main__":
    main()