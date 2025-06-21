// Quick fix to check if SRE agents are being loaded
// Run this in the browser console on the MCP Integration page

async function debugAgents() {
    const response = await fetch('http://localhost:8000/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 100, offset: 0 })
    });
    
    const data = await response.json();
    const agents = data.agents;
    
    console.log('Total agents:', agents.length);
    
    const sreAgents = agents.filter(agent => 
        agent.display_name?.includes('SRE') || 
        agent.canonical_name?.includes('sre') ||
        agent.display_name?.includes('ServiceNow')
    );
    
    console.log('SRE agents found:', sreAgents.length);
    console.log('SRE agents:', sreAgents);
    
    // Try to manually update the dropdown
    const select = document.querySelector('select');
    if (select) {
        console.log('Current options:', select.options.length);
        console.log('First few options:', Array.from(select.options).slice(0, 5).map(o => o.text));
    }
    
    return sreAgents;
}

debugAgents();