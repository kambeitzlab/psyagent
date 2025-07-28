#!/bin/bash

# Navigate to project directory (if not already there)
cd /Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab

# Get current date and time
current_time=$(date "+%Y-%m-%d_%H-%M-%S")

# Add all changes
git add .

# Commit with automatic timestamp
git commit -m "Backup at $current_time"

# Push to GitHub
git push origin stable_version
