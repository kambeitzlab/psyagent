#!/usr/bin/env python3
"""
Simple Simulation Interface
Direct, user-friendly way to define and run AI agent psychological research simulations
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
    """Simple simulation builder - users work directly with this"""
    
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
    
    def daily_assessment_steps(self, num_days: int) -> List[int]:
        """Helper: Generate steps for daily assessments (2 hours before end of day)"""
        steps_per_day = self.steps_per_hour * 24
        return [day * steps_per_day - 8 for day in range(1, num_days + 1)]
    
    def time_to_step(self, day: int, hour: int) -> int:
        """Helper: Convert day/hour to simulation step"""
        steps_per_day = self.steps_per_hour * 24
        return (day - 1) * steps_per_day + hour * self.steps_per_hour
    
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
        """Generate summary of this simulation"""
        steps_per_day = self.steps_per_hour * 24
        total_steps = self.duration_in_days * steps_per_day
        
        lines = [
            f"Simulation: {self.name}",
            f"Type: {self.type}",
            f"Origin: {self.origin}",
            f"Duration: {self.duration_in_days} days ({total_steps} steps)",
            f"Resolution: {self.steps_per_hour} steps/hour ({60//self.steps_per_hour} min intervals)",
            f"Agents: {', '.join(self.agents)}",
            f"Assessments: {len(self.assessments)} configured",
            f"Events: {len(self.events)} configured"
        ]
        
        if self.assessments:
            lines.append("Assessment schedule:")
            for assessment in self.assessments:
                lines.append(f"  • {assessment.name}: {len(assessment.steps)} administrations")
        
        if self.events:
            lines.append("Scheduled events:")
            for event in self.events:
                day = (event.step // (self.steps_per_hour * 24)) + 1
                hour = (event.step % (self.steps_per_hour * 24)) // self.steps_per_hour
                lines.append(f"  • {event.name} (Day {day}, {hour:02d}:00): {event.event_type}")
        
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
            
            # Convert to simulation manager format
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
            
            print(f"🚀 Running {total_steps} steps...")
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
        """Convert to simulation manager config format"""
        steps_per_day = self.steps_per_hour * 24
        total_steps = self.duration_in_days * steps_per_day
        
        # Convert assessments
        questionnaires = []
        for assessment in self.assessments:
            for step in assessment.steps:
                questionnaires.append({
                    "name": assessment.name,
                    "step": step,
                    "target_agents": self.agents,
                    "description": f"{assessment.description} at step {step}"
                })
        
        # Convert events
        timed_events = []
        for event in self.events:
            timed_events.append({
                "name": event.name,
                "step": event.step,
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
    
    def _get_parent_steps(self) -> int:
        """Get total steps of parent simulation for branching"""
        try:
            if self.origin == "base_the_ville_isabella_maria_klaus":
                return 0
            
            from simulation_manager import simulation_manager
            parent_dir = simulation_manager.simulations_root / self.origin
            metadata_file = parent_dir / "metadata.json"
            
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                config = metadata.get('experiment_config', {})
                return config.get('total_steps', 0)
            
            return 0
        except Exception as e:
            print(f"Warning: Could not determine parent steps: {e}")
            return 0

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