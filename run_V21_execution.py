#!/usr/bin/env python3
"""
V21 Execution Script - Run the brief trauma therapy study
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def run_v21_study():
    """Execute all V21 simulations in sequence"""
    
    print("🚀 EXECUTING V21 BRIEF TRAUMA & THERAPY STUDY")
    print("=" * 50)
    
    # Define simulation execution order
    simulations = [
        {
            "name": "V21_brief_trauma_therapy_test_baseline",
            "description": "3-day baseline with daily PHQ-9",
            "duration": "3 days (144 steps)"
        },
        {
            "name": "V21_brief_trauma_therapy_test_control", 
            "description": "Control: No intervention",
            "duration": "4 days (192 steps)"
        },
        {
            "name": "V21_brief_trauma_therapy_test_trauma_only",
            "description": "Trauma only condition",
            "duration": "4 days (192 steps)"
        },
        {
            "name": "V21_brief_trauma_therapy_test_trauma_therapy",
            "description": "Trauma + enhanced therapy",
            "duration": "4 days (192 steps)"
        }
    ]
    
    print(f"📋 Simulation Sequence:")
    for i, sim in enumerate(simulations, 1):
        print(f"   {i}. {sim['name']}")
        print(f"      {sim['description']} - {sim['duration']}")
    
    print(f"\n⏱️  Estimated total runtime: ~30-45 minutes")
    print(f"💾 Results will be stored in centralized locations")
    
    # Execute simulations
    completed = []
    failed = []
    
    for i, sim in enumerate(simulations, 1):
        sim_name = sim['name']
        print(f"\n🔄 [{i}/{len(simulations)}] Running {sim_name}...")
        print(f"    {sim['description']}")
        
        try:
            # Change to the reverie backend directory
            os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
            
            # Run simulation using the backend script
            result = subprocess.run([
                'python', 'run_simulation.py',
                'base_the_ville_isabella_maria_klaus',  # origin simulation
                sim_name,  # target simulation
                '--headless'
            ], capture_output=True, text=True, timeout=900)  # 15 minute timeout per simulation
            
            if result.returncode == 0:
                completed.append(sim_name)
                print(f"    ✅ {sim_name} completed successfully")
            else:
                failed.append(sim_name)
                print(f"    ❌ {sim_name} failed with return code {result.returncode}")
                print(f"    Error output: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            failed.append(sim_name)
            print(f"    ⏰ {sim_name} timed out after 15 minutes")
            
        except Exception as e:
            failed.append(sim_name)
            print(f"    ❌ {sim_name} failed with exception: {e}")
    
    # Summary
    print(f"\n📊 EXECUTION SUMMARY")
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
    
    print(f"\n🔬 Next Steps:")
    print(f"   1. Analyze PHQ-9 scores across conditions")
    print(f"   2. Check trauma event retrieval in assessments")
    print(f"   3. Examine specific therapeutic memories created")
    print(f"   4. Compare therapy effectiveness")
    
    return len(completed) == len(simulations)

if __name__ == "__main__":
    success = run_v21_study()
    if success:
        print("\n🎉 V21 STUDY COMPLETED SUCCESSFULLY!")
    else:
        print("\n⚠️  V21 STUDY COMPLETED WITH SOME FAILURES")
        sys.exit(1)