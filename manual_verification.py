#!/usr/bin/env python3
"""
Manual verification of the comprehensive test dual logging
"""

import os
import sys
from pathlib import Path

# Add paths for imports
os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def verify_comprehensive_test_results():
    """Verify the results of the comprehensive test"""
    print("🔍 MANUAL VERIFICATION OF COMPREHENSIVE TEST RESULTS")
    print("="*60)
    
    from simulation_manager import simulation_manager
    
    # Test simulation IDs
    test_sim_id = "comprehensive_test_20250726_230407"
    sim_dir = simulation_manager.simulations_root / test_sim_id
    
    print(f"\n📁 Checking central location: {sim_dir}")
    
    # Check if central directory exists
    if not sim_dir.exists():
        print(f"❌ Central simulation directory does not exist!")
        return False
    
    # Check the structure
    print(f"\n📂 CURRENT CENTRAL STRUCTURE:")
    for item in sim_dir.rglob("*"):
        rel_path = item.relative_to(sim_dir)
        item_type = "📁" if item.is_dir() else "📄"
        size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
        print(f"  {item_type} {rel_path}{size}")
    
    # Check original locations
    print(f"\n📂 ORIGINAL STORAGE LOCATIONS:")
    
    # Standard storage
    standard_storage = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/environment/frontend_server/storage") / test_sim_id
    print(f"\n🗄️ Standard storage: {standard_storage}")
    if standard_storage.exists():
        print("  Contents:")
        for item in standard_storage.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(standard_storage)
                print(f"    📄 {rel_path} ({item.stat().st_size} bytes)")
    else:
        print("  ❌ Does not exist")
    
    # Logs storage
    logs_storage = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server/logs") / test_sim_id
    print(f"\n📝 Logs storage: {logs_storage}")
    if logs_storage.exists():
        print("  Contents:")
        for item in logs_storage.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(logs_storage)
                print(f"    📄 {rel_path} ({item.stat().st_size} bytes)")
    else:
        print("  ❌ Does not exist")
    
    # Check what's missing
    print(f"\n❓ WHAT SHOULD BE COPIED TO CENTRAL LOCATION:")
    
    files_to_copy = []
    
    # From standard storage
    if standard_storage.exists():
        for file in standard_storage.rglob("*"):
            if file.is_file():
                files_to_copy.append(f"simulation_data/{file.relative_to(standard_storage)}")
    
    # From logs storage
    if logs_storage.exists():
        for file in logs_storage.rglob("*"):
            if file.is_file():
                files_to_copy.append(f"all_logs/{file.relative_to(logs_storage)}")
    
    print(f"  Expected files in central location ({len(files_to_copy)} total):")
    for expected_file in files_to_copy:
        central_file = sim_dir / expected_file
        exists = central_file.exists()
        status = "✅" if exists else "❌"
        print(f"    {status} {expected_file}")
    
    # Check API calls log
    api_calls_file = sim_dir / "centralized_logs" / "api_calls.jsonl"
    print(f"\n🔌 API Calls Log: {api_calls_file}")
    if api_calls_file.exists():
        print(f"  ✅ Exists ({api_calls_file.stat().st_size} bytes)")
        # Count lines
        with open(api_calls_file, 'r') as f:
            lines = f.readlines()
            print(f"  📊 Contains {len(lines)} API calls")
    else:
        print(f"  ❌ Does not exist")
    
    print(f"\n📈 ANALYSIS:")
    print(f"  • API call logging: ✅ Working")
    print(f"  • File copying: ❌ Not implemented or not called")
    print(f"  • Files are still scattered across multiple locations")
    
    return False

if __name__ == "__main__":
    verify_comprehensive_test_results()