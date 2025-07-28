import os
import json
from datetime import datetime

class SimulationLogger:
    def __init__(self, simulation_name):
        self.simulation_name = simulation_name
        self.log_dir = f"logs/{simulation_name}"
        os.makedirs(self.log_dir, exist_ok=True)
        self.events_file = os.path.join(self.log_dir, "events.jsonl")
        self.events = []
        self.questionnaire_file = os.path.join(self.log_dir, "questionnaire_results.jsonl")

    

    def log_event(self, agent_name, timestamp, event_type, details):
        event_record = {
            "agent": agent_name,
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "event_type": event_type,
            "details": details,
        }
        self.events.append(event_record)
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event_record) + "\n")
        
        # Special handling for questionnaire results
        if event_type == "questionnaire":
            with open(self.questionnaire_file, "a") as f:
                f.write(json.dumps(details) + "\n")
                
            # Handle the different format of responses
            if 'responses' in details and isinstance(details['responses'], dict):
                # Convert dictionary responses to format expected by logger
                formatted_responses = []
                for item_id, response_data in details['responses'].items():
                    formatted_response = {
                        'item_number': item_id,
                        'short_name': f'item_{item_id}',
                        'response': response_data['score'],
                        'timestamp': timestamp.isoformat() if timestamp else datetime.now().isoformat()
                    }
                    formatted_responses.append(formatted_response)
                
                # Log individual item responses for easier analysis
                items_file = os.path.join(self.log_dir, f"{details['questionnaire']}_items.jsonl")
                for response in formatted_responses:
                    item_record = {
                        'agent': agent_name,
                        'questionnaire': details['questionnaire'],
                        'item_number': response['item_number'],
                        'item_short_name': response['short_name'],
                        'response': response['response'],
                        'timestamp': response['timestamp']
                    }
                    with open(items_file, "a") as f:
                        f.write(json.dumps(item_record) + "\n")



    def save_all(self):
        # Optional: Call this at the end to save all in one file if needed.
        with open(os.path.join(self.log_dir, "all_events.json"), "w") as f:
            json.dump(self.events, f, indent=2)
