#!/usr/bin/env python3
"""
Comprehensive Test of Simulation Interface
Tests all functionality: assessments, trauma events, therapy, and file generation
"""

from simulation_interface import *
import time
import shutil
from pathlib import Path

def cleanup_test_simulations():
    """Clean up any existing test simulations"""
    try:
        from simulation_manager import simulation_manager
        test_names = [
            "Test_Baseline_Interface",
            "Test_Control_Interface", 
            "Test_Trauma_Only_Interface",
            "Test_Trauma_Therapy_Interface"
        ]
        
        for name in test_names:
            sim_dir = simulation_manager.simulations_root / name
            if sim_dir.exists():
                shutil.rmtree(sim_dir)
                print(f"✓ Cleaned up {name}")
                
    except Exception as e:
        print(f"Warning: Could not cleanup: {e}")

def verify_files_generated(simulation_name: str) -> dict:
    """Verify that all expected files were generated"""
    
    try:
        from simulation_manager import simulation_manager
        sim_dir = simulation_manager.simulations_root / simulation_name
        
        results = {
            "simulation_exists": sim_dir.exists(),
            "metadata_exists": (sim_dir / "metadata.json").exists(),
            "centralized_logs": (sim_dir / "all_logs").exists(),
            "assessment_results": (sim_dir / "assessment_results").exists(),
            "events_log": (sim_dir / "all_logs" / "simulation_logs" / "events.jsonl").exists() if (sim_dir / "all_logs").exists() else False,
            "therapy_events": (sim_dir / "all_logs" / "simulation_logs" / "therapy_events.jsonl").exists() if (sim_dir / "all_logs").exists() else False,
            "debug_log": (sim_dir / "all_logs" / "simulation_debug.log").exists() if (sim_dir / "all_logs").exists() else False
        }
        
        # Count assessment files
        if results["assessment_results"]:
            assessment_files = list((sim_dir / "assessment_results").glob("**/*.json"))
            results["assessment_count"] = len(assessment_files)
        else:
            results["assessment_count"] = 0
            
        return results
        
    except Exception as e:
        return {"error": str(e)}

def analyze_events_log(simulation_name: str):
    """Analyze events log for trauma and therapy events"""
    
    try:
        from simulation_manager import simulation_manager
        sim_dir = simulation_manager.simulations_root / simulation_name
        events_file = sim_dir / "all_logs" / "simulation_logs" / "events.jsonl"
        
        if not events_file.exists():
            return {"error": "Events log not found"}
        
        trauma_events = 0
        therapy_events = 0
        assessment_events = 0
        
        with open(events_file, 'r') as f:
            for line in f:
                try:
                    import json
                    event = json.loads(line.strip())
                    event_type = event.get('event_type', '')
                    
                    if 'trauma' in event.get('details', {}).get('description', '').lower():
                        trauma_events += 1
                    elif event_type == 'therapy_session':
                        therapy_events += 1
                    elif event_type == 'assessment':
                        assessment_events += 1
                        
                except:
                    continue
        
        return {
            "trauma_events": trauma_events,
            "therapy_events": therapy_events, 
            "assessment_events": assessment_events
        }
        
    except Exception as e:
        return {"error": str(e)}

