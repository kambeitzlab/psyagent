"""
experiment/assessment_config.py
Configuration for mental health assessments
"""

import json
import os
from pathlib import Path


def load_assessment_config(config_file=None):
    """
    Load mental health assessment configuration from JSON file.
    
    Args:
        config_file: Path to the config file (optional)
        
    Returns:
        Dictionary with assessment configuration
    """
    if config_file is None:
        # Use default path
        base_path = Path(__file__).parent
        config_file = os.path.join(base_path, "assessment_config.json")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Return a default configuration if file not found
        return {
            "assessments": [
                {
                    "name": "PHQ-9",
                    "target_agents": ["Isabella Rodriguez", "Maria Lopez", "Klaus Mueller"],
                    "time": "08:00",  # Format: HH:MM in 24-hour format
                    "frequency": "daily",  # Options: daily, weekly, monthly
                    "start_date": "2023-02-13"  # Format: YYYY-MM-DD
                },
                {
                    "name": "GAD-7",
                    "target_agents": ["Isabella Rodriguez", "Maria Lopez"],
                    "time": "08:30",
                    "frequency": "daily",
                    "start_date": "2023-02-13"
                },
                {
                    "name": "K10",
                    "target_agents": ["Klaus Mueller"],
                    "time": "09:00",
                    "frequency": "weekly",
                    "start_date": "2023-02-13"
                }
            ]
        }