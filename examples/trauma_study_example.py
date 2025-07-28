#!/usr/bin/env python3
"""
Trauma Study Example
===================

This example demonstrates how to create a comprehensive trauma research study
with baseline and experimental phases.
"""

import sys
import os

# Add the parent directory to path to import simulation_interface
sys.path.append('..')
from simulation_interface import *

def create_trauma_research_study():
    """Create a complete trauma research study with baseline and trauma phases"""
    
    print("🔬 TRAUMA RESEARCH STUDY SETUP")
    print("=" * 50)
    
    # ========================================================================
    # Phase 1: Baseline Study (5 days)
    # ========================================================================
    
    print("\n📋 Phase 1: Creating Baseline Study")
    print("-" * 30)
    
    baseline = create_simulation()
    baseline.name = "Trauma_Study_Baseline"
    baseline.description = "5-day baseline to establish normal behavior patterns"
    baseline.origin = "base_the_ville_isabella_maria_klaus"
    baseline.steps_per_hour = 4
    baseline.duration_in_days = 5
    baseline.agents = ["Maria Lopez", "Isabella Rodriguez"]
    baseline.type = "baseline"
    
    # Daily PHQ-9 and weekly GAD-7 assessments
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=baseline.daily_assessment_steps(5),
            description="Daily depression assessment during baseline"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[baseline.time_to_step(1, 18), baseline.time_to_step(5, 18)],
            description="Pre/post anxiety assessment"
        )
    ]
    
    print(f"Baseline Configuration:")
    print(f"  Duration: {baseline.duration_in_days} days")
    print(f"  Agents: {', '.join(baseline.agents)}")
    print(f"  Assessments: {len(baseline.assessments)} types")
    print(f"  Step range: {baseline.get_absolute_step_range()}")
    
    # ========================================================================
    # Phase 2: Trauma Study (7 days)
    # ========================================================================
    
    print("\n📋 Phase 2: Creating Trauma Study")
    print("-" * 30)
    
    trauma_study = create_simulation()
    trauma_study.name = "Trauma_Study_Experimental"
    trauma_study.description = "7-day trauma exposure study"
    trauma_study.origin = "Trauma_Study_Baseline"  # Branch from baseline
    trauma_study.steps_per_hour = 4
    trauma_study.duration_in_days = 7
    trauma_study.agents = ["Maria Lopez", "Isabella Rodriguez"]
    trauma_study.type = "trauma_only"
    
    # Continue daily assessments plus additional trauma-specific measures
    trauma_study.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=trauma_study.daily_assessment_steps(7),
            description="Daily depression tracking post-trauma"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[trauma_study.time_to_step(1, 20), 
                   trauma_study.time_to_step(4, 20),
                   trauma_study.time_to_step(7, 20)],
            description="Anxiety assessment at key timepoints"
        ),
        AssessmentConfig(
            name="K10",
            steps=[trauma_study.time_to_step(2, 12),
                   trauma_study.time_to_step(6, 12)],
            description="Psychological distress assessment"
        )
    ]
    
    # Traumatic events schedule
    trauma_study.events = [
        # Primary traumatic event
        EventConfig(
            name="car_accident_witness",
            step=trauma_study.time_to_step(1, 14),  # Day 1, 2 PM
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria witnesses a severe multi-car accident with multiple casualties. "
                       "She sees injured people, hears screaming, and feels helpless being unable "
                       "to provide meaningful assistance. The traumatic images and sounds create "
                       "lasting emotional distress and intrusive memories."
        ),
        
        # Secondary traumatic exposure for comparison
        EventConfig(
            name="workplace_incident",
            step=trauma_study.time_to_step(1, 16),  # Day 1, 4 PM
            event_type="negative", 
            target_agent="Isabella Rodriguez",
            description="Isabella witnesses a serious workplace accident where a colleague "
                       "falls from scaffolding and is critically injured. She experiences "
                       "intense distress and guilt about workplace safety protocols."
        ),
        
        # Trigger event (news/media exposure)
        EventConfig(
            name="news_report_trigger",
            step=trauma_study.time_to_step(3, 19),  # Day 3, 7 PM
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria sees a news report about a similar car accident, triggering "
                       "vivid flashbacks and renewed anxiety about the incident she witnessed. "
                       "The report includes graphic details that intensify her distress."
        ),
        
        # Social trigger event
        EventConfig(
            name="conversation_trigger",
            step=trauma_study.time_to_step(5, 12),  # Day 5, 12 PM
            event_type="negative",
            target_agent="Isabella Rodriguez", 
            description="Isabella overhears colleagues discussing workplace safety failures, "
                       "triggering memories of the accident she witnessed and feelings of guilt."
        )
    ]
    
    print(f"Trauma Study Configuration:")
    print(f"  Duration: {trauma_study.duration_in_days} days")
    print(f"  Step range: {trauma_study.get_absolute_step_range()}")
    print(f"  Trauma events: {len(trauma_study.events)}")
    print(f"  Assessment points: {sum(len(a.steps) for a in trauma_study.assessments)}")
    
    # ========================================================================
    # Display Study Timeline
    # ========================================================================
    
    print(f"\n📅 COMPLETE STUDY TIMELINE")
    print("=" * 50)
    
    baseline_start, baseline_end = baseline.get_absolute_step_range()
    trauma_start, trauma_end = trauma_study.get_absolute_step_range()
    
    print(f"Study Days 1-5:  Baseline Phase (Steps {baseline_start}-{baseline_end})")
    print(f"Study Days 6-12: Trauma Phase (Steps {trauma_start}-{trauma_end})")
    print(f"Total Duration:  12 days ({trauma_end} steps)")
    
    print(f"\nAssessment Schedule:")
    all_assessments = []
    
    # Collect all assessments
    for assessment in baseline.assessments:
        for step in assessment.steps:
            day = step // 96 + 1
            all_assessments.append(f"Day {day}: {assessment.name} (Step {step})")
    
    for assessment in trauma_study.assessments:
        for step in assessment.steps:
            day = step // 96 + 1
            all_assessments.append(f"Day {day}: {assessment.name} (Step {step})")
    
    for assessment in sorted(all_assessments)[:10]:  # Show first 10
        print(f"  {assessment}")
    if len(all_assessments) > 10:
        print(f"  ... and {len(all_assessments) - 10} more assessments")
    
    print(f"\nTrauma Events Schedule:")
    for event in trauma_study.events:
        day = event.step // 96 + 1
        hour = (event.step % 96) // 4
        print(f"  Day {day}, {hour:02d}:00 - {event.name} ({event.target_agent})")
    
    return baseline, trauma_study

