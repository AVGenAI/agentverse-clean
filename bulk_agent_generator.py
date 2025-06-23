#!/usr/bin/env python3
"""
Bulk Agent Generator - Creates 10,000 diverse AI agents
"""
import json
import random
import uuid
from datetime import datetime
from typing import Dict, List, Any
import itertools

# Agent categories and their specializations
AGENT_DOMAINS = {
    "engineering": {
        "types": ["backend", "frontend", "fullstack", "mobile", "devops", "security", "data", "ml", "cloud", "embedded"],
        "skills": ["Python", "JavaScript", "Go", "Rust", "Java", "C++", "React", "Vue", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "PostgreSQL", "MongoDB", "Redis", "GraphQL", "REST", "gRPC", "Microservices"],
        "tools": ["git", "docker", "kubectl", "terraform", "ansible", "jenkins", "gitlab", "prometheus", "grafana", "elasticsearch"]
    },
    "sre": {
        "types": ["infrastructure", "monitoring", "incident", "automation", "performance", "reliability", "platform", "observability"],
        "skills": ["Incident Response", "SLO Management", "Monitoring", "Alerting", "Automation", "Troubleshooting", "Root Cause Analysis", "Capacity Planning", "Disaster Recovery", "High Availability"],
        "tools": ["prometheus", "grafana", "pagerduty", "datadog", "newrelic", "splunk", "elk", "terraform", "ansible", "kubernetes"]
    },
    "data": {
        "types": ["analyst", "engineer", "scientist", "architect", "visualization", "pipeline", "quality", "governance"],
        "skills": ["SQL", "Python", "R", "Spark", "Hadoop", "ETL", "Data Modeling", "Statistics", "Machine Learning", "Deep Learning", "Data Visualization", "Big Data", "Stream Processing"],
        "tools": ["spark", "hadoop", "airflow", "kafka", "tableau", "powerbi", "jupyter", "databricks", "snowflake", "redshift"]
    },
    "security": {
        "types": ["appsec", "infosec", "devsecops", "compliance", "forensics", "pentesting", "governance", "architect"],
        "skills": ["Vulnerability Assessment", "Penetration Testing", "Security Auditing", "Incident Response", "Compliance", "Risk Management", "Cryptography", "Network Security", "Cloud Security", "Zero Trust"],
        "tools": ["nmap", "burpsuite", "metasploit", "wireshark", "vault", "snyk", "sonarqube", "owasp", "kali", "splunk"]
    },
    "product": {
        "types": ["manager", "owner", "analyst", "designer", "researcher", "strategist", "growth", "marketing"],
        "skills": ["Product Strategy", "User Research", "Analytics", "Roadmapping", "Agile", "Scrum", "Market Analysis", "A/B Testing", "UX Design", "Customer Development"],
        "tools": ["jira", "confluence", "figma", "mixpanel", "amplitude", "productboard", "roadmunk", "aha", "miro", "notion"]
    },
    "ai_ml": {
        "types": ["research", "engineer", "scientist", "nlp", "cv", "rl", "generative", "llm", "optimization"],
        "skills": ["TensorFlow", "PyTorch", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "GANs", "Transformers", "MLOps", "Model Optimization"],
        "tools": ["tensorflow", "pytorch", "huggingface", "wandb", "mlflow", "kubeflow", "sagemaker", "vertexai", "colab", "jupyter"]
    },
    "business": {
        "types": ["analyst", "intelligence", "operations", "strategy", "consultant", "process", "transformation", "innovation"],
        "skills": ["Business Analysis", "Process Optimization", "Strategic Planning", "Financial Modeling", "Market Research", "Competitive Analysis", "Change Management", "Project Management"],
        "tools": ["excel", "powerbi", "tableau", "salesforce", "sap", "oracle", "quickbooks", "asana", "monday", "slack"]
    },
    "support": {
        "types": ["customer", "technical", "enterprise", "specialist", "escalation", "success", "onboarding", "training"],
        "skills": ["Customer Service", "Technical Support", "Troubleshooting", "Communication", "Problem Solving", "Documentation", "Training", "Escalation Management"],
        "tools": ["zendesk", "freshdesk", "intercom", "jira", "confluence", "slack", "zoom", "loom", "notion", "helpscout"]
    }
}

# Model preferences
MODELS = {
    "primary": ["gpt-4o", "gpt-4o-mini", "claude-3-opus", "claude-3-sonnet", "gemini-pro", "llama-3-70b", "mixtral-8x7b"],
    "fallback": ["gpt-3.5-turbo", "claude-instant", "llama-2-70b", "mistral-7b"]
}

# Company names for variety
COMPANIES = ["TechCorp", "DataFlow", "CloudNine", "SecureNet", "AIvance", "DevOps Pro", "Analytics Inc", "CyberShield", "Platform X", "Innovation Labs"]

