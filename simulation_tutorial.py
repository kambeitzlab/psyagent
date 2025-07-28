#!/usr/bin/env python3
"""
🔬 AI Agent Psychological Research Simulation Tutorial
===================================================

This tutorial demonstrates how to use the simple simulation interface to create
and run AI agent psychological research studies. The interface allows you to:

- Create baseline and experimental simulations
- Schedule mental health assessments (PHQ-9, GAD-7, etc.)
- Administer trauma events and therapy interventions
- Track agent behavior and psychological responses
- Generate research data for statistical analysis

Requirements:
- OpenAI API key configured in openai_config.json
- Run from: agentic_collab/reverie/backend_server/ directory
"""

# Import the simulation interface
from simulation_interface import *
import time

def tutorial_1_basic_baseline():
    """
    Tutorial 1: Basic Baseline Simulation
    
    This creates a simple baseline simulation to establish normal behavior patterns.
    Baseline simulations are used as control conditions for comparison.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 1: Basic Baseline Simulation")
    print("="*60)
    
    # Create a new simulation instance
    baseline = create_simulation()
    
    # Configure basic parameters with direct property access
    baseline.name = "Tutorial_Baseline_Study"                    # Unique simulation name
    baseline.description = "7-day baseline to establish normal behavior patterns"
    baseline.origin = "base_the_ville_isabella_maria_klaus"      # Base simulation to start from
    baseline.steps_per_hour = 4                                  # Time resolution (15-min intervals)
    baseline.duration_in_days = 7                               # Length of study
    baseline.agents = ["Maria Lopez", "Isabella Rodriguez"]      # Participants to include
    baseline.type = "baseline"                                   # Simulation type
    
    # Schedule daily PHQ-9 depression assessments
    # Helper function generates steps for daily assessments (2 hours before end of day)
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",                                        # Standard depression questionnaire
            steps=baseline.daily_assessment_steps(7),           # Daily for 7 days
            description="Daily PHQ-9 depression assessment during baseline"
        )
    ]
    
    # No events scheduled - this is a baseline condition
    baseline.events = []
    
    # Print simulation summary
    print("\n📋 Simulation Configuration:")
    print(baseline.summary())
    
    # Validate configuration before running
    errors = baseline.validate()
    if errors:
        print(f"\n❌ Configuration errors found:")
        for error in errors:
            print(f"  • {error}")
        return False
    
    print(f"\n✅ Configuration valid - ready to run!")
    
    # Uncomment the line below to actually run the simulation
    # This will take several minutes and use OpenAI API credits
    # success = baseline.run()
    
    print(f"\n💡 To run this simulation, uncomment: baseline.run()")
    print(f"📁 Results will be saved to: simulations/{baseline.name}/")
    
    return True

def tutorial_2_trauma_study():
    """
    Tutorial 2: Trauma Event Study
    
    This demonstrates how to create a simulation with traumatic events to study
    psychological impact and recovery patterns.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 2: Trauma Event Study")
    print("="*60)
    
    # Create trauma study simulation
    trauma_study = create_simulation()
    
    # Configure trauma study parameters
    trauma_study.name = "Tutorial_Trauma_Study"
    trauma_study.description = "5-day study examining trauma impact on depression"
    trauma_study.origin = "Tutorial_Baseline_Study"             # Branch from baseline
    trauma_study.steps_per_hour = 4
    trauma_study.duration_in_days = 5
    trauma_study.agents = ["Maria Lopez"]                       # Single participant
    trauma_study.type = "trauma_only"
    
    # Schedule assessments to track trauma impact
    trauma_study.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=trauma_study.daily_assessment_steps(5),       # Daily monitoring
            description="Daily PHQ-9 to track trauma impact"
        ),
        AssessmentConfig(
            name="GAD-7",                                       # Anxiety assessment
            steps=[trauma_study.time_to_step(1, 20),           # Day 1, 8 PM
                   trauma_study.time_to_step(3, 20),           # Day 3, 8 PM  
                   trauma_study.time_to_step(5, 20)],          # Day 5, 8 PM
            description="GAD-7 anxiety assessment post-trauma"
        )
    ]
    
    # Schedule traumatic events
    trauma_study.events = [
        EventConfig(
            name="car_accident_witness",
            step=trauma_study.time_to_step(1, 14),             # Day 1, 2 PM
            event_type="negative",                             # Traumatic event type
            target_agent="Maria Lopez",
            description="Maria witnesses a severe car accident involving multiple casualties. "
                       "She sees injured people and feels helpless being unable to provide "
                       "meaningful assistance. The images and sounds are disturbing and create "
                       "lasting emotional distress."
        ),
        EventConfig(
            name="news_report_trigger",
            step=trauma_study.time_to_step(3, 19),             # Day 3, 7 PM  
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria sees a news report about a similar accident, triggering "
                       "vivid flashbacks and renewed anxiety about the incident she witnessed."
        )
    ]
    
    print("\n📋 Trauma Study Configuration:")
    print(trauma_study.summary())
    
    print(f"\n💡 This study examines trauma impact over {trauma_study.duration_in_days} days")
    print(f"🔬 Scheduled events: {len(trauma_study.events)} trauma-related")
    print(f"📊 Assessments: {sum(len(a.steps) for a in trauma_study.assessments)} total")
    
    return trauma_study

