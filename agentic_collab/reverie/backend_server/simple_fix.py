#!/usr/bin/env python3
"""
Simple Fix - Just analyze therapy simulation results
"""

import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Load assessment results from ONLY the therapy simulation
assessment_dir = Path("../../simulations/Quick_Therapy_Example/assessment_results/Maria_Lopez")

# Load all PHQ-9 files
phq9_files = sorted(assessment_dir.glob("PHQ-9_*.json"))
print(f"Found {len(phq9_files)} PHQ-9 files")

# Parse assessment data
data = []
for file in phq9_files:
    with open(file) as f:
        result = json.load(f)
        total_score = sum(r['score'] for r in result['responses'].values())
        step = int(file.stem.split('_step')[-1])
        
        data.append({
            'timestamp': result['timestamp'],
            'total_score': total_score,
            'step': step,
            'day': step // 96 + 1,  # Convert steps to days
            'filename': file.name   # Add filename to see which files we're loading
        })

# Create DataFrame
df = pd.DataFrame(data)

print(f"\n📊 THERAPY SIMULATION RESULTS:")
print(df[['day', 'total_score', 'filename']])

# Basic statistics
print(f"\nPHQ-9 Results Summary:")
print(f"Mean score: {df['total_score'].mean():.1f}")
print(f"Range: {df['total_score'].min()} - {df['total_score'].max()}")
print(f"Trend: {'Improving' if df['total_score'].iloc[-1] < df['total_score'].iloc[0] else 'Stable/Worsening'}")

# Show trauma effect
day1_score = df[df['day'] == 1]['total_score'].iloc[0] if len(df[df['day'] == 1]) > 0 else None
if day1_score:
    later_scores = df[df['day'] > 1]['total_score'].mean()
    print(f"\nTrauma impact analysis:")
    print(f"Day 1 (trauma day): {day1_score}")
    print(f"Days 2-5 (post-therapy): {later_scores:.1f}")
    print(f"Change: {later_scores - day1_score:+.1f} points")

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(df['day'], df['total_score'], 'ro-', linewidth=2, markersize=8, label='Trauma + Therapy')

# Mark trauma event
plt.axvline(x=1, color='red', linestyle=':', alpha=0.8, linewidth=2)
plt.text(1.1, df['total_score'].max(), 'Trauma\nEvent', rotation=0, va='top', fontsize=10)

# Mark therapy sessions (Days 1, 3, 5 based on your configuration)
therapy_days = [1, 3, 5]
for day in therapy_days:
    plt.axvline(x=day, color='green', linestyle=':', alpha=0.6, linewidth=1.5)

plt.text(3, 1, 'Therapy Sessions\n(Days 1, 3, 5)', ha='center', va='center',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))

plt.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Mild depression threshold')
plt.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Moderate depression threshold')
plt.xlabel('Study Day')
plt.ylabel('PHQ-9 Total Score')
plt.title('Depression Scores During Trauma + Therapy Study (Therapy Simulation Only)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(0.5, 5.5)
plt.ylim(-0.5, max(df['total_score']) + 1)
plt.tight_layout()
plt.savefig('phq9_therapy_only.png', dpi=300)
plt.show()