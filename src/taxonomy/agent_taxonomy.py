"""
Agent Taxonomy System - Standards for agent naming, discovery, and collaboration
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class AgentTier(Enum):
    """Agent hierarchy tiers"""
    SPECIALIST = "specialist"      # Individual contributor agents
    COORDINATOR = "coordinator"    # Can orchestrate specialist agents
    MANAGER = "manager"           # Can manage coordinators and specialists
    DIRECTOR = "director"         # Strategic oversight of managers
    

class CollaborationPattern(Enum):
    """How agents can collaborate"""
    PEER_TO_PEER = "peer_to_peer"           # Direct collaboration
    HIERARCHICAL = "hierarchical"            # Through chain of command
    SKILL_BASED = "skill_based"              # Based on matching skills
    WORKFLOW_BASED = "workflow_based"        # Part of defined workflow
    ADVISORY = "advisory"                    # Consultation only


@dataclass
class AgentTaxonomy:
    """Complete taxonomy definition for an agent"""
    # Unique identifier following pattern: {domain}.{subdomain}.{specialty}.{instance}
    agent_id: str
    
    # Human-readable name
    display_name: str
    
    # Hierarchical classification
    domain: str          # Top-level domain (engineering, business, etc.)
    subdomain: str       # Specific area (backend, frontend, sales, etc.)
    specialty: str       # Detailed specialty (react, django, lead_gen, etc.)
    
    # Agent capabilities
    tier: AgentTier
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    
    # Collaboration metadata
    can_collaborate_with: List[str] = field(default_factory=list)  # Agent ID patterns
    collaboration_patterns: List[CollaborationPattern] = field(default_factory=list)
    preferred_handoffs: List[str] = field(default_factory=list)    # Specific agent IDs
    
    # Discovery metadata
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    language_support: List[str] = field(default_factory=list)
    
    # Operational metadata
    complexity_level: int = 1  # 1-5, where 5 is most complex
    response_time_sla: str = "standard"  # fast, standard, thorough
    cost_tier: str = "standard"  # economy, standard, premium
    
    # Version and lifecycle
    version: str = "1.0.0"
    status: str = "active"  # active, beta, deprecated
    
    def matches_pattern(self, pattern: str) -> bool:
        """Check if agent ID matches a pattern (supports wildcards)"""
        # Convert pattern to regex: engineering.*.* becomes engineering\..*\..*
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", self.agent_id))
    
    def can_collaborate(self, other_agent_id: str) -> bool:
        """Check if this agent can collaborate with another agent"""
        for pattern in self.can_collaborate_with:
            if re.match(pattern.replace("*", ".*"), other_agent_id):
                return True
        return other_agent_id in self.preferred_handoffs


class TaxonomyBuilder:
    """Helper class to build agent taxonomies with consistent standards"""
    
    # Standard domain mappings
    DOMAINS = {
        "engineering": ["backend", "frontend", "mobile", "database", "cloud", "ml", "blockchain", "systems"],
        "business": ["sales", "hr", "finance", "marketing", "legal", "operations", "supply_chain"],
        "sre_devops": ["monitoring", "cicd", "infrastructure", "containers", "security", "reliability"],
        "servicenow": ["itsm", "itom", "hrsd", "csm", "platform"],
        "data": ["engineering", "science", "analytics", "bi"],
        "security": ["application", "infrastructure", "operations", "compliance"],
        "support": ["technical", "customer_success", "product"],
        "project_mgmt": ["agile", "traditional", "program"],
        "qa": ["automation", "performance", "process"]
    }
    
    # Collaboration rules
    COLLABORATION_RULES = {
        # Engineering collaborations
        "engineering.backend.*": [
            "engineering.database.*",
            "engineering.cloud.*",
            "sre_devops.infrastructure.*",
            "qa.automation.*"
        ],
        "engineering.frontend.*": [
            "engineering.backend.*",
            "qa.automation.*",
            "support.product.*"
        ],
        
        # Business collaborations
        "business.sales.*": [
            "business.marketing.*",
            "data.analytics.*",
            "support.customer_success.*"
        ],
        "business.finance.*": [
            "business.operations.*",
            "data.analytics.*",
            "security.compliance.*"
        ],
        
        # SRE/DevOps collaborations
        "sre_devops.monitoring.*": [
            "sre_devops.infrastructure.*",
            "engineering.*.*",
            "security.operations.*"
        ],
        
        # Data collaborations
        "data.engineering.*": [
            "data.science.*",
            "data.analytics.*",
            "engineering.backend.*"
        ],
        
        # Cross-functional collaborations
        "project_mgmt.*.*": [
            "engineering.*.*",
            "business.*.*",
            "qa.*.*"
        ]
    }
    
    @classmethod
    def create_agent_id(cls, domain: str, subdomain: str, specialty: str, instance: int) -> str:
        """Create standardized agent ID"""
        # Normalize components
        domain = domain.lower().replace(" ", "_").replace("/", "_")
        subdomain = subdomain.lower().replace(" ", "_")
        specialty = specialty.lower().replace(" ", "_").replace("/", "_")
        
        return f"{domain}.{subdomain}.{specialty}.{instance:03d}"
    
    @classmethod
    def determine_tier(cls, role: str) -> AgentTier:
        """Determine agent tier based on role"""
        role_lower = role.lower()
        
        if any(word in role_lower for word in ["coordinator", "orchestrator", "lead"]):
            return AgentTier.COORDINATOR
        elif any(word in role_lower for word in ["manager", "head"]):
            return AgentTier.MANAGER
        elif any(word in role_lower for word in ["director", "chief"]):
            return AgentTier.DIRECTOR
        else:
            return AgentTier.SPECIALIST
    
    @classmethod
    def get_collaboration_patterns(cls, agent_id: str) -> List[str]:
        """Get potential collaboration patterns for an agent"""
        collaborators = []
        
        for pattern, targets in cls.COLLABORATION_RULES.items():
            if re.match(pattern.replace("*", ".*"), agent_id):
                collaborators.extend(targets)
        
        return list(set(collaborators))  # Remove duplicates
    
    @classmethod
    def generate_tags(cls, domain: str, subdomain: str, skills: List[str]) -> List[str]:
        """Generate discovery tags for an agent"""
        tags = [domain, subdomain]
        
        # Add skill-based tags
        for skill in skills:
            tags.append(skill.lower().replace(" ", "_"))
        
        # Add common tags
        if domain == "engineering":
            tags.extend(["technical", "development", "coding"])
        elif domain == "business":
            tags.extend(["business_process", "workflow", "automation"])
        elif domain == "sre_devops":
            tags.extend(["infrastructure", "operations", "reliability"])
        
        return list(set(tags))


def enhance_agent_with_taxonomy(agent_data: Dict[str, Any], instance_num: int) -> Dict[str, Any]:
    """Enhance existing agent data with taxonomy information"""
    
    # Map categories to domains
    category_to_domain = {
        "Engineering": "engineering",
        "Business Workflow": "business",
        "SRE/DevOps": "sre_devops",
        "ServiceNow": "servicenow",
        "Data & Analytics": "data",
        "Security": "security",
        "Customer Support": "support",
        "Project Management": "project_mgmt",
        "Quality Assurance": "qa"
    }
    
    domain = category_to_domain.get(agent_data.get("category", ""), "general")
    subdomain = agent_data.get("subcategory", "general").lower().replace(" ", "_")
    
    # Extract specialty from name
    name = agent_data.get("name", "")
    # Remove common suffixes like _1, Agent_1, etc.
    specialty = re.sub(r'(_\d+|Agent_\d+|Specialist_\d+|Engineer_\d+|Developer_\d+)$', '', name)
    specialty = specialty.lower().replace(" ", "_")
    
    # Create agent ID
    agent_id = TaxonomyBuilder.create_agent_id(domain, subdomain, specialty, instance_num)
    
    # Determine tier
    tier = TaxonomyBuilder.determine_tier(name)
    
    # Get collaboration patterns
    collaboration_patterns = TaxonomyBuilder.get_collaboration_patterns(agent_id)
    
    # Generate tags
    tags = TaxonomyBuilder.generate_tags(
        domain, 
        subdomain, 
        agent_data.get("skills", [])
    )
    
    # Create taxonomy
    taxonomy = AgentTaxonomy(
        agent_id=agent_id,
        display_name=agent_data.get("name", ""),
        domain=domain,
        subdomain=subdomain,
        specialty=specialty,
        tier=tier,
        skills=agent_data.get("skills", []),
        tools=agent_data.get("tools", []),
        can_collaborate_with=collaboration_patterns,
        collaboration_patterns=[
            CollaborationPattern.SKILL_BASED,
            CollaborationPattern.PEER_TO_PEER
        ],
        tags=tags,
        keywords=agent_data.get("skills", []) + [domain, subdomain],
        language_support=["en"],  # Default to English
        complexity_level=3 if tier in [AgentTier.MANAGER, AgentTier.DIRECTOR] else 2,
        response_time_sla="fast" if "support" in domain else "standard",
        cost_tier="premium" if tier in [AgentTier.MANAGER, AgentTier.DIRECTOR] else "standard"
    )
    
    # Add taxonomy to agent data
    agent_data["taxonomy"] = {
        "agent_id": taxonomy.agent_id,
        "display_name": taxonomy.display_name,
        "domain": taxonomy.domain,
        "subdomain": taxonomy.subdomain,
        "specialty": taxonomy.specialty,
        "tier": taxonomy.tier.value,
        "can_collaborate_with": taxonomy.can_collaborate_with,
        "collaboration_patterns": [p.value for p in taxonomy.collaboration_patterns],
        "preferred_handoffs": taxonomy.preferred_handoffs,
        "tags": taxonomy.tags,
        "keywords": taxonomy.keywords,
        "language_support": taxonomy.language_support,
        "complexity_level": taxonomy.complexity_level,
        "response_time_sla": taxonomy.response_time_sla,
        "cost_tier": taxonomy.cost_tier,
        "version": taxonomy.version,
        "status": taxonomy.status
    }
    
    # Update instructions to include collaboration info
    collab_text = f"\n\nCollaboration: You can collaborate with agents matching these patterns: {', '.join(collaboration_patterns[:3])}..."
    agent_data["instructions"] = agent_data.get("instructions", "") + collab_text
    
    return agent_data


class AgentDiscoveryService:
    """Service for discovering and matching agents"""
    
    def __init__(self, agents: List[Dict[str, Any]]):
        self.agents = agents
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for fast lookup"""
        self.by_id = {}
        self.by_domain = {}
        self.by_skill = {}
        self.by_tag = {}
        
        for agent in self.agents:
            taxonomy = agent.get("taxonomy", {})
            agent_id = taxonomy.get("agent_id")
            
            if agent_id:
                self.by_id[agent_id] = agent
                
                # Index by domain
                domain = taxonomy.get("domain")
                if domain not in self.by_domain:
                    self.by_domain[domain] = []
                self.by_domain[domain].append(agent)
                
                # Index by skills
                for skill in agent.get("skills", []):
                    if skill not in self.by_skill:
                        self.by_skill[skill] = []
                    self.by_skill[skill].append(agent)
                
                # Index by tags
                for tag in taxonomy.get("tags", []):
                    if tag not in self.by_tag:
                        self.by_tag[tag] = []
                    self.by_tag[tag].append(agent)
    
    def find_collaborators(self, agent_id: str) -> List[Dict[str, Any]]:
        """Find potential collaborators for an agent"""
        agent = self.by_id.get(agent_id)
        if not agent:
            return []
        
        collaborators = []
        taxonomy = agent.get("taxonomy", {})
        
        for pattern in taxonomy.get("can_collaborate_with", []):
            for other_agent in self.agents:
                other_id = other_agent.get("taxonomy", {}).get("agent_id")
                if other_id and other_id != agent_id:
                    if re.match(pattern.replace("*", ".*"), other_id):
                        collaborators.append(other_agent)
        
        return collaborators
    
    def find_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Find agents with a specific skill"""
        return self.by_skill.get(skill, [])
    
    def find_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Find agents in a specific domain"""
        return self.by_domain.get(domain, [])
    
    def find_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find agents matching an ID pattern"""
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        matches = []
        
        for agent in self.agents:
            agent_id = agent.get("taxonomy", {}).get("agent_id")
            if agent_id and re.match(f"^{regex_pattern}$", agent_id):
                matches.append(agent)
        
        return matches