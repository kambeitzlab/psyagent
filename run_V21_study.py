#!/usr/bin/env python3
# V21 Execution Script
import subprocess
import sys

simulations = [
    "V21_brief_trauma_therapy_test_baseline",
    "V21_brief_trauma_therapy_test_control", 
    "V21_brief_trauma_therapy_test_trauma_only",
    "V21_brief_trauma_therapy_test_trauma_therapy"
]

print("🚀 EXECUTING V21 STUDY")
for sim in simulations:
    print(f"Running {sim}...")
    try:
        subprocess.run([
            sys.executable, "run_simulation.py", 
            "--simulation", sim,
            "--headless"
        ], check=True)
        print(f"✓ {sim} completed")
    except Exception as e:
        print(f"❌ {sim} failed: {e}")

print("✅ V21 STUDY COMPLETED")
