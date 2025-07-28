#!/usr/bin/env python3
"""
Therapy Intervention Example
===========================

This example demonstrates how to create a comprehensive therapy intervention study
comparing trauma-only vs trauma+therapy conditions.
"""

import sys
import os

# Add the parent directory to path to import simulation_interface
sys.path.append('..')
from simulation_interface import *

def create_therapy_intervention_study():
    """Create a complete therapy intervention study with multiple conditions"""
    
    print("🏥 THERAPY INTERVENTION STUDY SETUP")
    print("=" * 50)
    
    # ========================================================================
    # Phase 1: Baseline Study (7 days)
    # ========================================================================
    
    print("\n📋 Phase 1: Creating Baseline Study")
    print("-" * 30)
    
    baseline = create_simulation()
    baseline.name = "Therapy_Study_Baseline"
    baseline.description = "7-day baseline for therapy intervention study"
    baseline.origin = "base_the_ville_isabella_maria_klaus"
    baseline.steps_per_hour = 4
    baseline.duration_in_days = 7
    baseline.agents = ["Maria Lopez", "Isabella Rodriguez", "Klaus Mueller"]
    baseline.type = "baseline"
    
    # Comprehensive baseline assessments
    baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=baseline.daily_assessment_steps(7),
            description="Daily depression assessment during baseline"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[baseline.time_to_step(1, 18), baseline.time_to_step(7, 18)],
            description="Pre/post anxiety assessment"
        )
    ]
    
    print(f"Baseline: {baseline.duration_in_days} days, {len(baseline.agents)} agents")
    
    # ========================================================================
    # Phase 2A: Trauma-Only Condition (10 days)
    # ========================================================================
    
    print("\n📋 Phase 2A: Creating Trauma-Only Condition")
    print("-" * 30)
    
    trauma_only = create_simulation()
    trauma_only.name = "Therapy_Study_Trauma_Only"
    trauma_only.description = "10-day trauma exposure without therapy"
    trauma_only.origin = "Therapy_Study_Baseline"
    trauma_only.steps_per_hour = 4
    trauma_only.duration_in_days = 10
    trauma_only.agents = ["Maria Lopez"]  # Single agent for this condition
    trauma_only.type = "trauma_only"
    
    # Trauma-only assessments
    trauma_only.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=trauma_only.daily_assessment_steps(10),
            description="Daily depression tracking without therapy"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[trauma_only.time_to_step(d, 20) for d in [1, 3, 6, 10]],
            description="Anxiety assessment at key timepoints"
        )
    ]
    
    # Trauma events without therapy intervention
    trauma_only.events = [
        EventConfig(
            name="workplace_trauma",
            step=trauma_only.time_to_step(1, 10),
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria witnesses a severe workplace accident where a colleague "
                       "falls from scaffolding and suffers critical injuries. She experiences "
                       "intense emotional distress, survivor guilt, and helplessness."
        ),
        EventConfig(
            name="trauma_reminder",
            step=trauma_only.time_to_step(5, 15),
            event_type="negative",
            target_agent="Maria Lopez",
            description="Maria visits the workplace where the accident occurred, triggering "
                       "intense flashbacks and renewed anxiety about the traumatic event."
        )
    ]
    
    print(f"Trauma-Only: {trauma_only.duration_in_days} days, {len(trauma_only.events)} trauma events")
    
    # ========================================================================
    # Phase 2B: Trauma + Therapy Condition (10 days)
    # ========================================================================
    
    print("\n📋 Phase 2B: Creating Trauma + Therapy Condition")
    print("-" * 30)
    
    trauma_therapy = create_simulation()
    trauma_therapy.name = "Therapy_Study_Trauma_Therapy"
    trauma_therapy.description = "10-day trauma exposure with therapy intervention"
    trauma_therapy.origin = "Therapy_Study_Baseline"
    trauma_therapy.steps_per_hour = 4
    trauma_therapy.duration_in_days = 10
    trauma_therapy.agents = ["Isabella Rodriguez"]  # Different agent for comparison
    trauma_therapy.type = "trauma_therapy"
    
    # Therapy condition assessments
    trauma_therapy.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=trauma_therapy.daily_assessment_steps(10),
            description="Daily depression tracking with therapy"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[trauma_therapy.time_to_step(d, 20) for d in [1, 3, 6, 10]],
            description="Anxiety assessment during therapy treatment"
        ),
        AssessmentConfig(
            name="K10",
            steps=[trauma_therapy.time_to_step(2, 12), trauma_therapy.time_to_step(8, 12)],
            description="Psychological distress before/after therapy"
        )
    ]
    
    # Trauma + comprehensive therapy intervention
    trauma_therapy.events = [
        # Initial trauma event (same type as trauma-only condition)
        EventConfig(
            name="workplace_trauma",
            step=trauma_therapy.time_to_step(1, 10),
            event_type="negative",
            target_agent="Isabella Rodriguez",
            description="Isabella witnesses a severe workplace accident where a colleague "
                       "falls from scaffolding and suffers critical injuries. She experiences "
                       "intense emotional distress, survivor guilt, and helplessness."
        ),
        
        # Emergency therapy session (same day)
        EventConfig(
            name="emergency_therapy_session",
            step=trauma_therapy.time_to_step(1, 16),
            event_type="therapy",
            target_agent="Isabella Rodriguez",
            description="Emergency therapy session focusing on acute trauma response. "
                       "Therapist provides immediate emotional support, grounding techniques, "
                       "and helps Isabella process the initial shock and distress."
        ),
        
        # Structured therapy protocol (5 sessions over 10 days)
        EventConfig(
            name="therapy_session_2_assessment",
            step=trauma_therapy.time_to_step(3, 15),
            event_type="therapy",
            target_agent="Isabella Rodriguez",
            description="Second therapy session focusing on trauma assessment and "
                       "developing coping strategies. Introduction to cognitive restructuring "
                       "techniques to address guilt and self-blame."
        ),
        
        EventConfig(
            name="therapy_session_3_processing",
            step=trauma_therapy.time_to_step(5, 15),
            event_type="therapy",
            target_agent="Isabella Rodriguez",
            description="Third therapy session using EMDR (Eye Movement Desensitization "
                       "and Reprocessing) techniques to process traumatic memories and "
                       "reduce their emotional intensity."
        ),
        
        EventConfig(
            name="therapy_session_4_integration",
            step=trauma_therapy.time_to_step(7, 15),
            event_type="therapy",
            target_agent="Isabella Rodriguez",
            description="Fourth therapy session focusing on integration and meaning-making. "
                       "Helping Isabella develop a coherent narrative about the experience "
                       "and identify personal growth and resilience."
        ),
        
        EventConfig(
            name="therapy_session_5_consolidation",
            step=trauma_therapy.time_to_step(9, 15),
            event_type="therapy",
            target_agent="Isabella Rodriguez",
            description="Final therapy session focusing on consolidation and relapse prevention. "
                       "Reviewing progress, reinforcing coping skills, and developing a plan "
                       "for continued recovery and future challenges."
        ),
        
        # Trigger event to test therapy effectiveness
        EventConfig(
            name="trauma_reminder_test",
            step=trauma_therapy.time_to_step(8, 12),
            event_type="negative",
            target_agent="Isabella Rodriguez",
            description="Isabella visits the workplace where the accident occurred, providing "
                       "a test of therapy effectiveness in managing trauma-related triggers."
        )
    ]
    
    print(f"Trauma+Therapy: {trauma_therapy.duration_in_days} days, 5 therapy sessions")
    
    # ========================================================================
    # Phase 3: Control Condition (10 days)
    # ========================================================================
    
    print("\n📋 Phase 3: Creating Control Condition")
    print("-" * 30)
    
    control = create_simulation()
    control.name = "Therapy_Study_Control"
    control.description = "10-day control condition with no interventions"
    control.origin = "Therapy_Study_Baseline"
    control.steps_per_hour = 4
    control.duration_in_days = 10
    control.agents = ["Klaus Mueller"]  # Third agent for control
    control.type = "control"
    
    # Control assessments (same schedule as experimental conditions)
    control.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=control.daily_assessment_steps(10),
            description="Daily depression assessment in control condition"
        ),
        AssessmentConfig(
            name="GAD-7",
            steps=[control.time_to_step(d, 20) for d in [1, 3, 6, 10]],
            description="Anxiety assessment in control condition"
        )
    ]
    
    # No events for control condition
    control.events = []
    
    print(f"Control: {control.duration_in_days} days, no interventions")
    
    return baseline, trauma_only, trauma_therapy, control

