# 🚀 PsyAgent Quick Start Guide

## Overview

PsyAgent is a psychological research platform that simulates AI agents with realistic behaviors and mental health outcomes. This guide will walk you through setting up the platform and running your first mental health simulation.

## Prerequisites

- **Python 3.9 or higher** (Python 3.9.12 recommended)
- **OpenAI API account** with API key  
- **8GB+ RAM** (16GB recommended)
- **5GB+ disk space**
- **Python code editor** (VSCode, Spyder, PyCharm, or similar - optional but recommended)

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Create virtual environment
python -m venv psyagent-env

# Activate environment
# On Windows:
psyagent-env\Scripts\activate

# On macOS/Linux:
source psyagent-env/bin/activate
```

You should see `(psyagent-env)` in your terminal prompt.

## Step 2: Download and Install PsyAgent

### 2.1 Clone Repository

```bash
git clone https://github.com/yourusername/psyagent.git
cd psyagent
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This may take 3-5 minutes to download and install all packages.

## Step 3: Configure OpenAI API

### 3.1 Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. **Copy the key immediately** (you won't see it again)

### 3.2 Configure API Settings

1. **Copy the example config:**
   ```bash
   cp openai_config.json.example openai_config.json
   ```

2. **Edit the configuration file:**
   ```bash
   # On Windows, use notepad:
   notepad openai_config.json
   
   # On macOS/Linux, use any text editor:
   nano openai_config.json
   ```

3. **Replace the placeholder with your API key:**
   ```json
   {
       "client": "openai",
       "model": "gpt-4o-mini",
       "model-key": "YOUR_API_KEY_HERE",
       "model-costs": {
           "input": 0.15,
           "output": 0.60
       },
       "embeddings": "text-embedding-3-small",
       "cost-upperbound": 10
   }
   ```

   **Important:** Replace `YOUR_API_KEY_HERE` with your actual OpenAI API key.

## Step 4: Test Installation

```bash
python -c "from simulation_interface import create_simulation; print('✅ Installation successful!')"
```

If you see "✅ Installation successful!", you're ready to proceed!

## Step 5: Run Your First Simulation

### 5.1 Run the Demo

You can run the demo in two ways:

**Option A: Using a Python Code Editor (Recommended)**
1. Open your Python code editor (VSCode, Spyder, PyCharm, etc.)
2. Open the file: `examples/psyagent_short_demo_01.py`
3. Make sure your `psyagent-env` virtual environment is selected
4. Run the file using your editor's run button or command

**Option B: From Terminal**
```bash
python examples/psyagent_short_demo_01.py
```

### 5.2 What the Demo Does

The demo runs two connected simulations:

1. **Baseline Simulation (3 days)**
   - AI agent "Maria Lopez" goes through normal daily activities
   - PHQ-9 depression assessments administered daily
   - Establishes baseline mental health scores

2. **Trauma + Therapy Simulation (5 days)**
   - Continues from baseline simulation
   - Day 1: Maria witnesses a traumatic accident
   - Day 1: Emergency therapy session
   - Day 3 & 5: Follow-up therapy sessions
   - Daily PHQ-9 assessments track recovery

### 5.3 Expected Output

```
🚀 PSYAGENT SHORT DEMO
============================================================

📋 Define Baseline Simulation
----------------------------------------
✅ Baseline Study Configuration:
   Name: Baseline_Simulation_01
   Duration: 3 days
   Agent: Maria Lopez
   Assessments: Daily PHQ-9

🔄 Running baseline simulation...
✅ Baseline simulation completed!

📋 Define Simulation with Adverse Event and Therapy
----------------------------------------
✅ Therapy Study Configuration:
   Name: Trauma_and_Therapy_Simulation_01
   Duration: 5 days
   Events: 1 trauma + 3 therapy sessions
   Assessments: Daily PHQ-9

🔄 Running trauma + therapy simulation...
✅ Therapy simulation completed!

📊 Analysis Results:
   absolute_step  study_day  total_score       timestamp
0             23          1           3     2024-01-15T...
1             47          2           4     2024-01-16T...
2             71          3           5     2024-01-17T...
...
```

### 5.4 Simulation Time

- **Baseline simulation:** ~5-10 minutes
- **Trauma + therapy simulation:** ~10-15 minutes
- **Total runtime:** ~15-25 minutes
- **Estimated API cost:** $2-5 USD

## Step 6: Understanding Results

### 6.1 Output Files

Results are saved in:
```
simulations/
├── Baseline_Simulation_01/
│   ├── assessment_results/
│   │   └── Maria_Lopez/
│   │       ├── PHQ-9_step_23.json
│   │       ├── PHQ-9_step_47.json
│   │       └── PHQ-9_step_71.json
│   └── simulation_logs/
└── Trauma_and_Therapy_Simulation_01/
    ├── assessment_results/
    │   └── Maria_Lopez/
    │       ├── PHQ-9_step_95.json  # Day 4
    │       ├── PHQ-9_step_119.json # Day 5
    │       └── ... (continues from baseline)
    └── simulation_logs/
```

### 6.2 PHQ-9 Scores

- **0-4:** Minimal depression
- **5-9:** Mild depression  
- **10-14:** Moderate depression
- **15-19:** Moderately severe depression
- **20-27:** Severe depression

### 6.3 Expected Pattern

- **Baseline:** Low, stable scores (2-5)
- **Post-trauma:** Spike in scores (8-15)
- **Post-therapy:** Gradual decrease (therapy effectiveness)

## Troubleshooting

### Common Issues

**1. "ImportError: No module named..."**
```bash
# Ensure virtual environment is activated
source psyagent-env/bin/activate  # macOS/Linux
# or
psyagent-env\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**2. "OpenAI API Error"**
- Check your API key is correct in `openai_config.json`
- Verify you have API credits in your OpenAI account
- Ensure no extra spaces in the API key

**3. "Permission Denied" / File Access Errors**
```bash
# On macOS/Linux, fix permissions:
chmod +x examples/psyagent_short_demo_01.py

# Run from correct directory:
cd psyagent
python examples/psyagent_short_demo_01.py
```

**4. High API Costs**
- The demo uses `gpt-4o-mini` (cost-effective)
- Adjust `cost-upperbound` in config to limit spending
- Monitor usage at [platform.openai.com/usage](https://platform.openai.com/usage)

### Getting Help

- **Issues:** [GitHub Issues](https://github.com/yourusername/psyagent/issues)
- **Documentation:** See `docs/` folder
- **Examples:** See `examples/` folder for more demos

## Next Steps

After running the demo successfully:

1. **Explore more examples:** `examples/` folder contains various research scenarios
2. **Read the tutorial:** `docs/TUTORIAL.md` for advanced usage
3. **Create custom studies:** Use the `simulation_interface` to design your own research
4. **Analyze data:** Import results into R, Python, or SPSS for statistical analysis

---

This setup guide should take **15-30 minutes** to complete and will have you running your first psychological AI simulation!