# Behavioral traits
BEHAVIORS = {
    "communication_style": ["concise", "detailed", "technical", "friendly", "formal", "casual"],
    "problem_approach": ["systematic", "creative", "analytical", "pragmatic", "innovative"],
    "collaboration": ["proactive", "responsive", "independent", "team-oriented"],
    "decision_making": ["data-driven", "intuitive", "consensus-seeking", "decisive"]
}

def generate_agent_name(domain: str, agent_type: str, index: int) -> tuple:
    """Generate agent name and ID"""
    # Create variations in naming
    prefixes = ["Senior", "Lead", "Principal", "Staff", "Junior", "Expert", "Chief"]
    suffixes = ["Specialist", "Engineer", "Analyst", "Architect", "Consultant", "Expert", "Lead"]
    
    prefix = random.choice(prefixes) if random.random() > 0.5 else ""
    suffix = random.choice(suffixes)
    
    display_name = f"{prefix} {agent_type.title()} {suffix}".strip()
    agent_id = f"{domain}_{agent_type}_{str(index).zfill(4)}"
    canonical_name = f"av.{domain}.{agent_type}.v1.{uuid.uuid4().hex[:8]}"
    
    return agent_id, display_name, canonical_name

def generate_instructions(domain: str, agent_type: str, skills: List[str]) -> str:
    """Generate detailed instructions for the agent"""
    skill_list = ", ".join(skills[:5])
    
    templates = [
        f"You are an expert {agent_type} specialist in the {domain} domain. Your core competencies include {skill_list}. You provide accurate, actionable insights and solutions while maintaining best practices in your field.",
        f"As a {agent_type} professional specializing in {domain}, you excel at {skill_list}. You approach problems systematically and deliver high-quality solutions that meet both technical and business requirements.",
        f"You are a seasoned {domain} {agent_type} with deep expertise in {skill_list}. You combine technical excellence with practical experience to help teams achieve their goals efficiently.",
        f"Your role is as a {agent_type} expert focusing on {domain} challenges. With mastery of {skill_list}, you provide strategic guidance and hands-on solutions to complex problems."
    ]
    
    base_instruction = random.choice(templates)
    
    # Add domain-specific instructions
    domain_specific = {
        "engineering": "You follow clean code principles, emphasize testing, and prioritize maintainability.",
        "sre": "You focus on reliability, incident prevention, and maintaining high availability systems.",
        "data": "You ensure data quality, optimize for performance, and maintain data governance standards.",
        "security": "You prioritize security best practices, threat prevention, and compliance requirements.",
        "ai_ml": "You stay current with latest research, optimize model performance, and ensure ethical AI practices."
    }
    
    if domain in domain_specific:
        base_instruction += f" {domain_specific[domain]}"
    
    return base_instruction