def display_study_design(baseline, trauma_only, trauma_therapy, control):
    """Display comprehensive study design overview"""
    
    print(f"\n📊 COMPLETE STUDY DESIGN OVERVIEW")
    print("=" * 60)
    
    # Timeline overview
    baseline_start, baseline_end = baseline.get_absolute_step_range()
    trauma_start, trauma_end = trauma_only.get_absolute_step_range()
    
    print(f"Study Timeline:")
    print(f"  Phase 1 (Baseline):     Days 1-7   (Steps {baseline_start}-{baseline_end})")
    print(f"  Phase 2 (Experimental): Days 8-17  (Steps {trauma_start}-{trauma_end})")
    print(f"  Total Duration:         17 days    ({trauma_end} steps)")
    
    # Experimental conditions
    print(f"\nExperimental Conditions:")
    conditions = [
        ("Control", control, "No interventions"),
        ("Trauma-Only", trauma_only, f"{len(trauma_only.events)} trauma events"),
        ("Trauma+Therapy", trauma_therapy, f"{len([e for e in trauma_therapy.events if e.event_type == 'therapy'])} therapy sessions")
    ]
    
    for name, condition, description in conditions:
        agent = condition.agents[0]
        assessments = sum(len(a.steps) for a in condition.assessments)
        print(f"  {name:15} | {agent:20} | {assessments:2d} assessments | {description}")
    
    # Statistical design
    print(f"\nStatistical Design:")
    print(f"  Design Type:     Between-subjects comparison")
    print(f"  Primary Outcome: PHQ-9 depression scores")
    print(f"  Secondary:       GAD-7 anxiety, K10 distress")
    print(f"  Analysis Plan:   Repeated measures ANOVA")
    print(f"  Comparisons:     Control vs Trauma vs Trauma+Therapy")
    
    # Expected outcomes
    print(f"\nExpected Outcomes:")
    print(f"  ✓ Control:         Stable baseline scores")
    print(f"  ✓ Trauma-Only:     Elevated depression/anxiety scores")
    print(f"  ✓ Trauma+Therapy:  Initial elevation, then improvement")
    print(f"  ✓ Effect Size:     Large difference between conditions")

