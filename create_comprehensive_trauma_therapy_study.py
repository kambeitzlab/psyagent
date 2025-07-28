#!/usr/bin/env python3
"""
Comprehensive Trauma and Therapy Study Design
Create a well-designed study to clearly demonstrate trauma effects and therapy efficacy
"""

import os
import sys
import json
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def create_comprehensive_study():
    """Create a comprehensive trauma and therapy study with optimal parameters"""
    
    print("🧪 COMPREHENSIVE TRAUMA & THERAPY STUDY")
    print("=" * 50)
    
    try:
        from simulation_manager import simulation_manager
        print(f"✓ SimulationManager loaded")
    except Exception as e:
        print(f"❌ Failed to import SimulationManager: {e}")
        return False
    
    # Study parameters (optimized for clear effect detection)
    study_config = {
        "experiment_name": "comprehensive_trauma_therapy_V22",
        "baseline_duration": 7,    # 7 days baseline for stable measurement
        "branch_duration": 14,     # 14 days for trauma/therapy effects to develop
        "steps_per_hour": 4,       # 4 steps/hour for more granular behavior
        "hours_per_day": 24,
        "agents": ["Maria Lopez"]
    }
    
    # Calculate simulation parameters
    steps_per_day = study_config["steps_per_hour"] * study_config["hours_per_day"]
    baseline_steps = study_config["baseline_duration"] * steps_per_day
    branch_steps = study_config["branch_duration"] * steps_per_day
    
    print(f"📊 Study Design:")
    print(f"   Baseline: {study_config['baseline_duration']} days ({baseline_steps} steps)")
    print(f"   Branches: {study_config['branch_duration']} days ({branch_steps} steps each)")
    print(f"   Resolution: {study_config['steps_per_hour']} steps/hour (15 min intervals)")
    print(f"   Total duration: {study_config['baseline_duration'] + study_config['branch_duration']} days per condition")
    
    # Create baseline simulation with daily PHQ-9 assessments
    baseline_config = {
        "simulation_name": f"{study_config['experiment_name']}_baseline",
        "total_steps": baseline_steps,
        "steps_per_hour": study_config["steps_per_hour"],
        "description": "7-day baseline with daily PHQ-9 assessments for stable measurement",
        "simulation_type": "baseline",
        "questionnaires": []
    }
    
    # Add daily PHQ-9 assessments for baseline (end of each day)
    for day in range(1, study_config["baseline_duration"] + 1):
        assessment_step = day * steps_per_day - 8  # 2 hours before midnight
        baseline_config["questionnaires"].append({
            "name": "PHQ-9",
            "step": assessment_step,
            "target_agents": study_config["agents"],
            "description": f"Day {day} baseline PHQ-9 assessment"
        })
    
    print(f"\n🏗️  Creating baseline simulation...")
    try:
        baseline_sim = simulation_manager.create_simulation(
            simulation_id=baseline_config["simulation_name"],
            config=baseline_config,
            agents=study_config["agents"]
        )
        print(f"✓ Baseline created: {baseline_sim.simulation_id}")
        print(f"  📋 {len(baseline_config['questionnaires'])} daily PHQ-9 assessments scheduled")
    except Exception as e:
        print(f"❌ Failed to create baseline: {e}")
        return False
    
    # Define branch configurations with optimized timing
    branches = {
        "control": {
            "description": "Control condition: No trauma, no therapy - natural progression",
            "events": []
        },
        "trauma_only": {
            "description": "Trauma condition: Severe trauma event, no therapeutic intervention",
            "events": [
                {
                    "name": "severe_assault_trauma",
                    "step": 32,  # Day 1, 8 AM (8 hours into branch)
                    "type": "negative",
                    "target": "Maria Lopez",
                    "description": "While walking to the college library early in the morning, Maria witnesses a brutal assault where a young student is violently attacked by multiple assailants. Maria watches in horror as the victim is severely beaten and left unconscious. Despite wanting to help, Maria freezes in terror and feels overwhelming helplessness. The incident leaves Maria deeply traumatized with persistent intrusive thoughts, guilt about not intervening, and fear of similar situations."
                }
            ]
        },
        "trauma_therapy": {
            "description": "Treatment condition: Trauma event + intensive therapy intervention",
            "events": [
                {
                    "name": "severe_assault_trauma",
                    "step": 32,  # Day 1, 8 AM
                    "type": "negative", 
                    "target": "Maria Lopez",
                    "description": "While walking to the college library early in the morning, Maria witnesses a brutal assault where a young student is violently attacked by multiple assailants. Maria watches in horror as the victim is severely beaten and left unconscious. Despite wanting to help, Maria freezes in terror and feels overwhelming helplessness. The incident leaves Maria deeply traumatized with persistent intrusive thoughts, guilt about not intervening, and fear of similar situations."
                },
                {
                    "name": "trauma_therapy_session_1",
                    "step": 72,  # Day 1, 6 PM (same day as trauma)
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Emergency therapy session with Dr. Sarah Thompson focusing on acute trauma response, psychoeducation about trauma reactions, and initial stabilization techniques. Session covers breathing exercises, grounding techniques, and normalizing the freeze response."
                },
                {
                    "name": "trauma_therapy_session_2",
                    "step": 168,  # Day 3, 6 PM
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Second therapy session focusing on processing traumatic memories, cognitive restructuring of guilt and self-blame, and developing personalized coping strategies for intrusive thoughts and hypervigilance."
                },
                {
                    "name": "trauma_therapy_session_3",
                    "step": 264,  # Day 5, 6 PM
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Third therapy session working on exposure therapy techniques, building resilience, and creating safety plans for triggering situations. Focus on visualization exercises and building confidence in personal agency."
                },
                {
                    "name": "trauma_therapy_session_4",
                    "step": 456,  # Day 9, 6 PM
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Fourth therapy session focusing on integration of coping skills, relapse prevention, and building long-term emotional regulation strategies. Review progress and adjust treatment plan."
                },
                {
                    "name": "trauma_therapy_session_5",
                    "step": 648,  # Day 13, 6 PM
                    "type": "therapy",
                    "target": "Maria Lopez",
                    "description": "Final therapy session focusing on consolidating therapeutic gains, building ongoing self-care practices, and establishing confidence in managing trauma-related symptoms independently."
                }
            ]
        }
    }
    
    print(f"\n🌿 Creating branch simulations...")
    created_branches = []
    
    for branch_name, branch_info in branches.items():
        branch_config = {
            "simulation_name": f"{study_config['experiment_name']}_{branch_name}",
            "total_steps": branch_steps,
            "steps_per_hour": study_config["steps_per_hour"],
            "description": branch_info["description"],
            "simulation_type": branch_name,
            "questionnaires": [],
            "timed_events": branch_info["events"]
        }
        
        # Add daily PHQ-9 assessments for branch (end of each day)
        for day in range(1, study_config["branch_duration"] + 1):
            assessment_step = day * steps_per_day - 8  # 2 hours before midnight
            branch_config["questionnaires"].append({
                "name": "PHQ-9", 
                "step": assessment_step,
                "target_agents": study_config["agents"],
                "description": f"Day {day} {branch_name} PHQ-9 assessment"
            })
        
        print(f"\n  🔄 Creating {branch_name} branch...")
        print(f"    Events: {len(branch_info['events'])}")
        print(f"    PHQ-9 assessments: {len(branch_config['questionnaires'])}")
        
        try:
            branch_sim = simulation_manager.branch_simulation(
                parent_id=baseline_config["simulation_name"],
                target_id=branch_config["simulation_name"],
                branch_type=branch_name,
                branch_config=branch_config,
                branched_at_step=baseline_steps
            )
            created_branches.append(branch_sim)
            print(f"    ✓ {branch_name} branch created: {branch_sim.simulation_id}")
        except Exception as e:
            print(f"    ❌ Failed to create {branch_name} branch: {e}")
            return False
    
    # Display comprehensive study summary
    print(f"\n🎯 STUDY SUMMARY")
    print("=" * 20)
    print(f"Experiment: {study_config['experiment_name']}")
    print(f"Total simulations: 4 (1 baseline + 3 conditions)")
    print(f"Total duration: {study_config['baseline_duration'] + study_config['branch_duration']} days per condition")
    print(f"Temporal resolution: {study_config['steps_per_hour']} steps/hour (15-minute intervals)")
    print(f"Assessment frequency: Daily PHQ-9 at end of each day")
    
    print(f"\n📊 ASSESSMENT SCHEDULE:")
    print(f"Baseline: {study_config['baseline_duration']} PHQ-9 assessments")
    print(f"Control: {study_config['branch_duration']} PHQ-9 assessments")
    print(f"Trauma-only: {study_config['branch_duration']} PHQ-9 assessments")
    print(f"Trauma+therapy: {study_config['branch_duration']} PHQ-9 assessments")
    print(f"Total assessments: {study_config['baseline_duration'] + 3 * study_config['branch_duration']}")
    
    print(f"\n⚡ INTERVENTION TIMELINE (Trauma+Therapy):")
    print(f"Day 1, 8 AM: Severe assault trauma (step 32)")
    print(f"Day 1, 6 PM: Emergency therapy session (step 72)")
    print(f"Day 3, 6 PM: Trauma processing session (step 168)")
    print(f"Day 5, 6 PM: Exposure therapy session (step 264)")
    print(f"Day 9, 6 PM: Integration session (step 456)")
    print(f"Day 13, 6 PM: Final consolidation session (step 648)")
    
    print(f"\n🔬 EXPECTED OUTCOMES:")
    print(f"✓ Baseline: Stable PHQ-9 scores (0-2 range)")
    print(f"✓ Control: Continued stability")
    print(f"✓ Trauma-only: Significant PHQ-9 elevation (6-12 range)")
    print(f"✓ Trauma+therapy: Initial elevation with gradual improvement")
    print(f"✓ Clear separation between conditions by day 7-14")
    
    print(f"\n✅ Comprehensive study created successfully!")
    print(f"Ready for execution with enhanced therapeutic insights")
    
    return True

def main():
    """Main execution function"""
    
    return create_comprehensive_study()

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 STUDY SETUP COMPLETED!")
        print(f"Execute with: python run_comprehensive_study.py")
    else:
        print(f"\n⚠️  STUDY SETUP FAILED")
    sys.exit(0 if success else 1)