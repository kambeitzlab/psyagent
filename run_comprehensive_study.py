#!/usr/bin/env python3
"""
Execute Comprehensive Trauma & Therapy Study V22
Run the complete study with enhanced therapeutic insights
"""

import os
import sys
import json
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def run_simulation_with_manager(simulation_name):
    """Run a single simulation using the SimulationManager approach"""
    
    print(f"\n🔄 Running {simulation_name}...")
    
    try:
        os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
        
        from reverie import run_simulation_programmatically
        from simulation_manager import simulation_manager
        
        # Get simulation metadata
        sim_dir = simulation_manager.simulations_root / simulation_name
        if not sim_dir.exists():
            print(f"❌ Simulation directory not found: {sim_dir}")
            return False
            
        metadata_file = sim_dir / "metadata.json"
        if not metadata_file.exists():
            print(f"❌ Metadata file not found: {metadata_file}")
            return False
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        config = metadata.get('experiment_config', {})
        total_steps = config.get('total_steps', 672)
        questionnaires = len(config.get('questionnaires', []))
        events = len(config.get('timed_events', []))
        
        # Add required parameters
        config['working_dir'] = str(simulation_manager.simulations_root)
        config['simulation_name'] = simulation_name
        
        print(f"   📊 Configuration:")
        print(f"     Steps: {total_steps}")
        print(f"     PHQ-9 assessments: {questionnaires}")
        print(f"     Events: {events}")
        print(f"   🧠 Enhanced therapeutic insights: ENABLED")
        
        # Run the simulation
        simulation = run_simulation_programmatically(
            origin_sim="base_the_ville_isabella_maria_klaus",
            target_sim=simulation_name,
            steps=total_steps,
            headless=True,
            config=config
        )
        
        print(f"   ✅ {simulation_name} completed successfully")
        print(f"   📈 Final: {len(simulation.personas)} personas at step {simulation.step}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ {simulation_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_study():
    """Execute the complete comprehensive trauma & therapy study"""
    
    print("🚀 EXECUTING COMPREHENSIVE TRAUMA & THERAPY STUDY V22")
    print("=" * 65)
    
    # Import simulation manager to verify simulations exist
    try:
        from simulation_manager import simulation_manager
        print(f"✓ SimulationManager loaded")
        print(f"  Root: {simulation_manager.simulations_root}")
    except Exception as e:
        print(f"❌ Failed to import SimulationManager: {e}")
        return False
    
    # List of V22 simulations in execution order
    simulations = [
        "comprehensive_trauma_therapy_V22_baseline",
        "comprehensive_trauma_therapy_V22_control", 
        "comprehensive_trauma_therapy_V22_trauma_only",
        "comprehensive_trauma_therapy_V22_trauma_therapy"
    ]
    
    # Verify all simulations exist
    print(f"\n🔍 Verifying simulations exist...")
    for sim_name in simulations:
        sim_dir = simulation_manager.simulations_root / sim_name
        if sim_dir.exists():
            # Check configuration
            metadata_file = sim_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            config = metadata.get('experiment_config', {})
            questionnaires = len(config.get('questionnaires', []))
            events = len(config.get('timed_events', []))
            print(f"   ✓ {sim_name}: {questionnaires} PHQ-9, {events} events")
        else:
            print(f"   ❌ {sim_name} - NOT FOUND")
            return False
    
    print(f"\n⏱️  Estimated runtime:")
    print(f"   Baseline (7 days): ~15-20 minutes")
    print(f"   Control (14 days): ~25-35 minutes")
    print(f"   Trauma-only (14 days): ~25-35 minutes")
    print(f"   Trauma+therapy (14 days + 5 sessions): ~30-40 minutes")
    print(f"   Total: ~1.5-2.5 hours")
    
    print(f"\n💾 Results will be stored in centralized locations")
    print(f"📊 49 total PHQ-9 assessments will be administered")
    print(f"🧠 Enhanced therapeutic insights will be extracted")
    
    # Execute simulations
    completed = []
    failed = []
    
    for i, sim_name in enumerate(simulations, 1):
        print(f"\n{'='*20} [{i}/{len(simulations)}] {'='*20}")
        
        # Show what this simulation will test
        if "baseline" in sim_name:
            print(f"📊 BASELINE: Establishing stable PHQ-9 measurements")
        elif "control" in sim_name:
            print(f"🔘 CONTROL: No intervention - natural progression")
        elif "trauma_only" in sim_name:
            print(f"⚡ TRAUMA ONLY: Severe assault + no therapy")
        elif "trauma_therapy" in sim_name:
            print(f"🩺 TRAUMA + THERAPY: Severe assault + 5 therapy sessions")
        
        success = run_simulation_with_manager(sim_name)
        
        if success:
            completed.append(sim_name)
        else:
            failed.append(sim_name)
    
    # Summary
    print(f"\n{'='*20} EXECUTION SUMMARY {'='*20}")
    print(f"✅ Completed: {len(completed)}/{len(simulations)}")
    for sim in completed:
        condition = sim.split('_')[-1]
        print(f"   • {condition}: ✓")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for sim in failed:
            condition = sim.split('_')[-1]
            print(f"   • {condition}: ✗")
    
    # Results information
    if completed:
        print(f"\n📁 Results locations:")
        print(f"   Assessment results: /simulations/[condition]/assessment_results/")
        print(f"   Therapy conversations: /simulations/[condition]/all_logs/therapy_events.jsonl")
        print(f"   All events: /simulations/[condition]/all_logs/events.jsonl")
        print(f"   Debug logs: /simulations/[condition]/all_logs/simulation_debug.log")
    
    print(f"\n🔬 Analysis ready for:")
    print(f"   1. Baseline stability verification (7 daily PHQ-9)")
    print(f"   2. Trauma impact measurement (control vs trauma-only)")
    print(f"   3. Therapy efficacy assessment (trauma-only vs trauma+therapy)")
    print(f"   4. Enhanced therapeutic insights validation")
    print(f"   5. Longitudinal trajectory analysis (21-day span)")
    
    return len(completed) == len(simulations)

if __name__ == "__main__":
    success = run_comprehensive_study()
    if success:
        print("\n🎉 COMPREHENSIVE STUDY COMPLETED SUCCESSFULLY!")
        print("Ready for analysis and visualization")
        sys.exit(0)
    else:
        print("\n⚠️  COMPREHENSIVE STUDY COMPLETED WITH FAILURES")
        sys.exit(1)