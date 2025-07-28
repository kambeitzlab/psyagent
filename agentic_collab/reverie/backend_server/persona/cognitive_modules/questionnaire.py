# persona/cognitive_modules/questionnaire.py
import json
from datetime import datetime
import random

class Questionnaire:
    def __init__(self, name, questions, scoring_system):
        self.name = name
        self.questions = questions
        self.scoring_system = scoring_system
    
    def administer(self, persona, timestamp):
        """
        Administer the questionnaire to a persona and get their responses
        """
        responses = []
        
        for i, question in enumerate(self.questions):
            # Get a response based on the persona's current state
            response_value = self.get_simulated_response(persona, question)
            
            responses.append({
                'item_number': i + 1,
                'question': question['text'],
                'response': response_value,
                'timestamp': timestamp.isoformat()
            })
        
        total_score = self.calculate_score(responses)
        
        # Create the result with both individual responses and total score
        result = {
            'questionnaire': self.name,
            'responses': responses,
            'total_score': total_score,
            'timestamp': timestamp.isoformat(),
            'agent': persona.name,
            'severity': self.interpret_score(total_score)
        }
        
        return result
    
    def get_simulated_response(self, persona, question):
        """Simulate responses based on persona's current emotional state"""
        # Check for recent negative events
        recent_negative_events = 0
        if hasattr(persona, 'a_mem') and hasattr(persona.a_mem, 'event_list'):
            for event in persona.a_mem.event_list[-20:]:  # Check last 20 events
                if 'negative' in event.get('keywords', []) or 'upsetting' in event.get('description', '').lower():
                    recent_negative_events += 1
        
        # Base probabilities
        if recent_negative_events > 0:
            # More likely to report symptoms if recent negative events
            weights = [0.2, 0.3, 0.3, 0.2]  # 0, 1, 2, 3
        else:
            # Less likely to report symptoms without negative events
            weights = [0.6, 0.2, 0.1, 0.1]  # 0, 1, 2, 3
        
        # Adjust based on question type (some questions might be more sensitive)
        if "thoughts that you would be better off dead" in question['text'].lower():
            # Lower probability for severe symptoms
            weights = [0.8, 0.15, 0.04, 0.01]
        
        return random.choices([0, 1, 2, 3], weights=weights)[0]
    
    def calculate_score(self, responses):
        """Calculate total score"""
        return sum(response['response'] for response in responses)
    
    def interpret_score(self, score):
        """Interpret PHQ-9 scores based on standard ranges"""
        if score <= 4:
            return "minimal depression"
        elif score <= 9:
            return "mild depression"
        elif score <= 14:
            return "moderate depression"
        elif score <= 19:
            return "moderately severe depression"
        else:
            return "severe depression"

class PHQ9(Questionnaire):
    def __init__(self):
        questions = [
            {
                'text': 'Little interest or pleasure in doing things',
                'short_name': 'anhedonia'
            },
            {
                'text': 'Feeling down, depressed, or hopeless',
                'short_name': 'depressed_mood'
            },
            {
                'text': 'Trouble falling or staying asleep, or sleeping too much',
                'short_name': 'sleep_problems'
            },
            {
                'text': 'Feeling tired or having little energy',
                'short_name': 'fatigue'
            },
            {
                'text': 'Poor appetite or overeating',
                'short_name': 'appetite'
            },
            {
                'text': 'Feeling bad about yourself - or that you are a failure or have let yourself or your family down',
                'short_name': 'guilt'
            },
            {
                'text': 'Trouble concentrating on things, such as reading the newspaper or watching television',
                'short_name': 'concentration'
            },
            {
                'text': 'Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual',
                'short_name': 'psychomotor'
            },
            {
                'text': 'Thoughts that you would be better off dead, or of hurting yourself',
                'short_name': 'suicidal_ideation'
            }
        ]
        
        super().__init__('PHQ-9', questions, 'sum')

class GAD7(Questionnaire):
    def __init__(self):
        questions = [
            {
                'text': 'Feeling nervous, anxious, or on edge',
                'short_name': 'nervous'
            },
            {
                'text': 'Not being able to stop or control worrying',
                'short_name': 'control_worry'
            },
            {
                'text': 'Worrying too much about different things',
                'short_name': 'excessive_worry'
            },
            {
                'text': 'Trouble relaxing',
                'short_name': 'trouble_relaxing'
            },
            {
                'text': 'Being so restless that it is hard to sit still',
                'short_name': 'restless'
            },
            {
                'text': 'Becoming easily annoyed or irritable',
                'short_name': 'irritable'
            },
            {
                'text': 'Feeling afraid, as if something awful might happen',
                'short_name': 'afraid'
            }
        ]
        
        super().__init__('GAD-7', questions, 'sum')
    
    def interpret_score(self, score):
        """Interpret GAD-7 scores"""
        if score <= 4:
            return "minimal anxiety"
        elif score <= 9:
            return "mild anxiety"
        elif score <= 14:
            return "moderate anxiety"
        else:
            return "severe anxiety"

class K10(Questionnaire):
    def __init__(self):
        questions = [
            {
                'text': 'During the last 30 days, about how often did you feel tired out for no good reason?',
                'short_name': 'tired'
            },
            {
                'text': 'During the last 30 days, about how often did you feel nervous?',
                'short_name': 'nervous'
            },
            {
                'text': 'During the last 30 days, about how often did you feel so nervous that nothing could calm you down?',
                'short_name': 'extreme_nervous'
            },
            {
                'text': 'During the last 30 days, about how often did you feel hopeless?',
                'short_name': 'hopeless'
            },
            {
                'text': 'During the last 30 days, about how often did you feel restless or fidgety?',
                'short_name': 'restless'
            },
            {
                'text': 'During the last 30 days, about how often did you feel so restless you could not sit still?',
                'short_name': 'extreme_restless'
            },
            {
                'text': 'During the last 30 days, about how often did you feel depressed?',
                'short_name': 'depressed'
            },
            {
                'text': 'During the last 30 days, about how often did you feel that everything was an effort?',
                'short_name': 'effort'
            },
            {
                'text': 'During the last 30 days, about how often did you feel so sad that nothing could cheer you up?',
                'short_name': 'sad'
            },
            {
                'text': 'During the last 30 days, about how often did you feel worthless?',
                'short_name': 'worthless'
            }
        ]
        
        super().__init__('K10', questions, 'sum')
    
    def get_simulated_response(self, persona, question):
        """K10 uses 1-5 scale instead of 0-3"""
        # Similar logic but with 1-5 scale
        recent_negative_events = 0
        if hasattr(persona, 'a_mem') and hasattr(persona.a_mem, 'event_list'):
            for event in persona.a_mem.event_list[-20:]:
                if 'negative' in event.get('keywords', []) or 'upsetting' in event.get('description', '').lower():
                    recent_negative_events += 1
        
        if recent_negative_events > 0:
            weights = [0.1, 0.2, 0.3, 0.3, 0.1]  # 1-5
        else:
            weights = [0.5, 0.3, 0.1, 0.08, 0.02]  # 1-5
        
        return random.choices([1, 2, 3, 4, 5], weights=weights)[0]
    
    def interpret_score(self, score):
        """Interpret K10 scores"""
        if score < 20:
            return "likely to be well"
        elif score <= 24:
            return "mild mental disorder"
        elif score <= 29:
            return "moderate mental disorder"
        else:
            return "severe mental disorder"