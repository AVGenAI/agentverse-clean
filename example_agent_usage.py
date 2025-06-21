#!/usr/bin/env python3
"""
Example: How AgentVerse Agents Work
Shows the complete flow from configuration to AI response
"""

# 1. AGENT CONFIGURATION (from agentverse_agents_1000.json)
django_agent_config = {
    "name": "DjangoDeveloper_1",
    "instructions": """You are an expert Django backend developer. You can:
- Design and implement RESTful APIs
- Optimize database queries and schema design
- Implement authentication and authorization
- Write unit and integration tests
- Debug and profile Django applications
- Follow Django best practices and conventions
- Implement microservices architecture
- Handle error handling and logging
- Work with caching strategies
- Implement background job processing

🤖 Agent ID: aiagents.engineering.backend_development.djangodeveloper
🎯 Specialties: Django, API Design, Database
🤝 Collaboration Style: peer, learner""",
    
    "model": "gpt-4o-mini",
    "category": "Engineering",
    "subcategory": "Backend Development",
    "skills": ["Django", "API Design", "Database", "Testing", "Microservices"],
    "tools": ["code_analyzer", "test_runner", "performance_profiler"],
    
    "enhanced_metadata": {
        "agent_uuid": "d894cd44259769d6",
        "canonical_name": "agentverse.engineering.backend_development.djangodeveloper",
        "display_name": "DjangoDeveloper_1",
        "avatar_emoji": "🔧",
        "capabilities": {
            "primary_expertise": ["Django", "API Design", "Database"],
            "secondary_expertise": ["Testing", "Microservices"]
        },
        "collaboration": {
            "style": ["mentor", "peer", "learner"],
            "upstream_dependencies": ["agentverse.engineering.architecture.*", "agentverse.data.*"],
            "downstream_dependents": ["agentverse.engineering.frontend.*", "agentverse.qa.*"]
        }
    }
}

# 2. AGENT CREATION (in agent_manager.py)
from agents import Agent, Tool

def create_django_agent(config, api_key):
    """Create a Django Developer agent with OpenAI SDK"""
    
    # Define tools for the agent
    def analyze_code(code: str, language: str = "python") -> str:
        """Analyze Django code for best practices"""
        # This would normally do real analysis
        return f"Analyzed {language} code. Found {len(code.split('\\n'))} lines."
    
    code_analyzer = Tool(
        name="code_analyzer",
        description="Analyze Django code for best practices and issues",
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The code to analyze"},
                "language": {"type": "string", "enum": ["python", "javascript"]}
            },
            "required": ["code"]
        },
        function=analyze_code
    )
    
    # Create the agent using OpenAI Agents SDK
    agent = Agent(
        name=config["enhanced_metadata"]["display_name"],
        model=config["model"],
        instructions=config["instructions"],
        tools=[code_analyzer],
        api_key=api_key
    )
    
    return agent

# 3. USING THE AGENT
def chat_with_django_agent():
    """Example conversation with Django agent"""
    
    # Create agent (normally done by agent_manager)
    agent = create_django_agent(django_agent_config, "sk-your-api-key")
    
    # User asks a question
    user_message = "How should I structure my Django REST API for a blog application?"
    
    # Agent responds (with OpenAI)
    response = agent.run(user_message)
    
    # The response would be something like:
    example_response = """
    As DjangoDeveloper_1, I'd recommend the following structure for your Django REST API blog application:

    ## Project Structure:
    ```
    blog_api/
    ├── blog_api/           # Project settings
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── apps/
    │   ├── posts/          # Blog posts app
    │   │   ├── models.py   # Post, Category models
    │   │   ├── serializers.py
    │   │   ├── views.py    # ViewSets or APIViews
    │   │   └── urls.py
    │   ├── users/          # User management
    │   │   ├── models.py   # Custom User model
    │   │   ├── serializers.py
    │   │   └── views.py
    │   └── comments/       # Comments system
    │       ├── models.py
    │       ├── serializers.py
    │       └── views.py
    └── requirements.txt
    ```

    ## Key Components:

    1. **Models** (posts/models.py):
    ```python
    from django.db import models
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class Category(models.Model):
        name = models.CharField(max_length=100)
        slug = models.SlugField(unique=True)

    class Post(models.Model):
        title = models.CharField(max_length=200)
        slug = models.SlugField(unique=True)
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        content = models.TextField()
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        categories = models.ManyToManyField(Category)
        published = models.BooleanField(default=False)
    ```

    2. **Serializers** (posts/serializers.py):
    ```python
    from rest_framework import serializers
    from .models import Post, Category

    class PostSerializer(serializers.ModelSerializer):
        author = serializers.ReadOnlyField(source='author.username')
        
        class Meta:
            model = Post
            fields = ['id', 'title', 'slug', 'author', 'content', 
                     'created_at', 'categories', 'published']
    ```

    3. **ViewSets** (posts/views.py):
    ```python
    from rest_framework import viewsets, permissions
    from .models import Post
    from .serializers import PostSerializer

    class PostViewSet(viewsets.ModelViewSet):
        queryset = Post.objects.filter(published=True)
        serializer_class = PostSerializer
        lookup_field = 'slug'
        
        def get_permissions(self):
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAuthenticated()]
            return [permissions.AllowAny()]
    ```

    ## Best Practices I Recommend:
    - Use ViewSets for standard CRUD operations
    - Implement proper authentication (JWT or Token)
    - Add pagination for list views
    - Use slug fields for SEO-friendly URLs
    - Implement caching with Redis
    - Add comprehensive tests
    - Use Django-filter for advanced filtering

    Would you like me to elaborate on any specific aspect?
    """
    
    return example_response