def test_baseline_simulation():
    """Test 1: Basic baseline simulation with assessments"""
    
    print("\n🧪 TEST 1: Baseline Simulation")
    print("=" * 40)
    
    # Configure baseline simulation
    test_baseline = create_simulation()
    test_baseline.name = "Test_Baseline_Interface"
    test_baseline.description = "Test baseline simulation with PHQ-9 assessments"
    test_baseline.origin = "base_the_ville_isabella_maria_klaus"
    test_baseline.steps_per_hour = 4
    test_baseline.duration_in_days = 3  # Short test
    test_baseline.agents = ["Maria Lopez"]
    test_baseline.type = "baseline"
    test_baseline.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=test_baseline.daily_assessment_steps(3),
            description="Daily PHQ-9 during baseline test"
        )
    ]
    
    # Run simulation
    success = test_baseline.run()
    
    if success:
        # Verify files
        files = verify_files_generated("Test_Baseline_Interface")
        events = analyze_events_log("Test_Baseline_Interface")
        
        print(f"\n📊 BASELINE TEST RESULTS:")
        print(f"  Simulation created: {'✅' if files.get('simulation_exists') else '❌'}")
        print(f"  Metadata file: {'✅' if files.get('metadata_exists') else '❌'}")
        print(f"  Centralized logs: {'✅' if files.get('centralized_logs') else '❌'}")
        print(f"  Assessment results: {'✅' if files.get('assessment_results') else '❌'}")
        print(f"  Events log: {'✅' if files.get('events_log') else '❌'}")
        print(f"  Assessment files: {files.get('assessment_count', 0)} (expected: 3)")
        
        return files.get('simulation_exists', False)
    
    return False

def test_trauma_only_simulation():
    """Test 2: Trauma-only simulation"""
    
    print("\n🧪 TEST 2: Trauma-Only Simulation")
    print("=" * 40)
    
    # Configure trauma simulation
    test_trauma = create_simulation()
    test_trauma.name = "Test_Trauma_Only_Interface"
    test_trauma.description = "Test trauma simulation with assessment"
    test_trauma.origin = "Test_Baseline_Interface"  # Branch from baseline
    test_trauma.steps_per_hour = 4
    test_trauma.duration_in_days = 3
    test_trauma.agents = ["Maria Lopez"]
    test_trauma.type = "trauma_only"
    test_trauma.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=test_trauma.daily_assessment_steps(3),
            description="Daily PHQ-9 after trauma"
        )
    ]
    test_trauma.events = [
        EventConfig(
            name="test_trauma_event",
            step=8,  # Early in simulation
            event_type="negative",
            target_agent="Maria Lopez",
            description="Test traumatic event: Maria witnesses a violent car accident where multiple people are severely injured. She feels helpless and unable to provide assistance, leading to feelings of guilt and distress."
        )
    ]
    
    # Run simulation
    success = test_trauma.run()
    
    if success:
        # Verify files and events
        files = verify_files_generated("Test_Trauma_Only_Interface")
        events = analyze_events_log("Test_Trauma_Only_Interface")
        
        print(f"\n📊 TRAUMA TEST RESULTS:")
        print(f"  Simulation created: {'✅' if files.get('simulation_exists') else '❌'}")
        print(f"  Assessment files: {files.get('assessment_count', 0)} (expected: 3)")
        print(f"  Trauma events found: {events.get('trauma_events', 0)} (expected: ≥1)")
        
        return files.get('simulation_exists', False) and events.get('trauma_events', 0) > 0
    
    return False

