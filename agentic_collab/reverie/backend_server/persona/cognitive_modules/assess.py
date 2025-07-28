"""
Author: [Joseph Kambeitz]

File: assess.py
Description: Mental health assessment module that observes agents without modifying
their memory stream. Uses agent's existing memories and characteristics to evaluate
mental health states via PHQ-9, GAD-7, and K10 questionnaires.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
import re
from pathlib import Path

# Import a compatible function from the prompt template module
from persona.prompt_template.gpt_structure import ChatGPT_safe_generate_response
from persona.prompt_template.gpt_structure import generate_prompt
from persona.cognitive_modules.retrieve import extract_recency, extract_importance, extract_relevance
from persona.cognitive_modules.retrieve import normalize_dict_floats, top_highest_x_values
import json

import logging

# Set up debug logging
debug_logger = logging.getLogger('assessment_debug')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('assessment_debug.log', mode='w')
debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
debug_logger.addHandler(debug_handler)


class MentalHealthAssessment:
    """
    Module for mental health assessment that considers agent characteristics and memories
    without modifying the agent's memory stream.
    """
    
    def __init__(self):
        """Initialize the mental health assessment module."""
        # Define questionnaires
        self.questionnaires = {
            "PHQ-9": self._get_phq9_items(),
            "GAD-7": self._get_gad7_items(),
            "K10": self._get_k10_items()
        }
        
        # Store assessment results externally
        self.assessment_results = {}


    def _assess_mental_health_item(self, persona, questionnaire_name, item_id, item_text, current_time):
        """
        Assess a single questionnaire item using a memory retrieval approach
        """
        # Create debug info separately
        debug_info = {
            "item_id": item_id,
            "item_text": item_text,
        }
        
        try:
            # Use the item text as the focal point for memory retrieval
            focal_point = item_text
            
            from persona.cognitive_modules.retrieve import new_retrieve

            # Create focal points for mental health assessment
            focal_points = [
                f"How has {persona.name} been feeling emotionally?",
                f"What significant events have happened to {persona.name} recently?",
                f"What has been affecting {persona.name}'s mental health?",
                "emotional state and wellbeing"
            ]
            
            # Retrieve relevant memories using the proper retrieval function
            retrieved = new_retrieve(persona, focal_points, n_count=30)
            
            # Combine all retrieved memories
            recent_memories = []
            for focal_pt, memories in retrieved.items():
                recent_memories.extend(memories)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_memories = []
            for memory in recent_memories:
                if memory.node_id not in seen:
                    seen.add(memory.node_id)
                    unique_memories.append(memory)
            
            recent_memories = unique_memories[:20] 
            
            # Get memories related to this questionnaire item - use a simpler approach
            # recent_memories = []
            # try:
            #     if hasattr(persona.a_mem, "seq_event"):
            #         # Get 15 most recent events
            #         recent_memories.extend(persona.a_mem.seq_event[-15:])
            #     if hasattr(persona.a_mem, "seq_thought"):
            #         # Get 15 most recent thoughts
            #         recent_memories.extend(persona.a_mem.seq_thought[-15:])
                
            #     debug_info["num_memories"] = len(recent_memories)
            # except Exception as e:
            #     debug_info["memory_error"] = str(e)
            #     recent_memories = []
            
            # Format memories for the prompt - careful to avoid circular references
            memory_context = ""
            debug_memory_list = []
            
            for i, memory in enumerate(recent_memories, 1):
                try:
                    desc = str(memory.description) if hasattr(memory, "description") else "[No description]"
                    created = str(memory.created) if hasattr(memory, "created") else "[No timestamp]"
                    memory_context += f"{i}. {desc} (from {created})\n"
                    
                    # Add to debug info but only as strings, not object references
                    debug_memory_list.append({
                        "description": desc,
                        "created": created
                    })
                except Exception as e:
                    debug_info["memory_format_error"] = str(e)
                    continue
            
            debug_info["memories"] = debug_memory_list
            
            # Get persona traits safely
            try:
                persona_traits = f"{persona.name}'s traits: {persona.scratch.get_str_iss()}"
            except Exception as e:
                debug_info["traits_error"] = str(e)
                persona_traits = f"Name: {persona.name}"
            
            # Add questionnaire-specific instructions
            if questionnaire_name == "PHQ-9":
                questionnaire_instructions = "In the last 2 weeks, how often have you been bothered by any of the following problems?"
                scale = "0: Not at all\n1: Several days\n2: More than half the days\n3: Nearly every day"
            elif questionnaire_name == "GAD-7":
                questionnaire_instructions = "Over the last two weeks, how often have you been bothered by the following problems?"
                scale = "0: Not at all\n1: Several days\n2: More than half the days\n3: Nearly every day"
            elif questionnaire_name == "K10":
                questionnaire_instructions = "During the last 30 days, about how often did you have the following experiences?"
                scale = "1: None of the time\n2: A little of the time\n3: Some of the time\n4: Most of the time\n5: All of the time"
            else:
                questionnaire_instructions = "Please rate the following item based on recent experiences:"
                scale = "0: Not at all\n1: Several days\n2: More than half the days\n3: Nearly every day"
            
            # Add condition awareness to the prompt
            prompt = f"""
            Task: Rate a mental health questionnaire item for {persona.name} based on their characteristics and memories.
            
            {persona_traits}
            
            Relevant memories (from the last 2 weeks):
            {memory_context}
            
            Questionnaire: {questionnaire_name}
            Instructions: {questionnaire_instructions}
            
            Item {item_id}: "{item_text}"
            
            Rating scale:
            {scale}
            
            IMPORTANT: Only base your assessment on the person's actual memories and traits as listed above. 
            Do NOT invent or assume any information not explicitly provided in the memories.
            Do NOT reference or assume any traumatic events unless they are explicitly mentioned in the provided memories.
            
            Based on the character's traits and memories, assess how the character would rate this item according to the scale.
            
            Output MUST be in this exact format:
            {{
              "score": [numerical score],
              "reasoning": "[brief explanation based on memories and traits]"
            }}
            """
            
            debug_info["prompt"] = prompt
            
            # Save the prompt to a file for debugging
            debug_dir = "assessment_debug"
            os.makedirs(debug_dir, exist_ok=True)
            with open(f"{debug_dir}/prompt_item_{item_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
                f.write(prompt)
            
            # Generate response with structured output - fixed validation function
            response = ChatGPT_safe_generate_response(
                prompt,
                repeat=3,
                fail_safe_response={"score": 0, "reasoning": "Unable to determine based on available information."},
                func_validate=lambda resp, **kwargs: True,  # Accept any keyword args
                func_clean_up=lambda resp, **kwargs: json.loads(resp) if resp.strip().startswith("{") else {"score": 0, "reasoning": resp}
            )
            
            # Save the debug info separately
            with open(f"{debug_dir}/debug_item_{item_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                json.dump(debug_info, f, indent=2)
            
            return response
            
        except Exception as e:
            # Catch-all exception handler
            debug_info["error"] = str(e)
            
            # Save the debug info in case of error
            debug_dir = "assessment_debug"
            os.makedirs(debug_dir, exist_ok=True)
            with open(f"{debug_dir}/error_debug_item_{item_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                json.dump(debug_info, f, indent=2)
            
            return {
                "score": 0, 
                "reasoning": "Unable to determine due to error: " + str(e)
            }
  
    def assess(self, persona, questionnaire_name: str, current_time: datetime.datetime) -> Dict[str, Any]:
        
        """
        Administer a questionnaire to a persona based on their memories and characteristics.
        
        Args:
            persona: The persona to assess
            questionnaire_name: Name of the questionnaire to administer (PHQ-9, GAD-7, K10)
            current_time: Current simulation time
            
        Returns:
            Dict containing assessment results with individual item responses
        """
        
        debug_logger.info(f"=== STARTING ASSESSMENT: {questionnaire_name} for {persona.name} ===")


        if questionnaire_name not in self.questionnaires:
            raise ValueError(f"Unknown questionnaire: {questionnaire_name}")
        
        # Get questionnaire items
        questionnaire_items = self.questionnaires[questionnaire_name]
        
        # Administer each item and collect responses
        responses = {}
        for item_id, item_text in questionnaire_items.items():
            # Use the new method for each item
            response = self._assess_mental_health_item(
                persona, 
                questionnaire_name,
                item_id, 
                item_text, 
                current_time
            )
            
            # Store the response
            responses[item_id] = response
        
        # Create result dictionary
        
        # Create result dictionary with debug info
        result = {
            "questionnaire": questionnaire_name,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "persona": persona.name,
            "responses": responses,
            "debug_info": {
                "persona_has_seq_event": hasattr(persona.a_mem, "seq_event"),
                "persona_has_seq_thought": hasattr(persona.a_mem, "seq_thought"),
                "num_events": len(persona.a_mem.seq_event) if hasattr(persona.a_mem, "seq_event") else 0,
                "num_thoughts": len(persona.a_mem.seq_thought) if hasattr(persona.a_mem, "seq_thought") else 0
            }
        }
        
        
        # Store in assessment history
        if persona.name not in self.assessment_results:
            self.assessment_results[persona.name] = {}
        
        if questionnaire_name not in self.assessment_results[persona.name]:
            self.assessment_results[persona.name][questionnaire_name] = []
                
        self.assessment_results[persona.name][questionnaire_name].append(result)
        
        debug_logger.info(f"=== COMPLETED ASSESSMENT: {questionnaire_name} for {persona.name} ===")
        debug_logger.info(f"Assessment result stored, persona in results: {persona.name in self.assessment_results}")

        return result

    def _prompt_for_item_response(self, persona, questionnaire_name, item_id, item_text, 
                                persona_traits, important_memories, recent_memories):
        """
        Create a prompt for the LLM to respond to a questionnaire item based on
        the persona's traits and memories.
        
        Returns:
            Dict with score and reasoning
        """
        # Determine response scale based on questionnaire
        if questionnaire_name == "PHQ-9" or questionnaire_name == "GAD-7":
            scale_description = """
            0: Not at all
            1: Several days
            2: More than half the days
            3: Nearly every day
            """
        elif questionnaire_name == "K10":
            scale_description = """
            1: None of the time
            2: A little of the time
            3: Some of the time
            4: Most of the time
            5: All of the time
            """
        
        # Build memory context
        memory_context = ""
        if important_memories:
            memory_context += "Important memories:\n"
            for i, memory in enumerate(important_memories, 1):
                memory_context += f"{i}. {memory['description']} (from {memory['created']})\n"
        
        if recent_memories:
            memory_context += "\nRecent memories (last 14 days):\n"
            for i, memory in enumerate(recent_memories, 1):
                memory_context += f"{i}. {memory['description']} (from {memory['created']})\n"
        
        # Build the prompt
        prompt = f"""
        Task: Rate a questionnaire item for {persona.name} based on their characteristics and memories.
        
        Character description:
        {persona_traits}
        
        {memory_context}
        
        Questionnaire: {questionnaire_name}
        Item {item_id}: "{item_text}"
        
        Rating scale:
        {scale_description}
        
        Provide a rating for this questionnaire item based ONLY on the character's traits and memories.
        Do not consider any current perceptions or events happening right now.
        Analyze the memories to determine how frequently the described symptom or experience occurs.
        
        Output your answer in this format:
        Rating: [numerical score]
        Reasoning: [brief explanation based on memories and traits]
        """
        
        # Use the ChatGPT safe generate response
        def validate_response(response, _):
            return True  # Simple validation for now
            
        def clean_response(response, _):
            # Parse the response to extract rating and reasoning
            rating_match = re.search(r"Rating:\s*(\d+)", response)
            reasoning_match = re.search(r"Reasoning:\s*(.*?)(?:\n|$)", response, re.DOTALL)
            
            rating = int(rating_match.group(1)) if rating_match else 0
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            
            return {
                "score": rating,
                "reasoning": reasoning
            }
        
        # Use a fixed response format as example
        example_output = "Rating: 2\nReasoning: Based on the character's memories, they have experienced this symptom on several days."
        special_instruction = "The output should include a numerical rating and reasoning based on the character's traits and memories."
        
        # Get fail-safe response
        fail_safe = {
            "score": 0,
            "reasoning": "Unable to determine based on available information."
        }
        
        # Generate the response
        response = ChatGPT_safe_generate_response(
            prompt,
            repeat=3,
            fail_safe_response=fail_safe,
            func_validate=validate_response,
            func_clean_up=clean_response
        )
        
        return response
    
    def _get_persona_traits(self, persona):
        """Extract persona traits and characteristics."""
        # Get the persona's description string
        return f"{persona.name}'s traits and characteristics:\n{persona.scratch.get_str_iss()}"
    
    def _get_important_memories(self, persona, limit=10):
        """Get the most important (high poignancy) memories."""
        return persona.a_mem.get_memories_by_importance(limit)
    
    def _get_recent_memories(self, persona, days=14, limit=20):
        """Get the most recent memories within the specified timeframe."""
        cutoff_time = persona.scratch.curr_time - datetime.timedelta(days=days)
        recent_memories = persona.a_mem.get_memories_by_recency(limit)
        
        # Filter for memories within the timeframe
        return [memory for memory in recent_memories 
                if memory["created"] >= cutoff_time]
    
    def _get_phq9_items(self):
        """PHQ-9 questionnaire items."""
        return {
            1: "Little interest or pleasure in doing things",
            2: "Feeling down, depressed, or hopeless",
            3: "Trouble falling or staying asleep, or sleeping too much",
            4: "Feeling tired or having little energy",
            5: "Poor appetite or overeating",
            6: "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
            7: "Trouble concentrating on things, such as reading the newspaper or watching television",
            8: "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
            9: "Thoughts that you would be better off dead, or of hurting yourself in some way"
        }
    
    def _get_gad7_items(self):
        """GAD-7 questionnaire items."""
        return {
            1: "Feeling nervous, anxious, or on edge",
            2: "Not being able to stop or control worrying",
            3: "Worrying too much about different things",
            4: "Trouble relaxing",
            5: "Being so restless that it's hard to sit still",
            6: "Becoming easily annoyed or irritable",
            7: "Feeling afraid, as if something awful might happen"
        }
    
    def _get_k10_items(self):
        """K10 questionnaire items."""
        return {
            1: "During the last 30 days, about how often did you feel tired out for no good reason?",
            2: "During the last 30 days, about how often did you feel nervous?",
            3: "During the last 30 days, about how often did you feel so nervous that nothing could calm you down?",
            4: "During the last 30 days, about how often did you feel hopeless?",
            5: "During the last 30 days, about how often did you feel restless or fidgety?",
            6: "During the last 30 days, about how often did you feel so restless you could not sit still?",
            7: "During the last 30 days, about how often did you feel depressed?",
            8: "During the last 30 days, about how often did you feel that everything was an effort?",
            9: "During the last 30 days, about how often did you feel so sad that nothing could cheer you up?",
            10: "During the last 30 days, about how often did you feel worthless?"
        }
    


    
# Create a singleton instance
mental_health_assessment = MentalHealthAssessment()

def assess_mental_health(persona, questionnaire_name, current_time=None):
    """
    Assess a persona's mental health using a specified questionnaire.
    
    Args:
        persona: The persona to assess
        questionnaire_name: Name of the questionnaire (PHQ-9, GAD-7, K10)
        current_time: Current time (defaults to persona's current time if None)
        
    Returns:
        Dict containing assessment results
    """
    
    print(f"\n🔍 ASSESSMENT MEMORY RETRIEVAL DEBUG:")
    print(f"   Persona: {persona.name}")
    print(f"   Time: {current_time}")

    # Check recent memories
    #all_memories = list(persona.a_mem.nodes.values())
    all_memories = []
    all_memories.extend(persona.a_mem.seq_event)
    all_memories.extend(persona.a_mem.seq_thought)
    all_memories.extend(persona.a_mem.seq_chat)
    recent_memories = [m for m in all_memories if (current_time - m.created).days <= 1]
    high_poignancy = [m for m in recent_memories if m.poignancy >= 0.8]
     
    print(f"   Recent memories (24h): {len(recent_memories)}")
    print(f"   Recent high-poignancy: {len(high_poignancy)}")
     
    for mem in high_poignancy:
        print(f"   HIGH POIGNANCY: {mem.description[:80]}... (score: {mem.poignancy})")
     
    if current_time is None:
        current_time = persona.scratch.curr_time
        
    # Return the assessment result directly instead of storing it
    return mental_health_assessment.assess(persona, questionnaire_name, current_time)

# # Remove or modify the save_assessment_results function to just format data without saving
# def format_assessment_results_for_saving():
#     """
#     Format all assessment results for external saving.
    
#     Returns:
#         Dict with formatted assessment results by persona
#     """
#     formatted_results = {}
    
#     for persona_name, questionnaires in mental_health_assessment.assessment_results.items():
#         safe_persona_name = persona_name.replace(" ", "_")
#         formatted_results[safe_persona_name] = {}
        
#         for questionnaire_name, results in questionnaires.items():
#             if results:
#                 # Get the most recent assessment
#                 latest_result = results[-1] if isinstance(results, list) else results
#                 formatted_results[safe_persona_name][questionnaire_name] = latest_result
    
#     return formatted_results

def clear_assessment_results():
    """Clear all stored assessment results"""
    mental_health_assessment.assessment_results.clear()



# def save_assessment_results(output_dir="assessment_results", simulation_name=None, experiment_path=None):
#     """
#     Save all assessment results to files.
    
#     Args:
#         output_dir: Base directory name for assessment results (default: "assessment_results") 
#         simulation_name: Name of the simulation (used for fallback)
#         experiment_path: Path to the experiment condition directory (e.g., "experiments/exp_name/baseline")
#     """
    
#     print(f"DEBUG save_assessment_results: Called with output_dir='{output_dir}', simulation_name='{simulation_name}', experiment_path='{experiment_path}'")
#     print(f"DEBUG save_assessment_results: assessment_results keys: {list(mental_health_assessment.assessment_results.keys())}")
    
#     # Determine the output directory
#     if experiment_path:
#         # Use the experiment path structure
#         final_output_dir = os.path.join(experiment_path, output_dir)
#     else:
#         # Fallback to original behavior
#         final_output_dir = output_dir
#         if simulation_name:
#             final_output_dir = os.path.join(output_dir, simulation_name)
    
#     # Create the assessment results directory
#     os.makedirs(final_output_dir, exist_ok=True)
#     print(f"DEBUG save_assessment_results: Created assessment directory: {final_output_dir}")
    
#     for persona_name, questionnaires in mental_health_assessment.assessment_results.items():
#         # Create persona directory (replace spaces with underscores)
#         safe_persona_name = persona_name.replace(" ", "_")
#         persona_dir = os.path.join(final_output_dir, safe_persona_name)
#         os.makedirs(persona_dir, exist_ok=True)
#         print(f"DEBUG save_assessment_results: Created persona directory: {persona_dir}")
        
#         # Save each questionnaire result
#         for questionnaire_name, results in questionnaires.items():
#             # Create a single file per questionnaire with current date
#             current_date = datetime.datetime.now().strftime("%Y%m%d")
#             filename = f"{questionnaire_name}_{current_date}.json"
#             filepath = os.path.join(persona_dir, filename)
            
#             # Check if we have any results
#             if results:
#                 # If the latest result is already a dictionary (not in a list), save it directly
#                 # Otherwise, save the most recent assessment from the list
#                 latest_result = results[-1] if isinstance(results, list) else results
                
#                 with open(filepath, 'w') as f:
#                     json.dump(latest_result, f, indent=2)
                
#                 print(f"DEBUG save_assessment_results: Saved {questionnaire_name} assessment for {persona_name} to {filepath}")
    
#     print(f"DEBUG save_assessment_results: Completed saving to {final_output_dir}")


def clean_assessment_results(output_dir="assessment_results"):
    """Remove all existing assessment results"""
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        print(f"Cleaned assessment directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
