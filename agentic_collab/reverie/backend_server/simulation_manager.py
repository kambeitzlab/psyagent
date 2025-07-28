#!/usr/bin/env python3
"""
SimulationManager - Flexible branching and continuation system for simulations

Provides git-like branching capabilities for expensive simulation research:
- Create baseline simulations 
- Continue simulations from any point
- Branch simulations for different conditions
- Centralized logging per simulation
- Cost-efficient storage with smart copying
"""

import os
import sys
import datetime
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationMetadata:
    """Handles simulation metadata and lineage tracking"""
    
    def __init__(self, simulation_id: str, parent_simulation: str = None, 
                 branch_type: str = "new", branched_at_step: int = 0):
        self.simulation_id = simulation_id
        self.parent_simulation = parent_simulation
        self.branch_type = branch_type  # new, continuation, trauma_condition, therapy_condition, etc.
        self.branched_at_step = branched_at_step
        self.current_step = 0
        self.total_steps = 0
        self.branch_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        self.experiment_config = None
        self.agents = []
        self.status = "created"  # created, running, completed, paused, failed
        self.children = []  # List of simulations branched from this one
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "simulation_id": self.simulation_id,
            "parent_simulation": self.parent_simulation,
            "branch_type": self.branch_type,
            "branched_at_step": self.branched_at_step,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "branch_timestamp": self.branch_timestamp,
            "experiment_config": self.experiment_config,
            "agents": self.agents,
            "status": self.status,
            "children": self.children
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SimulationMetadata':
        """Create from dictionary"""
        metadata = cls(
            simulation_id=data["simulation_id"],
            parent_simulation=data.get("parent_simulation"),
            branch_type=data.get("branch_type", "new"),
            branched_at_step=data.get("branched_at_step", 0)
        )
        metadata.current_step = data.get("current_step", 0)
        metadata.total_steps = data.get("total_steps", 0)
        metadata.branch_timestamp = data.get("branch_timestamp", "")
        metadata.experiment_config = data.get("experiment_config")
        metadata.agents = data.get("agents", [])
        metadata.status = data.get("status", "created")
        metadata.children = data.get("children", [])
        return metadata