def tutorial_3_therapy_intervention():
    """
    Tutorial 3: Therapy Intervention Study
    
    This shows how to create a comprehensive study with trauma + therapy intervention
    to measure therapeutic effectiveness.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 3: Therapy Intervention Study") 
    print("="*60)
    
    # Create therapy intervention study
    therapy_study = create_simulation()
    
    # Configure comprehensive therapy study
    therapy_study.name = "Tutorial_Therapy_Study"
    therapy_study.description = "10-day trauma + therapy intervention study"
    therapy_study.origin = "Tutorial_Baseline_Study"           # Branch from baseline
    therapy_study.steps_per_hour = 4
    therapy_study.duration_in_days = 10
    therapy_study.agents = ["Maria Lopez"]
    therapy_study.type = "trauma_therapy"
    
    # Comprehensive assessment schedule
    therapy_study.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=therapy_study.daily_assessment_steps(10),     # Daily depression tracking
            description="Daily PHQ-9 throughout treatment"
        ),
        AssessmentConfig(
            name="GAD-7", 
            steps=[therapy_study.time_to_step(d, 20) for d in [1, 3, 5, 7, 10]], # Every 2 days
            description="GAD-7 anxiety assessment during treatment"
        )
    ]
    
    # Trauma + therapy event sequence
    therapy_study.events = [
        # Initial trauma event
        EventConfig(
            name="workplace_accident",
            step=therapy_study.time_to_step(1, 10),            # Day 1, 10 AM
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria witnesses a serious workplace accident where a colleague "
                       "falls from scaffolding and is severely injured. She experiences "
                       "intense distress, guilt, and helplessness."
        ),
        
        # Emergency therapy session (same day)
        EventConfig(
            name="emergency_therapy_session",
            step=therapy_study.time_to_step(1, 16),            # Day 1, 4 PM
            event_type="therapy",
            target_agent="Maria Lopez", 
            description="Emergency therapy session focusing on acute trauma response. "
                       "Therapist helps Maria process immediate emotions, provides "
                       "grounding techniques, and establishes safety."
        ),
        
        # Follow-up therapy sessions
        EventConfig(
            name="therapy_session_2",
            step=therapy_study.time_to_step(3, 15),            # Day 3, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Second therapy session focusing on trauma processing. "
                       "Using cognitive restructuring to address guilt and self-blame. "
                       "Introduction of EMDR techniques for trauma memories."
        ),
        
        EventConfig(
            name="therapy_session_3", 
            step=therapy_study.time_to_step(5, 15),            # Day 5, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Third therapy session continuing EMDR processing. "
                       "Working on reducing emotional charge of traumatic memories "
                       "and developing coping strategies."
        ),
        
        EventConfig(
            name="therapy_session_4",
            step=therapy_study.time_to_step(7, 15),            # Day 7, 3 PM
            event_type="therapy", 
            target_agent="Maria Lopez",
            description="Fourth therapy session focusing on integration and meaning-making. "
                       "Helping Maria develop a coherent narrative about the experience "
                       "and identify personal growth."
        ),
        
        EventConfig(
            name="therapy_session_5",
            step=therapy_study.time_to_step(9, 15),            # Day 9, 3 PM
            event_type="therapy",
            target_agent="Maria Lopez", 
            description="Final therapy session focusing on consolidation and relapse prevention. "
                       "Reviewing progress, reinforcing coping skills, and planning "
                       "for continued recovery."
        )
    ]
    
    print("\n📋 Therapy Study Configuration:")  
    print(therapy_study.summary())
    
    print(f"\n🏥 Treatment protocol: 5 therapy sessions over {therapy_study.duration_in_days} days")
    print(f"📈 Expected outcome: Reduced depression and anxiety scores")
    print(f"🔬 Research design: Pre-post intervention with daily monitoring")
    
    return therapy_study

def tutorial_4_multi_condition_experiment():
    """
    Tutorial 4: Multi-Condition Experimental Design
    
    This demonstrates how to create a complete experimental study with multiple
    conditions for statistical comparison.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 4: Multi-Condition Experimental Design")
    print("="*60)
    
    # Create all experimental conditions
    conditions = {}
    
    # Condition 1: Control (no intervention)
    control = create_simulation()
    control.name = "Tutorial_Control_Condition"
    control.description = "Control condition - no interventions"
    control.origin = "Tutorial_Baseline_Study"
    control.steps_per_hour = 4
    control.duration_in_days = 10
    control.agents = ["Isabella Rodriguez"]
    control.type = "control"
    control.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=control.daily_assessment_steps(10),
            description="Daily PHQ-9 in control condition"
        )
    ]
    control.events = []  # No interventions
    conditions["control"] = control
    
    # Condition 2: Trauma only (no therapy)
    trauma_only = create_simulation()
    trauma_only.name = "Tutorial_Trauma_Only_Condition"
    trauma_only.description = "Trauma exposure without therapy intervention"
    trauma_only.origin = "Tutorial_Baseline_Study"
    trauma_only.steps_per_hour = 4
    trauma_only.duration_in_days = 10
    trauma_only.agents = ["Klaus Mueller"]
    trauma_only.type = "trauma_only"
    trauma_only.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=trauma_only.daily_assessment_steps(10),
            description="Daily PHQ-9 after trauma exposure"
        )
    ]
    trauma_only.events = [
        EventConfig(
            name="traumatic_event",
            step=trauma_only.time_to_step(1, 12),
            event_type="negative", 
            target_agent="Klaus Mueller",
            description="Klaus experiences a traumatic event without therapeutic intervention."
        )
    ]
    conditions["trauma_only"] = trauma_only
    
    # Condition 3: Trauma + therapy (from tutorial 3)
    therapy_condition = tutorial_3_therapy_intervention()  
    therapy_condition.name = "Tutorial_Trauma_Therapy_Condition"
    therapy_condition.agents = ["Maria Lopez"]
    conditions["trauma_therapy"] = therapy_condition
    
    # Print experimental design summary
    print(f"\n🔬 EXPERIMENTAL DESIGN SUMMARY:")
    print(f"{'Condition':<20} {'Agent':<20} {'Interventions':<30} {'Assessments'}")
    print("-" * 80)
    
    for name, sim in conditions.items():
        interventions = f"{len([e for e in sim.events if e.event_type == 'negative'])} trauma, " \
                       f"{len([e for e in sim.events if e.event_type == 'therapy'])} therapy"
        assessments = sum(len(a.steps) for a in sim.assessments)
        agent = sim.agents[0] if sim.agents else "None"
        print(f"{name:<20} {agent:<20} {interventions:<30} {assessments}")
    
    print(f"\n📊 Statistical Analysis Plan:")
    print(f"  • Primary outcome: PHQ-9 depression scores")
    print(f"  • Analysis: Repeated measures ANOVA")
    print(f"  • Comparisons: Control vs Trauma vs Trauma+Therapy")
    print(f"  • Hypothesis: Therapy reduces trauma-related depression")
    
    return conditions

