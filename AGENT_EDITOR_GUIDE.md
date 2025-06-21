# AgentVerse Agent Editor CLI Guide

## Overview
The Agent Editor is a powerful command-line tool for managing all 1000+ AgentVerse agents. Edit, update, validate, and bulk-modify agents with ease.

## Installation
```bash
# Ensure rich is installed
pip install rich

# Make executable
chmod +x agent_editor.py
```

## Commands

### 1. List Agents
```bash
# List all agents (default: 20)
python agent_editor.py list

# List agents in a specific domain
python agent_editor.py list --domain engineering

# List more agents
python agent_editor.py list --limit 50

# List all data analytics agents
python agent_editor.py list --domain data_analytics --limit 100
```

### 2. Show Agent Details
```bash
# Show by UUID (partial match works)
python agent_editor.py show d894cd44

# Show by name
python agent_editor.py show DjangoDeveloper_1

# Show by canonical name
python agent_editor.py show djangodeveloper
```

### 3. Find Agents
```bash
# Find by skill
python agent_editor.py find python

# Find by name
python agent_editor.py find developer

# Find by domain
python agent_editor.py find security
```

### 4. Edit Agent (Interactive)
```bash
# Edit specific agent
python agent_editor.py edit d894cd44

# Interactive menu options:
# 1. Display Name
# 2. Instructions
# 3. Skills
# 4. Tools
# 5. Avatar Emoji
# 6. Version
# 7. Category/Subcategory
# 8. Primary Expertise
# 9. Collaboration Style
```

### 5. Bulk Edit
```bash
# Update version for all engineering agents
python agent_editor.py bulk-edit engineering version 2.0.0

# Change model for all data agents
python agent_editor.py bulk-edit data_analytics model gpt-4o

# Update category for business agents
python agent_editor.py bulk-edit business_workflow category "Business Operations"
```

### 6. Add Skills
```bash
# Add skill to ALL agents
python agent_editor.py add-skill "AI Ethics"

# Add skill to specific domain
python agent_editor.py add-skill "Kubernetes" --domain engineering

# Add skill to security agents
python agent_editor.py add-skill "Zero Trust" --domain security
```

### 7. Validate Agents
```bash
# Check all agents for missing fields
python agent_editor.py validate
```

### 8. Export Agents
```bash
# Export all agents
python agent_editor.py export all_agents_backup.json

# Export only engineering agents
python agent_editor.py export engineering_agents.json --domain engineering

# Export security agents
python agent_editor.py export security_team.json --domain security
```

### 9. Restore from Backup
```bash
# List and restore from backups
python agent_editor.py restore
```

## Usage Examples

### Example 1: Update All Django Agents
```bash
# Find Django agents
python agent_editor.py find django

# Edit a specific Django agent
python agent_editor.py edit DjangoDeveloper_1

# Add Django 5.0 skill to all Django agents
python agent_editor.py add-skill "Django 5.0" --domain engineering
```

### Example 2: Create Custom Agent Team
```bash
# Export specific domain agents
python agent_editor.py export ml_team.json --domain data_analytics

# Edit the exported file
# Re-import by copying back to main config
```

### Example 3: Batch Updates
```bash
# Update all agents to version 2.0
python agent_editor.py bulk-edit engineering version 2.0.0
python agent_editor.py bulk-edit business_workflow version 2.0.0
python agent_editor.py bulk-edit data_analytics version 2.0.0

# Validate after updates
python agent_editor.py validate
```

### Example 4: Agent Maintenance
```bash
# 1. Create backup before major changes
cp src/config/agentverse_agents_1000.json agents_backup_$(date +%Y%m%d).json

# 2. Validate current state
python agent_editor.py validate

# 3. Make your changes
python agent_editor.py edit <agent_id>

# 4. Validate again
python agent_editor.py validate

# 5. Test with API
python test_agent_quality.py
```

## Advanced Usage

### Custom Scripts with Agent Editor
```python
#!/usr/bin/env python3
from agent_editor import AgentEditor

# Initialize editor
editor = AgentEditor()

# Find all Python agents
python_agents = editor.find_agent("python")

# Update each agent
for agent in python_agents:
    # Add new skill
    if "Python 3.12" not in agent.get('skills', []):
        agent['skills'].append("Python 3.12")
    
    # Update version
    agent['enhanced_metadata']['version'] = "2.0.0"

# Save changes
editor.save_agents()
```

### Bulk Operations Script
```bash
#!/bin/bash
# bulk_update.sh - Update all agents by domain

domains=("engineering" "business_workflow" "data_analytics" "security" "sre_devops")

for domain in "${domains[@]}"; do
    echo "Updating $domain agents..."
    python agent_editor.py bulk-edit "$domain" version "2.0.0"
    python agent_editor.py add-skill "GenAI" --domain "$domain"
done

python agent_editor.py validate
```

## Field Reference

### Editable Fields
- **Display Name**: Human-friendly name
- **Instructions**: Agent's system prompt
- **Skills**: List of capabilities
- **Tools**: Available functions
- **Avatar Emoji**: Visual identifier
- **Version**: Semantic version
- **Category**: High-level grouping
- **Subcategory**: Specific domain
- **Primary Expertise**: Top 3 skills
- **Collaboration Style**: mentor/peer/learner

### Read-Only Fields
- **UUID**: Unique identifier
- **Canonical Name**: System identifier
- **Created At**: Timestamp

## Best Practices

1. **Always Backup**: The editor auto-creates backups, but manual backups are recommended
2. **Validate After Changes**: Run validate command after bulk operations
3. **Test Changes**: Use the quality test scripts after major updates
4. **Version Control**: Consider committing agent config to git
5. **Incremental Updates**: Make small, testable changes

## Troubleshooting

### "No agent found"
- Use partial UUID match
- Try different search terms
- List agents to see available options

### Backup Recovery
```bash
# If something goes wrong
python agent_editor.py restore
# Select the most recent backup
```

### JSON Corruption
```bash
# Validate JSON syntax
python -m json.tool src/config/agentverse_agents_1000.json > /dev/null
```

## Integration with AgentVerse

After editing agents:
1. Restart the API to load changes
2. Test with: `python test_agent_quality.py`
3. Verify in UI at http://localhost:3000

## Future Features
- [ ] Agent templates
- [ ] Import from CSV
- [ ] Diff view for changes
- [ ] Agent performance metrics
- [ ] Collaborative editing