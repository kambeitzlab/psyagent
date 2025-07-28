import json
import os

def load_experiment_config(config_path=None):
    """
    Loads an experiment configuration from a JSON file.
    If no path is given, loads a default config file.
    """
    
    if config_path is None:
        # Default location relative to this file
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, "experiment_config.json")

    with open(config_path, "r") as f:
        config = json.load(f)
    



    return config