def tutorial_5_custom_assessments():
    """
    Tutorial 5: Custom Assessment Schedules
    
    Shows how to create flexible assessment schedules for different research needs.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 5: Custom Assessment Schedules")
    print("="*60)
    
    custom_study = create_simulation()
    custom_study.name = "Tutorial_Custom_Assessments"
    custom_study.description = "Demonstration of flexible assessment scheduling"
    custom_study.origin = "base_the_ville_isabella_maria_klaus" 
    custom_study.steps_per_hour = 4
    custom_study.duration_in_days = 14
    custom_study.agents = ["Maria Lopez", "Isabella Rodriguez"]
    custom_study.type = "custom"
    
    # Demonstrate different assessment scheduling patterns
    custom_study.assessments = [
        # Daily assessments for first week
        AssessmentConfig(
            name="PHQ-9",
            steps=[custom_study.time_to_step(d, 20) for d in range(1, 8)],  # Days 1-7, 8 PM
            description="Daily PHQ-9 during intensive monitoring period"
        ),
        
        # Weekly assessments for full study
        AssessmentConfig(
            name="GAD-7",
            steps=[custom_study.time_to_step(d, 18) for d in [1, 7, 14]],   # Weeks 1, 2, 3
            description="Weekly GAD-7 anxiety assessment"
        ),
        
        # Specific time points 
        AssessmentConfig(
            name="K10",  # Kessler-10 distress scale
            steps=[
                custom_study.time_to_step(1, 9),   # Baseline (Day 1, 9 AM)
                custom_study.time_to_step(3, 21),  # Post-event (Day 3, 9 PM)
                custom_study.time_to_step(14, 17)  # Follow-up (Day 14, 5 PM) 
            ],
            description="K10 distress assessment at key timepoints"
        ),
        
        # Multiple assessments per day
        AssessmentConfig(
            name="Brief_Mood_Check",
            steps=[
                custom_study.time_to_step(5, 9),   # Day 5: Morning
                custom_study.time_to_step(5, 13),  # Day 5: Afternoon  
                custom_study.time_to_step(5, 19),  # Day 5: Evening
            ],
            description="Multiple daily mood assessments on intensive monitoring day"
        )
    ]
    
    print(f"\n📅 Assessment Schedule Examples:")
    print(f"  Daily monitoring: {len([s for a in custom_study.assessments if a.name == 'PHQ-9' for s in a.steps])} PHQ-9 assessments")
    print(f"  Weekly tracking: {len([s for a in custom_study.assessments if a.name == 'GAD-7' for s in a.steps])} GAD-7 assessments")
    print(f"  Key timepoints: {len([s for a in custom_study.assessments if a.name == 'K10' for s in a.steps])} K10 assessments")
    print(f"  Intensive day: {len([s for a in custom_study.assessments if a.name == 'Brief_Mood_Check' for s in a.steps])} mood checks")
    
    # Show timing details
    print(f"\n⏰ Detailed Timing:")
    for assessment in custom_study.assessments:
        print(f"  {assessment.name}:")
        for step in assessment.steps[:3]:  # Show first 3 for brevity
            day = (step // (custom_study.steps_per_hour * 24)) + 1
            hour = (step % (custom_study.steps_per_hour * 24)) // custom_study.steps_per_hour
            print(f"    • Day {day}, {hour:02d}:00 (Step {step})")
        if len(assessment.steps) > 3:
            print(f"    • ... and {len(assessment.steps) - 3} more")
    
    return custom_study

def tutorial_6_helper_functions():
    """
    Tutorial 6: Helper Functions and Utilities
    
    Demonstrates useful helper functions for common simulation tasks.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 6: Helper Functions and Utilities")
    print("="*60)
    
    # Create example simulation
    example = create_simulation()
    example.name = "Helper_Functions_Demo"
    example.steps_per_hour = 4
    example.duration_in_days = 7
    
    print(f"\n🛠️  Available Helper Functions:")
    
    # 1. Daily assessment steps
    daily_steps = example.daily_assessment_steps(7)
    print(f"\n1. daily_assessment_steps(7):")
    print(f"   Purpose: Generate steps for daily assessments")
    print(f"   Returns: {daily_steps}")
    print(f"   Usage: Automatically schedules assessments 2 hours before end of each day")
    
    # 2. Time to step conversion
    print(f"\n2. time_to_step(day, hour):")
    print(f"   Purpose: Convert human-readable time to simulation step")
    print(f"   Examples:")
    for day, hour in [(1, 9), (3, 14), (7, 20)]:
        step = example.time_to_step(day, hour)
        print(f"     Day {day}, {hour:02d}:00 → Step {step}")
    
    # 3. Validation
    print(f"\n3. validate():")
    print(f"   Purpose: Check configuration for errors before running")
    example_errors = example.validate()
    print(f"   Returns: List of error messages (empty if valid)")
    print(f"   Current errors: {len(example_errors)}")
    
    # 4. Summary generation
    print(f"\n4. summary():")
    print(f"   Purpose: Generate human-readable simulation overview")
    print(f"   Returns: Formatted string with key parameters")
    print(f"   Example output:")
    print("   " + "\n   ".join(example.summary().split("\n")[:5]))
    print("   ...")
    
    # 5. Configuration conversion
    print(f"\n5. _to_simulation_config() (internal):")
    print(f"   Purpose: Convert user-friendly format to internal simulation format")
    print(f"   Handles: Assessment scheduling, event timing, parameter mapping")
    
    print(f"\n💡 Pro Tips:")
    print(f"  • Use daily_assessment_steps() for consistent daily monitoring")
    print(f"  • Use time_to_step() for precise event timing")
    print(f"  • Always call validate() before run() to catch errors early")
    print(f"  • Use summary() to review configuration before execution")

