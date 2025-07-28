#!/usr/bin/env python3
"""
Manually test the copying methods
"""

import os
import sys
from pathlib import Path

# Add paths for imports
os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def manual_copy_test():
    """Manually test copying for our comprehensive test"""
    print("🔧 MANUAL COPY TEST")
    print("="*40)
    
    test_sim_id = "comprehensive_test_20250726_230407"
    
    # Manual implementation of the copying logic
    try:
        from simulation_manager import simulation_manager
        import shutil
        
        # Debug path resolution
        print(f"Current file: {__file__}")
        print(f"Parent: {Path(__file__).parent}")
        print(f"Parent.parent: {Path(__file__).parent.parent}")
        print(f"Parent.parent.parent: {Path(__file__).parent.parent.parent}")
        
        # Check sim_dir exists
        sim_dir = simulation_manager.simulations_root / test_sim_id
        print(f"Simulation directory: {sim_dir}")
        print(f"Exists: {sim_dir.exists()}")
        
        if not sim_dir.exists():
            print("❌ Simulation directory doesn't exist!")
            return
        
        # Test copying logs
        print(f"\n📝 Testing log copying...")
        central_logs_dir = sim_dir / "all_logs"
        central_logs_dir.mkdir(exist_ok=True)
        
        # Copy simulation-specific logs
        sim_logs_dir = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server/logs") / test_sim_id
        print(f"Looking for logs at: {sim_logs_dir}")
        print(f"Logs exist: {sim_logs_dir.exists()}")
        
        if sim_logs_dir.exists():
            print(f"Files in logs dir:")
            for item in sim_logs_dir.rglob("*"):
                if item.is_file():
                    print(f"  📄 {item.relative_to(sim_logs_dir)} ({item.stat().st_size} bytes)")
            
            dest_logs = central_logs_dir / "simulation_logs"
            if dest_logs.exists():
                shutil.rmtree(dest_logs)
            shutil.copytree(sim_logs_dir, dest_logs)
            print(f"✅ Copied simulation logs to {dest_logs}")
        
        # Test copying simulation data
        print(f"\n💾 Testing simulation data copying...")
        storage_path = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/environment/frontend_server/storage") / test_sim_id
        print(f"Looking for storage at: {storage_path}")
        print(f"Storage exists: {storage_path.exists()}")
        
        if storage_path.exists():
            central_data_dir = sim_dir / "simulation_data"
            
            # Copy movement files
            movement_source = storage_path / "movement"
            if movement_source.exists():
                movement_dest = central_data_dir / "movement"
                if movement_dest.exists():
                    shutil.rmtree(movement_dest)
                shutil.copytree(movement_source, movement_dest)
                print(f"✅ Copied movement data ({len(list(movement_source.glob('*.json')))} files)")
            
            # Copy environment files
            environment_source = storage_path / "environment"
            if environment_source.exists():
                environment_dest = central_data_dir / "environment"
                if environment_dest.exists():
                    shutil.rmtree(environment_dest)
                shutil.copytree(environment_source, environment_dest)
                print(f"✅ Copied environment data ({len(list(environment_source.glob('*.json')))} files)")
            
            # Copy personas data
            personas_source = storage_path / "personas"
            if personas_source.exists():
                personas_dest = central_data_dir / "personas"
                if personas_dest.exists():
                    shutil.rmtree(personas_dest)
                shutil.copytree(personas_source, personas_dest)
                print(f"✅ Copied personas data")
            
            # Copy reverie metadata
            reverie_source = storage_path / "reverie"
            if reverie_source.exists():
                reverie_dest = central_data_dir / "reverie"
                if reverie_dest.exists():
                    shutil.rmtree(reverie_dest)
                shutil.copytree(reverie_source, reverie_dest)
                print(f"✅ Copied reverie metadata")
        
        print(f"\n✅ Manual copying completed!")
        
    except Exception as e:
        print(f"❌ Manual copying failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_copy_test()