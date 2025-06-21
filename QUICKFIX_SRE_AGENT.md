# Quick Fix: Making SRE Agent Visible in UI

The SRE agent is actually in the system and being returned by the API, but there might be a caching issue in the UI. Here are quick solutions:

## Solution 1: Force Refresh in Browser
1. Open the MCP Integration page: http://localhost:3000/mcp-integration (or port 3001/5173)
2. Open browser DevTools (F12)
3. Go to Network tab
4. Check "Disable cache"
5. Hard refresh the page (Cmd+Shift+R on Mac)

## Solution 2: Clear React Query Cache
Run this in the browser console:
```javascript
// Force refetch all queries
window.location.reload(true);
```

## Solution 3: Direct API Test
Open the debug page I created:
```bash
open /Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/debug_sre_agent.html
```

## Solution 4: Use Search Feature
In the MCP Integration page:
1. Click on the search input box
2. Type "SRE" or "ServiceNow"
3. The SRE agents should appear filtered

## What's Happening
- ✅ SRE agent was successfully added to the config file
- ✅ API is returning the SRE agent (verified via curl)
- ❓ UI might have cached the old agent list

## Direct Access
The SRE agent details:
- **ID**: sre_servicenow_001
- **Name**: SRE ServiceNow Specialist
- **Skills**: Incident Response, ServiceNow Platform, SLO Management, etc.

## If Still Not Visible
1. Check browser console for errors
2. Try incognito/private browsing mode
3. Check if UI is on port 3000, 3001, or 5173
4. Restart the UI dev server:
   ```bash
   cd agentverse_ui
   npm run dev
   ```