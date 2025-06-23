# Tools vs MCP Coupling Explained

## Current Status ✅

### 1. **Agent Tools (WORKING)**
The SRE ServiceNow agent has 5 built-in tools that are **fully functional**:
- `search_incidents` - Search ServiceNow incidents
- `create_incident` - Create new incidents  
- `update_incident` - Update existing incidents
- `calculate_slo_status` - Calculate SLO metrics
- `get_runbook` - Get runbooks for incident types

These tools are implemented using the `@function_tool` decorator and work with mock data.

**Test Results:**
```
✅ Agent responds to "Show me all critical incidents" - Returns incident data
✅ Agent responds to "What's the SLO status?" - Returns SLO calculations
✅ Agent responds to "Create a new incident" - Creates mock incident
✅ Agent responds to "Get runbook for high latency" - Returns runbook steps
```

### 2. **MCP Coupling (SEPARATE FEATURE)**
MCP (Model Context Protocol) coupling is for connecting to **external MCP servers** that provide real-time access to external systems.

**Current State:**
- Shows "Inactive" in UI because it's not connected to a real MCP server
- The ServiceNow MCP server would provide real-time access to actual ServiceNow data
- This is a separate system from the built-in tools

## The Architecture

```
User Query → Agent (with built-in tools) → Mock Responses
                    ↓
            [Future: MCP Coupling]
                    ↓
User Query → Agent → MCP Server → Real ServiceNow → Real Data
```

## Summary

1. **Tools are working** - The agent can respond to queries using its built-in tools
2. **MCP coupling is inactive** - This is normal, as we haven't connected to a real MCP server
3. **Both can coexist** - An agent can have built-in tools AND connect to MCP servers

The "Inactive" status in the MCP Integration page is **not a bug** - it accurately shows that the agent isn't connected to an external MCP server. The agent is still fully functional with its built-in tools.