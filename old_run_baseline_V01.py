# File: run_experiment.py
import os
import sys
import datetime
import json
import copy
import glob
import traceback


# Add the path to the directory containing reverie.py
os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

# Add the path to the directory containing reverie.py
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')  # Adjust this path

# Import necessary modules
from reverie import run_simulation_programmatically

def run_baseline_simulation(days=3, steps_per_hour=6):
    """
    Runs a baseline simulation for the specified number of days and saves it.
    
    Args:
        days: Number of simulation days to run
        steps_per_hour: Simulation steps per hour
    
    Returns:
        sim_code: The simulation code that can be used to continue the simulation
    """
    # Create a timestamp for the simulation name
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Calculate total steps
    total_steps = days * 24 * steps_per_hour
    
    print(f"Starting baseline simulation for {days} days ({total_steps} steps)...")
    print(f"Timestamp: {timestamp}")
    
    # Run the simulation
    simulation = run_simulation_programmatically(
        origin_sim="base_the_ville_isabella_maria_klaus",
        target_sim=f"baseline_{timestamp}",
        steps=total_steps,
        headless=True
    )
    
    # Save the simulation code for later reference
    output_info = {
        "baseline_sim_code": simulation.sim_code,
        "days_run": days,
        "steps_per_hour": steps_per_hour,
        "total_steps": total_steps,
        "timestamp": timestamp,
        "end_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save this information to a file
    with open(f"baseline_info_{timestamp}.json", "w") as f:
        json.dump(output_info, f, indent=2)
    
    print(f"Baseline simulation completed and saved as: {simulation.sim_code}")
    print(f"Reference information saved to: baseline_info_{timestamp}.json")
    
    return simulation.sim_code

if __name__ == "__main__":
    # Run the baseline simulation for 3 days
    baseline_sim_code = run_baseline_simulation(days=3)
    

# Import necessary modules
import glob
from utils import fs_storage  # Import the storage location from utils
import copy

from reverie import run_simulation_programmatically
from utils import fs_storage  # Import the storage location from utils

def get_latest_baseline():
    """Find the most recent baseline simulation by checking the baseline_info files"""
    info_files = glob.glob("baseline_info_*.json")
    if not info_files:
        return None
    
    # Sort by modification time (newest first)
    latest_file = max(info_files, key=os.path.getmtime)
    
    try:
        with open(latest_file, 'r') as f:
            info = json.load(f)
            return info.get('baseline_sim_code')
    except Exception as e:
        print(f"Error reading baseline file {latest_file}: {e}")
        return None

def verify_simulation_exists(sim_code):
    """Verify that a simulation folder exists"""
    sim_path = os.path.join(fs_storage, sim_code)
    return os.path.exists(sim_path)

def run_branched_experiment(baseline_sim_code=None, days=7, steps_per_hour=6):
    """
    Run a complete branched experiment with control, trauma, and recovery conditions.
    
    Args:
        baseline_sim_code: The simulation code to fork from (uses latest if None)
        days: Number of days to run each branch simulation
        steps_per_hour: Steps per hour in the simulation
        
    Returns:
        dict: Information about the experiment branches
    """
    # Find or validate baseline simulation
    if baseline_sim_code is None:
        baseline_sim_code = get_latest_baseline()
        if baseline_sim_code is None:
            raise ValueError("No baseline simulation found. Please run a baseline simulation first.")
    
    # Verify the baseline simulation exists
    if not verify_simulation_exists(baseline_sim_code):
        raise ValueError(f"Baseline simulation '{baseline_sim_code}' does not exist in {fs_storage}")
    
    # Create timestamp for this experiment
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Calculate total steps
    total_steps = days * 24 * steps_per_hour
    
    print(f"Starting branched experiment from baseline: {baseline_sim_code}")
    print(f"Each branch will run for {days} days ({total_steps} steps)")
    
    # Create base experiment configuration (shared settings)
    base_config = {
        "simulation_name": "mental_health_experiment",
        "questionnaires": [
            {
                "name": "PHQ-9",
                "frequency": "daily",
                "time": "20:00",
                "target_agents": ["Isabella Rodriguez", "Maria Lopez", "Klaus Mueller"]
            },
            {
                "name": "GAD-7", 
                "frequency": "daily",
                "time": "20:30",
                "target_agents": ["Isabella Rodriguez", "Maria Lopez", "Klaus Mueller"]
            }
        ]
    }
    
    # Define branch configurations
    branches = {
        "control": {
            "description": "Control condition - no special events",
            "timed_events": []  # No special events
        },
        "trauma": {
            "description": "Trauma condition - negative event for Isabella",
            "timed_events": [
                {
                    "name": "traumatic_event",
                    "type": "negative",
                    "time": "2023-02-13T08:30:00",  # Set time shortly after branch starts
                    "target": "Isabella Rodriguez",
                    "description": "Isabella receives devastating news about a family member being in a serious accident."
                }
            ]
        },
        "recovery": {
            "description": "Recovery condition - negative event followed by social support",
            "timed_events": [
                {
                    "name": "traumatic_event",
                    "type": "negative",
                    "time": "2023-02-13T08:30:00",  # Same traumatic event as trauma condition
                    "target": "Isabella Rodriguez",
                    "description": "Isabella receives devastating news about a family member being in a serious accident."
                },
                {
                    "name": "social_support",
                    "type": "positive",
                    "time": "2023-02-14T09:00:00",  # Support the next day
                    "target": "Isabella Rodriguez",
                    "description": "Maria visits Isabella to provide emotional support and help her cope with the difficult news."
                }
            ]
        }
    }
    
    # Results to track all branches
    experiment_results = {
        "baseline_sim_code": baseline_sim_code,
        "timestamp": timestamp,
        "days_per_branch": days,
        "steps_per_hour": steps_per_hour,
        "total_steps": total_steps,
        "branches": {}
    }
    
    # Run each branch
    for branch_name, branch_config in branches.items():
        print(f"\n--- Starting {branch_name.capitalize()} Branch ---")
        
        # Create a complete config for this branch
        config = copy.deepcopy(base_config)
        
        # Update simulation name with branch info
        config["simulation_name"] = f"{branch_name}_{timestamp}"
        
        # Add branch-specific settings
        config["timed_events"] = branch_config["timed_events"]
        
        # Save branch-specific config to a file
        config_path = f"{branch_name}_config_{timestamp}.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"Configuration saved to: {config_path}")
        print(f"Running {branch_name} branch with {len(config['timed_events'])} timed events")
        
        try:
            # Run the simulation for this branch, passing the config directly
            branch_sim = run_simulation_programmatically(
                origin_sim=baseline_sim_code,
                target_sim=config["simulation_name"],
                steps=total_steps,
                headless=True,
                config=config  # Pass the config directly
            )
            
            # Store results for this branch
            experiment_results["branches"][branch_name] = {
                "sim_code": branch_sim.sim_code,
                "config_path": config_path,
                "description": branch_config["description"],
                "success": True
            }
            
            print(f"✓ {branch_name.capitalize()} branch completed successfully: {branch_sim.sim_code}")
            
        except Exception as e:
            print(f"✗ Error running {branch_name} branch: {e}")
            experiment_results["branches"][branch_name] = {
                "sim_code": None,
                "config_path": config_path,
                "description": branch_config["description"],
                "error": str(e),
                "success": False
            }
    
    # Save experiment information
    experiment_file = f"experiment_{timestamp}.json"
    with open(experiment_file, "w") as f:
        json.dump(experiment_results, f, indent=2)
    
    print(f"\n--- Experiment Completed ---")
    print(f"Experiment information saved to: {experiment_file}")
    
    # Print a summary
    successful = sum(1 for branch in experiment_results["branches"].values() if branch["success"])
    print(f"Summary: {successful}/{len(branches)} branches completed successfully")
    
    for branch_name, branch_data in experiment_results["branches"].items():
        status = "✓ SUCCESS" if branch_data["success"] else "✗ FAILED"
        print(f"{status} - {branch_name.capitalize()}: {branch_data.get('sim_code', 'N/A')}")
    
    return experiment_results

def analyze_experiment_results(experiment_file=None):
    """
    Analyze the results of an experiment by examining assessment results across branches.
    
    Args:
        experiment_file: Path to the experiment JSON file (will use latest if None)
    """
    # Find the latest experiment file if none specified
    if experiment_file is None:
        experiment_files = glob.glob("experiment_*.json")
        if not experiment_files:
            print("No experiment files found.")
            return
        experiment_file = max(experiment_files, key=os.path.getmtime)
    
    print(f"Analyzing experiment results from: {experiment_file}")
    
    # Load the experiment data
    with open(experiment_file, 'r') as f:
        experiment = json.load(f)
    
    # Display basic experiment information
    print(f"Experiment timestamp: {experiment['timestamp']}")
    print(f"Baseline simulation: {experiment['baseline_sim_code']}")
    print(f"Duration: {experiment['days_per_branch']} days per branch")
    print(f"Branches: {', '.join(experiment['branches'].keys())}")
    
    # TODO: Implement detailed analysis by loading assessment results from each branch
    # This would involve loading the assessment files from each simulation
    # and comparing the mental health trajectories
    
    print("\nDetailed mental health analysis not yet implemented.")
    print("To implement analysis, you would need to:")
    print("1. Load assessment results from each simulation branch")
    print("2. Compare PHQ-9 and GAD-7 scores over time")
    print("3. Visualize the differences between branches")

# Example usage
if __name__ == "__main__":
    try:
        # Run the experiment
        results = run_branched_experiment(days=7)
        
        # Analyze the results
        # analyze_experiment_results()
        
    except Exception as e:
        print(f"Error running experiment: {e}")