# 4. WITH OLLAMA FALLBACK (in agent_manager.py)
async def chat_with_ollama_fallback(agent_id: str, message: str):
    """How AgentVerse handles Ollama + OpenAI fallback"""
    
    # First, try Ollama (local AI)
    if ollama_available:
        prompt = f"""You are {agent_config['display_name']}, an expert in {', '.join(agent_config['skills'])}.
        
User: {message}
Assistant:"""
        
        ollama_response = await ollama_chat(prompt)
        if ollama_response:
            return ollama_response
    
    # Fallback to OpenAI
    if openai_api_key:
        agent = create_django_agent(agent_config, openai_api_key)
        return agent.run(message)
    
    # Final fallback to mock
    return f"I'm {agent_config['display_name']}. {message} [Mock response - configure LLM]"

# 5. TOOLS IN ACTION
def example_with_tools():
    """Show how agents use tools"""
    
    user_message = """Can you analyze this Django view for issues?
    
    def get_posts(request):
        posts = Post.objects.all()
        return JsonResponse({'posts': posts})
    """
    
    # Agent would:
    # 1. Recognize code in the message
    # 2. Call the code_analyzer tool
    # 3. Provide analysis based on tool output + knowledge
    
    agent_response = """I'll analyze your Django view using my code analyzer.

    <calling tool: code_analyzer>
    
    I found several issues in your Django view:

    1. **Serialization Error**: You're trying to serialize QuerySet directly
       - `posts` is a QuerySet, not JSON-serializable
       - Fix: Use Django REST Framework serializers or values()
    
    2. **No Pagination**: Loading all posts can cause performance issues
       - Add pagination for large datasets
    
    3. **No Error Handling**: The view lacks exception handling
    
    Here's the corrected version:
    
    ```python
    from django.http import JsonResponse
    from django.core.paginator import Paginator
    from .models import Post
    
    def get_posts(request):
        try:
            posts = Post.objects.all().values('id', 'title', 'author', 'created_at')
            
            # Add pagination
            paginator = Paginator(posts, 20)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return JsonResponse({
                'posts': list(page_obj),
                'total': paginator.count,
                'pages': paginator.num_pages
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    ```
    
    This addresses all the issues and follows Django best practices.
    """
    
    return agent_response

if __name__ == "__main__":
    print("=== AgentVerse Agent Example ===\n")
    
    print("1. Agent Configuration:")
    print(f"   Name: {django_agent_config['name']}")
    print(f"   Skills: {', '.join(django_agent_config['skills'])}")
    print(f"   Tools: {', '.join(django_agent_config['tools'])}")
    
    print("\n2. Example Response:")
    print(chat_with_django_agent()[:500] + "...")
    
    print("\n3. With Tools:")
    print(example_with_tools()[:500] + "...")
    
    print("\n=== How It Works ===")
    print("1. Agent config defines personality, skills, and tools")
    print("2. Agent Manager creates OpenAI Agent instances")
    print("3. Agents respond based on their instructions")
    print("4. Tools enhance agent capabilities")
    print("5. Ollama provides local fallback option")