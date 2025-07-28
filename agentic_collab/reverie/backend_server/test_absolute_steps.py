#!/usr/bin/env python3
"""
Test Absolute Step Counting - Demonstration
==========================================

This demonstrates how the new absolute step counting works.
Branched simulations now continue step counting from where parent ended.
"""

from simulation_interface_absolute_steps import *

def demonstrate_absolute_steps():
    """Show how absolute step counting works"""
    
    print("🔢 ABSOLUTE STEP COUNTING DEMONSTRATION")
    print("=" * 60)
    
    # ----------------------------------------------------------------------------
    # Step 1: Create baseline simulation (3 days)
    # ----------------------------------------------------------------------------
    
    print("\n📋 STEP 1: Creating Baseline Simulation")
    print("-" * 40)
    
    baseline = create_simulation()
    baseline.name = "Absolute_Steps_Baseline"
    baseline.description = "3-day baseline with absolute step counting"
    baseline.origin = "base_the_ville_isabella_maria_klaus"
    baseline.steps_per_hour = 4
    baseline.duration_in_days = 3
    baseline.agents = ["Maria Lopez"]
    baseline.type = "baseline"
    
    # Schedule daily assessments
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=baseline.daily_assessment_steps(3),
            description="Daily PHQ-9 during baseline"
        )
    ]
    
    print("Baseline configuration:")
    print(f"  Duration: {baseline.duration_in_days} days")
    print(f"  Parent steps: {baseline._get_parent_steps()}")
    print(f"  Step range: {baseline.get_absolute_step_range()}")
    print(f"  Assessment steps: {baseline.assessments[0].steps}")
    
    # ----------------------------------------------------------------------------
    # Step 2: Create branched simulation (5 days) - should continue from baseline
    # ----------------------------------------------------------------------------
    
    print("\n📋 STEP 2: Creating Branched Simulation")
    print("-" * 40)
    
    therapy = create_simulation()
    therapy.name = "Absolute_Steps_Therapy"
    therapy.description = "5-day therapy study continuing from baseline"
    therapy.origin = "Absolute_Steps_Baseline"  # Branch from baseline
    therapy.steps_per_hour = 4
    therapy.duration_in_days = 5
    therapy.agents = ["Maria Lopez"]
    therapy.type = "trauma_therapy"
    
    # Schedule assessments and events
    therapy.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=therapy.daily_assessment_steps(5),
            description="Daily PHQ-9 during therapy"
        )
    ]
    
    therapy.events = [
        EventConfig(
            name="trauma_event",
            step=therapy.time_to_step(1, 10),  # Day 1, 10 AM
            event_type="negative",
            target_agent="Maria Lopez",
            description="Traumatic event"
        ),
        EventConfig(
            name="therapy_session",
            step=therapy.time_to_step(2, 15),  # Day 2, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Therapy session"
        )
    ]
    
    print("Therapy configuration:")
    print(f"  Duration: {therapy.duration_in_days} days")
    print(f"  Parent steps: {therapy._get_parent_steps()}")
    print(f"  Step range: {therapy.get_absolute_step_range()}")
    print(f"  Assessment steps: {therapy.assessments[0].steps}")
    print(f"  Event steps: {[e.step for e in therapy.events]}")
    
    # ----------------------------------------------------------------------------
    # Step 3: Show the continuous timeline
    # ----------------------------------------------------------------------------
    
    print("\n📊 STEP 3: Continuous Timeline Analysis")
    print("-" * 40)
    
    # Calculate baseline range
    baseline_start, baseline_end = baseline.get_absolute_step_range()
    therapy_start, therapy_end = therapy.get_absolute_step_range()
    
    print(f"Timeline Overview:")
    print(f"  Baseline simulation:  Steps {baseline_start:4d} to {baseline_end:4d} (Days 1-3)")
    print(f"  Therapy simulation:   Steps {therapy_start:4d} to {therapy_end:4d} (Days 4-8)")
    print(f"  Total study duration: Steps {baseline_start:4d} to {therapy_end:4d} (8 days)")
    
    print(f"\nAssessment Schedule:")
    print(f"  Baseline PHQ-9 steps: {baseline.assessments[0].steps}")
    print(f"  Therapy PHQ-9 steps:  {therapy.assessments[0].steps}")
    all_assessment_steps = sorted(baseline.assessments[0].steps + therapy.assessments[0].steps)
    print(f"  Combined timeline:    {all_assessment_steps}")
    
    print(f"\nEvent Schedule:")
    print(f"  Trauma event:   Step {therapy.events[0].step} (Absolute Day {therapy.events[0].step // 96 + 1})")
    print(f"  Therapy session: Step {therapy.events[1].step} (Absolute Day {therapy.events[1].step // 96 + 1})")
    
    # ----------------------------------------------------------------------------
    # Step 4: Show analysis implications
    # ----------------------------------------------------------------------------
    
    print("\n📈 STEP 4: Analysis Benefits")
    print("-" * 40)
    
    print("With absolute step counting:")
    print("  ✅ No confusion about which simulation data comes from")
    print("  ✅ Continuous timeline across all phases")
    print("  ✅ Easy to plot baseline → experimental progression")
    print("  ✅ Step numbers directly indicate study chronology")
    print("  ✅ Assessment data automatically sorted by time")
    
    # Show example analysis code
    print(f"\nExample Analysis Code:")
    analysis_code = '''
# Load all assessment data - steps are automatically in chronological order
import json
import pandas as pd
from pathlib import Path

# Combine data from both simulations
all_data = []

# Load baseline results
baseline_dir = Path("simulations/Absolute_Steps_Baseline/assessment_results/Maria_Lopez")
for file in baseline_dir.glob("PHQ-9_*.json"):
    with open(file) as f:
        result = json.load(f)
        step = int(file.stem.split('_step')[-1])
        score = sum(r['score'] for r in result['responses'].values())
        all_data.append({
            'phase': 'Baseline',
            'absolute_step': step,
            'study_day': step // 96 + 1,  # Absolute study day
            'total_score': score,
            'timestamp': result['timestamp']
        })

# Load therapy results  
therapy_dir = Path("simulations/Absolute_Steps_Therapy/assessment_results/Maria_Lopez")
for file in therapy_dir.glob("PHQ-9_*.json"):
    with open(file) as f:
        result = json.load(f)
        step = int(file.stem.split('_step')[-1])
        score = sum(r['score'] for r in result['responses'].values())
        all_data.append({
            'phase': 'Therapy',
            'absolute_step': step,
            'study_day': step // 96 + 1,  # Absolute study day
            'total_score': score,
            'timestamp': result['timestamp']
        })

# Create chronologically ordered DataFrame
df = pd.DataFrame(all_data)
df = df.sort_values('absolute_step')  # Perfect chronological order

# Plot continuous timeline
import matplotlib.pyplot as plt
plt.plot(df['study_day'], df['total_score'], 'o-')
plt.axvline(x=3.5, linestyle='--', label='Baseline → Therapy')
plt.xlabel('Study Day (Absolute)')
plt.ylabel('PHQ-9 Score')
plt.title('Continuous Timeline: Baseline → Therapy')
plt.legend()
plt.show()
'''
    
    print(analysis_code)
    
    return baseline, therapy

