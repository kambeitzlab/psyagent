#!/usr/bin/env python3
"""
Fixed Analysis - Separate Baseline and Treatment Results
"""

import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

def analyze_simulation_results():
    """Analyze results from both baseline and therapy simulations separately"""
    
    print("📊 ANALYZING SIMULATION RESULTS")
    print("=" * 50)
    
    # Load results from both simulations
    baseline_dir = Path("../../simulations/Quick_Baseline_Example/assessment_results/Maria_Lopez")
    therapy_dir = Path("../../simulations/Quick_Therapy_Example/assessment_results/Maria_Lopez")
    
    def load_phq9_data(assessment_dir, simulation_name):
        """Load PHQ-9 data from a specific simulation"""
        phq9_files = sorted(assessment_dir.glob("PHQ-9_*.json"))
        
        data = []
        for file in phq9_files:
            with open(file) as f:
                result = json.load(f)
                total_score = sum(r['score'] for r in result['responses'].values())
                step = int(file.stem.split('_step')[-1])
                
                data.append({
                    'simulation': simulation_name,
                    'timestamp': result['timestamp'],
                    'total_score': total_score,
                    'step': step,
                    'day': step // 96 + 1  # Convert to study day
                })
        
        return data
    
    # Load data from both simulations
    all_data = []
    
    if baseline_dir.exists():
        baseline_data = load_phq9_data(baseline_dir, "Baseline")
        all_data.extend(baseline_data)
        print(f"✓ Loaded {len(baseline_data)} baseline assessments")
    
    if therapy_dir.exists():
        therapy_data = load_phq9_data(therapy_dir, "Therapy")
        all_data.extend(therapy_data)
        print(f"✓ Loaded {len(therapy_data)} therapy assessments")
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    print(f"\n📋 Data Summary:")
    print(df.groupby('simulation').agg({
        'total_score': ['count', 'mean', 'min', 'max'],
        'day': ['min', 'max']
    }).round(2))
    
    # Separate analysis by simulation
    print(f"\n📈 SIMULATION COMPARISONS:")
    
    if 'Baseline' in df['simulation'].values:
        baseline_df = df[df['simulation'] == 'Baseline']
        baseline_mean = baseline_df['total_score'].mean()
        print(f"Baseline (3 days): Mean PHQ-9 = {baseline_mean:.1f}")
        print(f"  Scores: {baseline_df['total_score'].tolist()}")
    
    if 'Therapy' in df['simulation'].values:
        therapy_df = df[df['simulation'] == 'Therapy']
        therapy_mean = therapy_df['total_score'].mean()
        print(f"Therapy (5 days): Mean PHQ-9 = {therapy_mean:.1f}")
        print(f"  Scores: {therapy_df['total_score'].tolist()}")
        
        # Show trauma effect (Day 1 vs subsequent days)
        day1_score = therapy_df[therapy_df['day'] == 1]['total_score'].iloc[0]
        later_scores = therapy_df[therapy_df['day'] > 1]['total_score'].mean()
        print(f"  Day 1 (trauma): {day1_score}")
        print(f"  Days 2-5 (therapy): {later_scores:.1f}")
    
    # Plot comparison
    plt.figure(figsize=(12, 8))
    
    # Plot baseline data
    if 'Baseline' in df['simulation'].values:
        baseline_df = df[df['simulation'] == 'Baseline']
        plt.plot(baseline_df['day'], baseline_df['total_score'], 
                'bo-', linewidth=2, markersize=8, label='Baseline', alpha=0.7)
    
    # Plot therapy data with different x-axis (continuing from baseline)
    if 'Therapy' in df['simulation'].values:
        therapy_df = df[df['simulation'] == 'Therapy']
        # Adjust therapy days to continue from baseline (days 4-8 instead of 1-5)
        therapy_df_plot = therapy_df.copy()
        therapy_df_plot['adjusted_day'] = therapy_df_plot['day'] + 3  # Continue after 3-day baseline
        
        plt.plot(therapy_df_plot['adjusted_day'], therapy_df_plot['total_score'], 
                'ro-', linewidth=2, markersize=8, label='Trauma + Therapy', alpha=0.7)
        
        # Mark trauma event
        plt.axvline(x=4, color='red', linestyle=':', alpha=0.8, linewidth=2)
        plt.text(4.1, therapy_df['total_score'].max(), 'Trauma\nEvent', 
                rotation=0, va='top', fontsize=10)
        
        # Mark therapy sessions
        therapy_days = [4, 6, 8]  # Adjusted for continuous timeline
        for day in therapy_days:
            plt.axvline(x=day, color='green', linestyle=':', alpha=0.6, linewidth=1.5)
    
    # Add phase separator
    plt.axvline(x=3.5, color='black', linestyle='--', alpha=0.5, linewidth=2)
    plt.text(2, 6, 'Baseline\nPhase', ha='center', va='center', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    plt.text(6, 6, 'Experimental\nPhase', ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
    
    # Formatting
    plt.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Mild depression threshold')
    plt.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Moderate depression threshold')
    plt.xlabel('Study Day', fontsize=12)
    plt.ylabel('PHQ-9 Total Score', fontsize=12)
    plt.title('PHQ-9 Depression Scores: Baseline vs Trauma + Therapy', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.xlim(0.5, 8.5)
    plt.ylim(-0.5, max(df['total_score']) + 1)
    plt.tight_layout()
    plt.savefig('phq9_comparison_fixed.png', dpi=300)
    plt.show()
    
    return df

if __name__ == "__main__":
    df = analyze_simulation_results()