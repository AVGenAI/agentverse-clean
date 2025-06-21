#!/usr/bin/env python3
"""
Agent Behavior System
Implements advanced behavioral patterns and interaction models
"""

import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class InteractionMode(Enum):
    """Agent interaction modes"""
    COLLABORATIVE = "collaborative"
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    DELEGATED = "delegated"
    CONSULTATIVE = "consultative"

class ResponseStyle(Enum):
    """Response communication styles"""
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"

class ProblemSolvingApproach(Enum):
    """Problem solving approaches"""
    SYSTEMATIC = "systematic"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    ITERATIVE = "iterative"
    HOLISTIC = "holistic"

@dataclass
class BehaviorProfile:
    """Agent behavior profile"""
    interaction_mode: InteractionMode
    response_style: ResponseStyle
    problem_solving: ProblemSolvingApproach
    proactivity_level: float = 0.7  # 0-1 scale
    detail_preference: float = 0.5   # 0-1 scale
    risk_tolerance: float = 0.3      # 0-1 scale
    learning_rate: float = 0.8       # 0-1 scale
    collaboration_preference: float = 0.6  # 0-1 scale

@dataclass
class InteractionContext:
    """Context for agent interactions"""
    user_expertise: str = "intermediate"
    task_complexity: str = "medium"
    time_constraints: Optional[int] = None  # minutes
    quality_requirements: str = "high"
    collaboration_mode: str = "interactive"
    previous_interactions: List[Dict] = field(default_factory=list)

@dataclass
class BehaviorRule:
    """Behavioral rule definition"""
    name: str
    condition: Callable[[InteractionContext], bool]
    action: Callable[[Any], Any]
    priority: int = 5
    description: str = ""