def run_trauma_study(baseline, trauma_study):
    """Execute the complete trauma research study"""
    
    print(f"\n🚀 EXECUTING TRAUMA RESEARCH STUDY")
    print("=" * 50)
    
    # Validate configurations
    print("\n🔍 Validating configurations...")
    
    baseline_errors = baseline.validate()
    trauma_errors = trauma_study.validate()
    
    if baseline_errors or trauma_errors:
        print("❌ Configuration errors found:")
        for error in baseline_errors + trauma_errors:
            print(f"  • {error}")
        return False
    
    print("✅ All configurations valid!")
    
    # Execute baseline study
    print(f"\n📊 Phase 1: Running Baseline Study")
    print("-" * 40)
    
    baseline_success = baseline.run(show_summary=False) 
    
    if not baseline_success:
        print("❌ Baseline study failed!")
        return False
    
    print("✅ Baseline study completed successfully!")
    
    # Execute trauma study
    print(f"\n📊 Phase 2: Running Trauma Study")
    print("-" * 40)
    
    trauma_success = trauma_study.run(show_summary=False)
    
    if not trauma_success:
        print("❌ Trauma study failed!")
        return False
    
    print("✅ Trauma study completed successfully!")
    
    # Analysis preview
    print(f"\n📈 STUDY COMPLETED - ANALYSIS PREVIEW")
    print("=" * 50)
    print(f"✅ Baseline data: simulations/{baseline.name}/")
    print(f"✅ Trauma data: simulations/{trauma_study.name}/")
    print(f"📊 Ready for statistical analysis with continuous timeline data")
    print(f"🔬 Expected findings: Trauma impact on depression and anxiety scores")
    
    return True

def main():
    """Main function to set up and run trauma research study"""
    
    print("🧠 AI AGENT TRAUMA RESEARCH STUDY")
    print("=" * 60)
    print("""
This example creates a comprehensive trauma research study with:
• 5-day baseline phase with daily PHQ-9 assessments
• 7-day trauma phase with multiple traumatic events
• Continuous timeline with absolute step counting
• Multiple psychological assessments (PHQ-9, GAD-7, K10)
• Two participants for comparative analysis
    """)
    
    try:
        # Create study design
        baseline, trauma_study = create_trauma_research_study()
        
        # Ask user if they want to run the study
        response = input("\n🤔 Do you want to execute this study? (y/n): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            success = run_trauma_study(baseline, trauma_study)
            
            if success:
                print(f"\n🎉 Trauma research study completed successfully!")
                print(f"📁 Results available in:")
                print(f"   • simulations/{baseline.name}/")
                print(f"   • simulations/{trauma_study.name}/")
            else:
                print(f"\n❌ Study execution failed. Check error messages above.")
        else:
            print(f"\n💡 Study design created but not executed.")
            print(f"To run later, uncomment the execution lines in this script.")
            
    except Exception as e:
        print(f"\n❌ Error setting up trauma study: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()