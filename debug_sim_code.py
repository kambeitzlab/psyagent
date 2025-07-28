#!/usr/bin/env python3
"""
Debug sim_code attribute issue
"""

import os
import sys
from pathlib import Path

# Add paths for imports
os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def test_sim_code_issue():
    """Debug the sim_code issue"""
    print("🐛 DEBUGGING SIM_CODE ISSUE")
    print("="*40)
    
    from reverie import ReverieServer
    
    # Create a server like in our test
    test_sim_id = "comprehensive_test_20250726_230407"
    
    rs = ReverieServer(
        "base_the_ville_isabella_maria_klaus",
        test_sim_id,
        working_dir=None,
        simulation_name=test_sim_id,
        simulation_type="comprehensive_test",
        preserve_origin_state=False
    )
    
    print(f"sim_code attribute: {getattr(rs, 'sim_code', 'NOT FOUND')}")
    print(f"target_sim: {getattr(rs, 'target_sim', 'NOT FOUND')}")
    print(f"simulation_name: {getattr(rs, 'simulation_name', 'NOT FOUND')}")
    
    # Test the copying methods manually
    print(f"\n🧪 Testing _copy_logs_to_central_location()...")
    try:
        rs._copy_logs_to_central_location()
        print(f"✅ Method completed")
    except Exception as e:
        print(f"❌ Method failed: {e}")
    
    print(f"\n🧪 Testing _copy_simulation_data_to_central_location()...")
    try:
        rs._copy_simulation_data_to_central_location()
        print(f"✅ Method completed")
    except Exception as e:
        print(f"❌ Method failed: {e}")

if __name__ == "__main__":
    test_sim_code_issue()