def tutorial_7_running_and_results():
    """
    Tutorial 7: Running Simulations and Analyzing Results
    
    Shows how to execute simulations and work with the generated data.
    """
    
    print("\n" + "="*60)
    print("📚 TUTORIAL 7: Running Simulations and Analyzing Results")
    print("="*60)
    
    print(f"\n🚀 How to Run Simulations:")
    print(f"""
    # Create and configure simulation
    my_study = create_simulation()
    my_study.name = "My_Research_Study"
    # ... configure parameters ...
    
    # Run the simulation  
    success = my_study.run()
    
    if success:
        print("✅ Simulation completed successfully!")
    else:
        print("❌ Simulation failed - check logs for details")
    """)
    
    print(f"\n📁 Generated Files and Directories:")
    print(f"""
    simulations/My_Research_Study/
    ├── metadata.json                    # Simulation configuration and metadata
    ├── all_logs/                        # Centralized logging directory
    │   ├── simulation_debug.log         # Debug information
    │   └── simulation_logs/
    │       ├── events.jsonl             # All simulation events
    │       └── therapy_events.jsonl     # Therapy session details
    ├── assessment_results/              # Mental health assessment data
    │   └── [Agent_Name]/
    │       ├── PHQ-9_*.json            # Individual assessment results
    │       └── GAD-7_*.json            # Anxiety assessment results
    └── agent_data/                      # Agent memory and behavior data
        └── [Agent_Name]/
            ├── bootstrap_memory/        # Agent's memory system
            └── persona_state.json       # Current agent state
    """)
    
    print(f"\n📊 Data Analysis Examples:")
    print(f"""
    # Load assessment results
    import json
    import pandas as pd
    from pathlib import Path
    
    # Load PHQ-9 results for analysis
    sim_dir = Path("simulations/My_Research_Study")
    assessment_dir = sim_dir / "assessment_results" / "Maria Lopez"
    
    phq9_files = list(assessment_dir.glob("PHQ-9_*.json"))
    
    # Parse assessment data
    assessment_data = []
    for file in phq9_files:
        with open(file) as f:
            data = json.load(f)
            assessment_data.append({
                'timestamp': data['timestamp'],
                'total_score': sum(r['score'] for r in data['responses'].values()),
                'simulation_step': file.stem.split('_')[-1]
            })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(assessment_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Basic statistics
    print(f"Mean PHQ-9 score: {df['total_score'].mean():.2f}")
    print(f"Score range: {df['total_score'].min()} - {df['total_score'].max()}")
    
    # Plot results
    import matplotlib.pyplot as plt
    plt.plot(df['timestamp'], df['total_score'])
    plt.xlabel('Time')
    plt.ylabel('PHQ-9 Score')
    plt.title('Depression Scores Over Time')
    plt.show()
    """)
    
    print(f"\n🔧 Troubleshooting Common Issues:")
    print(f"""
    1. "Simulation already exists" error:
       → Change simulation name or delete existing simulation directory
    
    2. OpenAI API errors:
       → Check openai_config.json file exists and has valid API key
       → Verify sufficient API credits available
    
    3. Long execution times:
       → Reduce duration_in_days for testing
       → Use fewer agents during development
    
    4. Memory errors:
       → Reduce simulation complexity
       → Run simulations sequentially rather than in parallel
    
    5. Missing assessment data:
       → Check assessment step calculations
       → Verify simulation ran to completion
    """)

