"""
File: experiment_scheduler.py
Description: A step-based scheduler for events and questionnaires in agent simulations

This module manages scheduling of events and questionnaires based on simulation steps
rather than real-time or in-game time. This simplifies experiment configuration and
makes experiment results more deterministic.
"""

import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class ExperimentScheduler:
    """Manages step-based scheduling of events and questionnaires in a simulation"""
    
    def __init__(self):
        """Initialize the experiment scheduler"""
        self.step_events = defaultdict(list)  # Events scheduled at specific steps
        self.recurring_events = []  # Events that recur at regular intervals
        self.executed_events = set()  # Track executed events to avoid duplicates
        
    def load_from_config(self, config: Dict[str, Any]):
        """
        Load scheduler configuration from a config dictionary
        
        Args:
            config: Configuration dictionary with events and questionnaires
        """
        self.step_events = defaultdict(list)
        self.recurring_events = []
        self.executed_events = set()
        
        # Load one-time events
        if "timed_events" in config:
            for event in config["timed_events"]:
                # Handle events with exact step specification
                if "step" in event:
                    target_step = event["step"]
                    self.step_events[target_step].append(event)
                # Handle events with steps_after_branch_start specification
                elif "steps_after_branch_start" in event:
                    # Will be processed after we know the branch start step
                    self.step_events[event["steps_after_branch_start"]].append(event)
        
        # Load questionnaires (recurring events)
        if "questionnaires" in config:
            for questionnaire in config["questionnaires"]:
                for agent in questionnaire["target_agents"]:
                    # Convert time-based to step-based
                    if "time" in questionnaire and "frequency" in questionnaire:
                        # For backward compatibility with time-based configs
                        time_str = questionnaire["time"]
                        hours, minutes = map(int, time_str.split(":"))
                        # Assuming default step conversion from config or use 6
                        steps_per_hour = config.get("steps_per_hour", 6)
                        
                        # Convert to steps
                        offset_steps = int((hours * 60 + minutes) * steps_per_hour / 60)
                        
                        # Convert frequency to steps
                        if questionnaire["frequency"] == "daily":
                            frequency_steps = 24 * steps_per_hour
                        else:
                            # Default to daily if unknown
                            frequency_steps = 24 * steps_per_hour
                    else:
                        # Directly use step-based specification
                        offset_steps = questionnaire.get("offset_steps", 0)
                        frequency_steps = questionnaire.get("frequency_steps", 24 * config.get("steps_per_hour", 6))
                    
                    # Create recurring event
                    self.recurring_events.append({
                        "type": "questionnaire",
                        "name": questionnaire["name"],
                        "target": agent,
                        "offset_steps": offset_steps,
                        "frequency_steps": frequency_steps
                    })
                    
    def set_branch_start_step(self, start_step: int):
        """
        Set the starting step for branch events
        
        Args:
            start_step: Step number where the branch starts
        """
        # Adjust events that are relative to branch start
        events_to_adjust = []
        for relative_step, events in self.step_events.items():
            for event in events:
                if "steps_after_branch_start" in event:
                    events_to_adjust.append((relative_step, event))
        
        # Remove events from their relative positions
        for relative_step, event in events_to_adjust:
            self.step_events[relative_step].remove(event)
            
            # Add them at their absolute positions
            absolute_step = start_step + event["steps_after_branch_start"]
            event_copy = event.copy()
            event_copy["step"] = absolute_step
            self.step_events[absolute_step].append(event_copy)
    
    def get_events_for_step(self, current_step: int) -> List[Dict[str, Any]]:
        """
        Get all events scheduled for the current step
        
        Args:
            current_step: Current simulation step
            
        Returns:
            List of event dictionaries for the current step
        """
        events = []
        
        # Get one-time events for this step
        events.extend(self.step_events.get(current_step, []))
        
        # Check recurring events
        for event in self.recurring_events:
            offset_steps = event["offset_steps"]
            frequency_steps = event["frequency_steps"]
            
            # Calculate if this recurring event should trigger at this step
            if (current_step >= offset_steps and 
                (current_step - offset_steps) % frequency_steps == 0):
                
                # Create a unique ID for this recurring event instance
                event_id = f"{event['type']}_{event['name']}_{event['target']}_{current_step}"
                
                # Only execute if not already done
                if event_id not in self.executed_events:
                    event_instance = event.copy()
                    event_instance["event_id"] = event_id
                    events.append(event_instance)
                    self.executed_events.add(event_id)
        
        return events

# Create a singleton instance
experiment_scheduler = ExperimentScheduler()