def run_absolute_step_test():
    """Actually run the simulations to test absolute step counting"""
    
    print("\n🚀 RUNNING ABSOLUTE STEP COUNTING TEST")
    print("=" * 60)
    
    # Create and run baseline
    baseline = create_simulation()
    baseline.name = "Test_Absolute_Baseline"
    baseline.description = "Test baseline with absolute steps"
    baseline.origin = "base_the_ville_isabella_maria_klaus"
    baseline.steps_per_hour = 4
    baseline.duration_in_days = 2  # Short test
    baseline.agents = ["Maria Lopez"]
    baseline.type = "baseline"
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=baseline.daily_assessment_steps(2),
            description="Daily PHQ-9"
        )
    ]
    
    print("\n📋 Baseline Summary:")
    print(baseline.summary())
    
    # Uncomment to run baseline
    # success = baseline.run()
    
    # Create branched simulation
    therapy = create_simulation()
    therapy.name = "Test_Absolute_Therapy"
    therapy.description = "Test therapy with absolute steps"
    therapy.origin = "Test_Absolute_Baseline"
    therapy.steps_per_hour = 4
    therapy.duration_in_days = 3  # Short test
    therapy.agents = ["Maria Lopez"]
    therapy.type = "trauma_therapy"
    therapy.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=therapy.daily_assessment_steps(3),
            description="Daily PHQ-9 during therapy"
        )
    ]
    therapy.events = [
        EventConfig(
            name="test_event",
            step=therapy.time_to_step(1, 12),
            event_type="negative",
            target_agent="Maria Lopez",
            description="Test traumatic event"
        )
    ]
    
    print("\n📋 Therapy Summary:")
    print(therapy.summary())
    
    # Uncomment to run therapy
    # success = therapy.run()
    
    print("\n💡 To run test: Uncomment the .run() calls above")
    print("📊 Results will have continuous step numbering across simulations")

if __name__ == "__main__":
    # Demonstrate the concept
    baseline, therapy = demonstrate_absolute_steps()
    
    # Show test setup
    run_absolute_step_test()
    
    print("\n🎉 Absolute step counting demonstration complete!")
    print("\n📝 Key Benefits:")
    print("  • Continuous timeline across baseline and experimental phases")
    print("  • No confusion about which simulation data comes from") 
    print("  • Assessment data automatically in chronological order")
    print("  • Easy plotting and statistical analysis")
    print("  • Step numbers directly indicate study progression")