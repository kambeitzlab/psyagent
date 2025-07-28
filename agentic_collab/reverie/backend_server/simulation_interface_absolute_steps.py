#!/usr/bin/env python3
"""
Simple Simulation Interface with Absolute Step Counting
======================================================

This version implements absolute step counting for branched simulations.
When a simulation branches from a parent, step numbers continue from where 
the parent simulation ended, creating a continuous timeline.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Add backend to path
sys.path.append('agentic_collab/reverie/backend_server')

@dataclass
class AssessmentConfig:
    """Simple assessment configuration"""
    name: str = "PHQ-9"
    steps: List[int] = field(default_factory=list)
    description: str = ""

@dataclass  
class EventConfig:
    """Simple event configuration"""
    name: str = ""
    step: int = 0
    event_type: str = "negative"  # "negative", "therapy", "custom"
    target_agent: str = ""
    description: str = ""

class SimulationBuilder:
    """Simple simulation builder with absolute step counting"""
    
    def __init__(self):
        # Default values - users can override any of these
        self.name = "my_simulation"
        self.description = "My simulation description"
        self.origin = "base_the_ville_isabella_maria_klaus"  # Base simulation to start from
        self.steps_per_hour = 4
        self.duration_in_days = 7
        self.agents = ["Maria Lopez"]
        self.type = "baseline"  # "baseline", "control", "trauma_only", "trauma_therapy", "custom"
        self.assessments = []
        self.events = []
        self._executed = False
        self._parent_steps = None  # Cache for parent steps
    
    def _get_parent_steps(self) -> int:
        """Get total steps of parent simulation for absolute step counting"""
        if self._parent_steps is not None:
            return self._parent_steps
            
        try:
            if self.origin == "base_the_ville_isabella_maria_klaus":
                self._parent_steps = 0
                return 0
            
            from simulation_manager import simulation_manager
            parent_dir = simulation_manager.simulations_root / self.origin
            metadata_file = parent_dir / "metadata.json"
            
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                config = metadata.get('experiment_config', {})
                self._parent_steps = config.get('total_steps', 0)
                return self._parent_steps
            
            self._parent_steps = 0
            return 0
        except Exception as e:
            print(f"Warning: Could not determine parent steps: {e}")
            self._parent_steps = 0
            return 0
    
    def daily_assessment_steps(self, num_days: int) -> List[int]:
        """
        Helper: Generate steps for daily assessments (2 hours before end of day)
        Returns ABSOLUTE step numbers that continue from parent simulation
        """
        steps_per_day = self.steps_per_hour * 24
        parent_steps = self._get_parent_steps()
        
        # Generate relative steps, then add parent steps for absolute positioning
        relative_steps = [day * steps_per_day - 8 for day in range(1, num_days + 1)]
        absolute_steps = [step + parent_steps for step in relative_steps]
        
        return absolute_steps
    
    def time_to_step(self, day: int, hour: int) -> int:
        """
        Helper: Convert day/hour to ABSOLUTE simulation step
        For branched simulations, continues from parent simulation end
        """
        steps_per_day = self.steps_per_hour * 24
        parent_steps = self._get_parent_steps()
        
        # Calculate relative step within this simulation
        relative_step = (day - 1) * steps_per_day + hour * self.steps_per_hour
        
        # Add parent steps for absolute positioning
        absolute_step = relative_step + parent_steps
        
        return absolute_step
    
    def get_absolute_step_range(self) -> tuple:
        """Get the absolute step range this simulation will cover"""
        parent_steps = self._get_parent_steps()
        total_steps = self.duration_in_days * self.steps_per_hour * 24
        return (parent_steps, parent_steps + total_steps)
    
    def get_study_day_from_absolute_step(self, absolute_step: int) -> int:
        """Convert absolute step back to study day within this simulation"""
        parent_steps = self._get_parent_steps()
        relative_step = absolute_step - parent_steps
        steps_per_day = self.steps_per_hour * 24
        return (relative_step // steps_per_day) + 1
    
    def validate(self) -> List[str]:
        """Check configuration for errors"""
        errors = []
        
        if not self.name:
            errors.append("Simulation name cannot be empty")
        if not self.agents:
            errors.append("At least one agent must be specified")
        if self.duration_in_days < 1:
            errors.append("Duration must be at least 1 day")
        if self.steps_per_hour < 1:
            errors.append("Steps per hour must be at least 1")
        
        # Check for duplicate simulation names
        try:
            from simulation_manager import simulation_manager
            sim_dir = simulation_manager.simulations_root / self.name
            if sim_dir.exists() and not self._executed:
                errors.append(f"Simulation '{self.name}' already exists - choose a different name")
        except ImportError:
            pass  # Skip check if simulation_manager not available
            
        return errors
    
    def summary(self) -> str:
        """Generate summary of this simulation with absolute step information"""
        steps_per_day = self.steps_per_hour * 24
        total_steps = self.duration_in_days * steps_per_day
        parent_steps = self._get_parent_steps()
        start_step, end_step = self.get_absolute_step_range()
        
        lines = [
            f"Simulation: {self.name}",
            f"Type: {self.type}",
            f"Origin: {self.origin}",
            f"Duration: {self.duration_in_days} days ({total_steps} steps)",
            f"Resolution: {self.steps_per_hour} steps/hour ({60//self.steps_per_hour} min intervals)",
            f"Agents: {', '.join(self.agents)}",
        ]
        
        # Add absolute step range information
        if parent_steps > 0:
            lines.append(f"Absolute step range: {start_step} to {end_step} (continues from parent)")
            lines.append(f"Parent simulation ended at step: {parent_steps}")
        else:
            lines.append(f"Absolute step range: {start_step} to {end_step} (baseline simulation)")
        
        lines.extend([
            f"Assessments: {len(self.assessments)} configured",
            f"Events: {len(self.events)} configured"
        ])
        
        if self.assessments:
            lines.append("Assessment schedule (absolute steps):")
            for assessment in self.assessments:
                steps_display = assessment.steps[:3]  # Show first 3 for brevity
                steps_str = ", ".join(map(str, steps_display))
                if len(assessment.steps) > 3:
                    steps_str += f", ... (+{len(assessment.steps)-3} more)"
                lines.append(f"  • {assessment.name}: Steps {steps_str}")
        
        if self.events:
            lines.append("Scheduled events (absolute steps):")
            for event in self.events:
                # Convert absolute step back to relative day/hour for display
                relative_day = self.get_study_day_from_absolute_step(event.step)
                parent_steps = self._get_parent_steps()
                relative_step_in_day = (event.step - parent_steps) % (self.steps_per_hour * 24)
                hour = relative_step_in_day // self.steps_per_hour
                lines.append(f"  • {event.name} (Day {relative_day}, {hour:02d}:00, Step {event.step}): {event.event_type}")
        
        return "\n".join(lines)
    
    def run(self, headless: bool = True, show_summary: bool = True) -> bool:
        """Execute this simulation"""
        
        if show_summary:
            print(f"\n🔬 SIMULATION: {self.name.upper()}")
            print("=" * 50)
            print(self.summary())
        
        # Validate configuration
        errors = self.validate()
        if errors:
            print(f"\n❌ Configuration errors:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        try:
            # Import simulation components
            from simulation_manager import simulation_manager
            from reverie import run_simulation_programmatically
            
            print(f"\n🔄 Executing simulation...")
            
            # Convert to simulation manager format (with absolute steps)
            config = self._to_simulation_config()
            
            # Create or branch simulation
            if self.origin == "base_the_ville_isabella_maria_klaus" or self.type == "baseline":
                # Create new baseline simulation
                sim = simulation_manager.create_simulation(
                    simulation_id=self.name,
                    config=config,
                    agents=self.agents
                )
                print(f"✓ Created baseline simulation: {sim.simulation_id}")
            else:
                # Branch from existing simulation
                branched_at_step = self._get_parent_steps()
                sim = simulation_manager.branch_simulation(
                    parent_id=self.origin,
                    target_id=self.name,
                    branch_type=self.type,
                    branch_config=config,
                    branched_at_step=branched_at_step
                )
                print(f"✓ Created branch simulation: {sim.simulation_id} (branched at step {branched_at_step})")
            
            # Execute simulation
            total_steps = self.duration_in_days * self.steps_per_hour * 24
            
            # Add required config parameters
            config['working_dir'] = str(simulation_manager.simulations_root)
            config['simulation_name'] = self.name
            
            # Show scheduling information with absolute steps
            start_step, end_step = self.get_absolute_step_range()  
            print(f"🚀 Running {total_steps} steps (absolute steps {start_step} to {end_step})...")
            print(f"📋 {len(config.get('questionnaires', []))} assessments scheduled")
            print(f"⚡ {len(config.get('timed_events', []))} events scheduled")
            
            simulation = run_simulation_programmatically(
                origin_sim=self.origin,
                target_sim=self.name,
                steps=total_steps,
                headless=headless,
                config=config
            )
            
            print(f"✅ Simulation completed successfully!")
            print(f"📈 Results: {len(simulation.personas)} personas, final step {simulation.step}")
            print(f"📁 Results saved to: simulations/{self.name}/")
            
            self._executed = True
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _to_simulation_config(self) -> dict:
        """Convert to simulation manager config format with absolute step numbers"""
        steps_per_day = self.steps_per_hour * 24
        total_steps = self.duration_in_days * steps_per_day
        
        # Convert assessments with absolute step numbers
        questionnaires = []
        for assessment in self.assessments:
            for step in assessment.steps:
                questionnaires.append({
                    "name": assessment.name,
                    "step": step,  # Already absolute from helper functions
                    "target_agents": self.agents,
                    "description": f"{assessment.description} at absolute step {step}"
                })
        
        # Convert events with absolute step numbers
        timed_events = []
        for event in self.events:
            timed_events.append({
                "name": event.name,
                "step": event.step,  # Already absolute from helper functions
                "type": event.event_type,
                "target": event.target_agent,
                "description": event.description
            })
        
        return {
            "simulation_name": self.name,
            "total_steps": total_steps,
            "steps_per_hour": self.steps_per_hour,
            "description": self.description,
            "simulation_type": self.type,
            "questionnaires": questionnaires,
            "timed_events": timed_events
        }

# Helper function to create simulation instances
def create_simulation() -> SimulationBuilder:
    """Create a new simulation configuration"""
    return SimulationBuilder()

# Global instances for easy access (users can use these directly)
baseline_simulation = create_simulation()
trauma_therapy_simulation = create_simulation()
control_simulation = create_simulation()
trauma_only_simulation = create_simulation()
custom_simulation = create_simulation()