def run_intervention_study(baseline, trauma_only, trauma_therapy, control):
    """Execute the complete therapy intervention study"""
    
    print(f"\n🚀 EXECUTING THERAPY INTERVENTION STUDY")
    print("=" * 60)
    
    conditions = [
        ("Baseline", baseline),
        ("Control", control),
        ("Trauma-Only", trauma_only),
        ("Trauma+Therapy", trauma_therapy)
    ]
    
    # Validate all conditions
    print(f"\n🔍 Validating all conditions...")
    all_valid = True
    
    for name, condition in conditions:
        errors = condition.validate()
        if errors:
            print(f"❌ {name} configuration errors:")
            for error in errors:
                print(f"    • {error}")
            all_valid = False
        else:
            print(f"✅ {name} configuration valid")
    
    if not all_valid:
        return False
    
    # Execute studies in sequence
    for name, condition in conditions:
        print(f"\n📊 Executing {name} Condition")
        print("-" * 40)
        
        success = condition.run(show_summary=False)
        
        if success:
            print(f"✅ {name} completed successfully!")
        else:
            print(f"❌ {name} failed!")
            return False
    
    # Study completion summary
    print(f"\n🎉 THERAPY INTERVENTION STUDY COMPLETED")
    print("=" * 60)
    
    print(f"✅ All conditions executed successfully!")
    print(f"📁 Results saved to:")
    for name, condition in conditions:
        print(f"   • simulations/{condition.name}/")
    
    print(f"\n📊 Ready for analysis with continuous timeline data:")
    print(f"   • Between-subjects comparison across conditions")
    print(f"   • Repeated measures analysis within subjects")
    print(f"   • Effect size calculations for therapy benefit")
    
    return True

def main():
    """Main function to set up and run therapy intervention study"""
    
    print("🧠 AI AGENT THERAPY INTERVENTION STUDY")
    print("=" * 70)
    print("""
This example creates a comprehensive therapy intervention study with:
• 7-day baseline phase establishing normal behavior
• 3 experimental conditions: Control, Trauma-Only, Trauma+Therapy
• 5-session structured therapy protocol for intervention group
• Multiple psychological assessments (PHQ-9, GAD-7, K10)
• Continuous timeline for clean statistical analysis
• Between-subjects design for therapy effectiveness research
    """)
    
    try:
        # Create study design
        baseline, trauma_only, trauma_therapy, control = create_therapy_intervention_study()
        
        # Display comprehensive overview
        display_study_design(baseline, trauma_only, trauma_therapy, control)
        
        # Ask user if they want to run the study
        response = input("\n🤔 Do you want to execute this complete study? (y/n): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            success = run_intervention_study(baseline, trauma_only, trauma_therapy, control)
            
            if success:
                print(f"\n🎉 Therapy intervention study completed successfully!")
                print(f"🔬 Ready for statistical analysis and publication!")
            else:
                print(f"\n❌ Study execution failed. Check error messages above.")
        else:
            print(f"\n💡 Study design created but not executed.")
            print(f"Individual conditions can be run by calling .run() on each simulation.")
            
    except Exception as e:
        print(f"\n❌ Error setting up therapy intervention study: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()