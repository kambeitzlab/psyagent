import datetime

class AssessmentScheduler:
    def __init__(self):
        self.scheduled_assessments = []
        self.completed_assessments = set()
    
    def add_schedule(self, questionnaire_name, agent_name, time_str, frequency):
        """Add a questionnaire schedule"""
        scheduled_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        self.scheduled_assessments.append({
            'questionnaire': questionnaire_name,
            'agent': agent_name,
            'time': scheduled_time,
            'frequency': frequency
        })
    
    def load_from_config(self, config):
        """Load schedules from a configuration"""
        if 'questionnaires' in config:
            for q_config in config['questionnaires']:
                for agent in q_config['target_agents']:
                    self.add_schedule(
                        q_config['name'],
                        agent,
                        q_config['time'],
                        q_config['frequency']
                    )
    
    def get_due_assessments(self, current_datetime):
        """Get assessments that are due at the current datetime"""
        current_time = current_datetime.time()
        current_date = current_datetime.date()
        current_minute = current_time.hour * 60 + current_time.minute
        
        due_assessments = []
        
        for schedule in self.scheduled_assessments:
            scheduled_time = schedule['time']
            scheduled_minute = scheduled_time.hour * 60 + scheduled_time.minute
            
            # Calculate a unique ID for this assessment instance
            assessment_id = f"{schedule['agent']}_{schedule['questionnaire']}_{current_date.isoformat()}"
            
            # Check if this assessment is due at this exact time
            # Using a 5-minute window to account for simulation step timing
            time_diff = current_minute - scheduled_minute
            
            if 0 <= time_diff < 5 and assessment_id not in self.completed_assessments:
                due_assessments.append({
                    'agent': schedule['agent'],
                    'questionnaire': schedule['questionnaire'],
                    'assessment_id': assessment_id,
                    'scheduled_time': scheduled_time
                })
        
        return due_assessments
    
    def mark_completed(self, assessment_id):
        """Mark an assessment as completed"""
        self.completed_assessments.add(assessment_id)