def main():
    """
    Main tutorial runner - demonstrates all functionality
    """
    
    print("🎓 AI AGENT PSYCHOLOGICAL RESEARCH SIMULATION TUTORIAL")
    print("=" * 70)
    print("""
This tutorial demonstrates the simple simulation interface for creating
AI agent psychological research studies. Each tutorial section shows
different aspects of the system.

📚 Tutorial Sections:
  1. Basic Baseline Simulation - Establish normal behavior patterns
  2. Trauma Event Study - Study psychological impact of negative events  
  3. Therapy Intervention - Measure therapeutic effectiveness
  4. Multi-Condition Experiment - Complete experimental designs
  5. Custom Assessment Schedules - Flexible measurement timing
  6. Helper Functions - Useful utilities and tools
  7. Running and Results - Execution and data analysis

⚠️  Note: Actual simulation execution requires OpenAI API credits.
    Examples show configuration only - uncomment .run() calls to execute.
    """)
    
    # Run all tutorial sections
    tutorials = [
        tutorial_1_basic_baseline,
        tutorial_2_trauma_study, 
        tutorial_3_therapy_intervention,
        tutorial_4_multi_condition_experiment,
        tutorial_5_custom_assessments,
        tutorial_6_helper_functions,
        tutorial_7_running_and_results
    ]
    
    for i, tutorial_func in enumerate(tutorials, 1):
        try:
            result = tutorial_func()
            print(f"\n✅ Tutorial {i} completed successfully!")
        except Exception as e:
            print(f"\n❌ Tutorial {i} encountered an error: {e}")
        
        # Pause between tutorials
        if i < len(tutorials):
            input(f"\nPress Enter to continue to Tutorial {i+1}...")
    
    print(f"\n🎉 Tutorial completed! You're ready to create your own studies.")
    print(f"\n📖 Next Steps:")
    print(f"  1. Copy and modify examples for your research needs")
    print(f"  2. Configure OpenAI API credentials")
    print(f"  3. Start with short test simulations (1-2 days)")
    print(f"  4. Gradually increase complexity as you gain experience")
    print(f"  5. Analyze results using the provided data analysis patterns")

if __name__ == "__main__":
    main()