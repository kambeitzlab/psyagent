# 🧠 AI Agent Psychological Research Platform

A comprehensive simulation platform for conducting psychological research with AI agents, built on Stanford's "Generative Agents" framework. This platform enables researchers to study mental health, trauma responses, therapeutic interventions, and behavioral patterns through realistic AI agent simulations.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Getting Started

**New to PsyAgent?** Start with our [**Quick Start Guide**](QUICK_START.md) for step-by-step setup instructions and your first simulation!

## 🎯 Overview

This platform provides a simple, user-friendly interface for creating complex psychological research studies with AI agents. Researchers can:

- **Design Multi-Phase Studies**: Create baseline → experimental → follow-up study designs
- **Administer Assessments**: Deploy standardized questionnaires (PHQ-9, GAD-7, K10) 
- **Study Interventions**: Implement trauma events, therapy sessions, and behavioral modifications
- **Analyze Behavior**: Track psychological responses and behavioral changes over time
- **Generate Research Data**: Export results for statistical analysis and publication

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/kambeitzlab/ai-agent-psychological-research.git
cd ai-agent-psychological-research

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API
cp openai_config.json.example openai_config.json
# Edit openai_config.json with your API key
```

### 2. Run Your First Study

```python
from simulation_interface import *

# Create a 3-day baseline study
baseline = create_simulation()
baseline.name = "My_First_Study"
baseline.duration_in_days = 3
baseline.agents = ["Maria Lopez"]
baseline.assessments = [
    AssessmentConfig(
        name="PHQ-9",
        steps=baseline.daily_assessment_steps(3),
        description="Daily depression assessment"
    )
]

# Run the simulation
baseline.run()
```

### 3. Analyze Results

```python
import pandas as pd
from pathlib import Path

# Load assessment data
assessment_dir = Path("simulations/My_First_Study/assessment_results/Maria_Lopez")
data = []

