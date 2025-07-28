#!/usr/bin/env python3
"""
🚀 Quick Start Example - AI Agent Psychological Research
======================================================

This is a minimal example to get you started immediately with the simulation interface.
Copy this code and modify it for your research needs.

Run from: agentic_collab/reverie/backend_server/ directory
Required: OpenAI API key in openai_config.json
"""

from simulation_interface import *

def quick_baseline_example():
    """Create and run a simple 3-day baseline study"""
    
    print("🔬 Creating baseline study...")
    
    # Create simulation with direct property access
    baseline = create_simulation()
    baseline.name = "Quick_Baseline_Example"
    baseline.description = "Simple 3-day baseline study"
    baseline.origin = "base_the_ville_isabella_maria_klaus"
    baseline.steps_per_hour = 4              # 15-minute intervals
    baseline.duration_in_days = 3            # Short study for testing
    baseline.agents = ["Maria Lopez"]        # Single participant
    baseline.type = "baseline"
    
    # Schedule daily PHQ-9 depression assessments
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=baseline.daily_assessment_steps(3),  # Daily for 3 days
            description="Daily depression assessment"
        )
    ]
    
    # Print configuration
    print("\n📋 Study Configuration:")
    print(baseline.summary())
    
    # Validate before running
    errors = baseline.validate()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  • {error}")
        return False
    
    print("\n✅ Configuration valid!")
    
    # Uncomment to run (uses OpenAI API credits)
    # success = baseline.run()
    # if success:
    #     print(f"📁 Results saved to: simulations/{baseline.name}/")
    
    print("\n💡 To execute: uncomment baseline.run() above")
    return True

def quick_trauma_therapy_example():
    """Create a trauma + therapy intervention study"""
    
    print("\n🏥 Creating trauma + therapy study...")
    
    # Create trauma therapy study
    therapy_study = create_simulation() 
    therapy_study.name = "Quick_Therapy_Example"
    therapy_study.description = "5-day trauma and therapy study"
    therapy_study.origin = "Quick_Baseline_Example"  # Branch from baseline
    therapy_study.steps_per_hour = 4
    therapy_study.duration_in_days = 5
    therapy_study.agents = ["Maria Lopez"]
    therapy_study.type = "trauma_therapy"
    
    # Daily assessments
    therapy_study.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=therapy_study.daily_assessment_steps(5),
            description="Daily PHQ-9 during treatment"
        )
    ]
    
    # Trauma event + therapy sessions
    therapy_study.events = [
        # Traumatic event on Day 1
        EventConfig(
            name="traumatic_incident",
            step=therapy_study.time_to_step(1, 10),  # Day 1, 10 AM
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria witnesses a serious accident that causes emotional distress, "
                       "guilt, and intrusive thoughts about the incident."
        ),
        
        # Emergency therapy session same day
        EventConfig(
            name="emergency_therapy",
            step=therapy_study.time_to_step(1, 16),  # Day 1, 4 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Emergency therapy session focusing on acute trauma response and "
                       "immediate coping strategies."
        ),
        
        # Follow-up therapy sessions
        EventConfig(
            name="therapy_session_2",
            step=therapy_study.time_to_step(3, 15),  # Day 3, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Therapy session using cognitive processing therapy techniques "
                       "to help process the traumatic experience."
        ),
        
        EventConfig(
            name="therapy_session_3",
            step=therapy_study.time_to_step(5, 15),  # Day 5, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Final therapy session focusing on integration and developing "
                       "long-term coping strategies."
        )
    ]
    
    print("\n📋 Therapy Study Configuration:")
    print(therapy_study.summary())
    
    # Validate
    errors = therapy_study.validate()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  • {error}")
        return False
    
    print("\n✅ Configuration valid!")
    print("💡 Expected outcome: Reduced depression scores after therapy")
    
    # Uncomment to run
    # success = therapy_study.run()
    
    return True

def analyze_results_example():
    """Example of how to analyze simulation results"""
    
    print("\n📊 Result Analysis Example:")
    
    analysis_code = '''
# Example: Load and analyze PHQ-9 results
import json
import pandas as pd
from pathlib import Path

# Load assessment results
sim_dir = Path("simulations/Quick_Therapy_Example")
assessment_dir = sim_dir / "assessment_results" / "Maria Lopez"

# Load all PHQ-9 files
phq9_files = sorted(assessment_dir.glob("PHQ-9_*.json"))

# Parse assessment data
data = []
for file in phq9_files:
    with open(file) as f:
        result = json.load(f)
        total_score = sum(r['score'] for r in result['responses'].values())
        data.append({
            'timestamp': result['timestamp'],
            'total_score': total_score,
            'step': int(file.stem.split('_')[-1])
        })

# Create DataFrame
df = pd.DataFrame(data)
df['day'] = df['step'] // 96 + 1  # Convert steps to days

# Basic statistics
print(f"PHQ-9 Results Summary:")
print(f"Mean score: {df['total_score'].mean():.1f}")
print(f"Range: {df['total_score'].min()} - {df['total_score'].max()}")
print(f"Trend: {'Improving' if df['total_score'].iloc[-1] < df['total_score'].iloc[0] else 'Stable/Worsening'}")

# Plot results
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(df['day'], df['total_score'], 'bo-', linewidth=2, markersize=8)
plt.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Mild depression threshold')
plt.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Moderate depression threshold')
plt.xlabel('Study Day')
plt.ylabel('PHQ-9 Total Score')
plt.title('Depression Scores During Trauma + Therapy Study')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('phq9_results.png', dpi=300)
plt.show()
'''
    
    print(analysis_code)

def main():
    """Run quick start examples"""
    
    print("🚀 QUICK START EXAMPLES")
    print("=" * 40)
    print("""
These examples show the basic usage patterns for psychological research simulations.
Modify the parameters below for your specific research needs.

⚠️  Remember to:
  1. Run from agentic_collab/reverie/backend_server/ directory
  2. Have OpenAI API key configured in openai_config.json
  3. Uncomment .run() calls to actually execute simulations
    """)
    
    # Run examples
    try:
        # Example 1: Baseline study
        quick_baseline_example()
        
        # Example 2: Therapy intervention
        quick_trauma_therapy_example()
        
        # Example 3: Analysis
        analyze_results_example()
        
        print("\n🎉 Quick start examples completed!")
        print("\n📚 For more advanced features, see simulation_tutorial.py")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have the simulation_interface module available")

if __name__ == "__main__":
    main()