def test_trauma_therapy_simulation():
    """Test 3: Trauma + therapy simulation"""
    
    print("\n🧪 TEST 3: Trauma + Therapy Simulation")
    print("=" * 40)
    
    # Configure trauma+therapy simulation
    test_therapy = create_simulation()
    test_therapy.name = "Test_Trauma_Therapy_Interface"
    test_therapy.description = "Test trauma with therapy intervention"
    test_therapy.origin = "Test_Baseline_Interface"
    test_therapy.steps_per_hour = 4
    test_therapy.duration_in_days = 4  # Slightly longer for therapy
    test_therapy.agents = ["Maria Lopez"]
    test_therapy.type = "trauma_therapy"
    test_therapy.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=test_therapy.daily_assessment_steps(4),
            description="Daily PHQ-9 during treatment"
        )
    ]
    test_therapy.events = [
        EventConfig(
            name="test_trauma_event",
            step=8,  # Day 1, early
            event_type="negative",
            target_agent="Maria Lopez",
            description="Test traumatic event: Maria witnesses a serious workplace accident where a colleague is badly injured. She experiences intense distress and guilt about not being able to prevent the incident."
        ),
        EventConfig(
            name="test_therapy_session_1",
            step=32,  # Day 1, later
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Emergency therapy session focusing on acute trauma response and initial coping strategies."
        ),
        EventConfig(
            name="test_therapy_session_2",
            step=test_therapy.time_to_step(3, 18),  # Day 3, 6 PM
            event_type="therapy",
            target_agent="Maria Lopez",
            description="Follow-up therapy session for trauma processing and developing long-term coping mechanisms."
        )
    ]
    
    # Run simulation
    success = test_therapy.run()
    
    if success:
        # Verify files and events
        files = verify_files_generated("Test_Trauma_Therapy_Interface")
        events = analyze_events_log("Test_Trauma_Therapy_Interface")
        
        print(f"\n📊 THERAPY TEST RESULTS:")
        print(f"  Simulation created: {'✅' if files.get('simulation_exists') else '❌'}")
        print(f"  Assessment files: {files.get('assessment_count', 0)} (expected: 4)")
        print(f"  Trauma events found: {events.get('trauma_events', 0)} (expected: ≥1)")
        print(f"  Therapy events found: {events.get('therapy_events', 0)} (expected: 2)")
        print(f"  Therapy events log: {'✅' if files.get('therapy_events') else '❌'}")
        
        return (files.get('simulation_exists', False) and 
                events.get('trauma_events', 0) > 0 and 
                events.get('therapy_events', 0) >= 2)
    
    return False

def test_control_simulation():
    """Test 4: Control simulation (no interventions)"""
    
    print("\n🧪 TEST 4: Control Simulation")
    print("=" * 40)
    
    # Configure control simulation
    test_control = create_simulation()
    test_control.name = "Test_Control_Interface"
    test_control.description = "Test control simulation - no interventions"
    test_control.origin = "Test_Baseline_Interface"
    test_control.steps_per_hour = 4
    test_control.duration_in_days = 3
    test_control.agents = ["Maria Lopez"]
    test_control.type = "control"
    test_control.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=test_control.daily_assessment_steps(3),
            description="Daily PHQ-9 during control period"
        )
    ]
    # No events - this is control condition
    
    # Run simulation
    success = test_control.run()
    
    if success:
        # Verify files
        files = verify_files_generated("Test_Control_Interface")
        
        print(f"\n📊 CONTROL TEST RESULTS:")
        print(f"  Simulation created: {'✅' if files.get('simulation_exists') else '❌'}")
        print(f"  Assessment files: {files.get('assessment_count', 0)} (expected: 3)")
        
        return files.get('simulation_exists', False)
    
    return False

def main():
    """Run comprehensive tests"""
    
    print("🔬 COMPREHENSIVE SIMULATION INTERFACE TESTS")
    print("=" * 60)
    
    # Clean up previous tests
    print("\n🧹 Cleaning up previous test simulations...")
    cleanup_test_simulations()
    
    # Run tests
    test_results = {
        "baseline": False,
        "trauma_only": False,
        "trauma_therapy": False,
        "control": False
    }
    
    try:
        # Test 1: Baseline
        test_results["baseline"] = test_baseline_simulation()
        time.sleep(2)  # Brief pause between tests
        
        # Test 2: Trauma only (depends on baseline)
        if test_results["baseline"]:
            test_results["trauma_only"] = test_trauma_only_simulation()
            time.sleep(2)
        
        # Test 3: Trauma + therapy (depends on baseline)
        if test_results["baseline"]:
            test_results["trauma_therapy"] = test_trauma_therapy_simulation()
            time.sleep(2)
        
        # Test 4: Control (depends on baseline)
        if test_results["baseline"]:
            test_results["control"] = test_control_simulation()
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print(f"\n📊 FINAL TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Simulation interface is working correctly.")
        print("\n📁 Test results available in:")
        print("  - simulations/Test_Baseline_Interface/")
        print("  - simulations/Test_Trauma_Only_Interface/")  
        print("  - simulations/Test_Trauma_Therapy_Interface/")
        print("  - simulations/Test_Control_Interface/")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)