class AgentBehaviorSystem:
    """Manages agent behavioral patterns and interactions"""
    
    def __init__(self):
        self.behavior_profiles = self._initialize_behavior_profiles()
        self.behavior_rules = self._initialize_behavior_rules()
        self.interaction_patterns = self._initialize_interaction_patterns()
        self.adaptation_strategies = self._initialize_adaptation_strategies()
    
    def _initialize_behavior_profiles(self) -> Dict[str, BehaviorProfile]:
        """Initialize behavior profiles for different agent types"""
        return {
            "engineering_expert": BehaviorProfile(
                interaction_mode=InteractionMode.COLLABORATIVE,
                response_style=ResponseStyle.TECHNICAL,
                problem_solving=ProblemSolvingApproach.SYSTEMATIC,
                proactivity_level=0.8,
                detail_preference=0.9,
                risk_tolerance=0.3,
                learning_rate=0.9,
                collaboration_preference=0.7
            ),
            "business_analyst": BehaviorProfile(
                interaction_mode=InteractionMode.CONSULTATIVE,
                response_style=ResponseStyle.EXECUTIVE,
                problem_solving=ProblemSolvingApproach.ANALYTICAL,
                proactivity_level=0.7,
                detail_preference=0.6,
                risk_tolerance=0.4,
                learning_rate=0.7,
                collaboration_preference=0.8
            ),
            "data_scientist": BehaviorProfile(
                interaction_mode=InteractionMode.AUTONOMOUS,
                response_style=ResponseStyle.ANALYTICAL,
                problem_solving=ProblemSolvingApproach.ITERATIVE,
                proactivity_level=0.6,
                detail_preference=0.8,
                risk_tolerance=0.5,
                learning_rate=0.9,
                collaboration_preference=0.5
            ),
            "security_specialist": BehaviorProfile(
                interaction_mode=InteractionMode.SUPERVISED,
                response_style=ResponseStyle.TECHNICAL,
                problem_solving=ProblemSolvingApproach.SYSTEMATIC,
                proactivity_level=0.9,
                detail_preference=0.95,
                risk_tolerance=0.1,
                learning_rate=0.8,
                collaboration_preference=0.4
            ),
            "support_specialist": BehaviorProfile(
                interaction_mode=InteractionMode.COLLABORATIVE,
                response_style=ResponseStyle.EDUCATIONAL,
                problem_solving=ProblemSolvingApproach.CREATIVE,
                proactivity_level=0.8,
                detail_preference=0.5,
                risk_tolerance=0.3,
                learning_rate=0.7,
                collaboration_preference=0.9
            ),
            "devops_engineer": BehaviorProfile(
                interaction_mode=InteractionMode.AUTONOMOUS,
                response_style=ResponseStyle.TECHNICAL,
                problem_solving=ProblemSolvingApproach.ITERATIVE,
                proactivity_level=0.9,
                detail_preference=0.7,
                risk_tolerance=0.4,
                learning_rate=0.8,
                collaboration_preference=0.6
            )
        }
    
    def _initialize_behavior_rules(self) -> List[BehaviorRule]:
        """Initialize behavioral rules"""
        return [
            BehaviorRule(
                name="high_complexity_detailed_response",
                condition=lambda ctx: ctx.task_complexity == "high",
                action=lambda agent: setattr(agent, 'detail_preference', min(1.0, agent.detail_preference + 0.2)),
                priority=8,
                description="Increase detail for complex tasks"
            ),
            BehaviorRule(
                name="time_constraint_efficiency",
                condition=lambda ctx: ctx.time_constraints is not None and ctx.time_constraints < 30,
                action=lambda agent: setattr(agent, 'detail_preference', max(0.3, agent.detail_preference - 0.3)),
                priority=9,
                description="Reduce detail under time pressure"
            ),
            BehaviorRule(
                name="novice_user_education",
                condition=lambda ctx: ctx.user_expertise == "novice",
                action=lambda agent: setattr(agent, 'response_style', ResponseStyle.EDUCATIONAL),
                priority=7,
                description="Use educational style for novice users"
            ),
            BehaviorRule(
                name="expert_user_technical",
                condition=lambda ctx: ctx.user_expertise == "expert",
                action=lambda agent: setattr(agent, 'response_style', ResponseStyle.TECHNICAL),
                priority=7,
                description="Use technical style for expert users"
            ),
            BehaviorRule(
                name="critical_task_caution",
                condition=lambda ctx: ctx.quality_requirements == "critical",
                action=lambda agent: setattr(agent, 'risk_tolerance', max(0.1, agent.risk_tolerance - 0.2)),
                priority=10,
                description="Reduce risk tolerance for critical tasks"
            ),
            BehaviorRule(
                name="collaborative_mode_adjustment",
                condition=lambda ctx: ctx.collaboration_mode == "team",
                action=lambda agent: setattr(agent, 'collaboration_preference', min(1.0, agent.collaboration_preference + 0.2)),
                priority=6,
                description="Increase collaboration in team mode"
            ),
            BehaviorRule(
                name="learning_from_feedback",
                condition=lambda ctx: len(ctx.previous_interactions) > 5,
                action=lambda agent: setattr(agent, 'learning_rate', min(1.0, agent.learning_rate + 0.1)),
                priority=5,
                description="Increase learning rate with more interactions"
            )
        ]
    
    def _initialize_interaction_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize interaction patterns"""
        return {
            "code_review": {
                "pattern": "systematic_analysis",
                "steps": [
                    {"action": "analyze_structure", "detail": "high"},
                    {"action": "check_patterns", "detail": "medium"},
                    {"action": "suggest_improvements", "detail": "high"},
                    {"action": "provide_examples", "detail": "medium"}
                ],
                "communication": "technical",
                "collaboration": "iterative"
            },
            "problem_diagnosis": {
                "pattern": "investigative",
                "steps": [
                    {"action": "gather_information", "detail": "high"},
                    {"action": "analyze_symptoms", "detail": "high"},
                    {"action": "identify_root_cause", "detail": "medium"},
                    {"action": "propose_solutions", "detail": "high"}
                ],
                "communication": "analytical",
                "collaboration": "interactive"
            },
            "implementation_guidance": {
                "pattern": "educational",
                "steps": [
                    {"action": "explain_concept", "detail": "medium"},
                    {"action": "provide_example", "detail": "high"},
                    {"action": "guide_implementation", "detail": "high"},
                    {"action": "review_result", "detail": "medium"}
                ],
                "communication": "educational",
                "collaboration": "mentoring"
            },
            "optimization_task": {
                "pattern": "iterative",
                "steps": [
                    {"action": "baseline_measurement", "detail": "medium"},
                    {"action": "identify_bottlenecks", "detail": "high"},
                    {"action": "implement_improvements", "detail": "medium"},
                    {"action": "measure_impact", "detail": "medium"}
                ],
                "communication": "analytical",
                "collaboration": "autonomous"
            },
            "emergency_response": {
                "pattern": "rapid_action",
                "steps": [
                    {"action": "assess_situation", "detail": "low"},
                    {"action": "immediate_mitigation", "detail": "low"},
                    {"action": "implement_fix", "detail": "medium"},
                    {"action": "post_mortem", "detail": "high"}
                ],
                "communication": "concise",
                "collaboration": "directive"
            }
        }
    
    def _initialize_adaptation_strategies(self) -> Dict[str, Callable]:
        """Initialize adaptation strategies"""
        return {
            "user_preference_learning": self._adapt_to_user_preferences,
            "task_pattern_recognition": self._adapt_to_task_patterns,
            "performance_optimization": self._adapt_for_performance,
            "collaboration_enhancement": self._adapt_collaboration_style,
            "context_awareness": self._adapt_to_context
        }
    
    def _adapt_to_user_preferences(self, profile: BehaviorProfile, context: InteractionContext) -> BehaviorProfile:
        """Adapt behavior based on user preferences"""
        # Analyze previous interactions
        if context.previous_interactions:
            feedback_scores = [i.get('feedback_score', 0.5) for i in context.previous_interactions[-5:]]
            avg_score = sum(feedback_scores) / len(feedback_scores)
            
            # Adjust based on feedback
            if avg_score > 0.8:
                # Current approach working well, slightly increase current preferences
                profile.proactivity_level = min(1.0, profile.proactivity_level + 0.05)
            elif avg_score < 0.4:
                # Need to adjust approach
                profile.detail_preference = 0.5  # Reset to balanced
                profile.response_style = ResponseStyle.CONVERSATIONAL
        
        return profile
    
    def _adapt_to_task_patterns(self, profile: BehaviorProfile, context: InteractionContext) -> BehaviorProfile:
        """Adapt based on task patterns"""
        # Identify task type patterns
        recent_tasks = [i.get('task_type') for i in context.previous_interactions[-10:]]
        
        if recent_tasks.count('debugging') > 5:
            profile.problem_solving = ProblemSolvingApproach.SYSTEMATIC
            profile.detail_preference = min(1.0, profile.detail_preference + 0.1)
        elif recent_tasks.count('design') > 5:
            profile.problem_solving = ProblemSolvingApproach.CREATIVE
            profile.collaboration_preference = min(1.0, profile.collaboration_preference + 0.1)
        
        return profile
    
    def _adapt_for_performance(self, profile: BehaviorProfile, context: InteractionContext) -> BehaviorProfile:
        """Adapt for optimal performance"""
        if context.time_constraints and context.time_constraints < 15:
            # Extreme time pressure
            profile.detail_preference = 0.3
            profile.proactivity_level = 0.9
            profile.interaction_mode = InteractionMode.AUTONOMOUS
        elif context.quality_requirements == "critical":
            # High quality requirements
            profile.detail_preference = 0.9
            profile.risk_tolerance = 0.1
            profile.problem_solving = ProblemSolvingApproach.SYSTEMATIC
        
        return profile
    
    def _adapt_collaboration_style(self, profile: BehaviorProfile, context: InteractionContext) -> BehaviorProfile:
        """Adapt collaboration style"""
        if context.collaboration_mode == "pair_programming":
            profile.interaction_mode = InteractionMode.COLLABORATIVE
            profile.collaboration_preference = 0.9
            profile.proactivity_level = 0.6  # Let partner lead sometimes
        elif context.collaboration_mode == "review":
            profile.interaction_mode = InteractionMode.CONSULTATIVE
            profile.detail_preference = 0.8
            profile.response_style = ResponseStyle.ANALYTICAL
        
        return profile
    
    def _adapt_to_context(self, profile: BehaviorProfile, context: InteractionContext) -> BehaviorProfile:
        """General context adaptation"""
        # Time of day adaptation (simulated)
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            # Late night/early morning - assume urgent
            profile.proactivity_level = min(1.0, profile.proactivity_level + 0.1)
            profile.detail_preference = max(0.4, profile.detail_preference - 0.2)
        
        return profile
    
    def generate_behavior_config(self, agent_type: str, context: InteractionContext) -> Dict[str, Any]:
        """Generate behavior configuration for an agent"""
        
        # Get base profile
        base_profile = self.behavior_profiles.get(
            agent_type, 
            self.behavior_profiles["engineering_expert"]
        )
        
        # Apply adaptation strategies
        adapted_profile = base_profile
        for strategy_name, strategy_func in self.adaptation_strategies.items():
            adapted_profile = strategy_func(adapted_profile, context)
        
        # Apply behavior rules
        applicable_rules = sorted(
            [rule for rule in self.behavior_rules if rule.condition(context)],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in applicable_rules:
            rule.action(adapted_profile)
        
        # Generate configuration
        config = {
            "behavior_profile": {
                "interaction_mode": adapted_profile.interaction_mode.value,
                "response_style": adapted_profile.response_style.value,
                "problem_solving_approach": adapted_profile.problem_solving.value,
                "proactivity_level": adapted_profile.proactivity_level,
                "detail_preference": adapted_profile.detail_preference,
                "risk_tolerance": adapted_profile.risk_tolerance,
                "learning_rate": adapted_profile.learning_rate,
                "collaboration_preference": adapted_profile.collaboration_preference
            },
            "applied_rules": [rule.name for rule in applicable_rules],
            "context_adaptations": self._get_context_adaptations(context),
            "recommended_patterns": self._get_recommended_patterns(adapted_profile, context),
            "communication_guidelines": self._get_communication_guidelines(adapted_profile),
            "collaboration_settings": self._get_collaboration_settings(adapted_profile)
        }
        
        return config
    
    def _get_context_adaptations(self, context: InteractionContext) -> List[str]:
        """Get list of context adaptations"""
        adaptations = []
        
        if context.time_constraints:
            adaptations.append(f"time_optimized (< {context.time_constraints} min)")
        if context.user_expertise == "novice":
            adaptations.append("beginner_friendly")
        elif context.user_expertise == "expert":
            adaptations.append("expert_mode")
        if context.quality_requirements == "critical":
            adaptations.append("high_precision")
        if len(context.previous_interactions) > 10:
            adaptations.append("historically_informed")
        
        return adaptations
    
    def _get_recommended_patterns(self, profile: BehaviorProfile, context: InteractionContext) -> List[str]:
        """Get recommended interaction patterns"""
        patterns = []
        
        # Map problem-solving approach to patterns
        approach_patterns = {
            ProblemSolvingApproach.SYSTEMATIC: ["code_review", "problem_diagnosis"],
            ProblemSolvingApproach.CREATIVE: ["implementation_guidance", "optimization_task"],
            ProblemSolvingApproach.ANALYTICAL: ["problem_diagnosis", "optimization_task"],
            ProblemSolvingApproach.ITERATIVE: ["optimization_task", "implementation_guidance"],
            ProblemSolvingApproach.HOLISTIC: ["code_review", "implementation_guidance"]
        }
        
        patterns.extend(approach_patterns.get(profile.problem_solving, []))
        
        # Add context-specific patterns
        if context.time_constraints and context.time_constraints < 30:
            patterns.append("emergency_response")
        
        return list(set(patterns))  # Remove duplicates
    
    def _get_communication_guidelines(self, profile: BehaviorProfile) -> Dict[str, Any]:
        """Get communication guidelines based on profile"""
        guidelines = {
            "verbosity": "high" if profile.detail_preference > 0.7 else "medium" if profile.detail_preference > 0.4 else "low",
            "technical_level": {
                ResponseStyle.TECHNICAL: "expert",
                ResponseStyle.EXECUTIVE: "business",
                ResponseStyle.EDUCATIONAL: "explanatory",
                ResponseStyle.CONVERSATIONAL: "casual",
                ResponseStyle.ANALYTICAL: "data-driven"
            }.get(profile.response_style, "balanced"),
            "proactive_suggestions": profile.proactivity_level > 0.7,
            "include_examples": profile.response_style in [ResponseStyle.EDUCATIONAL, ResponseStyle.CONVERSATIONAL],
            "include_metrics": profile.response_style == ResponseStyle.ANALYTICAL,
            "error_handling": "detailed" if profile.detail_preference > 0.6 else "summary"
        }
        
        return guidelines
    
    def _get_collaboration_settings(self, profile: BehaviorProfile) -> Dict[str, Any]:
        """Get collaboration settings"""
        return {
            "mode": profile.interaction_mode.value,
            "handoff_style": "detailed" if profile.detail_preference > 0.6 else "summary",
            "feedback_frequency": "continuous" if profile.collaboration_preference > 0.7 else "periodic",
            "decision_making": "consultative" if profile.collaboration_preference > 0.6 else "autonomous",
            "information_sharing": "proactive" if profile.proactivity_level > 0.7 else "on-request",
            "conflict_resolution": "collaborative" if profile.collaboration_preference > 0.5 else "directive"
        }
    
    def simulate_interaction(self, agent_type: str, context: InteractionContext, task: str) -> Dict[str, Any]:
        """Simulate an agent interaction with behavioral patterns"""
        
        # Generate behavior config
        config = self.generate_behavior_config(agent_type, context)
        
        # Select interaction pattern
        patterns = config['recommended_patterns']
        selected_pattern = self.interaction_patterns.get(
            patterns[0] if patterns else "code_review"
        )
        
        # Simulate interaction steps
        interaction_log = []
        for step in selected_pattern['steps']:
            interaction_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": step['action'],
                "detail_level": step['detail'],
                "behavior_modifiers": {
                    "proactivity": config['behavior_profile']['proactivity_level'],
                    "risk_assessment": 1.0 - config['behavior_profile']['risk_tolerance']
                }
            })
        
        # Generate response
        response = {
            "interaction_id": str(uuid.uuid4()),
            "agent_type": agent_type,
            "task": task,
            "behavior_config": config,
            "interaction_pattern": selected_pattern['pattern'],
            "steps_executed": interaction_log,
            "estimated_duration": len(selected_pattern['steps']) * 5,  # minutes
            "confidence_level": 0.9 * (1.0 - config['behavior_profile']['risk_tolerance']),
            "collaboration_readiness": config['behavior_profile']['collaboration_preference']
        }
        
        return response

def demonstrate_behavior_system():
    """Demonstrate the behavior system"""
    system = AgentBehaviorSystem()
    
    console.print(Panel.fit(
        "[bold cyan]Agent Behavior System Demonstration[/bold cyan]",
        border_style="cyan"
    ))
    
    # Test different contexts
    test_contexts = [
        {
            "name": "Urgent Bug Fix",
            "context": InteractionContext(
                user_expertise="expert",
                task_complexity="high",
                time_constraints=15,
                quality_requirements="critical",
                collaboration_mode="autonomous"
            ),
            "agent": "engineering_expert",
            "task": "Fix critical production bug"
        },
        {
            "name": "Teaching Session",
            "context": InteractionContext(
                user_expertise="novice",
                task_complexity="medium",
                time_constraints=60,
                quality_requirements="high",
                collaboration_mode="interactive"
            ),
            "agent": "support_specialist",
            "task": "Explain API integration"
        },
        {
            "name": "Security Audit",
            "context": InteractionContext(
                user_expertise="intermediate",
                task_complexity="high",
                time_constraints=None,
                quality_requirements="critical",
                collaboration_mode="supervised"
            ),
            "agent": "security_specialist",
            "task": "Perform security audit"
        }
    ]
    
    for test in test_contexts:
        console.print(f"\n[yellow]Scenario: {test['name']}[/yellow]")
        
        # Generate behavior config
        config = system.generate_behavior_config(test['agent'], test['context'])
        
        # Display behavior profile
        profile = config['behavior_profile']
        table = Table(title="Behavior Profile")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Interaction Mode", profile['interaction_mode'])
        table.add_row("Response Style", profile['response_style'])
        table.add_row("Problem Solving", profile['problem_solving_approach'])
        table.add_row("Proactivity", f"{profile['proactivity_level']:.2f}")
        table.add_row("Detail Level", f"{profile['detail_preference']:.2f}")
        table.add_row("Risk Tolerance", f"{profile['risk_tolerance']:.2f}")
        
        console.print(table)
        
        # Show applied rules
        if config['applied_rules']:
            console.print(f"Applied Rules: {', '.join(config['applied_rules'])}")
        
        # Show adaptations
        if config['context_adaptations']:
            console.print(f"Adaptations: {', '.join(config['context_adaptations'])}")

if __name__ == "__main__":
    demonstrate_behavior_system()