def generate_agent(index: int, domain: str, agent_type: str) -> Dict[str, Any]:
    """Generate a single agent with all metadata"""
    agent_id, display_name, canonical_name = generate_agent_name(domain, agent_type, index)
    
    # Select skills and tools
    available_skills = AGENT_DOMAINS[domain]["skills"]
    available_tools = AGENT_DOMAINS[domain]["tools"]
    
    primary_skills = random.sample(available_skills, min(8, len(available_skills)))
    secondary_skills = random.sample(available_skills, min(5, len(available_skills)))
    tools = random.sample(available_tools, min(6, len(available_tools)))
    
    # Generate behavior traits
    behavior = {
        trait: random.choice(values) 
        for trait, values in BEHAVIORS.items()
    }
    
    # Create tool mastery
    tools_mastery = {
        tool: {
            "proficiency": random.choice(["expert", "advanced", "intermediate"]),
            "years_experience": random.randint(1, 10)
        }
        for tool in tools
    }
    
    # Generate agent metadata
    agent = {
        "id": index,
        "instructions": generate_instructions(domain, agent_type, primary_skills),
        "enhanced_metadata": {
            "agent_uuid": agent_id,
            "canonical_name": canonical_name,
            "display_name": display_name,
            "avatar_emoji": random.choice(["🤖", "🧠", "💻", "🔧", "📊", "🔒", "🚀", "⚡", "🎯", "🛡️"]),
            "version": f"1.{random.randint(0, 5)}.{random.randint(0, 20)}",
            "created_at": datetime.now().isoformat(),
            "created_by": random.choice(COMPANIES),
            "taxonomy": {
                "domain": domain,
                "type": agent_type,
                "specialization": random.choice(primary_skills[:3]).lower().replace(" ", "_"),
                "industry": random.choice(["technology", "finance", "healthcare", "retail", "manufacturing", "education"])
            },
            "capabilities": {
                "primary_expertise": primary_skills,
                "secondary_skills": secondary_skills,
                "tools_mastery": tools_mastery,
                "integration_capabilities": ["API", "webhook", "event-driven", "batch", "real-time"],
                "supported_platforms": random.sample(["linux", "windows", "macos", "cloud", "kubernetes", "serverless"], 3)
            },
            "model_preferences": {
                "primary": random.choice(MODELS["primary"]),
                "fallback": random.choice(MODELS["fallback"]),
                "context_window": random.choice([4096, 8192, 16384, 32768, 128000]),
                "temperature": round(random.uniform(0.3, 0.9), 2),
                "languages": ["English"] + random.sample(["Spanish", "French", "German", "Chinese", "Japanese", "Portuguese"], random.randint(0, 2))
            },
            "behavior": behavior,
            "collaboration": {
                "style": [random.choice(["autonomous", "collaborative", "supervisory"])],
                "upstream_dependencies": random.sample([f"agent_{i}" for i in range(100, 200)], random.randint(0, 3)),
                "downstream_dependents": random.sample([f"agent_{i}" for i in range(200, 300)], random.randint(0, 3)),
                "communication_preferences": ["async", "sync", "event-driven"]
            },
            "performance": {
                "success_rate": round(random.uniform(0.85, 0.99), 3),
                "avg_response_time": f"{random.uniform(0.5, 3.0):.1f}s",
                "completed_tasks": random.randint(1000, 50000),
                "error_rate": round(random.uniform(0.001, 0.05), 3)
            },
            "quality": {
                "trust_score": round(random.uniform(0.8, 0.99), 2),
                "reliability_score": round(random.uniform(0.85, 0.99), 2),
                "accuracy_score": round(random.uniform(0.9, 0.99), 2),
                "certification_level": random.choice(["standard", "advanced", "expert", "master"])
            },
            "discovery": {
                "keywords": primary_skills[:5] + [domain, agent_type],
                "problem_domains": random.sample([
                    "automation", "optimization", "analysis", "security", "performance",
                    "scalability", "reliability", "compliance", "integration", "monitoring"
                ], 3),
                "use_cases": [f"Use case {i}" for i in range(1, random.randint(3, 6))]
            },
            "lifecycle": {
                "status": random.choice(["active", "beta", "stable", "deprecated"]),
                "maintenance_schedule": random.choice(["weekly", "monthly", "quarterly"]),
                "last_updated": datetime.now().isoformat(),
                "deprecation_date": None
            },
            "mcp_coupling": {
                "compatible": True,
                "preferred_servers": random.sample(["servicenow", "github", "slack", "jira", "datadog"], random.randint(1, 3)),
                "protocol_version": "1.0",
                "connection_type": random.choice(["direct", "proxy", "bridge"])
            }
        }
    }
    
    return agent

def generate_bulk_agents(count: int = 10000) -> List[Dict[str, Any]]:
    """Generate specified number of agents with balanced distribution"""
    agents = []
    
    # Calculate distribution
    agents_per_domain = count // len(AGENT_DOMAINS)
    remaining = count % len(AGENT_DOMAINS)
    
    index = 1
    for domain, config in AGENT_DOMAINS.items():
        domain_count = agents_per_domain + (1 if remaining > 0 else 0)
        remaining = max(0, remaining - 1)
        
        # Distribute across types within domain
        agents_per_type = domain_count // len(config["types"])
        type_remaining = domain_count % len(config["types"])
        
        for agent_type in config["types"]:
            type_count = agents_per_type + (1 if type_remaining > 0 else 0)
            type_remaining = max(0, type_remaining - 1)
            
            for _ in range(type_count):
                if index <= count:
                    agent = generate_agent(index, domain, agent_type)
                    agents.append(agent)
                    index += 1
    
    return agents

def save_agents(agents: List[Dict[str, Any]], filename: str = "agentverse_agents_10000.json"):
    """Save agents to JSON file"""
    # Don't add path if already included
    if "/" in filename:
        output_path = filename
    else:
        output_path = f"src/config/{filename}"
    
    with open(output_path, 'w') as f:
        json.dump(agents, f, indent=2)
    
    print(f"✅ Generated {len(agents)} agents and saved to {output_path}")
    
    # Print statistics
    domains = {}
    for agent in agents:
        domain = agent["enhanced_metadata"]["taxonomy"]["domain"]
        domains[domain] = domains.get(domain, 0) + 1
    
    print("\n📊 Agent Distribution:")
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count} agents")

if __name__ == "__main__":
    print("🚀 Generating 10,000 AI agents...")
    agents = generate_bulk_agents(10000)
    save_agents(agents)
    print("\n✨ Generation complete!")