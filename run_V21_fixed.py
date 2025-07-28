#!/usr/bin/env python3
"""
V21 Fixed Execution Script - Run simulations using SimulationManager approach
"""

import os
import sys
import json
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def run_simulation_with_manager(simulation_name):
    """Run a single simulation using the proper SimulationManager approach"""
    
    print(f"\n🔄 Running {simulation_name}...")
    
    try:
        # Change to the reverie backend directory
        os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
        
        # Import the simulation runner
        from reverie import run_simulation_programmatically
        from simulation_manager import simulation_manager
        
        # Get simulation metadata
        sim_dir = simulation_manager.simulations_root / simulation_name
        if not sim_dir.exists():
            print(f"❌ Simulation directory not found: {sim_dir}")
            return False
            
        # Load simulation config
        metadata_file = sim_dir / "metadata.json"
        if not metadata_file.exists():
            print(f"❌ Metadata file not found: {metadata_file}")
            return False
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        config = metadata.get('config', {})
        total_steps = config.get('total_steps', 144)
        
        # Add required working_dir and simulation_name to config
        config['working_dir'] = str(simulation_manager.simulations_root)
        config['simulation_name'] = simulation_name
        
        print(f"   📊 Configuration: {total_steps} steps")
        print(f"   📁 Working dir: {config['working_dir']}")
        
        # Run the simulation
        simulation = run_simulation_programmatically(
            origin_sim="base_the_ville_isabella_maria_klaus",
            target_sim=simulation_name,
            steps=total_steps,
            headless=True,
            config=config
        )
        
        print(f"   ✅ {simulation_name} completed successfully")
        print(f"   📈 Results: {len(simulation.personas)} personas, simulation step {simulation.step}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ {simulation_name} failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_v21_study_fixed():
    """Execute all V21 simulations using the correct approach"""
    
    print("🚀 EXECUTING V21 BRIEF TRAUMA & THERAPY STUDY (FIXED)")
    print("=" * 60)
    
    # Import simulation manager to verify simulations exist
    try:
        from simulation_manager import simulation_manager
        print(f"✓ SimulationManager loaded")
        print(f"  Root: {simulation_manager.simulations_root}")
    except Exception as e:
        print(f"❌ Failed to import SimulationManager: {e}")
        return False
    
    # List of V21 simulations in execution order
    simulations = [
        "V21_brief_trauma_therapy_test_baseline",
        "V21_brief_trauma_therapy_test_control", 
        "V21_brief_trauma_therapy_test_trauma_only",
        "V21_brief_trauma_therapy_test_trauma_therapy"
    ]
    
    # Verify all simulations exist
    print(f"\n🔍 Verifying simulations exist...")
    for sim_name in simulations:
        sim_dir = simulation_manager.simulations_root / sim_name
        if sim_dir.exists():
            print(f"   ✓ {sim_name}")
        else:
            print(f"   ❌ {sim_name} - NOT FOUND")
            return False
    
    print(f"\n⏱️  Estimated total runtime: ~30-45 minutes")
    print(f"💾 Results will be stored in centralized locations")
    
    # Execute simulations
    completed = []
    failed = []
    
    for i, sim_name in enumerate(simulations, 1):
        print(f"\n{'='*20} [{i}/{len(simulations)}] {'='*20}")
        
        success = run_simulation_with_manager(sim_name)
        
        if success:
            completed.append(sim_name)
        else:
            failed.append(sim_name)
    
    # Summary
    print(f"\n{'='*20} EXECUTION SUMMARY {'='*20}")
    print(f"✅ Completed: {len(completed)}/{len(simulations)}")
    for sim in completed:
        print(f"   • {sim}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for sim in failed:
            print(f"   • {sim}")
    
    # Results locations
    if completed:
        print(f"\n📁 Results can be found in:")
        print(f"   /simulations/[simulation_name]/all_logs/")
        print(f"   - therapy_events.jsonl (detailed therapy conversations)")
        print(f"   - events.jsonl (all simulation events)")
        print(f"   /simulations/[simulation_name]/assessment_results/")
        print(f"   - PHQ-9 assessment JSON files")
    
    print(f"\n🔬 Analysis Steps:")
    print(f"   1. Check PHQ-9 scores: Control vs Trauma Only vs Trauma+Therapy")
    print(f"   2. Verify trauma memories retrieved during assessments")
    print(f"   3. Examine enhanced therapeutic memories created")
    print(f"   4. Compare therapy effectiveness between conditions")
    
    return len(completed) == len(simulations)

if __name__ == "__main__":
    success = run_v21_study_fixed()
    if success:
        print("\n🎉 V21 STUDY COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  V21 STUDY COMPLETED WITH FAILURES")
        sys.exit(1)