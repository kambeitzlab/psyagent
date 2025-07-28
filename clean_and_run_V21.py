#!/usr/bin/env python3
"""
Clean existing V21 simulations and run fresh study
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def clean_v21_simulations():
    """Remove existing V21 simulation directories to avoid conflicts"""
    
    print("🧹 CLEANING EXISTING V21 SIMULATIONS")
    print("=" * 45)
    
    # List of V21 simulation names
    v21_simulations = [
        "V21_brief_trauma_therapy_test_baseline",
        "V21_brief_trauma_therapy_test_control", 
        "V21_brief_trauma_therapy_test_trauma_only",
        "V21_brief_trauma_therapy_test_trauma_therapy"
    ]
    
    # Clean from frontend_server storage
    storage_path = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/environment/frontend_server/storage")
    
    print(f"🗂️  Cleaning frontend storage: {storage_path}")
    for sim_name in v21_simulations:
        sim_storage_dir = storage_path / sim_name
        if sim_storage_dir.exists():
            shutil.rmtree(sim_storage_dir)
            print(f"   ✓ Removed {sim_name}")
        else:
            print(f"   - {sim_name} (not found)")
    
    # Clean from SimulationManager simulations
    try:
        from simulation_manager import simulation_manager
        sim_manager_root = simulation_manager.simulations_root
        
        print(f"\n🗂️  Cleaning SimulationManager: {sim_manager_root}")
        for sim_name in v21_simulations:
            sim_manager_dir = sim_manager_root / sim_name
            if sim_manager_dir.exists():
                shutil.rmtree(sim_manager_dir)
                print(f"   ✓ Removed {sim_name}")
            else:
                print(f"   - {sim_name} (not found)")
    except Exception as e:
        print(f"   ⚠️  Could not clean SimulationManager: {e}")
    
    print(f"\n✅ Cleanup completed")

def recreate_v21_experiment():
    """Recreate the V21 experiment configurations"""
    
    print(f"\n🧪 RECREATING V21 EXPERIMENT")
    print("=" * 35)
    
    try:
        from simulation_manager import simulation_manager
        print(f"✓ SimulationManager loaded")
    except Exception as e:
        print(f"❌ Failed to import SimulationManager: {e}")
        return False
    
    # Experiment configuration
    experiment_config = {
        "experiment_name": "V21_brief_trauma_therapy_test",
        "baseline_duration": 3,  # 3 days
        "branch_duration": 4,    # 4 days each branch
        "steps_per_hour": 2,     # 2 steps per hour
        "hours_per_day": 24,
        "agents": ["Maria Lopez"]
    }
    
    # Calculate simulation parameters
    steps_per_day = experiment_config["steps_per_hour"] * experiment_config["hours_per_day"]
    baseline_steps = experiment_config["baseline_duration"] * steps_per_day
    branch_steps = experiment_config["branch_duration"] * steps_per_day
    
    print(f"📊 Recreating with:")
    print(f"   Baseline: {baseline_steps} steps")
    print(f"   Branches: {branch_steps} steps each")
    
    # Create baseline simulation
    baseline_config = {
        "simulation_name": f"{experiment_config['experiment_name']}_baseline",
        "total_steps": baseline_steps,
        "steps_per_hour": experiment_config["steps_per_hour"],
        "description": "3-day baseline with daily PHQ-9 assessments",
        "simulation_type": "baseline",
        "questionnaires": []
    }
    
    # Add daily PHQ-9 assessments for baseline
    for day in range(1, experiment_config["baseline_duration"] + 1):
        assessment_step = day * steps_per_day - 12
        baseline_config["questionnaires"].append({
            "name": "PHQ-9",
            "step": assessment_step,
            "target_agents": experiment_config["agents"],
            "description": f"Day {day} baseline PHQ-9 assessment"
        })
    
    try:
        baseline_sim = simulation_manager.create_simulation(
            simulation_id=baseline_config["simulation_name"],
            config=baseline_config,
            agents=experiment_config["agents"]
        )
        print(f"✓ Baseline recreated: {baseline_sim.simulation_id}")
    except Exception as e:
        print(f"❌ Failed to recreate baseline: {e}")
        return False
    
    # Define branch configurations
    branches = {
        "control": {
            "description": "Control condition: No trauma, no therapy",
            "events": []
        },
        "trauma_only": {
            "description": "Trauma condition: Trauma event on day 1, no therapy",
            "events": [
                {
                    "name": "witness_violence_trauma",
                    "step": 12,
                    "type": "negative",
                    "target": "Maria Lopez",
                    "description": "While walking through the town square, Maria witnesses a brutal mugging where a young mother with a baby is violently attacked. Maria freezes in terror, unable to help as the attacker injures the woman before stealing her purse. The woman's baby cries uncontrollably. Maria is haunted by her inability to act and learns later that the victim was hospitalized with serious injuries."
                }
            ]
        },
        "trauma_therapy": {
            "description": "Treatment condition: Trauma event + enhanced therapy sessions",
            "events": [
                {
                    "name": "witness_violence_trauma",
                    "step": 12,
                    "type": "negative", 
                    "target": "Maria Lopez",
                    "description": "While walking through the town square, Maria witnesses a brutal mugging where a young mother with a baby is violently attacked. Maria freezes in terror, unable to help as the attacker injures the woman before stealing her purse. The woman's baby cries uncontrollably. Maria is haunted by her inability to act and learns later that the victim was hospitalized with serious injuries."
                },
                {
                    "name": "therapy_session_1",
                    "step": 36,
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Maria starts CBT for witness trauma and moral injury. The therapist validates her freeze response as a normal survival mechanism. Session 1 covers trauma psychoeducation and challenges Maria's self-critical thoughts about not helping. They begin identifying cognitive distortions and practice grounding techniques for managing intrusive thoughts about the assault."
                },
                {
                    "name": "therapy_session_2", 
                    "step": 84,
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Therapy session 2: Focus on processing the traumatic memory and developing coping strategies for intrusive thoughts and guilt feelings."
                }
            ]
        }
    }
    
    # Create branch simulations
    created_branches = []
    for branch_name, branch_info in branches.items():
        branch_config = {
            "simulation_name": f"{experiment_config['experiment_name']}_{branch_name}",
            "total_steps": branch_steps,
            "steps_per_hour": experiment_config["steps_per_hour"],
            "description": branch_info["description"],
            "simulation_type": branch_name,
            "questionnaires": [],
            "timed_events": branch_info["events"]
        }
        
        # Add daily PHQ-9 assessments for branch
        for day in range(1, experiment_config["branch_duration"] + 1):
            assessment_step = day * steps_per_day - 12
            branch_config["questionnaires"].append({
                "name": "PHQ-9", 
                "step": assessment_step,
                "target_agents": experiment_config["agents"],
                "description": f"Day {day} {branch_name} PHQ-9 assessment"
            })
        
        try:
            branch_sim = simulation_manager.branch_simulation(
                parent_id=baseline_config["simulation_name"],
                target_id=branch_config["simulation_name"],
                branch_type=branch_name,
                branch_config=branch_config,
                branched_at_step=baseline_steps
            )
            created_branches.append(branch_sim)
            print(f"✓ {branch_name} branch recreated: {branch_sim.simulation_id}")
        except Exception as e:
            print(f"❌ Failed to recreate {branch_name} branch: {e}")
            return False
    
    print(f"\n✅ V21 experiment recreated successfully")
    return True

def run_simulation_with_manager(simulation_name):
    """Run a single simulation"""
    
    print(f"\n🔄 Running {simulation_name}...")
    
    try:
        os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
        
        from reverie import run_simulation_programmatically
        from simulation_manager import simulation_manager
        
        # Get simulation metadata
        sim_dir = simulation_manager.simulations_root / simulation_name
        metadata_file = sim_dir / "metadata.json"
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Get the full experiment config from metadata (includes questionnaires & events)
        config = metadata.get('experiment_config', {})
        total_steps = config.get('total_steps', 144)
        
        # Add required parameters to config
        config['working_dir'] = str(simulation_manager.simulations_root)
        config['simulation_name'] = simulation_name
        
        # Ensure simulation_type is set
        if 'simulation_type' not in config:
            if 'baseline' in simulation_name:
                config['simulation_type'] = 'baseline'
            elif 'control' in simulation_name:
                config['simulation_type'] = 'control'
            elif 'trauma_only' in simulation_name:
                config['simulation_type'] = 'trauma_only'
            elif 'trauma_therapy' in simulation_name:
                config['simulation_type'] = 'trauma_therapy'
            else:
                config['simulation_type'] = 'experiment'
        
        print(f"   📊 Running {total_steps} steps...")
        
        # Run the simulation
        simulation = run_simulation_programmatically(
            origin_sim="base_the_ville_isabella_maria_klaus",
            target_sim=simulation_name,
            steps=total_steps,
            headless=True,
            config=config
        )
        
        print(f"   ✅ {simulation_name} completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ {simulation_name} failed: {e}")
        return False

def main():
    """Main execution function"""
    
    print("🧪 V21 CLEAN & RUN SCRIPT")
    print("=" * 30)
    
    # Step 1: Clean existing simulations
    clean_v21_simulations()
    
    # Step 2: Recreate experiment
    if not recreate_v21_experiment():
        print("❌ Failed to recreate experiment")
        return False
    
    # Step 3: Run all simulations
    print(f"\n🚀 RUNNING V21 SIMULATIONS")
    print("=" * 30)
    
    simulations = [
        "V21_brief_trauma_therapy_test_baseline",
        "V21_brief_trauma_therapy_test_control", 
        "V21_brief_trauma_therapy_test_trauma_only",
        "V21_brief_trauma_therapy_test_trauma_therapy"
    ]
    
    completed = []
    failed = []
    
    for i, sim_name in enumerate(simulations, 1):
        print(f"\n[{i}/{len(simulations)}] {sim_name}")
        success = run_simulation_with_manager(sim_name)
        
        if success:
            completed.append(sim_name)
        else:
            failed.append(sim_name)
    
    # Summary
    print(f"\n📊 FINAL SUMMARY")
    print("=" * 20)
    print(f"✅ Completed: {len(completed)}/{len(simulations)}")
    for sim in completed:
        print(f"   • {sim}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for sim in failed:
            print(f"   • {sim}")
    
    return len(completed) == len(simulations)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 V21 STUDY COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  V21 STUDY COMPLETED WITH FAILURES")
        sys.exit(1)