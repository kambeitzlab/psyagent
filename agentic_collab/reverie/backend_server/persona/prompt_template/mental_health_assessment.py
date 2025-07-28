"""
persona/prompt_template/mental_health_assessment.py
Prompt template for mental health assessment
"""

import re
from persona.prompt_template.gpt_structure import get_prompt_template

def run_gpt_prompt_mental_health_assessment(prompt):
    """
    Run the GPT prompt for mental health assessment.
    
    Args:
        prompt: The assessment prompt
        
    Returns:
        GPT's response to the prompt
    """
    prompt_template = get_prompt_template("mental_health_assessment")
    prompt_input = {
        "prompt": prompt
    }
    return run_gpt_prompt(prompt_template, prompt_input)