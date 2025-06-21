import os
from dotenv import load_dotenv
from agents import Runner, Tool, Handoff
from ..core.agent_factory import AgentFactory, AgentConfig
from ..providers import ProviderConfig


def create_multi_agent_system():
    load_dotenv()
    
    factory = AgentFactory()
    
    # Register provider
    openai_config = ProviderConfig(
        name="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.7
    )
    factory.register_provider("openai", openai_config)
    
    # Create specialized agents
    
    # 1. Research Agent
    research_config = AgentConfig(
        name="ResearchAgent",
        instructions="""You are a research specialist. Your job is to:
        - Gather information on topics
        - Provide detailed analysis
        - Cite sources when possible
        
        When you've completed your research, hand off to the WriterAgent.""",
        provider="openai"
    )
    research_agent = factory.create_agent(research_config)
    
    # 2. Writer Agent
    writer_config = AgentConfig(
        name="WriterAgent",
        instructions="""You are a professional writer. Your job is to:
        - Take research and create well-structured content
        - Write in a clear, engaging style
        - Format content appropriately
        
        When you need code examples, hand off to the CoderAgent.""",
        provider="openai"
    )
    writer_agent = factory.create_agent(writer_config)
    
    # 3. Coder Agent
    coder_config = AgentConfig(
        name="CoderAgent",
        instructions="""You are an expert programmer. Your job is to:
        - Write clean, efficient code
        - Add helpful comments
        - Follow best practices
        
        When code is complete, hand back to the WriterAgent.""",
        provider="openai"
    )
    coder_agent = factory.create_agent(coder_config)
    
    # 4. Reviewer Agent
    reviewer_config = AgentConfig(
        name="ReviewerAgent",
        instructions="""You are a quality assurance specialist. Your job is to:
        - Review content for accuracy
        - Check for clarity and completeness
        - Suggest improvements
        
        Provide final approval or request revisions.""",
        provider="openai"
    )
    reviewer_agent = factory.create_agent(reviewer_config)
    
    # Add handoff capabilities
    research_agent.add_tool(Handoff(agents=[writer_agent]))
    writer_agent.add_tool(Handoff(agents=[coder_agent, reviewer_agent]))
    coder_agent.add_tool(Handoff(agents=[writer_agent]))
    
    return {
        "research": research_agent,
        "writer": writer_agent,
        "coder": coder_agent,
        "reviewer": reviewer_agent
    }


def main():
    agents = create_multi_agent_system()
    
    print("Multi-Agent System Example")
    print("-" * 40)
    
    # Start with research agent
    query = "Create a comprehensive guide on building AI agents with Python, including code examples"
    
    print(f"\nUser: {query}")
    print("\nStarting multi-agent workflow...")
    
    result = Runner.run_sync(agents["research"], query)
    print(f"\nFinal Output:\n{result.final_output}")
    
    # Show which agents were involved
    print("\nAgents involved in this task:")
    for message in result.messages:
        if hasattr(message, 'name'):
            print(f"- {message.name}")


if __name__ == "__main__":
    main()