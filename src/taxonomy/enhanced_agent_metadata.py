"""
Enhanced Agent Metadata System with Rich Discovery and Collaboration Features
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class AgentCapabilityProfile:
    """Detailed capability profile for agent matching"""
    primary_expertise: List[str] = field(default_factory=list)
    secondary_expertise: List[str] = field(default_factory=list)
    tools_mastery: Dict[str, int] = field(default_factory=dict)  # tool: proficiency_level (1-10)
    industry_knowledge: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages_supported: List[str] = field(default_factory=list)
    frameworks_expertise: Dict[str, str] = field(default_factory=dict)  # framework: expertise_level
    

@dataclass
class CollaborationProfile:
    """How this agent collaborates with others"""
    collaboration_style: List[str] = field(default_factory=list)  # ["mentor", "peer", "learner", "coordinator"]
    preferred_team_size: str = "small"  # small(2-3), medium(4-6), large(7+)
    communication_protocols: List[str] = field(default_factory=list)  # ["sync", "async", "webhook", "event-driven"]
    handoff_style: str = "detailed"  # minimal, standard, detailed
    escalation_paths: List[str] = field(default_factory=list)  # Agent IDs for escalation
    delegation_capabilities: List[str] = field(default_factory=list)  # What can be delegated
    

@dataclass 
class PerformanceProfile:
    """Performance characteristics and SLAs"""
    avg_response_time_ms: int = 1000
    complexity_handling: str = "medium"  # low, medium, high, expert
    parallel_task_capacity: int = 3
    memory_context_limit: int = 8000  # tokens
    reliability_score: float = 0.99  # 0-1
    error_handling_style: str = "graceful"  # fail-fast, graceful, retry-heavy
    

@dataclass
class DiscoveryMetadata:
    """Rich metadata for agent discovery"""
    search_keywords: Set[str] = field(default_factory=set)
    problem_domains: List[str] = field(default_factory=list)  # Types of problems this agent solves
    solution_patterns: List[str] = field(default_factory=list)  # Common solution approaches
    integration_points: List[str] = field(default_factory=list)  # Systems/APIs it can integrate with
    data_formats: List[str] = field(default_factory=list)  # JSON, XML, CSV, etc.
    compliance_standards: List[str] = field(default_factory=list)  # GDPR, HIPAA, SOC2, etc.
    

@dataclass
class EnhancedAgentMetadata:
    """Comprehensive agent metadata for discovery and collaboration"""
    
    # Core Identity
    agent_uuid: str  # Globally unique identifier
    canonical_name: str  # Formal agent name: {org}.{domain}.{function}.{specialization}
    display_name: str  # Human-friendly name
    avatar_emoji: str  # Visual identifier 
    
    # Versioning & Lifecycle
    version: str = "1.0.0"
    created_at: str = ""
    last_updated: str = ""
    deprecation_date: Optional[str] = None
    successor_agent_id: Optional[str] = None
    
    # Capability Profile
    capabilities: AgentCapabilityProfile = field(default_factory=AgentCapabilityProfile)
    
    # Collaboration Profile  
    collaboration: CollaborationProfile = field(default_factory=CollaborationProfile)
    
    # Performance Profile
    performance: PerformanceProfile = field(default_factory=PerformanceProfile)
    
    # Discovery Metadata
    discovery: DiscoveryMetadata = field(default_factory=DiscoveryMetadata)
    
    # Network & Dependencies
    upstream_dependencies: List[str] = field(default_factory=list)  # Agents this depends on
    downstream_dependents: List[str] = field(default_factory=list)  # Agents that depend on this
    peer_network: List[str] = field(default_factory=list)  # Frequent collaborators
    
    # Operational Metadata
    deployment_regions: List[str] = field(default_factory=list)  # Geographic/logical regions
    availability_schedule: str = "24/7"  # 24/7, business-hours, on-demand
    maintenance_windows: List[str] = field(default_factory=list)
    
    # Quality & Trust
    trust_score: float = 0.95  # 0-1, based on historical performance
    verified_by: List[str] = field(default_factory=list)  # Other agents that vouch for this one
    quality_badges: List[str] = field(default_factory=list)  # ["gold-certified", "battle-tested", etc.]
    
    # Usage & Analytics
    total_interactions: int = 0
    success_rate: float = 0.0
    popular_use_cases: List[str] = field(default_factory=list)
    avg_user_rating: float = 0.0
    
    # Custom Attributes
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def generate_agent_uuid(self) -> str:
        """Generate a unique UUID based on agent properties"""
        unique_string = f"{self.canonical_name}-{datetime.now().isoformat()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def to_discovery_document(self) -> Dict[str, Any]:
        """Convert to a searchable discovery document"""
        return {
            "agent_uuid": self.agent_uuid,
            "canonical_name": self.canonical_name,
            "display_name": self.display_name,
            "avatar": self.avatar_emoji,
            "description": self._generate_description(),
            "capabilities": self._flatten_capabilities(),
            "collaboration_style": self.collaboration.collaboration_style,
            "search_terms": list(self.discovery.search_keywords),
            "problem_domains": self.discovery.problem_domains,
            "integrations": self.discovery.integration_points,
            "trust_score": self.trust_score,
            "availability": self.availability_schedule,
            "version": self.version
        }
    
    def _generate_description(self) -> str:
        """Generate a natural language description"""
        primary = ", ".join(self.capabilities.primary_expertise[:3])
        return f"A {self.display_name} specializing in {primary}"
    
    def _flatten_capabilities(self) -> List[str]:
        """Flatten all capabilities for search"""
        caps = []
        caps.extend(self.capabilities.primary_expertise)
        caps.extend(self.capabilities.secondary_expertise)
        caps.extend(self.capabilities.tools_mastery.keys())
        caps.extend(self.capabilities.frameworks_expertise.keys())
        return list(set(caps))


class MetadataEnricher:
    """Enrich agents with enhanced metadata"""
    
    # Emoji mapping for visual identification
    EMOJI_MAP = {
        "engineering": "🔧",
        "backend": "⚙️",
        "frontend": "🎨",
        "mobile": "📱",
        "database": "🗄️",
        "cloud": "☁️",
        "ml": "🤖",
        "blockchain": "🔗",
        "business": "💼",
        "sales": "💰",
        "hr": "👥",
        "finance": "💳",
        "marketing": "📢",
        "sre_devops": "🚀",
        "monitoring": "📊",
        "security": "🔒",
        "support": "🤝",
        "data": "📈",
        "qa": "✅",
        "project_mgmt": "📋"
    }
    
    # Capability mappings
    CAPABILITY_PROFILES = {
        "ReactDeveloper": {
            "primary": ["React", "JavaScript", "Frontend Development"],
            "secondary": ["Redux", "TypeScript", "CSS", "Testing"],
            "tools": {"webpack": 8, "babel": 7, "jest": 8, "eslint": 9},
            "frameworks": {"React": "expert", "Next.js": "advanced", "Gatsby": "intermediate"}
        },
        "PythonDeveloper": {
            "primary": ["Python", "Backend Development", "API Design"],
            "secondary": ["Django", "FastAPI", "PostgreSQL", "Redis"],
            "tools": {"pytest": 9, "black": 8, "mypy": 7, "poetry": 8},
            "frameworks": {"Django": "expert", "FastAPI": "expert", "Flask": "advanced"}
        },
        "DataEngineer": {
            "primary": ["Data Engineering", "ETL", "Data Pipelines"],
            "secondary": ["Spark", "Airflow", "SQL", "Python"],
            "tools": {"spark": 9, "airflow": 8, "dbt": 8, "kafka": 7},
            "frameworks": {"PySpark": "expert", "Pandas": "expert", "Dask": "advanced"}
        }
    }
    
    @classmethod
    def create_enhanced_metadata(cls, agent_data: Dict[str, Any]) -> EnhancedAgentMetadata:
        """Create rich metadata for an agent"""
        
        # Extract base information
        name = agent_data.get("name", "Unknown")
        category = agent_data.get("category", "general")
        subcategory = agent_data.get("subcategory", "general")
        skills = agent_data.get("skills", [])
        
        # Generate canonical name
        org = "aiagents"
        domain = category.lower().replace(" ", "_").replace("/", "_")
        function = subcategory.lower().replace(" ", "_")
        specialization = name.split("_")[0].lower()
        canonical_name = f"{org}.{domain}.{function}.{specialization}"
        
        # Create metadata
        metadata = EnhancedAgentMetadata(
            agent_uuid="",  # Will be generated
            canonical_name=canonical_name,
            display_name=name,
            avatar_emoji=cls._get_emoji(domain, function),
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        # Generate UUID
        metadata.agent_uuid = metadata.generate_agent_uuid()
        
        # Set capability profile
        cls._set_capability_profile(metadata, name, skills)
        
        # Set collaboration profile
        cls._set_collaboration_profile(metadata, category)
        
        # Set performance profile
        cls._set_performance_profile(metadata, category)
        
        # Set discovery metadata
        cls._set_discovery_metadata(metadata, agent_data)
        
        # Set network dependencies
        cls._set_network_dependencies(metadata, canonical_name)
        
        return metadata
    
    @classmethod
    def _get_emoji(cls, domain: str, function: str) -> str:
        """Get appropriate emoji for agent"""
        return cls.EMOJI_MAP.get(function, cls.EMOJI_MAP.get(domain, "🤖"))
    
    @classmethod
    def _set_capability_profile(cls, metadata: EnhancedAgentMetadata, name: str, skills: List[str]):
        """Set capability profile based on agent type"""
        
        # Try to match known profiles
        for profile_key, profile_data in cls.CAPABILITY_PROFILES.items():
            if profile_key in name:
                metadata.capabilities.primary_expertise = profile_data["primary"]
                metadata.capabilities.secondary_expertise = profile_data["secondary"]
                metadata.capabilities.tools_mastery = profile_data["tools"]
                metadata.capabilities.frameworks_expertise = profile_data["frameworks"]
                break
        else:
            # Default capabilities based on skills
            metadata.capabilities.primary_expertise = skills[:3] if skills else ["General"]
            metadata.capabilities.secondary_expertise = skills[3:6] if len(skills) > 3 else []
        
        # Add common capabilities
        metadata.capabilities.languages_supported = ["English"]
        metadata.capabilities.industry_knowledge = ["Technology", "Software Development"]
    
    @classmethod
    def _set_collaboration_profile(cls, metadata: EnhancedAgentMetadata, category: str):
        """Set collaboration profile based on agent category"""
        
        if "Manager" in metadata.display_name or "Lead" in metadata.display_name:
            metadata.collaboration.collaboration_style = ["coordinator", "mentor"]
            metadata.collaboration.preferred_team_size = "medium"
        elif "Senior" in metadata.display_name:
            metadata.collaboration.collaboration_style = ["mentor", "peer"]
            metadata.collaboration.preferred_team_size = "small"
        else:
            metadata.collaboration.collaboration_style = ["peer", "learner"]
            metadata.collaboration.preferred_team_size = "small"
        
        metadata.collaboration.communication_protocols = ["sync", "async", "webhook"]
        metadata.collaboration.handoff_style = "detailed"
    
    @classmethod
    def _set_performance_profile(cls, metadata: EnhancedAgentMetadata, category: str):
        """Set performance profile based on agent type"""
        
        if category in ["Engineering", "Data & Analytics"]:
            metadata.performance.complexity_handling = "high"
            metadata.performance.parallel_task_capacity = 5
        elif category in ["Customer Support"]:
            metadata.performance.complexity_handling = "medium"
            metadata.performance.avg_response_time_ms = 500
        else:
            metadata.performance.complexity_handling = "medium"
            metadata.performance.parallel_task_capacity = 3
    
    @classmethod
    def _set_discovery_metadata(cls, metadata: EnhancedAgentMetadata, agent_data: Dict[str, Any]):
        """Set discovery metadata for searchability"""
        
        # Extract keywords from various sources
        keywords = set()
        
        # From name
        name_parts = metadata.display_name.split("_")
        keywords.update([part.lower() for part in name_parts])
        
        # From skills
        keywords.update([skill.lower() for skill in agent_data.get("skills", [])])
        
        # From category/subcategory
        keywords.add(agent_data.get("category", "").lower())
        keywords.add(agent_data.get("subcategory", "").lower())
        
        metadata.discovery.search_keywords = keywords
        
        # Set problem domains based on category
        if "Engineering" in agent_data.get("category", ""):
            metadata.discovery.problem_domains = [
                "software development", "system design", "code optimization",
                "bug fixing", "architecture planning"
            ]
        elif "Business" in agent_data.get("category", ""):
            metadata.discovery.problem_domains = [
                "process automation", "workflow optimization", "reporting",
                "compliance", "resource management"
            ]
        
        # Set integration points
        metadata.discovery.integration_points = agent_data.get("tools", [])
        metadata.discovery.data_formats = ["JSON", "XML", "CSV", "YAML"]
    
    @classmethod 
    def _set_network_dependencies(cls, metadata: EnhancedAgentMetadata, canonical_name: str):
        """Set network relationships"""
        
        # Set upstream dependencies based on agent type
        if "frontend" in canonical_name:
            metadata.upstream_dependencies = [
                "aiagents.engineering.backend.*",
                "aiagents.engineering.database.*"
            ]
        elif "backend" in canonical_name:
            metadata.upstream_dependencies = [
                "aiagents.engineering.database.*",
                "aiagents.sre_devops.infrastructure.*"
            ]
        
        # Quality badges
        metadata.quality_badges = ["verified", "production-ready"]
        metadata.trust_score = 0.95


def enhance_agent_with_rich_metadata(agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance agent with rich metadata"""
    
    # Create enhanced metadata
    metadata = MetadataEnricher.create_enhanced_metadata(agent_data)
    
    # Convert to dictionary
    metadata_dict = {
        "agent_uuid": metadata.agent_uuid,
        "canonical_name": metadata.canonical_name,
        "display_name": metadata.display_name,
        "avatar_emoji": metadata.avatar_emoji,
        "version": metadata.version,
        "created_at": metadata.created_at,
        "capabilities": {
            "primary_expertise": metadata.capabilities.primary_expertise,
            "secondary_expertise": metadata.capabilities.secondary_expertise,
            "tools_mastery": metadata.capabilities.tools_mastery,
            "frameworks_expertise": metadata.capabilities.frameworks_expertise,
            "languages_supported": metadata.capabilities.languages_supported,
            "industry_knowledge": metadata.capabilities.industry_knowledge
        },
        "collaboration": {
            "style": metadata.collaboration.collaboration_style,
            "team_size": metadata.collaboration.preferred_team_size,
            "protocols": metadata.collaboration.communication_protocols,
            "handoff_style": metadata.collaboration.handoff_style
        },
        "performance": {
            "response_time_ms": metadata.performance.avg_response_time_ms,
            "complexity": metadata.performance.complexity_handling,
            "parallel_capacity": metadata.performance.parallel_task_capacity,
            "reliability": metadata.performance.reliability_score
        },
        "discovery": {
            "keywords": list(metadata.discovery.search_keywords),
            "problem_domains": metadata.discovery.problem_domains,
            "integrations": metadata.discovery.integration_points,
            "data_formats": metadata.discovery.data_formats
        },
        "network": {
            "upstream": metadata.upstream_dependencies,
            "downstream": metadata.downstream_dependents,
            "peers": metadata.peer_network
        },
        "quality": {
            "trust_score": metadata.trust_score,
            "badges": metadata.quality_badges
        }
    }
    
    agent_data["enhanced_metadata"] = metadata_dict
    
    # Update agent instructions with metadata info
    collab_info = f"\n\n🤖 Agent ID: {metadata.canonical_name}\n"
    collab_info += f"🎯 Specialties: {', '.join(metadata.capabilities.primary_expertise[:3])}\n"
    collab_info += f"🤝 Collaboration Style: {', '.join(metadata.collaboration.collaboration_style)}"
    
    agent_data["instructions"] = agent_data.get("instructions", "") + collab_info
    
    return agent_data