class CentralizedLogger:
    """Centralized logging system for simulation events"""
    
    def __init__(self, simulation_dir: Path):
        self.simulation_dir = simulation_dir
        self.logs_dir = simulation_dir / "centralized_logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize log files
        self.memory_events_log = self.logs_dir / "memory_events.jsonl"
        self.conversations_log = self.logs_dir / "conversations.jsonl"
        self.api_calls_log = self.logs_dir / "api_calls.jsonl"
        self.assessments_log = self.logs_dir / "assessments.jsonl"
        self.timeline_log = self.logs_dir / "timeline.jsonl"
        
    def log_memory_event(self, agent: str, step: int, event_type: str, description: str, 
                        poignancy: float = None, keywords: List[str] = None):
        """Log memory-related events"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "agent": agent,
            "event_type": event_type,  # added, retrieved, reflected
            "description": description,
            "poignancy": poignancy,
            "keywords": keywords or []
        }
        self._append_log(self.memory_events_log, entry)
        
    def log_conversation(self, step: int, participants: List[str], content: str, 
                        context: str = None, memories_retrieved: List[str] = None):
        """Log conversation events"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "participants": participants,
            "content": content,
            "context": context,
            "memories_retrieved": memories_retrieved or []
        }
        self._append_log(self.conversations_log, entry)
        
    def log_api_call(self, step: int, agent: str, prompt_type: str, prompt: str, 
                    response: str, cost: float = None, tokens: Dict = None):
        """Log API calls with full prompt/response"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "agent": agent,
            "prompt_type": prompt_type,  # planning, conversation, assessment, etc.
            "prompt": prompt,
            "response": response,
            "cost": cost,
            "tokens": tokens or {}
        }
        self._append_log(self.api_calls_log, entry)
        
    def log_assessment(self, step: int, agent: str, questionnaire: str, 
                      memories_used: List[str], responses: Dict, scores: Dict):
        """Log assessment events"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "agent": agent,
            "questionnaire": questionnaire,
            "memories_used": memories_used,
            "responses": responses,
            "scores": scores
        }
        self._append_log(self.assessments_log, entry)
        
    def log_timeline_event(self, step: int, event_type: str, description: str, 
                          agents_affected: List[str] = None, data: Dict = None):
        """Log major timeline events"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "event_type": event_type,  # simulation_start, event_trigger, assessment, simulation_end
            "description": description,
            "agents_affected": agents_affected or [],
            "data": data or {}
        }
        self._append_log(self.timeline_log, entry)
        
    def _append_log(self, log_file: Path, entry: Dict):
        """Append entry to JSONL log file"""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to log {log_file}: {e}")

class SimulationManager:
    """Main simulation management class"""
    
    def __init__(self, simulations_root: str = None):
        if simulations_root is None:
            simulations_root = "/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/simulations"
        
        self.simulations_root = Path(simulations_root)
        self.simulations_root.mkdir(exist_ok=True)
        
        # Storage paths for existing system compatibility  
        self.storage_path = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/environment/frontend_server/storage")
        self.experiment_results_path = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/experiment_results")
        
        logger.info(f"SimulationManager initialized with root: {self.simulations_root}")
    
    def create_simulation(self, simulation_id: str, config: Dict, agents: List[str]) -> SimulationMetadata:
        """Create a new simulation"""
        logger.info(f"Creating new simulation: {simulation_id}")
        
        # Create simulation directory
        sim_dir = self.simulations_root / simulation_id
        if sim_dir.exists():
            raise ValueError(f"Simulation {simulation_id} already exists")
        
        sim_dir.mkdir()
        
        # Create metadata
        metadata = SimulationMetadata(simulation_id=simulation_id)
        metadata.agents = agents
        metadata.total_steps = config.get('total_steps', 0)
        # Save the full config instead of just the path
        metadata.experiment_config = config
        metadata.status = "created"
        
        # Save metadata
        self._save_metadata(sim_dir, metadata)
        
        # Create centralized logger
        logger_instance = CentralizedLogger(sim_dir)
        
        # Create data directories
        (sim_dir / "simulation_data").mkdir()
        (sim_dir / "assessment_results").mkdir()
        
        logger.info(f"Created simulation structure at: {sim_dir}")
        return metadata
    
    def continue_simulation(self, parent_id: str, target_id: str, 
                          additional_steps: int) -> SimulationMetadata:
        """Continue a simulation from where it left off"""
        logger.info(f"Continuing simulation {parent_id} -> {target_id} for {additional_steps} steps")
        
        parent_dir = self.simulations_root / parent_id
        if not parent_dir.exists():
            raise ValueError(f"Parent simulation {parent_id} not found")
        
        # Load parent metadata
        parent_metadata = self._load_metadata(parent_dir)
        
        # Create target simulation
        target_dir = self.simulations_root / target_id
        if target_dir.exists():
            raise ValueError(f"Target simulation {target_id} already exists")
        
        # Copy parent simulation data
        logger.info(f"Copying simulation data from {parent_id} to {target_id}")
        shutil.copytree(parent_dir, target_dir)
        
        # Update metadata for continuation
        metadata = SimulationMetadata(
            simulation_id=target_id,
            parent_simulation=parent_id,
            branch_type="continuation",
            branched_at_step=parent_metadata.current_step
        )
        metadata.agents = parent_metadata.agents
        metadata.current_step = parent_metadata.current_step
        metadata.total_steps = parent_metadata.current_step + additional_steps
        metadata.status = "created"
        
        # Save updated metadata
        self._save_metadata(target_dir, metadata)
        
        # Update parent's children list
        parent_metadata.children.append(target_id)
        self._save_metadata(parent_dir, parent_metadata)
        
        logger.info(f"Created continuation simulation: {target_id}")
        return metadata
    
    def branch_simulation(self, parent_id: str, target_id: str, branch_type: str,
                         branch_config: Dict, branched_at_step: int = None) -> SimulationMetadata:
        """Branch a simulation for different experimental conditions"""
        logger.info(f"Branching simulation {parent_id} -> {target_id} (type: {branch_type})")
        
        parent_dir = self.simulations_root / parent_id
        if not parent_dir.exists():
            raise ValueError(f"Parent simulation {parent_id} not found")
        
        # Load parent metadata
        parent_metadata = self._load_metadata(parent_dir)
        
        # Use current step as branch point if not specified
        if branched_at_step is None:
            branched_at_step = parent_metadata.current_step
        
        # Create target simulation
        target_dir = self.simulations_root / target_id
        if target_dir.exists():
            raise ValueError(f"Target simulation {target_id} already exists")
        
        # Copy parent simulation data up to branch point
        logger.info(f"Copying simulation data from {parent_id} to {target_id}")
        shutil.copytree(parent_dir, target_dir)
        
        # Create branch metadata
        metadata = SimulationMetadata(
            simulation_id=target_id,
            parent_simulation=parent_id,
            branch_type=branch_type,
            branched_at_step=branched_at_step
        )
        metadata.agents = parent_metadata.agents
        metadata.current_step = branched_at_step
        metadata.total_steps = branch_config.get('total_steps', parent_metadata.total_steps)
        # Save the full branch config instead of just the path
        metadata.experiment_config = branch_config
        metadata.status = "created"
        
        # Save branch metadata
        self._save_metadata(target_dir, metadata)
        
        # Update parent's children list
        parent_metadata.children.append(target_id)
        self._save_metadata(parent_dir, parent_metadata)
        
        # Log branch creation
        logger_instance = CentralizedLogger(target_dir)
        logger_instance.log_timeline_event(
            step=branched_at_step,
            event_type="branch_created",
            description=f"Branched from {parent_id} with type {branch_type}",
            data={"parent_id": parent_id, "branch_type": branch_type}
        )
        
        logger.info(f"Created branch simulation: {target_id}")
        return metadata
    
    def get_simulation_tree(self, root_id: str) -> Dict:
        """Get the full tree structure of a simulation and its branches"""
        root_dir = self.simulations_root / root_id
        if not root_dir.exists():
            raise ValueError(f"Simulation {root_id} not found")
        
        def build_tree(sim_id: str) -> Dict:
            sim_dir = self.simulations_root / sim_id
            if not sim_dir.exists():
                return {"id": sim_id, "status": "not_found", "children": []}
            
            metadata = self._load_metadata(sim_dir)
            
            tree = {
                "id": sim_id,
                "parent": metadata.parent_simulation,
                "branch_type": metadata.branch_type,
                "branched_at_step": metadata.branched_at_step,
                "current_step": metadata.current_step,
                "total_steps": metadata.total_steps,
                "status": metadata.status,
                "agents": metadata.agents,
                "children": []
            }
            
            for child_id in metadata.children:
                tree["children"].append(build_tree(child_id))
            
            return tree
        
        return build_tree(root_id)
    
    def get_logger(self, simulation_id: str) -> CentralizedLogger:
        """Get centralized logger for a simulation"""
        sim_dir = self.simulations_root / simulation_id
        if not sim_dir.exists():
            raise ValueError(f"Simulation {simulation_id} not found")
        
        return CentralizedLogger(sim_dir)
    
    def update_simulation_status(self, simulation_id: str, status: str, current_step: int = None):
        """Update simulation status and progress"""
        sim_dir = self.simulations_root / simulation_id
        if not sim_dir.exists():
            raise ValueError(f"Simulation {simulation_id} not found")
        
        metadata = self._load_metadata(sim_dir)
        metadata.status = status
        if current_step is not None:
            metadata.current_step = current_step
        
        self._save_metadata(sim_dir, metadata)
        logger.info(f"Updated {simulation_id}: status={status}, step={current_step}")
    
    def _save_metadata(self, sim_dir: Path, metadata: SimulationMetadata):
        """Save metadata to simulation directory"""
        metadata_file = sim_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def _load_metadata(self, sim_dir: Path) -> SimulationMetadata:
        """Load metadata from simulation directory"""
        metadata_file = sim_dir / "metadata.json"
        if not metadata_file.exists():
            raise ValueError(f"No metadata found in {sim_dir}")
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        return SimulationMetadata.from_dict(data)
    
    def list_simulations(self) -> List[Dict]:
        """List all simulations with basic info"""
        simulations = []
        
        for sim_dir in self.simulations_root.iterdir():
            if sim_dir.is_dir() and (sim_dir / "metadata.json").exists():
                try:
                    metadata = self._load_metadata(sim_dir)
                    simulations.append({
                        "id": metadata.simulation_id,
                        "parent": metadata.parent_simulation,
                        "branch_type": metadata.branch_type,
                        "status": metadata.status,
                        "current_step": metadata.current_step,
                        "total_steps": metadata.total_steps,
                        "agents": metadata.agents
                    })
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {sim_dir}: {e}")
        
        return simulations
    
    def cleanup_old_simulations(self, keep_days: int = 30):
        """Clean up old simulations (optional maintenance)"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        
        for sim_dir in self.simulations_root.iterdir():
            if sim_dir.is_dir() and (sim_dir / "metadata.json").exists():
                try:
                    metadata = self._load_metadata(sim_dir)
                    branch_date = datetime.datetime.strptime(
                        metadata.branch_timestamp.split('_')[0], '%Y-%m-%d'
                    )
                    
                    if branch_date < cutoff_date and metadata.status in ["completed", "failed"]:
                        logger.info(f"Cleaning up old simulation: {metadata.simulation_id}")
                        shutil.rmtree(sim_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup {sim_dir}: {e}")

# Global instance for easy access
simulation_manager = SimulationManager()