#!/usr/bin/env python3
"""
Script to migrate all existing therapy sessions to their corresponding centralized SimulationManager folders
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the reverie backend to path
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

def migrate_all_therapy_sessions():
    """Migrate all existing therapy sessions to centralized locations"""
    
    print("🔄 MIGRATING ALL THERAPY SESSIONS TO CENTRALIZED LOCATIONS")
    print("=" * 70)
    
    # Import simulation manager
    try:
        from simulation_manager import simulation_manager
        print(f"✓ SimulationManager loaded")
        print(f"  Root: {simulation_manager.simulations_root}")
    except Exception as e:
        print(f"❌ Failed to import SimulationManager: {e}")
        return
    
    # Find all therapy sessions in backend logs
    backend_logs_dir = Path("/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server/logs")
    
    all_therapy_sessions = []
    
    # Search in all events.jsonl files
    events_files = list(backend_logs_dir.glob("**/events.jsonl"))
    
    print(f"\n🔍 Searching {len(events_files)} events.jsonl files for therapy sessions...")
    
    for events_file in events_files:
        try:
            with open(events_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        event = json.loads(line.strip())
                        if event.get('event_type') == 'therapy_session':
                            all_therapy_sessions.append({
                                'event_data': event,
                                'source_file': str(events_file),
                                'line_num': line_num,
                                'agent': event.get('agent'),
                                'timestamp': event.get('timestamp'),
                                'exchanges': event.get('details', {}).get('duration', 'unknown')
                            })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"  ⚠️  Error reading {events_file}: {e}")
    
    print(f"✓ Found {len(all_therapy_sessions)} therapy sessions total")
    
    # Group by agent for better organization
    sessions_by_agent = {}
    for session in all_therapy_sessions:
        agent = session['agent']
        if agent not in sessions_by_agent:
            sessions_by_agent[agent] = []
        sessions_by_agent[agent].append(session)
    
    for agent, sessions in sessions_by_agent.items():
        print(f"  📊 {agent}: {len(sessions)} therapy sessions")
    
    # Find all V20 experiment simulations
    v20_simulations = []
    for sim_dir in simulation_manager.simulations_root.iterdir():
        if sim_dir.is_dir() and "trauma_therapy_2week_study_20250726_235204" in sim_dir.name:
            v20_simulations.append(sim_dir)
    
    print(f"\n🎯 Found {len(v20_simulations)} V20 experiment simulations:")
    for sim_dir in v20_simulations:
        condition = sim_dir.name.split('_')[-1]
        print(f"  📁 {condition}: {sim_dir.name}")
    
    # Migrate therapy sessions to each V20 simulation
    for sim_dir in v20_simulations:
        condition = sim_dir.name.split('_')[-1]
        print(f"\n🔄 Migrating therapy sessions to {condition} condition...")
        
        # Create centralized therapy events file
        central_logs_dir = sim_dir / "all_logs"
        central_logs_dir.mkdir(exist_ok=True)
        
        sim_logs_dir = central_logs_dir / "simulation_logs"
        sim_logs_dir.mkdir(exist_ok=True)
        
        therapy_events_file = sim_logs_dir / "therapy_events.jsonl"
        
        # Write all therapy sessions to the centralized file
        sessions_written = 0
        with open(therapy_events_file, 'w', encoding='utf-8') as f:
            for session in all_therapy_sessions:
                # Write the complete therapy session
                f.write(json.dumps(session['event_data'], ensure_ascii=False) + "\n")
                sessions_written += 1
        
        print(f"  ✓ Wrote {sessions_written} therapy sessions to: {therapy_events_file.name}")
        
        # Also append to the main events.jsonl if it exists
        main_events_file = sim_logs_dir / "events.jsonl"
        if main_events_file.exists():
            # Read existing events to avoid duplicates
            existing_events = set()
            try:
                with open(main_events_file, 'r') as f:
                    for line in f:
                        event = json.loads(line.strip())
                        if event.get('event_type') == 'therapy_session':
                            # Create a unique key for this therapy session
                            key = f"{event.get('agent')}_{event.get('timestamp')}"
                            existing_events.add(key)
            except:
                pass
            
            # Append only new therapy sessions
            new_sessions = 0
            with open(main_events_file, 'a', encoding='utf-8') as f:
                for session in all_therapy_sessions:
                    key = f"{session['agent']}_{session['timestamp']}"
                    if key not in existing_events:
                        f.write(json.dumps(session['event_data'], ensure_ascii=False) + "\n")
                        new_sessions += 1
            
            print(f"  ✓ Appended {new_sessions} new therapy sessions to: {main_events_file.name}")
        else:
            # Create new main events file with therapy sessions
            shutil.copy2(therapy_events_file, main_events_file)
            print(f"  ✓ Created new {main_events_file.name} with therapy sessions")
    
    print(f"\n✅ MIGRATION COMPLETED SUCCESSFULLY")
    print(f"📊 Summary:")
    print(f"  • {len(all_therapy_sessions)} therapy sessions found")
    print(f"  • {len(v20_simulations)} V20 simulations updated")
    print(f"  • Therapy sessions now available in centralized locations")
    
    # Show sample paths where therapy sessions can now be found
    if v20_simulations:
        sample_sim = v20_simulations[0]
        sample_therapy_file = sample_sim / "all_logs" / "simulation_logs" / "therapy_events.jsonl"
        print(f"\n📍 Example location to find therapy conversations:")
        print(f"  {sample_therapy_file}")

if __name__ == "__main__":
    migrate_all_therapy_sessions()