for file in assessment_dir.glob("PHQ-9_*.json"):
    with open(file) as f:
        result = json.load(f)
        step = int(file.stem.split('_step')[-1])
        score = sum(r['score'] for r in result['responses'].values())
        data.append({'study_day': step // 96 + 1, 'phq9_score': score})

df = pd.DataFrame(data)
print(df)
```

## 📚 Key Features

### Simple Interface
- **Direct Property Access**: `simulation.name = "My Study"`
- **Intuitive Configuration**: No complex nested objects
- **One-Line Execution**: `simulation.run()`

### Advanced Research Capabilities
- **Continuous Timeline**: Absolute step counting across study phases
- **Branched Designs**: Create control, trauma-only, and therapy conditions
- **Realistic AI Behavior**: Agents with memory, personality, and social interactions
- **Clinical Assessments**: Validated psychological questionnaires

### Research-Ready Output
- **Structured Data**: JSON and CSV export formats
- **Statistical Analysis**: Compatible with R, Python, SPSS
- **Visualization**: Built-in plotting capabilities
- **Reproducible**: Complete simulation state preservation

## 🔬 Example Studies

### Trauma Response Study
```python
# Study trauma impact on depression scores
trauma_study = create_simulation()
trauma_study.name = "Trauma_Response_Study"
trauma_study.origin = "Baseline_Study"  # Branch from baseline
trauma_study.duration_in_days = 5
trauma_study.type = "trauma_only"

trauma_study.events = [
    EventConfig(
        name="car_accident",
        step=trauma_study.time_to_step(1, 10),
        event_type="negative",
        target_agent="Maria Lopez",
        description="Maria witnesses a severe car accident..."
    )
]

trauma_study.assessments = [
    AssessmentConfig(
        name="PHQ-9",
        steps=trauma_study.daily_assessment_steps(5),
        description="Daily PHQ-9 post-trauma"
    )
]

trauma_study.run()
```

### Therapy Intervention Study
```python
# Study therapeutic effectiveness
therapy_study = create_simulation()
therapy_study.name = "Therapy_Intervention_Study"
therapy_study.origin = "Baseline_Study"
therapy_study.duration_in_days = 10
therapy_study.type = "trauma_therapy"

therapy_study.events = [
    # Trauma event
    EventConfig(
        name="workplace_incident",
        step=therapy_study.time_to_step(1, 9),
        event_type="negative",
        target_agent="Maria Lopez",
        description="Workplace trauma event"
    ),
    # Therapy sessions
    EventConfig(
        name="therapy_session_1",
        step=therapy_study.time_to_step(1, 16),
        event_type="therapy",
        target_agent="Maria Lopez",
        description="Emergency therapy session"
    ),
    # Additional sessions...
]

therapy_study.run()
```

## 📊 Assessment Tools

### Supported Questionnaires
- **PHQ-9**: Depression severity assessment
- **GAD-7**: Generalized anxiety disorder scale
- **K10**: Kessler psychological distress scale
- **Custom**: Define your own assessment instruments

### Assessment Configuration
```python
# Daily assessments
AssessmentConfig(
    name="PHQ-9",
    steps=simulation.daily_assessment_steps(7),  # Daily for 7 days
    description="Daily depression monitoring"
)

# Custom timing
AssessmentConfig(
    name="GAD-7",
    steps=[simulation.time_to_step(1, 12),      # Day 1, 12 PM
           simulation.time_to_step(7, 18)],     # Day 7, 6 PM
    description="Pre/post anxiety assessment"
)
```

## 🔧 Architecture

### Core Components
- **Simulation Interface** (`simulation_interface.py`): User-friendly research interface
- **Agent Engine** (`agentic_collab/reverie/`): AI agent simulation system
- **Assessment System** (`persona/cognitive_modules/assess.py`): Psychological evaluation
- **Memory System**: Three-tier memory architecture (associative, spatial, scratch)
- **Planning System**: Hierarchical planning (daily → hourly → task)

### Data Flow
```
User Configuration → Simulation Manager → Agent Engine → Assessment System → Results Database
```

## 📁 Repository Structure

```
ai-agent-psychological-research/
├── README.md                          # This file
├── simulation_interface.py            # Main user interface
├── requirements.txt                   # Python dependencies
├── openai_config.json.example        # API configuration template
├── docs/                              # Documentation
│   ├── TUTORIAL.md                    # Complete tutorial
│   ├── API_REFERENCE.md               # API documentation
│   └── EXAMPLES.md                    # Example studies
├── examples/                          # Example scripts
│   ├── quick_start_example.py         # Basic usage
│   ├── trauma_study_example.py        # Trauma research
│   └── therapy_intervention_example.py # Therapy studies
├── tests/                             # Test files
│   └── test_simulation_interface.py   # Interface tests
└── agentic_collab/                    # Core simulation engine
    └── reverie/backend_server/        # Backend components
```

## 🛠️ Installation & Setup

### System Requirements
- Python 3.9 or higher
- OpenAI API access with GPT-4 or GPT-3.5-turbo
- 8GB+ RAM (16GB recommended for large studies)
- 10GB+ disk space for simulation data

### Detailed Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/kambeitzlab/ai-agent-psychological-research.git
   cd ai-agent-psychological-research
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OpenAI API**
   ```bash
   cp openai_config.json.example agentic_collab/openai_config.json
   ```
   
   Edit the configuration file:
   ```json
   {
     "client": "openai",
     "model": "gpt-4o-mini",
     "model-key": "your-api-key-here",
     "model-costs": {"input": 0.5, "output": 1.5},
     "embeddings": "text-embedding-3-small",
     "cost-upperbound": 10
   }
   ```

5. **Test Installation**
   ```bash
   cd agentic_collab/reverie/backend_server
   python -c "from simulation_interface import create_simulation; print('✅ Installation successful!')"
   ```

## 📖 Documentation

- **[Complete Tutorial](docs/TUTORIAL.md)**: Step-by-step guide to creating studies
- **[Quick Start Guide](examples/quick_start_example.py)**: Ready-to-run examples
- **[API Reference](docs/API_REFERENCE.md)**: Detailed function documentation
- **[Example Studies](docs/EXAMPLES.md)**: Real research use cases

## 🎓 Tutorials

### Basic Usage
```bash
cd agentic_collab/reverie/backend_server
python simulation_tutorial.py  # Interactive tutorial
```

### Example Studies
```bash
python examples/quick_start_example.py        # Basic 3-day study
python examples/trauma_study_example.py       # Trauma response research
python examples/therapy_intervention_example.py # Therapy effectiveness
```

## 🔬 Research Applications

### Published Studies
This platform has been used for research in:
- Trauma response patterns in AI agents
- Therapeutic intervention effectiveness
- Depression and anxiety assessment validation
- Social behavior and memory formation

### Research Domains
- **Clinical Psychology**: Depression, anxiety, PTSD assessment
- **Behavioral Science**: Social interaction, decision-making
- **Computational Psychiatry**: Mental health modeling
- **Human-AI Interaction**: Agent behavior studies

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Development installation
git clone https://github.com/kambeitzlab/ai-agent-psychological-research.git
cd ai-agent-psychological-research
pip install -e .

# Run tests
python -m pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Principal Investigator**: [Dr. Joseph Kambeitz](mailto:joseph.kambeitz@your-institution.edu)
- **Lab Website**: [kambeitzlab.org](https://kambeitzlab.org)
- **Issues**: [GitHub Issues](https://github.com/kambeitzlab/ai-agent-psychological-research/issues)

## 🙏 Acknowledgments

- Built on Stanford's "Generative Agents" framework
- OpenAI GPT models for agent cognition
- Research supported by [Your Institution/Grants]

## 📈 Citation

If you use this platform in your research, please cite:

```bibtex
@software{kambeitz_ai_agent_psych_2024,
  title={AI Agent Psychological Research Platform},
  author={Kambeitz, Joseph and Contributors},
  year={2024},
  url={https://github.com/kambeitzlab/ai-agent-psychological-research},
  version={1.0}
}
```

---

**Made with ❤️ by the Kambeitz Lab for advancing psychological science through AI**