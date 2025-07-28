"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: reverie.py
Description: This is the main program for running generative agent simulations
that defines the ReverieServer class. This class maintains and records all  
states related to the simulation. The primary mode of interaction for those  
running the simulation should be through the open_server function, which  
enables the simulator to input command-line prompts for running and saving  
the simulation, among other tasks.

Release note (June 14, 2023) -- Reverie implements the core simulation 
mechanism described in my paper entitled "Generative Agents: Interactive 
Simulacra of Human Behavior." If you are reading through these lines after 
having read the paper, you might notice that I use older terms to describe 
generative agents and their cognitive modules here. Most notably, I use the 
term "personas" to refer to generative agents, "associative memory" to refer 
to the memory stream, and "reverie" to refer to the overarching simulation 
framework.
"""

import sys
import os

# Add the project root (agentic_collab) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import json
import datetime
import time
import math
import os
import shutil
import traceback
from pathlib import Path

from global_methods import read_file_to_list, check_if_file_exists, copyanything, freeze
from utils import maze_assets_loc, fs_storage, fs_temp_storage
from maze import Maze


from persona.cognitive_modules.questionnaire import PHQ9, GAD7, K10
from persona.cognitive_modules.assess import assess_mental_health #, save_assessment_results
#from assess import assess_mental_health
from persona.persona import Persona
from persona.cognitive_modules.converse import load_history_via_whisper
from persona.prompt_template.run_gpt_prompt import run_plugin

from assessment_scheduler import AssessmentScheduler
from logger import SimulationLogger
# Initialize logger
logger = SimulationLogger("simulation_events_log") 
#from experiment.experiment_config import load_experiment_config
#from experiment_scheduler import experiment_scheduler


current_file = os.path.abspath(__file__)

def trace_calls_and_lines(frame, event, arg):
  if event == 'call':
    code = frame.f_code
    filename = code.co_filename
    short_filename = os.path.relpath(filename)
    if os.path.abspath(filename).startswith(os.getcwd()):
    # # if os.path.abspath(filename).startswith():
    # # if filename == current_file:
      print(f"Calling function: {code.co_name} in {short_filename}:{code.co_firstlineno}")


import logging

# Set up debug logging to a separate file
debug_logger = logging.getLogger('debug')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('simulation_debug.log', mode='w')
debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
debug_logger.addHandler(debug_handler)


##############################################################################
#                                  REVERIE                                   #
##############################################################################

logfile_name = "log.txt"

class ReverieServer: 
  def __init__(self, 
               fork_sim_code,
               sim_code,
               working_dir=None,        
               simulation_name=None,    
               simulation_type=None,
               #simulation_results_path=None,
               preserve_origin_state=False):
    
    print ("(reverie): Temp storage: ", fs_temp_storage)
    
    # Store preserve_origin_state flag
    self.preserve_origin_state = preserve_origin_state
    
    print(f"DEBUG __init__: Initializing ReverieServer with preserve_origin_state={preserve_origin_state}")
    

    self.exp_config = {}
    self.logger = None
    self.scheduled_events = []
    self.next_event_idx = 0
    self.scheduled_questionnaires = []
    self.last_questionnaire_time = {}
    self.administered_questionnaires = set()  # Track which questionnaires have been administered
    self.simulation_type = simulation_type  # "baseline", "control", or "experiment"

    # Store working directory and simulation info  # ADD THIS BLOCK
    self.working_dir = Path(working_dir) if working_dir else None
    self.simulation_name = simulation_name
    self.simulation_type = simulation_type

    #self.simulation_results_path = simulation_results_path  # Path to save results
    self.assessment_results = {}  # Store assessment results locally
    self.administered_questionnaire_ids = set()  # Track to prevent duplicates

    print(f"DEBUG __init__: Initializing ReverieServer with preserve_origin_state={preserve_origin_state}")
    print(f"DEBUG __init__: Working dir: {self.working_dir}")
    print(f"DEBUG __init__: Simulation name: {self.simulation_name}")
 
    
    # FORKING FROM A PRIOR SIMULATION:
    # <fork_sim_code> indicates the simulation we are forking from. 
    # Interestingly, all simulations must be forked from some initial 
    # simulation, where the first simulation is "hand-crafted".
    self.fork_sim_code = fork_sim_code
    fork_folder = f"{fs_storage}/{self.fork_sim_code}"

    # <sim_code> indicates our current simulation. The first step here is to 
    # copy everything that's in <fork_sim_code>, but edit its 
    # reverie/meta/json's fork variable. 
    self.sim_code = sim_code
    sim_folder = f"{fs_storage}/{self.sim_code}"
    copyanything(fork_folder, sim_folder)

    with open(f"{sim_folder}/reverie/meta.json") as json_file:  
      reverie_meta = json.load(json_file)

    with open(f"{sim_folder}/reverie/meta.json", "w") as outfile: 
      reverie_meta["fork_sim_code"] = fork_sim_code
      outfile.write(json.dumps(reverie_meta, indent=2))
    
    
    print(f"DEBUG: Loading simulation state from meta.json: {reverie_meta}")

    # LOADING REVERIE'S GLOBAL VARIABLES
    # The start datetime of the Reverie: 
    # <start_datetime> is the datetime instance for the start datetime of 
    # the Reverie instance. Once it is set, this is not really meant to 
    # change. It takes a string date in the following example form: 
    # "June 25, 2022"
    # e.g., ...strptime(June 25, 2022, "%B %d, %Y")
    #self.start_time = datetime.datetime.strptime(
    #                    f"{reverie_meta['start_date']}, 00:00:00",  
    #                    "%B %d, %Y, %H:%M:%S")
    # <curr_time> is the datetime instance that indicates the game's current
    # time. This gets incremented by <sec_per_step> amount everytime the world
    # progresses (that is, everytime curr_env_file is recieved). 
    #self.curr_time = datetime.datetime.strptime(reverie_meta['curr_time'], 
    #                                            "%B %d, %Y, %H:%M:%S")
    
    
    # CRITICAL TIME HANDLING SECTION:
    # Get the time from the fork simulation
    fork_time = datetime.datetime.strptime(reverie_meta['curr_time'], "%B %d, %Y, %H:%M:%S")
    print(f"DEBUG __init__: Fork time from meta.json: {fork_time}")
    
    # Always initialize start_time from meta
    self.start_time = datetime.datetime.strptime(
                      f"{reverie_meta['start_date']}, 00:00:00",  
                      "%B %d, %Y, %H:%M:%S")
    
    # Set current time based on preserve_origin_state flag
    if self.preserve_origin_state:
        # Use the time from the forked simulation directly
        self.curr_time = fork_time
        print(f"DEBUG __init__: PRESERVING ORIGIN TIME: {self.curr_time}")
    else:
        # For clean start, use the start time
        self.curr_time = self.start_time
        print(f"DEBUG __init__: USING START TIME: {self.curr_time}")
      
    
    
    # <sec_per_step> denotes the number of seconds in game time that each 
    # step moves foward. 
    self.sec_per_step = reverie_meta['sec_per_step']
    
    # <maze> is the main Maze instance. Note that we pass in the maze_name
    # (e.g., "double_studio") to instantiate Maze. 
    # e.g., Maze("double_studio")
    self.block_remaps = reverie_meta['block_remaps'] if 'block_remaps' in reverie_meta else None
    self.maze = Maze(reverie_meta['maze_name'], self.block_remaps)
    
    # <step> denotes the number of steps that our game has taken. A step here
    # literally translates to the number of moves our personas made in terms
    # of the number of tiles. 
    self.step = reverie_meta['step']

    # SETTING UP PERSONAS IN REVERIE
    # <personas> is a dictionary that takes the persona's full name as its 
    # keys, and the actual persona instance as its values.
    # This dictionary is meant to keep track of all personas who are part of
    # the Reverie instance. 
    # e.g., ["Isabella Rodriguez"] = Persona("Isabella Rodriguezs")
    self.personas = dict()
    # <personas_tile> is a dictionary that contains the tile location of
    # the personas (!-> NOT px tile, but the actual tile coordinate).
    # The tile take the form of a set, (row, col). 
    # e.g., ["Isabella Rodriguez"] = (58, 39)
    self.personas_tile = dict()
    
    # # <persona_convo_match> is a dictionary that describes which of the two
    # # personas are talking to each other. It takes a key of a persona's full
    # # name, and value of another persona's full name who is talking to the 
    # # original persona. 
    # # e.g., dict["Isabella Rodriguez"] = ["Maria Lopez"]
    # self.persona_convo_match = dict()
    # # <persona_convo> contains the actual content of the conversations. It
    # # takes as keys, a pair of persona names, and val of a string convo. 
    # # Note that the key pairs are *ordered alphabetically*. 
    # # e.g., dict[("Adam Abraham", "Zane Xu")] = "Adam: baba \n Zane:..."
    # self.persona_convo = dict()


    # Initialize the experiment scheduler
    self.current_step = 0
    
    # Load experiment configurations including events and questionnaires
    #experiment_scheduler.load_from_config(self.exp_config)
    
    
    # Loading in all personas. 
    init_env_file = f"{sim_folder}/environment/{str(self.step)}.json"
    init_env = json.load(open(init_env_file))
    for persona_name in reverie_meta['persona_names']: 
      persona_folder = f"{sim_folder}/personas/{persona_name}"
      p_x = init_env[persona_name]["x"]
      p_y = init_env[persona_name]["y"]
      curr_persona = Persona(persona_name, persona_folder)

      self.personas[persona_name] = curr_persona
      self.personas_tile[persona_name] = (p_x, p_y)
      self.maze.tiles[p_y][p_x]["events"].add(curr_persona.scratch
                                              .get_curr_event_and_desc())

    # REVERIE SETTINGS PARAMETERS:  
    # <server_sleep> denotes the amount of time that our while loop rests each
    # cycle; this is to not kill our machine. 
    self.server_sleep = 0.1

    # SIGNALING THE FRONTEND SERVER: 
    # curr_sim_code.json contains the current simulation code, and
    # curr_step.json contains the current step of the simulation. These are 
    # used to communicate the code and step information to the frontend. 
    # Note that step file is removed as soon as the frontend opens up the 
    # simulation. 
    curr_sim_code = dict()
    curr_sim_code["sim_code"] = self.sim_code
    with open(f"{fs_temp_storage}/curr_sim_code.json", "w") as outfile: 
      outfile.write(json.dumps(curr_sim_code, indent=2))
    
    curr_step = dict()
    curr_step["step"] = self.step
    with open(f"{fs_temp_storage}/curr_step.json", "w") as outfile: 
      outfile.write(json.dumps(curr_step, indent=2))
  
    
    
  def set_experiment_config(self, config):
    """
    Set the experiment configuration after initialization
    
    Args:
        config: Dictionary with experiment configuration
        
    Returns:
        self (for method chaining)
    """
    print(f"DEBUG set_experiment_config: Called with preserve_origin_state={self.preserve_origin_state}")
    print(f"DEBUG set_experiment_config: Current time before config: {self.curr_time}")
    

    if "working_dir" in config:
        self.experiment_dir = Path(config["working_dir"])

    self.exp_config = config
    
    # Initialize logger with simulation name from config
    if "simulation_name" in config:
        self.logger = SimulationLogger(config["simulation_name"])
    
    """Set the experiment configuration after initialization"""
    print(f"DEBUG set_experiment_config: Called with preserve_origin_state={self.preserve_origin_state}")
    print(f"DEBUG set_experiment_config: Current time before config: {self.curr_time}")
    
    self.exp_config = config
    
    # Initialize logger with simulation name from config
    if "simulation_name" in config:
        self.logger = SimulationLogger(config["simulation_name"])
    
    # CRITICAL TIME HANDLING
    # Only modify times if not preserving origin state
    if not self.preserve_origin_state:
        
        self.step = 0
        print(f"DEBUG: Fresh simulation starting from step {self.step}")
        
        if "start_date" in config:
            # Parse the start date from config
            new_start_time = datetime.datetime.strptime(
                f"{config['start_date']}, 00:00:00",  
                "%B %d, %Y, %H:%M:%S"
            )
            
            # Add start time if provided
            if "start_time" in config:
                hours, minutes = map(int, config["start_time"].split(":"))
                new_start_time = new_start_time.replace(hour=hours, minute=minutes)
            
            # Update start_time
            self.start_time = new_start_time
            
            # IMPORTANT: Only update curr_time for fresh simulations
            self.curr_time = new_start_time
            print(f"DEBUG set_experiment_config: Updated times for fresh simulation: {self.curr_time}")
    else:
        print(f"DEBUG set_experiment_config: Preserving origin times - curr_time: {self.curr_time}")
        print(f"DEBUG: Experiment starting from step {self.step}")
    
    # VALIDATE EXPERIMENT RESULTS PATH - REQUIRED
    
    # VALIDATE AND SET WORKING DIRECTORY AND SIMULATION INFO
    if "working_dir" in config and "simulation_name" in config:
        self.working_dir = Path(config["working_dir"])
        self.simulation_name = config["simulation_name"]
        
        # Validate that the working directory exists
        if not self.working_dir.exists():
            raise FileNotFoundError(
                f"Working directory does not exist: {self.working_dir}. "
                f"Please ensure the working directory is created before starting the simulation."
            )
        
        # Construct the experiment directory path
        self.experiment_dir = Path(self.working_dir)
        #self.experiment_dir = self.working_dir / self.simulation_name
        if not self.experiment_dir.exists():
            raise FileNotFoundError(
                f"Experiment directory does not exist: {self.experiment_dir}. "
                f"Please ensure the experiment folder structure is created before starting the simulation."
            )
        
        print(f"✓ Validated working directory: {self.working_dir}")
        print(f"✓ Validated experiment directory: {self.experiment_dir}")
    else:
        raise ValueError(
            "working_dir and simulation_name are required in config. "
            "Please provide both the working directory path and simulation name."
        )
    
    # Extract simulation type
    if "simulation_type" in config:
        self.simulation_type = config["simulation_type"]
    else:
        raise ValueError("simulation_type is required in config.")
    
        
    # Set up steps per hour if provided
    if "steps_per_hour" in config:
        # Calculate seconds per step based on steps per hour
        steps_per_hour = config["steps_per_hour"]
        self.sec_per_step = int(3600 / steps_per_hour)
    
    # Set up scheduled events based on step numbers instead of times
    self.scheduled_events = []
    self.next_event_idx = 0
    
    if 'timed_events' in config:
        for event in config['timed_events']:
            if "step" in event:
                # Store the step number in the event
                self.scheduled_events.append(event)
    
    # Set up scheduled questionnaires
    self.scheduled_questionnaires = []
    self.last_questionnaire_time = {}
    self.administered_questionnaires = set()
    
    if 'questionnaires' in config:
        for q_config in config['questionnaires']:
            # Process step-based questionnaires
            if "offset_steps" in q_config and "frequency_steps" in q_config:
                for agent in q_config['target_agents']:
                    self.scheduled_questionnaires.append({
                        'name': q_config['name'],
                        'agent': agent,
                        'offset_steps': q_config['offset_steps'],
                        'frequency_steps': q_config['frequency_steps']
                    })
                    print(f"Scheduled {q_config['name']} for {agent} at step offset {q_config['offset_steps']}")
    
    return self
  

  def check_scheduled_events(self):
        """Check for scheduled events at the current step"""
        
        print(f"🔍 STEP DEBUG: Current step={self.step}, Questionnaires in config: {[q.get('step') for q in self.exp_config.get('questionnaires', [])]}")
        print(f"🔍 STEP DEBUG: Current step={self.step}, Questionnaires scheduled at steps: {[q.get('step') for q in self.exp_config.get('questionnaires', [])]}")

        # DEBUG: Track how many times this method is called
        if not hasattr(self, '_debug_call_tracker'):
            self._debug_call_tracker = {}
        
        call_key = f"step_{self.step}"
        if call_key not in self._debug_call_tracker:
            self._debug_call_tracker[call_key] = 0
        
        self._debug_call_tracker[call_key] += 1
        
        print(f"\n🔍 DEBUG: check_scheduled_events() called {self._debug_call_tracker[call_key]} times for step {self.step}")
        
                
        # DEBUG: Show what's in the config
        questionnaires = self.exp_config.get('questionnaires', [])
        step_questionnaires = [q for q in questionnaires if q.get("step") == self.step]
        
        print(f"📋 Total questionnaires in config: {len(questionnaires)}")
        print(f"📋 Questionnaires for step {self.step}: {len(step_questionnaires)}")
        
        if step_questionnaires:
            print("📋 Step questionnaires:")
            for i, q in enumerate(step_questionnaires):
                print(f"  {i+1}. {q}")
        
        # If this is being called multiple times, show the call stack
        if self._debug_call_tracker[call_key] > 1:
            print(f"⚠️  WARNING: This is call #{self._debug_call_tracker[call_key]} for step {self.step}!")
            print("📍 Call stack:")
            import traceback
            traceback.print_stack(limit=5)
        
        print() # Empty line for readability
        
        # Continue with your existing logic below...
        events_to_process = []
        
        debug_logger.info(f"=== CHECKING EVENTS FOR STEP {self.step} ===")
        debug_logger.info(f"exp_config questionnaires = {self.exp_config.get('questionnaires', [])}")
    
        print(f"DEBUG: Checking events for step {self.step}")
        
        # Check for questionnaires scheduled at specific steps
        questionnaires_found = 0
        for config_item in self.exp_config.get("questionnaires", []):
            if config_item.get("step") == self.step:  # Exact step match
                questionnaires_found += 1
                print(f"DEBUG: Found questionnaire {config_item['name']} scheduled for step {self.step}")
                # Create questionnaire event
                events_to_process.append({
                    "type": "questionnaire",
                    "name": config_item["name"],
                    "target_agents": config_item["target_agents"],
                    "step": config_item["step"]
                })
    
        debug_logger.info(f"Found {questionnaires_found} questionnaires for step {self.step}")
        debug_logger.info(f"Total events to process: {len(events_to_process)}")
        
        for config_item in self.exp_config.get("questionnaires", []):
            if config_item.get("step") == self.step:
                questionnaires_found += 1
                print(f"DEBUG: Found questionnaire {config_item['name']} at step {self.step}")


        # Check if any one-time events should trigger at this step
        while self.next_event_idx < len(self.scheduled_events):
            event = self.scheduled_events[self.next_event_idx]
            
            if "step" in event and event["step"] <= self.step:
                events_to_process.append(event)
                self.next_event_idx += 1
            else:
                break
        
        debug_logger.info(f"=== FINISHED CHECKING EVENTS FOR STEP {self.step} ===")
        
        # Process all events
        for event in events_to_process:
            if event["type"] == "questionnaire":
                # Process for each target agent
                for agent in event.get("target_agents", []):
                    agent_event = {
                        "type": "questionnaire",
                        "name": event["name"],
                        "target": agent,
                        "step": event.get("step", self.step)
                    }
                    print(f"DEBUG: About to call _administer_questionnaire with: {agent_event}")
                    self._administer_questionnaire(agent_event)
                    print(f"DEBUG: Returned from _administer_questionnaire")
            else:
                self._process_event(event)

  


  def _administer_questionnaire(self, event):
    """Administer a questionnaire to an agent"""
    print(f"DEBUG: _administer_questionnaire called with event: {event}")
    
    agent_name = event["target"]
    questionnaire_name = event["name"]
    
    print(f"DEBUG: Administering {questionnaire_name} to {agent_name}")
    
    # Create unique ID to prevent duplicate administration
    unique_id = f"{agent_name}_{questionnaire_name}_{self.step}_{self.curr_time.strftime('%Y%m%d_%H%M%S')}"
    
    if unique_id in self.administered_questionnaire_ids:
        debug_logger.info(f"Questionnaire {unique_id} already administered, skipping")
        print(f"DEBUG: Questionnaire {unique_id} already administered, skipping")
        return
    
    self.administered_questionnaire_ids.add(unique_id)
    
    print(f"DEBUG: Checking if {agent_name} exists in personas: {agent_name in self.personas}")
    
    if agent_name in self.personas:
        persona = self.personas[agent_name]
        print(f"DEBUG: Found persona {agent_name}, calling assess_mental_health")
        
        try:
            result = assess_mental_health(persona, questionnaire_name, self.curr_time)
            print(f"DEBUG: assess_mental_health returned: {result is not None}")
            
            # SAVE DIRECTLY TO EXPERIMENT FOLDER
            self._save_assessment_result_to_file(agent_name, questionnaire_name, result)
            print(f"DEBUG: Called _save_assessment_result_to_file")
            
        except Exception as e:
            print(f"DEBUG ERROR in _administer_questionnaire: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"DEBUG: Agent {agent_name} NOT found in personas")
        print(f"DEBUG: Available personas: {list(self.personas.keys())}")
        

  def _save_assessment_result_to_file(self, agent_name, questionnaire_name, result):
    """
    Save assessment result directly to the experiment folder structure
    AND to SimulationManager centralized logs if available
    
    Args:
        agent_name: Name of the agent being assessed
        questionnaire_name: Name of the questionnaire (PHQ-9, GAD-7, etc.)
        result: Assessment result dictionary
    """
    try:
        print(f"DEBUG: Starting to save assessment for {agent_name}")
        print(f"DEBUG: self.experiment_dir = {self.experiment_dir}")
        print(f"DEBUG: self.simulation_type = {self.simulation_type}")
    
        import json
        import datetime
        from pathlib import Path
        
        # Save to SimulationManager centralized logs first (if available)
        self._save_to_simulation_manager_logs(agent_name, questionnaire_name, result)
        
        # Construct the path: working_dir/simulation_name/simulation_type_simulation/agent_name/assessment_results
        sim_type_mapping = {
            "baseline": "baseline_simulation",
            "trauma_therapy": "trauma_therapy_simulation",
            "trauma_only": "trauma_only_simulation", 
            "control": "control_simulation",
            "experiment": "experiment_simulation"  # Keep for backward compatibility
        }
        
        simulation_folder = sim_type_mapping.get(self.simulation_type, f"{self.simulation_type}_simulation")
        safe_agent_name = agent_name.replace(" ", "_")
        
        # Use the experiment_dir that was set in set_experiment_config
        agent_dir = self.experiment_dir / simulation_folder / safe_agent_name / "assessment_results"
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp and simulation info
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds
        filename = f"{questionnaire_name}_{self.simulation_type}_{timestamp}_step{self.step}.json"
        filepath = agent_dir / filename
        
        # Ensure unique filename
        counter = 1
        while filepath.exists():
            filename = f"{questionnaire_name}_{self.simulation_type}_{timestamp}_step{self.step}_{counter}.json"
            filepath = agent_dir / filename
            counter += 1
        
        # Save the assessment result
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        debug_logger.info(f"Saved assessment result to: {filepath}")
        print(f"✓ Saved {questionnaire_name} assessment for {agent_name} to: {filepath}")
        
        # ALSO copy the file to SimulationManager central location
        self._copy_assessment_to_central_location(filepath, agent_name, questionnaire_name)
        
    except Exception as e:
        debug_logger.error(f"ERROR saving assessment result to file: {e}")
        import traceback
        debug_logger.error(traceback.format_exc())
        print(f"✗ Failed to save assessment result for {agent_name}: {e}")
        raise

  def _save_to_simulation_manager_logs(self, agent_name, questionnaire_name, result):
    """
    Save assessment result to SimulationManager centralized logs
    """
    try:
        # Try to import and use SimulationManager
        from simulation_manager import simulation_manager
        
        # Get the current simulation name
        sim_name = getattr(self, 'sim_code', None)
        if not sim_name:
            print(f"DEBUG: No sim_code found, skipping SimulationManager logging")
            return
        
        # Get centralized logger
        logger = simulation_manager.get_logger(sim_name)
        
        # Extract memories used from debug_info if available
        memories_used = []
        if 'debug_info' in result:
            memories_used = [
                f"Events: {result['debug_info'].get('num_events', 0)}",
                f"Thoughts: {result['debug_info'].get('num_thoughts', 0)}"
            ]
        
        # Extract scores from responses
        scores = {}
        total_score = 0
        if 'responses' in result:
            for item, response in result['responses'].items():
                if isinstance(response, dict) and 'score' in response:
                    scores[f"item_{item}"] = response['score']
                    total_score += response['score']
        scores['total_score'] = total_score
        
        # Log to centralized assessments log
        logger.log_assessment(
            step=self.step,
            agent=agent_name,
            questionnaire=questionnaire_name,
            memories_used=memories_used,
            responses=result.get('responses', {}),
            scores=scores
        )
        
        print(f"✓ Logged assessment to SimulationManager: {sim_name}")
        
    except ImportError:
        print(f"DEBUG: SimulationManager not available, skipping centralized logging")
    except Exception as e:
        print(f"DEBUG: Failed to log to SimulationManager: {e}")
        # Don't raise - this is optional enhancement

  def _copy_assessment_to_central_location(self, source_filepath, agent_name, questionnaire_name):
    """
    Copy assessment file to SimulationManager central location
    """
    try:
        from simulation_manager import simulation_manager
        import shutil
        from pathlib import Path
        
        # Get current simulation name
        sim_name = getattr(self, 'sim_code', None)
        if not sim_name:
            return
        
        # Create central assessment directory
        sim_dir = simulation_manager.simulations_root / sim_name
        central_assessment_dir = sim_dir / "assessment_results" / agent_name.replace(" ", "_")
        central_assessment_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        filename = Path(source_filepath).name
        central_filepath = central_assessment_dir / filename
        shutil.copy2(source_filepath, central_filepath)
        
        print(f"✓ Copied assessment to central location: {central_filepath}")
        
    except Exception as e:
        print(f"DEBUG: Failed to copy assessment to central location: {e}")

  def _copy_logs_to_central_location(self):
    """
    Copy various log files to SimulationManager central location
    Called at end of simulation
    """
    try:
        from simulation_manager import simulation_manager
        import shutil
        from pathlib import Path
        import glob
        
        sim_name = getattr(self, 'sim_code', None)
        if not sim_name:
            return
        
        sim_dir = simulation_manager.simulations_root / sim_name
        central_logs_dir = sim_dir / "all_logs"
        central_logs_dir.mkdir(exist_ok=True)
        
        # Copy cost logs (find the most recent ones)
        cost_logs_dir = Path(__file__).parent / "cost-logs"
        if cost_logs_dir.exists():
            # Find cost logs from today
            import datetime
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            cost_files = list(cost_logs_dir.glob(f"*{today}*.json"))
            
            for cost_file in cost_files[-2:]:  # Copy last 2 cost files
                shutil.copy2(cost_file, central_logs_dir / f"cost_log_{cost_file.name}")
                print(f"✓ Copied cost log: {cost_file.name}")
        
        # Copy debug logs  
        debug_log = Path(__file__).parent / "assessment_debug.log"
        if debug_log.exists():
            shutil.copy2(debug_log, central_logs_dir / "assessment_debug.log")
            print(f"✓ Copied assessment debug log")
        
        sim_debug_log = Path(__file__).parent / "simulation_debug.log"
        if sim_debug_log.exists():
            shutil.copy2(sim_debug_log, central_logs_dir / "simulation_debug.log")
            print(f"✓ Copied simulation debug log")
        
        # Copy simulation-specific logs
        sim_logs_dir = Path(__file__).parent / "logs" / sim_name
        if sim_logs_dir.exists():
            shutil.copytree(sim_logs_dir, central_logs_dir / "simulation_logs", dirs_exist_ok=True)
            print(f"✓ Copied simulation-specific logs")
        
        # NEW: Copy main events.jsonl that contains therapy sessions
        main_events_log = Path(__file__).parent / "logs" / "events.jsonl"
        if main_events_log.exists():
            # Ensure simulation_logs directory exists
            sim_logs_dest = central_logs_dir / "simulation_logs"
            sim_logs_dest.mkdir(exist_ok=True)
            
            # Copy the main events file
            shutil.copy2(main_events_log, sim_logs_dest / "main_events.jsonl")
            print(f"✓ Copied main events.jsonl (contains therapy sessions)")
        
        # NEW: Copy any therapy-specific log directories
        logs_base_dir = Path(__file__).parent / "logs"
        if logs_base_dir.exists():
            therapy_log_patterns = [
                "trauma_therapy_simulation",
                "*therapy*",
                "*trauma*"
            ]
            
            for pattern in therapy_log_patterns:
                matching_dirs = list(logs_base_dir.glob(pattern))
                for therapy_dir in matching_dirs:
                    if therapy_dir.is_dir():
                        therapy_events_file = therapy_dir / "events.jsonl"
                        if therapy_events_file.exists():
                            # Ensure destination directory exists
                            therapy_dest_dir = central_logs_dir / "therapy_logs" / therapy_dir.name
                            therapy_dest_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Copy the therapy events file
                            shutil.copy2(therapy_events_file, therapy_dest_dir / "events.jsonl")
                            print(f"✓ Copied therapy events from {therapy_dir.name}")
        
    except Exception as e:
        print(f"DEBUG: Failed to copy logs to central location: {e}")

  def _copy_simulation_data_to_central_location(self):
    """
    Copy simulation data (movement, environment, personas) to central location
    """
    try:
        from simulation_manager import simulation_manager
        import shutil
        from pathlib import Path
        
        sim_name = getattr(self, 'sim_code', None)
        if not sim_name:
            return
        
        # Find the source simulation data  
        # Path should be: agentic_collab/environment/frontend_server/storage/sim_name
        # Current file is: agentic_collab/reverie/backend_server/reverie.py
        # So we need: ../../environment/frontend_server/storage/sim_name
        storage_path = Path(__file__).parent.parent.parent / "environment" / "frontend_server" / "storage" / sim_name
        if not storage_path.exists():
            print(f"DEBUG: Simulation storage not found: {storage_path}")
            return
        
        # Destination in SimulationManager
        sim_dir = simulation_manager.simulations_root / sim_name
        central_data_dir = sim_dir / "simulation_data"
        
        # Copy movement files
        movement_source = storage_path / "movement"
        if movement_source.exists():
            movement_dest = central_data_dir / "movement"
            if movement_dest.exists():
                shutil.rmtree(movement_dest)
            shutil.copytree(movement_source, movement_dest)
            print(f"✓ Copied movement data ({len(list(movement_source.glob('*.json')))} files)")
        
        # Copy environment files
        environment_source = storage_path / "environment"
        if environment_source.exists():
            environment_dest = central_data_dir / "environment"
            if environment_dest.exists():
                shutil.rmtree(environment_dest)
            shutil.copytree(environment_source, environment_dest)
            print(f"✓ Copied environment data ({len(list(environment_source.glob('*.json')))} files)")
        
        # Copy personas data
        personas_source = storage_path / "personas"
        if personas_source.exists():
            personas_dest = central_data_dir / "personas"
            if personas_dest.exists():
                shutil.rmtree(personas_dest)
            shutil.copytree(personas_source, personas_dest)
            print(f"✓ Copied personas data")
        
        # Copy reverie metadata
        reverie_source = storage_path / "reverie"
        if reverie_source.exists():
            reverie_dest = central_data_dir / "reverie"
            if reverie_dest.exists():
                shutil.rmtree(reverie_dest)
            shutil.copytree(reverie_source, reverie_dest)
            print(f"✓ Copied reverie metadata")
        
    except Exception as e:
        print(f"DEBUG: Failed to copy simulation data to central location: {e}")


  def _process_event(self, event):
        """Process a scheduled event"""
        event_type = event.get("type", "")
        target = event.get("target", "")
        description = event.get("description", "")
        
        if target in self.personas:
            persona = self.personas[target]
            
            print(f"Processing {event_type} event for {target} at step {self.step}")
            print(f"Event details: {event}")
            
            # ADD THIS CHECK FOR THERAPY EVENTS
            if event_type == "therapy":
                print(f"🔍 DEBUG: Therapy event detected, calling _conduct_therapy_session")
                self._conduct_therapy_session(persona, target)
                return  # Important: return early to avoid trauma processing

            # Use proper poignancy scores
            if event_type == "negative":
                   poignancy_score = 9  # Very high for trauma (was 0.9)
            else:
                   poignancy_score = 5  # Moderate for other events              
             

            # FOLLOW THE SAME PATTERN AS perceive.py
            desc_embedding_in = description
            
            # Check if embedding already exists, otherwise generate it
            if desc_embedding_in in persona.a_mem.embeddings:
                event_embedding = persona.a_mem.embeddings[desc_embedding_in]
            else:
                from persona.prompt_template.gpt_structure import get_embedding
                event_embedding = get_embedding(desc_embedding_in)
            
            # Create embedding_pair exactly like perceive.py does
            embedding_pair = (desc_embedding_in, event_embedding)
            
            # Set proper keywords for trauma
            if event_type == "negative":
                keywords = {
                    "negative", "scheduled_event", "trauma", "loss", "grief", 
                    "emotional", "significant", "mental_health", "depression", "distress"
                }
            else:
                keywords = {event_type, "scheduled_event"}
            
            # Add the event using the same method as normal events
            persona.a_mem.add_event(
                created=self.curr_time,
                expiration=self.curr_time + datetime.timedelta(days=30),
                s=target,
                p="experienced",
                o=event_type + "_event",
                description=description,
                keywords=keywords,
                poignancy=poignancy_score,  # High poignancy for trauma
                embedding_pair=embedding_pair,  # Proper embedding pair
                filling=[]
            )
            
            print(f"Scheduled {event_type} event triggered for {target}: {description}")
              
              # Log event
            if self.logger:
                  self.logger.log_event(target, self.curr_time, "scheduled_event", {
                      "type": event_type,
                      "description": description
                  })
                  self.logger.save_all()
                  
            print(f"Added trauma event with embedding key: '{desc_embedding_in}'")
            
#----------------------------------------------------------------------------
# Code for therapy sessions
#---------------------------------------------------------------------------- 
   

  def _conduct_therapy_session(self, persona, agent_name):
    """Conduct a therapy session via phone call using GPT-generated therapist responses"""
    print(f"Starting therapy session for {agent_name} at step {self.step}")
    
    try:
        # Import the conversation functions
        from persona.cognitive_modules.converse import generate_one_utterance, generate_summarize_agent_relationship
        from persona.cognitive_modules.retrieve import new_retrieve
        from persona.prompt_template.run_gpt_prompt import run_gpt_prompt_generate_next_convo_line
        
        # Create a more complete virtual therapist persona
        class VirtualTherapist:
            def __init__(self):
                def get_str_iss(self=None):
                    return "Dr. Sarah Thompson is a licensed clinical psychologist specializing in trauma therapy and grief counseling."
                
                self.scratch = type('obj', (object,), {
                    'name': 'Dr. Sarah Thompson',
                    'act_description': 'conducting a therapy session over the phone',
                    'curr_time': None,
                    'get_str_iss': get_str_iss  # ← Use a proper function
                })()
            
                # Add therapist background for better context
                self.therapist_background = (
                    "Dr. Sarah Thompson is a licensed clinical psychologist with 15 years of experience "
                    "specializing in trauma therapy, grief counseling, and cognitive behavioral therapy. "
                    "She is warm, empathetic, and uses evidence-based therapeutic techniques. "
                    "She asks thoughtful questions, validates emotions, and helps clients develop coping strategies."
                )
        
        virtual_therapist = VirtualTherapist()
        
        # Initialize conversation
        curr_chat = []
        therapy_duration = 8
        
        print(f"📞 {agent_name} receives a call from Dr. Sarah Thompson for their scheduled therapy session")
        
        # Therapist opens the session
        opening_message = "Hello, how are you feeling today? I'm glad we could connect for our session."
        curr_chat.append([virtual_therapist.scratch.name, opening_message])
        print(f"Dr. Thompson: {opening_message}")
        
        # Therapy session conversation loop
        for i in range(therapy_duration):
            # Patient speaks
            if i == 0:
                focal_points = ["therapy", "emotional well-being", "current feelings", "recent experiences"]
            else:
                # Use recent conversation context
                recent_chat = []
                for chat_turn in curr_chat[-4:]:  # Last 4 exchanges
                    recent_chat.append(": ".join(chat_turn))
                focal_points = ["therapy session", "emotional support"] + recent_chat
                
            retrieved = new_retrieve(persona, focal_points, 25)
            
            # Generate patient's response
            utt, end = generate_one_utterance(
                self.maze, 
                persona, 
                virtual_therapist, 
                retrieved, 
                curr_chat
            )
            
            curr_chat.append([persona.scratch.name, utt])
            print(f"{persona.scratch.name}: {utt}")
            
            if end and i > 2:  # Don't end too early
                break
            
            # Generate therapist's response
            therapist_response = self._generate_therapist_response(
                virtual_therapist, 
                persona, 
                curr_chat, 
                i
            )
            
            curr_chat.append([virtual_therapist.scratch.name, therapist_response])
            print(f"Dr. Thompson: {therapist_response}")
        
        # ✅ CORRECT: Closing and memory addition AFTER the loop
        closing_message = self._generate_therapy_closing(virtual_therapist, persona, curr_chat)
        curr_chat.append([virtual_therapist.scratch.name, closing_message])
        print(f"Dr. Thompson: {closing_message}")
        
        # Extract specific therapeutic content and coping strategies from the conversation
        therapeutic_insights = self._extract_therapeutic_insights(curr_chat, agent_name)
        
        # Add multiple specific memory events for different therapeutic aspects
        from persona.prompt_template.gpt_structure import get_embedding
        
        for insight in therapeutic_insights:
            desc_embedding_in = insight["description"]
            
            if desc_embedding_in in persona.a_mem.embeddings:
                event_embedding = persona.a_mem.embeddings[desc_embedding_in]
            else:
                event_embedding = get_embedding(desc_embedding_in)
            
            embedding_pair = (desc_embedding_in, event_embedding)
            
            persona.a_mem.add_event(
                created=self.curr_time,
                expiration=self.curr_time + datetime.timedelta(days=30),
                s=agent_name,
                p=insight["predicate"],
                o=insight["object"],
                description=insight["description"],
                keywords=insight["keywords"],
                poignancy=insight["poignancy"],
                embedding_pair=embedding_pair,
                filling=[]
            )
        
        print(f"✓ Added {len(therapeutic_insights)} specific therapeutic memories for {agent_name}")
        
        # Log the complete therapy session
        if self.logger:
            self.logger.log_event(agent_name, self.curr_time, "therapy_session", {
                "type": "phone_call",
                "therapist": "Dr. Sarah Thompson",
                "duration": f"{len(curr_chat)}_exchanges",
                "conversation": curr_chat
            })
        
        # NEW: Also log directly to SimulationManager centralized location
        self._log_therapy_session_to_central_location(agent_name, curr_chat)
        
        # Extract specific therapeutic content and coping strategies from the conversation
        print(f"🧠 Extracting therapeutic insights for {agent_name}...")
        therapeutic_insights = self._extract_therapeutic_insights(curr_chat, agent_name)
        
        # Add multiple specific memory events for different therapeutic aspects
        from persona.prompt_template.gpt_structure import get_embedding
        
        insights_added = 0
        for insight in therapeutic_insights:
            try:
                desc_embedding_in = insight["description"]
                
                if desc_embedding_in in persona.a_mem.embeddings:
                    event_embedding = persona.a_mem.embeddings[desc_embedding_in]
                else:
                    event_embedding = get_embedding(desc_embedding_in)
                
                embedding_pair = (desc_embedding_in, event_embedding)
                
                # Create detailed memory event
                created = persona.a_mem.add_memory(
                    desc_embedding_in,
                    self.curr_time,
                    embedding_pair,
                    poignancy=insight.get("poignancy", 7),
                    keywords=set(insight.get("keywords", [])),
                    filling=insight.get("object", "therapeutic_insight")
                )
                
                if created:
                    insights_added += 1
                    print(f"  ✓ Added therapeutic insight: {desc_embedding_in[:60]}...")
                    
            except Exception as e:
                print(f"  ✗ Failed to add insight: {e}")
        
        print(f"✓ Therapy session completed for {agent_name} - {insights_added} insights extracted")
        return curr_chat
        
    except Exception as e:
        print(f"✗ Error during therapy session for {agent_name}: {e}")
        import traceback
        traceback.print_exc()
        return []    

  def _log_therapy_session_to_central_location(self, agent_name, curr_chat):
    """
    Log therapy session directly to SimulationManager centralized location
    """
    try:
        from simulation_manager import simulation_manager
        import json
        from pathlib import Path
        
        sim_name = getattr(self, 'sim_code', None)
        if not sim_name:
            return
        
        # Create therapy session log entry
        therapy_log_entry = {
            "agent": agent_name,
            "timestamp": self.curr_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event_type": "therapy_session",
            "details": {
                "type": "phone_call",
                "therapist": "Dr. Sarah Thompson",
                "duration": f"{len(curr_chat)}_exchanges",
                "conversation": curr_chat
            }
        }
        
        # Get centralized logging directory
        sim_dir = simulation_manager.simulations_root / sim_name
        central_logs_dir = sim_dir / "all_logs"
        central_logs_dir.mkdir(exist_ok=True)
        
        # Create simulation_logs subdirectory if it doesn't exist
        sim_logs_dir = central_logs_dir / "simulation_logs"
        sim_logs_dir.mkdir(exist_ok=True)
        
        # Append to centralized events.jsonl file
        central_events_file = sim_logs_dir / "events.jsonl"
        with open(central_events_file, "a", encoding='utf-8') as f:
            f.write(json.dumps(therapy_log_entry, ensure_ascii=False) + "\n")
        
        print(f"✓ Logged therapy session to centralized location: {central_events_file}")
        
    except Exception as e:
        print(f"DEBUG: Failed to log therapy session to central location: {e}")

  def _extract_therapeutic_insights(self, curr_chat, agent_name):
    """
    Extract specific therapeutic content, coping strategies, and insights from therapy conversation
    to create meaningful memory events that can influence future behavior
    """
    try:
        from persona.prompt_template.gpt_structure import ChatGPT_safe_generate_response
        
        # Build conversation text for analysis
        conversation_text = ""
        for speaker, utterance in curr_chat:
            conversation_text += f"{speaker}: {utterance}\n"
        
        # Create prompt to extract therapeutic insights
        extraction_prompt = f"""
        Analyze this therapy session conversation and extract specific therapeutic insights, coping strategies, and behavioral recommendations that the patient learned or should remember.

        Conversation:
        {conversation_text}

        Extract the following types of therapeutic content:
        1. Specific coping strategies mentioned (e.g., "take breathing breaks when overwhelmed")
        2. Behavioral recommendations (e.g., "journal emotions weekly on Sunday evenings")  
        3. Insights about emotional patterns (e.g., "grief triggers happen during busy work moments")
        4. Therapeutic techniques learned (e.g., "use mindfulness body scans during work")
        5. Plans for future sessions or follow-up actions

        For each insight, provide:
        - A specific, actionable description that could influence future behavior
        - The type of insight (coping_strategy, behavioral_plan, emotional_insight, etc.)
        - Keywords for memory retrieval

        Output format (JSON array):
        [
          {{
            "description": "Specific actionable insight or strategy",
            "type": "coping_strategy|behavioral_plan|emotional_insight|therapeutic_technique",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "importance": 1-10
          }}
        ]

        Focus on extracting 3-5 most important insights that could realistically influence the patient's future behavior and decision-making.
        """
        
        # Generate insights using GPT
        response = ChatGPT_safe_generate_response(
            extraction_prompt,
            repeat=3,
            fail_safe_response=[],
            func_validate=lambda resp, **kwargs: True,
            func_clean_up=lambda resp, **kwargs: self._parse_therapeutic_insights_response(resp, agent_name)
        )
        
        return response if response else []
        
    except Exception as e:
        print(f"DEBUG: Failed to extract therapeutic insights: {e}")
        # Fallback: create basic therapy memory
        return [{
            "description": f"{agent_name} had a therapy session with Dr. Sarah Thompson focusing on emotional support and coping strategies",
            "predicate": "participated_in",
            "object": "therapy_session",
            "keywords": {"therapy", "emotional_support", "coping", "Dr_Thompson"},
            "poignancy": 7
        }]

  def _parse_therapeutic_insights_response(self, response, agent_name):
    """Parse GPT response and convert to memory event format"""
    try:
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            insights_data = json.loads(json_match.group())
        else:
            # Fallback parsing
            insights_data = []
        
        # Convert to memory event format
        memory_events = []
        
        for insight in insights_data:
            # Determine predicate and object based on insight type
            insight_type = insight.get("type", "emotional_insight")
            
            if insight_type == "coping_strategy":
                predicate = "learned"
                obj = "coping_strategy"
            elif insight_type == "behavioral_plan":
                predicate = "planned"
                obj = "behavioral_change"
            elif insight_type == "therapeutic_technique":
                predicate = "learned"
                obj = "therapeutic_technique"
            else:
                predicate = "understood"
                obj = "emotional_insight"
            
            # Create keywords set
            keywords = set(insight.get("keywords", []))
            keywords.update({"therapy", "Dr_Thompson", "mental_health", insight_type})
            
            # Calculate poignancy (importance for memory retrieval)
            importance = insight.get("importance", 7)
            poignancy = min(10, max(6, importance))  # Ensure therapeutic content has good retrieval chances
            
            memory_events.append({
                "description": insight["description"],
                "predicate": predicate,
                "object": obj,
                "keywords": keywords,
                "poignancy": poignancy
            })
        
        # Ensure we have at least one memory event
        if not memory_events:
            memory_events.append({
                "description": f"{agent_name} received professional therapeutic support from Dr. Sarah Thompson, focusing on emotional wellbeing and coping strategies",
                "predicate": "received",
                "object": "therapeutic_support",
                "keywords": {"therapy", "emotional_support", "Dr_Thompson", "mental_health"},
                "poignancy": 7
            })
        
        return memory_events
        
    except Exception as e:
        print(f"DEBUG: Failed to parse therapeutic insights: {e}")
        return [{
            "description": f"{agent_name} had a meaningful therapy session with Dr. Sarah Thompson",
            "predicate": "participated_in",
            "object": "therapy_session", 
            "keywords": {"therapy", "Dr_Thompson", "mental_health"},
            "poignancy": 7
        }]

  def _generate_therapist_response(self, therapist, patient, curr_chat, turn_number):
    """Generate a contextually appropriate therapist response using GPT"""
    try:
        from persona.prompt_template.run_gpt_prompt import run_gpt_prompt_generate_next_convo_line
        
        # Build conversation context
        prev_convo = ""
        for row in curr_chat[-6:]:  # Use last 6 exchanges for context
            prev_convo += f'{row[0]}: {row[1]}\n'
        
        # Create therapist context based on session progress
        if turn_number == 0:
            therapist_context = (
                "Dr. Sarah Thompson is beginning a therapy session. She should ask an open-ended question "
                "to understand how the patient is feeling and what they want to discuss today."
            )
        elif turn_number < 3:
            therapist_context = (
                "Dr. Sarah Thompson is in the early part of the session. She should validate the patient's "
                "feelings and ask follow-up questions to better understand their emotional state and recent experiences."
            )
        elif turn_number < 6:
            therapist_context = (
                "Dr. Sarah Thompson is in the middle of the session. She should explore the patient's thoughts "
                "and feelings more deeply, perhaps asking about coping strategies or offering gentle insights."
            )
        else:
            therapist_context = (
                "Dr. Sarah Thompson is toward the end of the session. She should help the patient consolidate "
                "what they've discussed and perhaps suggest practical steps or coping strategies."
            )
        
        # Enhanced therapist description for better GPT responses
        therapist_description = (
            f"{therapist.therapist_background} "
            f"Currently {therapist_context} "
            "She responds with empathy, asks thoughtful questions, and provides professional therapeutic guidance. "
            "Her responses are warm but professional, typically 1-2 sentences long."
        )
        
        # FIXED: Use correct parameter names
        response, debug_info = run_gpt_prompt_generate_next_convo_line(
            therapist,                    # persona
            therapist_description,        # interlocutor_desc  
            prev_convo,                   # prev_convo
            therapist_context,            # retrieved_summary (changed from therapist_context)
            verbose=True                  # Add verbose for debugging
        )
        
        if response and response != "...":  # Check for the fail_safe response
            return response
        else:
            # Fallback responses if GPT fails
            fallbacks = [
                "I understand. Can you tell me more about that?",
                "How did that make you feel?",
                "That sounds very difficult for you.",
                "What thoughts went through your mind when that happened?",
                "How are you coping with these feelings?"
            ]
            return fallbacks[turn_number % len(fallbacks)]
            
    except Exception as e:
        print(f"Error generating therapist response: {e}")
        import traceback
        traceback.print_exc()
        return "I'm here to listen. Please continue." 
  
    
   
  def _generate_therapy_closing(self, therapist, patient, curr_chat):
    """Generate an appropriate closing for the therapy session"""
    try:
        from persona.prompt_template.run_gpt_prompt import run_gpt_prompt_generate_next_convo_line
        
        # Build conversation summary (keep it shorter to avoid issues)
        session_summary = ""
        for row in curr_chat[-6:]:  # Only last 6 exchanges instead of 10
            session_summary += f'{row[0]}: {row[1]}\n'
        
        # Simple, direct prompt
        closing_context = "Dr. Sarah Thompson is ending the therapy session with a warm, professional closing."
        
        therapist_description = "Dr. Sarah Thompson is a therapist ending a session. She provides supportive, brief closings."
        
        response = run_gpt_prompt_generate_next_convo_line(
            therapist,
            therapist_description,
            session_summary,
            closing_context
        )
        
        if response and len(response) > 0:
            return response[0]
        else:
            # Use fallback if GPT fails
            return "Thank you for sharing with me today. Remember to be gentle with yourself, and I'll talk to you again soon."
            
    except Exception as e:
        print(f"Error generating therapy closing: {e}")
        return "Take care of yourself. I'll talk to you again soon."  
    
  def save_assessment_results_to_experiment_path(self):
        """Save all assessment results to the experiment path"""
        if not self.experiment_results_path or not self.assessment_results:
            debug_logger.info("No experiment path or no assessment results to save")
            return
        
        import os
        from pathlib import Path
        
        results_base_path = Path(self.experiment_results_path)
        
        for agent_name, questionnaires in self.assessment_results.items():
            # Create agent directory (replace spaces with underscores)
            safe_agent_name = agent_name.replace(" ", "_")
            agent_dir = results_base_path / safe_agent_name / "assessment_results"
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each questionnaire result
            for questionnaire_name, results in questionnaires.items():
                if results:
                    # Create filename with simulation type and timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{questionnaire_name}_{self.simulation_type}_{timestamp}.json"
                    filepath = agent_dir / filename
                    
                    # Save all results for this questionnaire
                    with open(filepath, 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    debug_logger.info(f"Saved {len(results)} {questionnaire_name} assessments for {agent_name} to {filepath}")

  def save(self): 
      """
      Save all Reverie progress -- this includes Reverie's global state as well
      as all the personas and assessment results.  
    
      INPUT
        None
      OUTPUT 
        None
        * Saves all relevant data to the designated memory directory
      """
      # <sim_folder> points to the current simulation folder.
      sim_folder = f"{fs_storage}/{self.sim_code}"

      # Save Reverie meta information.
      reverie_meta = dict() 
      reverie_meta["fork_sim_code"] = self.fork_sim_code
      reverie_meta["start_date"] = self.start_time.strftime("%B %d, %Y")
      reverie_meta["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")
      reverie_meta["sec_per_step"] = self.sec_per_step
      reverie_meta["maze_name"] = self.maze.maze_name
      reverie_meta["persona_names"] = list(self.personas.keys())
      reverie_meta["step"] = self.step
      reverie_meta["block_remaps"] = self.block_remaps
      reverie_meta_f = f"{sim_folder}/reverie/meta.json"
      with open(reverie_meta_f, "w") as outfile: 
        outfile.write(json.dumps(reverie_meta, indent=2))
    
      # Save the personas.
      for persona_name, persona in self.personas.items(): 
        save_folder = f"{sim_folder}/personas/{persona_name}/bootstrap_memory"
        persona.save(save_folder)
        


  def start_path_tester_server(self): 
    """
    Starts the path tester server. This is for generating the spatial memory
    that we need for bootstrapping a persona's state. 

    To use this, you need to open server and enter the path tester mode, and
    open the front-end side of the browser. 

    INPUT 
      None
    OUTPUT 
      None
      * Saves the spatial memory of the test agent to the path_tester_env.json
        of the temp storage. 
    """
    def print_tree(tree): 
      def _print_tree(tree, depth):
        dash = " >" * depth

        if type(tree) == type(list()): 
          if tree:
            print (dash, tree)
          return 

        for key, val in tree.items(): 
          if key: 
            print (dash, key)
          _print_tree(val, depth+1)
      
      _print_tree(tree, 0)

    # <curr_vision> is the vision radius of the test agent. Recommend 8 as 
    # our default. 
    curr_vision = 8
    # <s_mem> is our test spatial memory. 
    s_mem = dict()

    # The main while loop for the test agent. 
    while (True): 
      try: 
        curr_dict = {}
        tester_file = fs_temp_storage + "/path_tester_env.json"
        if check_if_file_exists(tester_file): 
          with open(tester_file) as json_file: 
            curr_dict = json.load(json_file)
            os.remove(tester_file)
          
          # Current camera location
          curr_sts = self.maze.sq_tile_size
          curr_camera = (int(math.ceil(curr_dict["x"]/curr_sts)), 
                         int(math.ceil(curr_dict["y"]/curr_sts))+1)
          curr_tile_det = self.maze.access_tile(curr_camera)

          # Initiating the s_mem
          world = curr_tile_det["world"]
          if curr_tile_det["world"] not in s_mem: 
            s_mem[world] = dict()

          # Iterating throughn the nearby tiles.
          nearby_tiles = self.maze.get_nearby_tiles(curr_camera, curr_vision)
          for i in nearby_tiles: 
            i_det = self.maze.access_tile(i)
            if (curr_tile_det["sector"] == i_det["sector"] 
                and curr_tile_det["arena"] == i_det["arena"]): 
              if i_det["sector"] != "": 
                if i_det["sector"] not in s_mem[world]: 
                  s_mem[world][i_det["sector"]] = dict()
              if i_det["arena"] != "": 
                if i_det["arena"] not in s_mem[world][i_det["sector"]]: 
                  s_mem[world][i_det["sector"]][i_det["arena"]] = list()
              if i_det["game_object"] != "": 
                if (i_det["game_object"] 
                    not in s_mem[world][i_det["sector"]][i_det["arena"]]):
                  s_mem[world][i_det["sector"]][i_det["arena"]] += [
                                                         i_det["game_object"]]

        # Incrementally outputting the s_mem and saving the json file. 
        print ("= " * 15)
        out_file = fs_temp_storage + "/path_tester_out.json"
        with open(out_file, "w") as outfile: 
          outfile.write(json.dumps(s_mem, indent=2))
        print_tree(s_mem)

      except:
        pass

      time.sleep(self.server_sleep * 10)
     


  def start_server(self, int_counter, headless=False): 
    """
    The main backend server of Reverie. 
    This function retrieves the environment file from the frontend to 
    understand the state of the world, calls on each personas to make 
    decisions based on the world state, and saves their moves at certain step
    intervals. 
    INPUT
      int_counter: Integer value for the number of steps left for us to take
                  in this iteration. 
    OUTPUT 
      None
    """
    print(f"DEBUG start_server: Starting server with preserve_origin_state={self.preserve_origin_state}")
    print(f"DEBUG start_server: Current time: {self.curr_time}, step: {self.step}")
    print(f"DEBUG: Starting simulation at step {self.step}, will run {int_counter} more steps")
    print(f"DEBUG: Final step will be {self.step + int_counter}")

    # <sim_folder> points to the current simulation folder.
    sim_folder = f"{fs_storage}/{self.sim_code}"

    # When a persona arrives at a game object, we give a unique event
    # to that object. 
    # e.g., ('double studio[...]:bed', 'is', 'unmade', 'unmade')
    # Later on, before this cycle ends, we need to return that to its 
    # initial state, like this: 
    # e.g., ('double studio[...]:bed', None, None, None)
    # So we need to keep track of which event we added. 
    # <game_obj_cleanup> is used for that. 
    game_obj_cleanup = dict()

    if self.preserve_origin_state:
        print(f"Continuing simulation from previous state at step {self.step}")
        # Ensure we don't reset any agent mental states when retrieving the environment

    # The main while loop of Reverie. 
    while (True): 
      # Done with this iteration if <int_counter> reaches 0. 
      if int_counter == 0: 
        break

      # Create environment file in headless mode if it doesn't exist
      curr_env_file = f"{sim_folder}/environment/{self.step}.json"
      env_retrieved = False
      new_env = None
      
      # For headless mode, we need to generate environment files
      if headless and not check_if_file_exists(curr_env_file):
          print(f"Creating environment file for step {self.step} in headless mode")
          # Create environment file based on current persona positions
          env_data = {}
          for persona_name, curr_tile in self.personas_tile.items():
              env_data[persona_name] = {
                  "x": curr_tile[0],
                  "y": curr_tile[1],
                  "maze": self.maze.maze_name
              }
          
          # Create the environment directory if it doesn't exist
          env_dir = f"{sim_folder}/environment"
          os.makedirs(env_dir, exist_ok=True)
          
          # Write the environment file
          with open(curr_env_file, "w") as outfile:
              outfile.write(json.dumps(env_data, indent=2))
          
          print(f"Created environment file for step {self.step}")
          env_retrieved = True
          new_env = env_data
      
      # Try to retrieve the environment file if we haven't done so already
      if not env_retrieved:
          try: 
              # Try and save block for robustness of the while loop.
              with open(curr_env_file) as json_file:
                  new_env = json.load(json_file)
                  env_retrieved = True
          except Exception as e: 
              print(f"Error loading environment file for step {self.step}: {e}")
              # If we're in headless mode, we should create the file
              if headless:
                  time.sleep(self.server_sleep)
                  continue  # Try again in the next loop iteration
              else:
                  # In interactive mode, wait for the frontend to create it
                  time.sleep(self.server_sleep)
                  continue  # Try again in the next loop iteration
       
      
      # ---------------------------------------------------------------------
      # START OF SIMULATION STEPS
      # ---------------------------------------------------------------------
      
      # If we have environment data, proceed with the simulation step
      if env_retrieved and new_env is not None: 
          # This is where we go through <game_obj_cleanup> to clean up all 
          # object actions that were used in this cylce. 
          for key, val in game_obj_cleanup.items(): 
              # We turn all object actions to their blank form (with None). 
              self.maze.turn_event_from_tile_idle(key, val)
          # Then we initialize game_obj_cleanup for this cycle. 
          game_obj_cleanup = dict()


          # ---------------------------------------------------------------------
          # Check for scheduled events for this step
          # ---------------------------------------------------------------------

          self.check_scheduled_events()
          
          # We first move our personas in the backend environment to match 
          # the frontend environment. 
          for persona_name, persona in self.personas.items(): 
              # <curr_tile> is the tile that the persona was at previously. 
              curr_tile = self.personas_tile[persona_name]
              # <new_tile> is the tile that the persona will move to right now,
              # during this cycle. 
              new_tile = (new_env[persona_name]["x"], 
                          new_env[persona_name]["y"])

              # We actually move the persona on the backend tile map here. 
              self.personas_tile[persona_name] = new_tile
              self.maze.remove_subject_events_from_tile(persona.name, curr_tile)
              self.maze.add_event_from_tile(persona.scratch
                                          .get_curr_event_and_desc(), new_tile)

              # Now, the persona will travel to get to their destination. *Once*
              # the persona gets there, we activate the object action.
              if not persona.scratch.planned_path:
                  # We add that new object action event to the backend tile map.
                  # At its creation, it is stored in the persona's backend.
                  curr_obj_event_and_desc = freeze(
                      persona.scratch.get_curr_obj_event_and_desc()
                  )
                  game_obj_cleanup[curr_obj_event_and_desc] = new_tile
                  self.maze.add_event_from_tile(
                      curr_obj_event_and_desc,
                      new_tile,
                  )
                  # We also need to remove the temporary blank action for the
                  # object that is currently taking the action.
                  blank = (
                      tuple(persona.scratch.get_curr_obj_event_and_desc())[0],
                      None,
                      None,
                      None,
                  )
                  self.maze.remove_event_from_tile(blank, new_tile)

          # Then we need to actually have each of the personas perceive and
          # move. The movement for each of the personas comes in the form of
          # x y coordinates where the persona will move towards. e.g., (50, 34)
          # This is where the core brains of the personas are invoked.
          movements = {"persona": dict(), "meta": dict()}
          # This will only be used in headless mode
          next_env = {}

          print(f"Running cognitive processes for step {self.step}...")
          
          for persona_name, persona in self.personas.items():
              # <next_tile> is a x,y coordinate. e.g., (58, 9)
              # <pronunciatio> is an emoji. e.g., "\ud83d\udca4"
              # <description> is a string description of the movement. e.g.,
              #   writing her next novel (editing her novel)
              #   @ double studio:double studio:common room:sofa
              
              print(f"  Processing {persona_name}...")
              start_time = time.time()
              execution = persona.move(self.maze, self.personas, self.personas_tile[persona_name], self.curr_time)
              end_time = time.time()
              print(f"  {persona_name} processed in {end_time - start_time:.2f} seconds")
              
              # Log agent movement
              if self.logger:
                  self.logger.log_event(persona.name, self.curr_time, "move", {
                          "tile": execution[0],
                          "description": execution[2],
                          "emoji": execution[1]
                      })

              # Optionally extract for later use:
              next_tile, pronunciatio, description = execution

              movements["persona"][persona_name] = {}
              movements["persona"][persona_name]["movement"] = next_tile
              movements["persona"][persona_name][
                "pronunciatio"
              ] = pronunciatio
              movements["persona"][persona_name]["description"] = description
              movements["persona"][persona_name][
                "chat"
              ] = persona.scratch.chat

              if headless:
                next_env[persona_name] = {
                  "x": next_tile[0],
                  "y": next_tile[1],
                  "maze": self.maze.maze_name,
                }

          # Include the meta information about the current stage in the
          # movements dictionary.
          movements["meta"]["curr_time"] = self.curr_time.strftime(
              "%B %d, %Y, %H:%M:%S"
          )

          # We then write the personas' movements to a file that will be sent
          # to the frontend server.
          # Example json output:
          # {"persona": {"Maria Lopez": {"movement": [58, 9]}},
          #  "persona": {"Klaus Mueller": {"movement": [38, 12]}},
          #  "meta": {curr_time: <datetime>}}
          movementFolder = f"{sim_folder}/movement"
          if not os.path.exists(movementFolder):
              os.mkdir(movementFolder)
          curr_move_file = f"{sim_folder}/movement/{self.step}.json"
          with open(curr_move_file, "w") as outfile:
              outfile.write(json.dumps(movements, indent=2))

          # Run any plugins that are in the plugin folder.
          if os.path.exists(f"{sim_folder}/plugins"):
              plugins = os.listdir(f"{sim_folder}/plugins")

              for plugin in plugins:
                  plugin_path = f"{sim_folder}/plugins/{plugin}"
                  prompt_files = os.listdir(f"{plugin_path}/prompt_template")
                  plugin_config_path = f"{plugin_path}/config.json"

                  with open(plugin_config_path) as plugin_config_file:
                      plugin_config = json.load(plugin_config_file)

                  # Currently only works for 2-agent sims
                  conversation = list(movements["persona"].values())[0]["chat"]

                  time_condition = self.curr_time.time() >= datetime.datetime.strptime(
                      plugin_config["run_between"]["start_time"], "%H:%M:%S"
                    ).time() and self.curr_time.time() <= datetime.datetime.strptime(
                      plugin_config["run_between"]["end_time"], "%H:%M:%S"
                    ).time()
                  conversation_condition = (True if not plugin_config["conversations_only"]
                    else (True if conversation else False))

                  if (time_condition and conversation_condition):
                    for prompt_file in prompt_files:
                      prompt_file_path = (
                        f"{plugin_path}/prompt_template/{prompt_file}"
                      )
                      response = run_plugin(
                        prompt_file_path,
                        movements,
                        self.personas,
                      )

                      with open(
                        f"{plugin_path}/output/{self.step}-{prompt_file}.json",
                        "w",
                      ) as outfile:
                        outfile.write(json.dumps(response, indent=2))

          # If we're running in headless mode, also create the environment file
          # to immediately trigger the next simulation step
          if headless:
              next_env_file = f"{sim_folder}/environment/{self.step + 1}.json"
              with open(next_env_file, "w") as outfile:
                  outfile.write(json.dumps(next_env, indent=2))
              print(f"Created environment file for next step {self.step + 1}")
              
          # After this cycle, the world takes one step forward, and the
          # current time moves by <sec_per_step> amount.
          self.step += 1
          self.curr_time += datetime.timedelta(seconds=self.sec_per_step)
          if self.logger:
              self.logger.save_all()
              print(f"DEBUG: Saved logs at step {self.step}")
          
          int_counter -= 1
      else:
          # If we don't have environment data, wait a bit and try again
          time.sleep(self.server_sleep)

    # Sleep so we don't burn our machines.
    time.sleep(self.server_sleep)
    
    

  def open_server(self, input_command: str = None) -> None:
    """
    Open up an interactive terminal prompt that lets you run the simulation
    step by step and probe agent state.

    INPUT
      None
    OUTPUT
      None
    """
    print("Note: The agents in this simulation package are computational")
    print("constructs powered by generative agents architecture and LLM. We")
    print("clarify that these agents lack human-like agency, consciousness,")
    print("and independent decision-making.\n---")

    # <sim_folder> points to the current simulation folder.
    sim_folder = f"{fs_storage}/{self.sim_code}"
    headless = None

    while True:
      if not input_command:
        sim_command = input("Enter option: ")
      else:
        sim_command = input_command
      sim_command = sim_command.strip()
      print(sim_command)
      ret_str = ""

      try:
        if sim_command.lower() in ["f", "fin", "finish", "save and finish"]:
          # Finishes the simulation environment and saves the progress.
          # Example: fin
          self.save()
          break

        elif sim_command.lower() == "start path tester mode":
          # Starts the path tester and removes the currently forked sim files.
          # Note that once you start this mode, you need to exit out of the
          # session and restart in case you want to run something else.
          shutil.rmtree(sim_folder)
          self.start_path_tester_server()

        elif sim_command.lower() == "exit":
          # Finishes the simulation environment but does not save the progress
          # and erases all saved data from current simulation.
          # Example: exit
          shutil.rmtree(sim_folder)
          break

        elif sim_command.lower() == "save":
          # Saves the current simulation progress.
          # Example: save
          self.save()

        elif sim_command[:3].lower() == "run":
          # Runs the number of steps specified in the prompt.
          # Example: run 1000
          if headless is None:
            headless = False
            print("Setting headless to False.")
          elif headless:
            print(
                "Invalid command: Headless mode is on. Use 'headless' instead."
            )
            continue
          int_count = int(sim_command.split()[-1])
          self.start_server(int_count)

        elif sim_command[:8].lower() == "headless":
          # Runs the simulation in headless mode, which means that it will
          # run without the frontend server.
          # Example: headless 1000
          if headless is None:
            headless = True
            print("Setting headless to True.")
          elif not headless:
            print(
              "Invalid command: Headless mode is off. Use 'run' instead."
            )
            continue
          int_count = int(sim_command.split()[-1])
          self.start_server(int_count, headless=True)

        elif "print persona schedule" in sim_command[:22].lower():
          # Print the decomposed schedule of the persona specified in the
          # prompt.
          # Example: print persona schedule Isabella Rodriguez
          ret_str += self.personas[
            " ".join(sim_command.split()[-2:])
          ].scratch.get_str_daily_schedule_summary()

        elif "print all persona schedule" in sim_command[:26].lower():
          # Print the decomposed schedule of all personas in the world.
          # Example: print all persona schedule
          for persona_name, persona in self.personas.items():
            ret_str += f"{persona_name}\n"
            ret_str += (
                f"{persona.scratch.get_str_daily_schedule_summary()}\n"
            )
            ret_str += f"---\n"

        elif "print hourly org persona schedule" in sim_command.lower():
          # Print the hourly schedule of the persona specified in the prompt.
          # This one shows the original, non-decomposed version of the
          # schedule.
          # Ex: print persona schedule Isabella Rodriguez
          ret_str += self.personas[
            " ".join(sim_command.split()[-2:])
          ].scratch.get_str_daily_schedule_hourly_org_summary()

        elif "print persona current tile" in sim_command[:26].lower():
          # Print the x y tile coordinate of the persona specified in the
          # prompt.
          # Ex: print persona current tile Isabella Rodriguez
          ret_str += str(
            self.personas[
              " ".join(sim_command.split()[-2:])
            ].scratch.curr_tile
          )

        elif "print persona chatting with buffer" in sim_command.lower():
          # Print the chatting with buffer of the persona specified in the
          # prompt.
          # Ex: print persona chatting with buffer Isabella Rodriguez
          curr_persona = self.personas[" ".join(sim_command.split()[-2:])]
          for p_n, count in curr_persona.scratch.chatting_with_buffer.items():
            ret_str += f"{p_n}: {count}"

        elif "print persona associative memory (event)" in sim_command.lower():
          # Print the associative memory (event) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (event) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += self.personas[
            " ".join(sim_command.split()[-2:])
          ].a_mem.get_str_seq_events()

        elif (
          "print persona associative memory (thought)" in sim_command.lower()
        ):
          # Print the associative memory (thought) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (thought) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += self.personas[
            " ".join(sim_command.split()[-2:])
          ].a_mem.get_str_seq_thoughts()

        elif "print persona associative memory (chat)" in sim_command.lower():
          # Print the associative memory (chat) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (chat) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += self.personas[
            " ".join(sim_command.split()[-2:])
          ].a_mem.get_str_seq_chats()

        elif "print persona spatial memory" in sim_command.lower():
          # Print the spatial memory of the persona specified in the prompt
          # Ex: print persona spatial memory Isabella Rodriguez
          self.personas[" ".join(sim_command.split()[-2:])].s_mem.print_tree()

        elif "print current time" in sim_command[:18].lower():
          # Print the current time of the world.
          # Ex: print current time
          ret_str += f'{self.curr_time.strftime("%B %d, %Y, %H:%M:%S")}\n'
          ret_str += f"steps: {self.step}"

        elif "print tile event" in sim_command[:16].lower():
          # Print the tile events in the tile specified in the prompt
          # Ex: print tile event 50, 30
          cooordinate = [int(i.strip()) for i in sim_command[16:].split(",")]
          for i in self.maze.access_tile(cooordinate)["events"]:
            ret_str += f"{i}\n"

        elif "print tile details" in sim_command.lower():
          # Print the tile details of the tile specified in the prompt
          # Ex: print tile event 50, 30
          cooordinate = [int(i.strip()) for i in sim_command[18:].split(",")]
          for key, val in self.maze.access_tile(cooordinate).items():
            ret_str += f"{key}: {val}\n"

        elif "call -- analysis" in sim_command.lower():
          # Starts a stateless chat session with the agent. It does not save
          # anything to the agent's memory.
          # Ex: call -- analysis Isabella Rodriguez
          persona_name = sim_command[len("call -- analysis") :].strip()
          #self.personas[persona_name].open_convo_session("analysis", logger=logger)
          from persona.cognitive_modules.converse import open_convo_session
          open_convo_session(self.personas[persona_name], "analysis", logger=logger)

        elif "assess mental health" in sim_command.lower():
          # Format: assess mental health Isabella Rodriguez PHQ-9
          parts = sim_command.split()
          persona_name = " ".join(parts[3:-1])
          questionnaire_name = parts[-1]
          
          if persona_name in self.personas:
              persona = self.personas[persona_name]
              result = assess_mental_health(persona, questionnaire_name, self.curr_time)
              ret_str += f"Completed {questionnaire_name} assessment for {persona_name}\n"
              
              # Print item responses
              if 'responses' in result:
                  ret_str += "Responses:\n"
                  for item_id, response in result['responses'].items():
                      ret_str += f"  Item {item_id}: Score {response['score']}\n"
          else:
              ret_str += f"Persona {persona_name} not found."
              
        elif "call -- load history" in sim_command.lower():
          # Loads the agent history from a file.
          # Ex: call -- load history the_ville/agent_history_init_n3.csv
          # Ex: call -- load history ./environment/frontend_server/storage/base_the_ville_isabella_maria_klaus/agent_history.csv
          file_path = sim_command[len("call -- load history") :].strip()

          # If the file path starts with "./", interpret it as a relative path
          # starting from the project root.
          if file_path.startswith("./"):
            curr_file = "../../" + file_path[2:]
          else:
            # Otherwise, it's a relative path from the maze assets folder.
            curr_file = maze_assets_loc + "/" + file_path

          rows = read_file_to_list(curr_file, header=True, strip_trail=True)[
            1
          ]
          clean_whispers = []
          for row in rows:
            agent_name = row[0].strip()
            whispers = row[1].split(";")
            whispers = [whisper.strip() for whisper in whispers]
            for whisper in whispers:
              clean_whispers += [[agent_name, whisper]]

          load_history_via_whisper(self.personas, clean_whispers, self.curr_time)

        print(ret_str)

      except Exception as e:
        print("(reverie): Error: ", e)
        traceback.print_exc()
        # remove movement file if it exists
        movement_file = f"{sim_folder}/movement/{self.step}.json"
        if os.path.exists(movement_file):
          os.remove(movement_file)
        # remove environment file if it exists
        env_file = f"{sim_folder}/environment/{self.step}.json"
        if os.path.exists(env_file):
          os.remove(env_file)
        print(f"(reverie): Error at step {self.step}")
        if self.step > 0:
          self.step -= 1
          self.curr_time -= datetime.timedelta(seconds=self.sec_per_step)
        raise Exception(e, self.step, "stepback")
      else:
        # If an input command was passed, then execute one command and exit.
        if input_command:
          break
    
    self.logger.save_all()
    
    
    



if __name__ == "__main__":
  # rs = ReverieServer("base_the_ville_isabella_maria_klaus",
  #                    "July1_the_ville_isabella_maria_klaus-step-3-1")
  # rs = ReverieServer("July1_the_ville_isabella_maria_klaus-step-3-20",
  #                    "July1_the_ville_isabella_maria_klaus-step-3-21")
  # rs.open_server()

  # Get the simulation to fork from the user
  default = "base_the_ville_isabella_maria_klaus"
  origin_prompt = (
    f"Enter the name of the forked simulation (leave blank for {default}): "
  )
  origin = input(origin_prompt).strip()
  if not origin:
    origin = default
    print(origin)

  # Get the name of the new simulation from the user
  last_sim_code = ""
  try:
    with open(f"{fs_temp_storage}/curr_sim_code.json") as json_file:
      curr_sim_code = json.load(json_file)
      last_sim_code = curr_sim_code["sim_code"]
    target_prompt = f"Enter the name of the new simulation (last was {last_sim_code}): "
  except (FileNotFoundError, KeyError):
    target_prompt = "Enter the name of the new simulation: "

  target = input(target_prompt).strip()

  rs = ReverieServer(origin, target)
  rs.open_server()
  

def run_simulation_programmatically(origin_sim="base_the_ville_isabella_maria_klaus", 
                                   target_sim=None, 
                                   steps=100, 
                                   headless=True,
                                   config=None,
                                   continue_from_origin=False):
    """
    Run a simulation programmatically without any user input
    """
    
    # Generate a default target name if none provided
    if target_sim is None:
        target_sim = f"sim_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # REQUIRE config parameter - no default config allowed
    if config is None:
        raise ValueError(
            "Configuration is required for programmatic simulation runs. "
            "Please provide a config dictionary with at least 'simulation_name', "
            "'timed_events', and 'questionnaires' keys."
        )
    
    # Extract info from config
    working_dir = config.get("working_dir")
    simulation_name = config.get("simulation_name")
    simulation_type = config.get("simulation_type")
    
    print(f"DEBUG run_simulation_programmatically: Creating server with continue_from_origin={continue_from_origin}")
 
   
    # Create the server - CRITICAL: Pass preserve_origin_state correctly
    rs = ReverieServer(
        origin_sim, 
        target_sim, 
        working_dir=working_dir,         # ADD THIS
        simulation_name=simulation_name, # ADD THIS
        simulation_type=simulation_type, # ADD THIS
        #experiment_results_path=experiment_results_path,
        preserve_origin_state=continue_from_origin)
    
    print(f"DEBUG run_simulation_programmatically: Server created, preserve_origin_state={rs.preserve_origin_state}")
    print(f"DEBUG run_simulation_programmatically: Initial curr_time={rs.curr_time}")
    
    # Set the provided config
    rs.set_experiment_config(config)
    print(f"DEBUG run_simulation_programmatically: After set_experiment_config, curr_time={rs.curr_time}")

    # Run the simulation
    print(f"DEBUG run_simulation_programmatically: Starting server with curr_time={rs.curr_time}")
    rs.start_server(steps, headless=headless)
    
    # Save at the end
    rs.save()
    
    # Copy all logs and data to SimulationManager central location
    print("🗂️  Copying all files to central location...")
    rs._copy_logs_to_central_location()
    rs._copy_simulation_data_to_central_location()
    print("✅ All files copied to central location")
    
    return rs



