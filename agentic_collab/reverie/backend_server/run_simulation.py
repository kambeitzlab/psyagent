import os
import sys

# Add the path to the directory containing reverie.py
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

path = '/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server'
os.chdir(path)


import datetime
from reverie import run_simulation_programmatically


simulation = run_simulation_programmatically(
    origin_sim="base_the_ville_isabella_maria_klaus",
    target_sim="mental_health_test_sim_",# + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
    steps=10,
    headless=True
)



# You can now examine the simulation results
print(f"Simulation completed with {len(simulation.personas)} personas")
for persona_name, persona in simulation.personas.items():
    print(f"- {persona_name}: {len(persona.a_mem.event_list)} memories")
    
    
    
import os
import inspect
from persona.prompt_template.gpt_structure import get_embedding

# Print the exact file path being used



#----------------------------------------------------------------
#----------------------------------------------------------------
#----------------------------------------------------------------

import os
import sys
import datetime
import time
import json

# Add the path to the directory containing reverie.py
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
path = '/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server'
os.chdir(path)

# Import necessary modules
from reverie import run_simulation_programmatically
from persona.cognitive_modules.assess import assess_mental_health, save_assessment_results

def run_test():
    print("Starting test of mental health assessment implementation...")
    
    # Create a unique simulation name with timestamp
    target_sim = f"mental_health_test_sim_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Running simulation: {target_sim}")
    # Run the simulation for 5 steps
    simulation = run_simulation_programmatically(
        origin_sim="base_the_ville_isabella_maria_klaus",
        target_sim=target_sim,
        steps=5,
        headless=True
    )
    
    print(f"\nSimulation completed with {len(simulation.personas)} personas")
    for persona_name, persona in simulation.personas.items():
        # Get memory counts from the sequence lists
        event_count = len(persona.a_mem.seq_event)
        thought_count = len(persona.a_mem.seq_thought)
        chat_count = len(persona.a_mem.seq_chat)
        total_memories = event_count + thought_count + chat_count
        
        print(f"- {persona_name}: {total_memories} total memories")
        print(f"  Events: {event_count}, Thoughts: {thought_count}, Chats: {chat_count}")
    
    # Test the mental health assessment for each persona
    print("\nRunning mental health assessments...")
    
    # Directory to save assessment results
    assessment_dir = os.path.join(os.getcwd(), "assessment_results_test")
    os.makedirs(assessment_dir, exist_ok=True)
    
    # Test each questionnaire for each persona
    questionnaires = ["PHQ-9", "GAD-7", "K10"]
    assessment_results = {}
    
    for persona_name, persona in simulation.personas.items():
        assessment_results[persona_name] = {}
        
        print(f"\nAssessing {persona_name}:")
        for questionnaire in questionnaires:
            print(f"  Running {questionnaire}...")
            try:
                # Run the assessment
                start_time = time.time()
                result = assess_mental_health(persona, questionnaire, simulation.curr_time)
                duration = time.time() - start_time
                
                # Store the result
                assessment_results[persona_name][questionnaire] = result
                
                # Print summary of results
                if 'responses' in result:
                    total_score = sum(item['score'] for item in result['responses'].values())
                    print(f"  - {questionnaire} completed in {duration:.2f}s, total score: {total_score}")
                    
                    # Print a few sample responses
                    for item_id in list(result['responses'].keys())[:3]:  # First 3 items
                        response = result['responses'][item_id]
                        print(f"    Item {item_id}: Score {response['score']}")
                        print(f"      Reasoning: {response['reasoning'][:100]}..." if len(response['reasoning']) > 100 else f"      Reasoning: {response['reasoning']}")
                else:
                    print(f"  - {questionnaire} completed but no responses found")
            except Exception as e:
                print(f"  - Error running {questionnaire}: {str(e)}")
    
    # Save the assessment results
    print("\nSaving assessment results...")
    for persona_name, questionnaire_results in assessment_results.items():
        persona_dir = os.path.join(assessment_dir, persona_name)
        os.makedirs(persona_dir, exist_ok=True)
        
        for questionnaire, result in questionnaire_results.items():
            filename = f"{questionnaire}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            filepath = os.path.join(persona_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2)
                print(f"Saved {filepath}")
    
    # Also try the built-in save function
    save_assessment_results(assessment_dir)
    
    print("\nTest completed successfully!")
    
    return simulation, assessment_results

simulation, results = run_test()
