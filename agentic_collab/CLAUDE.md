# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Generative Agents simulation platform** for AI-powered psychological research, built on Stanford's "Generative Agents" paper. The system simulates AI personas with memory, cognition, and social behaviors, extended with mental health assessment capabilities for trauma and therapy research.

## Commands and Development Workflow

### Environment Setup
```bash
# Create conda environment
conda create -n simulacra python=3.9.12 pip
conda activate simulacra
pip install -r requirements.txt

# Configure OpenAI API
# Create openai_config.json with API keys, models, and cost limits
```

### Running Simulations

**Interactive Mode:**
```bash
./run_backend.sh base_the_ville_isabella_maria_klaus simulation-test
# Then use commands like: run 360, headless 100, assess mental health [agent] PHQ-9
```

**Automated Mode:**
```bash
./run_backend_automatic.sh -o base_origin -t target_sim -s 336 --ui None
# Arguments: -o (origin), -t (target), -s (steps), --ui (None/True/False)
```

**Programmatic Execution:**
```python
# Via run_simulation.py
from reverie import run_simulation_programmatically
simulation = run_simulation_programmatically(
    origin_sim="base_sim",
    target_sim="experiment_name", 
    steps=336,
    headless=True
)
```

### Frontend/Backend Architecture
```bash
# Start visualization server (optional for headless mode)
./run_frontend.sh [port]

# Backend simulation engine
./run_backend.sh [origin] [target]
```

## Core Architecture

### Simulation Engine (`reverie.py`)
- **ReverieServer**: Central orchestrator managing simulation state
- **Fork-based system**: New simulations inherit from existing states
- **Step-based time**: Configurable `sec_per_step` for temporal progression
- **Assessment integration**: Mental health questionnaires administered during simulation

### Agent/Persona System (`persona.py`)
**Three-tier memory architecture:**
- **Associative Memory**: Long-term event stream with recency/importance/relevance scoring
- **Spatial Memory**: Tree-structured environment knowledge 
- **Scratch Memory**: Short-term working memory

**Cognitive Modules:**
- `perceive.py`: Environmental attention and awareness
- `retrieve.py`: Memory retrieval with weighted scoring
- `plan.py`: Hierarchical planning (daily → hourly → task decomposition)  
- `reflect.py`: Meta-cognitive analysis and insight generation
- `execute.py`: Action execution and pathfinding
- `converse.py`: Dialogue and social interaction

### Mental Health Research Framework

**Assessment System (`assess.py`, `questionnaire.py`):**
- Non-invasive psychological evaluation using agent memories
- Standardized instruments: PHQ-9 (depression), GAD-7 (anxiety), K10 (distress)
- LLM-powered scoring based on agent's experiences and traits

**Experiment Scheduler (`experiment_scheduler.py`):**
- Step-based event scheduling for controlled studies
- Trauma event administration, therapy session management
- Multi-condition experiment support (baseline, intervention, control)

## Configuration System

### Core Config (`openai_config.json`)
```json
{
    "client": "openai",
    "model": "gpt-4o-mini", 
    "model-key": "<API-KEY>",
    "model-costs": {"input": 0.5, "output": 1.5},
    "embeddings": "text-embedding-3-small",
    "experiment-name": "study_name",
    "cost-upperbound": 10
}
```

### Experiment Configuration (JSON)
```json
{
    "simulation_name": "trauma_study",
    "total_steps": 336,
    "steps_per_hour": 2,
    "questionnaires": [
        {
            "name": "PHQ-9",
            "step": 168,
            "target_agents": ["Isabella Rodriguez"]
        }
    ],
    "timed_events": [
        {
            "name": "trauma_event",
            "step": 50,
            "type": "negative",
            "target": "agent_name",
            "description": "Event description"
        }
    ]
}
```

## Key File Locations

**Simulation Storage:** `environment/frontend_server/storage/[sim_name]/`
**Agent Data:** `personas/[agent_name]/bootstrap_memory/`
**Experiment Results:** `experiment_results/[study_name]/`
**Logs:** `logs/` and `reverie/backend_server/logs/`

## Important Implementation Details

### Memory System Architecture
- **Event-based memory**: Each experience stored as timestamped event with metadata
- **Retrieval scoring**: `recency_score * importance_score * relevance_score`
- **Reflection generation**: Agents periodically synthesize insights from memories
- **Spatial memory**: Hierarchical location knowledge (sector → arena → object)

### Assessment Pipeline
1. **Memory analysis**: Extract recent experiences relevant to questionnaire timeframe
2. **Trait-based scoring**: Use agent's personality and current state  
3. **LLM evaluation**: Generate realistic questionnaire responses
4. **Clinical scoring**: Apply standard scoring algorithms
5. **Result storage**: JSON output with reasoning and severity levels

### Experiment Execution Flow
1. **Configuration loading**: Parse experiment JSON with events and questionnaires
2. **Simulation forking**: Create new simulation from base state
3. **Step-based scheduling**: Execute events at predetermined simulation steps
4. **Assessment administration**: Questionnaires delivered at scheduled intervals
5. **Data collection**: Structured output for statistical analysis

### Simulation Time Management
- **Simulation steps**: Discrete time units (typically 10 minutes of in-game time)
- **Real-time mapping**: `steps_per_hour` controls temporal progression rate
- **Event scheduling**: All events tied to specific simulation steps for reproducibility

This architecture enables controlled psychological research with AI agents that exhibit realistic behavioral patterns and responses to interventions.