#!/usr/bin/env python3
"""
Agent Verse Taxonomy V2 - Enhanced Naming Conventions
"""
from typing import Dict, List, Optional
import hashlib
import time

class AgentTaxonomyV2:
    """
    Enhanced taxonomy system for Agent Verse
    
    Naming Convention:
    {namespace}.{domain}.{type}.{specialization}.{version}.{unique_id}
    
    Example: av.sre.specialist.monitoring.v2.3f4a2b1c
    """
    
    # Namespace
    NAMESPACE = "av"  # Agent Verse
    
    # Domains (Primary Categories)
    DOMAINS = {
        "sre": "Site Reliability Engineering",
        "devops": "Development Operations",
        "sec": "Security",
        "data": "Data & Analytics",
        "eng": "Engineering",
        "ml": "Machine Learning",
        "cloud": "Cloud Infrastructure",
        "net": "Networking",
        "db": "Database",
        "ui": "User Interface",
        "qa": "Quality Assurance",
        "fin": "Finance",
        "health": "Healthcare",
        "edu": "Education",
        "iot": "Internet of Things"
    }
    
    # Agent Types
    TYPES = {
        "spec": "Specialist",      # Domain expert
        "coord": "Coordinator",    # Multi-agent orchestrator
        "anal": "Analyzer",        # Data analyzer
        "exec": "Executor",        # Task executor
        "mon": "Monitor",          # System monitor
        "val": "Validator",        # Quality validator
        "opt": "Optimizer",        # Performance optimizer
        "gen": "Generator",        # Content generator
        "trans": "Transformer",    # Data transformer
        "guard": "Guardian"        # Security/compliance guard
    }
    
    # Specializations (Sub-domains)
    SPECIALIZATIONS = {
        "sre": ["incident", "slo", "monitoring", "capacity", "reliability"],
        "devops": ["ci", "cd", "k8s", "terraform", "ansible"],
        "sec": ["audit", "compliance", "threat", "access", "crypto"],
        "data": ["etl", "analytics", "viz", "warehouse", "pipeline"],
        "eng": ["frontend", "backend", "api", "mobile", "embedded"],
        "ml": ["nlp", "cv", "rl", "timeseries", "recommendation"],
        "cloud": ["aws", "azure", "gcp", "hybrid", "cost"],
        "db": ["sql", "nosql", "cache", "search", "graph"]
    }
    
    @staticmethod
    def generate_agent_id(
        domain: str,
        agent_type: str,
        specialization: Optional[str] = None,
        version: str = "v1",
        custom_suffix: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a complete agent identity with all taxonomy information
        """
        # Validate inputs
        domain_code = domain if domain in AgentTaxonomyV2.DOMAINS else "gen"
        type_code = agent_type if agent_type in AgentTaxonomyV2.TYPES else "spec"
        
        # Generate unique ID
        if custom_suffix:
            unique_id = custom_suffix
        else:
            # Generate 8-character unique ID based on timestamp and hash
            timestamp = str(int(time.time() * 1000000))
            hash_input = f"{domain}{agent_type}{specialization}{timestamp}"
            unique_id = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        
        # Build canonical name
        parts = [
            AgentTaxonomyV2.NAMESPACE,
            domain_code,
            type_code
        ]
        
        if specialization:
            parts.append(specialization.lower().replace(" ", "_"))
            
        parts.extend([version, unique_id])
        
        canonical_name = ".".join(parts)
        
        # Generate display name
        display_parts = []
        if specialization:
            display_parts.append(specialization.title())
        display_parts.append(AgentTaxonomyV2.TYPES.get(type_code, "Agent"))
        if domain_code != "gen":
            display_parts.append(f"({AgentTaxonomyV2.DOMAINS.get(domain_code, domain_code).split()[0]})")
            
        display_name = " ".join(display_parts)
        
        # Generate short ID for UI display
        short_id = f"{domain_code.upper()}-{type_code.upper()}-{unique_id[:4].upper()}"
        
        return {
            "canonical_name": canonical_name,
            "display_name": display_name,
            "short_id": short_id,
            "namespace": AgentTaxonomyV2.NAMESPACE,
            "domain": domain_code,
            "type": type_code,
            "specialization": specialization,
            "version": version,
            "unique_id": unique_id,
            "taxonomy_version": "2.0"
        }
    
    @staticmethod
    def parse_canonical_name(canonical_name: str) -> Dict[str, str]:
        """Parse a canonical name back into its components"""
        parts = canonical_name.split(".")
        
        result = {
            "canonical_name": canonical_name,
            "valid": False
        }
        
        if len(parts) >= 5 and parts[0] == AgentTaxonomyV2.NAMESPACE:
            result.update({
                "valid": True,
                "namespace": parts[0],
                "domain": parts[1],
                "type": parts[2],
                "version": parts[-2],
                "unique_id": parts[-1]
            })
            
            # Extract specialization if present
            if len(parts) > 5:
                result["specialization"] = parts[3]
                
        return result
    
    @staticmethod
    def get_hierarchy(domain: str) -> Dict[str, List[str]]:
        """Get the full hierarchy for a domain"""
        return {
            "domain": domain,
            "domain_name": AgentTaxonomyV2.DOMAINS.get(domain, "Unknown"),
            "available_types": list(AgentTaxonomyV2.TYPES.keys()),
            "specializations": AgentTaxonomyV2.SPECIALIZATIONS.get(domain, []),
            "naming_pattern": f"av.{domain}.<type>.[specialization].version.unique_id"
        }
    
    @staticmethod
    def validate_agent_name(canonical_name: str) -> Dict[str, any]:
        """Validate if an agent name follows the taxonomy"""
        parsed = AgentTaxonomyV2.parse_canonical_name(canonical_name)
        
        if not parsed["valid"]:
            return {
                "valid": False,
                "errors": ["Invalid canonical name format"]
            }
            
        errors = []
        warnings = []
        
        # Check domain
        if parsed["domain"] not in AgentTaxonomyV2.DOMAINS:
            warnings.append(f"Unknown domain: {parsed['domain']}")
            
        # Check type
        if parsed["type"] not in AgentTaxonomyV2.TYPES:
            warnings.append(f"Unknown type: {parsed['type']}")
            
        # Check version format
        if not parsed["version"].startswith("v"):
            errors.append(f"Version should start with 'v': {parsed['version']}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "parsed": parsed
        }

# Example usage
if __name__ == "__main__":
    # Generate some example agents
    examples = [
        AgentTaxonomyV2.generate_agent_id("sre", "spec", "incident"),
        AgentTaxonomyV2.generate_agent_id("ml", "anal", "nlp", "v2"),
        AgentTaxonomyV2.generate_agent_id("devops", "coord", "kubernetes"),
        AgentTaxonomyV2.generate_agent_id("data", "exec", "etl_pipeline", "v1", "prod001"),
    ]
    
    print("Agent Taxonomy V2 Examples:")
    print("=" * 80)
    
    for agent in examples:
        print(f"\nCanonical: {agent['canonical_name']}")
        print(f"Display:   {agent['display_name']}")
        print(f"Short ID:  {agent['short_id']}")
        print(f"Domain:    {agent['domain']} ({AgentTaxonomyV2.DOMAINS.get(agent['domain'])})")
        print(f"Type:      {agent['type']} ({AgentTaxonomyV2.TYPES.get(agent['type'])})")
        if agent.get('specialization'):
            print(f"Spec:      {agent['specialization']}")
            
    # Show hierarchy
    print("\n\nSRE Domain Hierarchy:")
    print("=" * 80)
    hierarchy = AgentTaxonomyV2.get_hierarchy("sre")
    print(f"Domain: {hierarchy['domain_name']}")
    print(f"Types: {', '.join([f'{k} ({v})' for k, v in AgentTaxonomyV2.TYPES.items()][:5])}")
    print(f"Specializations: {', '.join(hierarchy['specializations'])}")
    print(f"Pattern: {hierarchy['naming_pattern']}")