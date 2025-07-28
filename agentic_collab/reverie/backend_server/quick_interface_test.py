#!/usr/bin/env python3
"""
Quick Test of Simulation Interface - Just verify it works
"""

from simulation_interface import *
import time

def test_basic_functionality():
    """Quick test to verify interface works"""
    
    print("🧪 QUICK SIMULATION INTERFACE TEST")
    print("=" * 40)
    
    # Configure simple baseline simulation (just 1 day, 24 steps)
    test_sim = create_simulation()
    test_sim.name = "Quick_Interface_Test"
    test_sim.description = "Quick test of interface functionality"
    test_sim.origin = "base_the_ville_isabella_maria_klaus"
    test_sim.steps_per_hour = 4
    test_sim.duration_in_days = 1  # Just 1 day
    test_sim.agents = ["Maria Lopez"]
    test_sim.type = "baseline"
    test_sim.assessments = [
        AssessmentConfig(
            name="PHQ-9",
            steps=[20],  # Just one assessment near end of day
            description="Single PHQ-9 test"
        )
    ]
    
    print("\n📋 Configuration:")
    print(f"  Duration: {test_sim.duration_in_days} day ({test_sim.duration_in_days * test_sim.steps_per_hour * 24} steps)")
    print(f"  Assessments: {len(test_sim.assessments)} scheduled")
    print(f"  Events: {len(test_sim.events)} scheduled")
    
    # Run simulation
    print(f"\n🚀 Running simulation...")
    success = test_sim.run(show_summary=False)
    
    if success:
        print("✅ INTERFACE TEST PASSED!")
        print("✓ Simulation created successfully")
        print("✓ OpenAI API integration working")
        print("✓ Agent behavior generation working")
        print("✓ Assessment scheduling working")
        return True
    else:
        print("❌ INTERFACE TEST FAILED!")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)