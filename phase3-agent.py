"""

current test case:

Compare the growth of owning Google, Microsoft, or a home in Orlando, Florida over the past 3 years, 5 years, and 10 years. At what point does it make sense to invest in a home, or versus at what point does it make sense to invest in a tech stock?
Begin by logging the research questions.



Phase 3 Multi-Agent System - Research Orchestrator + Memory Agent
Goal: Main research agent with memory management capabilities

📋 RESEARCH DOCUMENT STRUCTURE:
{
    "findings": [
        {
            "content": "NYC population is 8.3 million",
            "source": "search_tool",
            "confidence": "high",
            "related_questions": ["What is the population of NYC?"],
            "timestamp": "2024-01-01T12:00:00"
        }
    ],
    "open_questions": [
        "What is the population of NYC?",
        "What is the population of San Francisco?"
    ],
    "closed_questions": [
        {
            "question": "What is the population of NYC?",
            "status": "closed_complete",
            "answer": "8.3 million people",
            "evidence": ["Search result from census data"],
            "confidence": "high",
            "closed": "2024-01-01T12:00:00"
        }
    ]
}

🎯 TEST CASES - Cool Research Questions:

1. Population Comparison:
   "What is the population of New York City divided by the population of San Francisco?"

2. Gaming Industry Analysis:
   "What are the top 3 highest-grossing video games of 2024? Calculate the total revenue. What percent of the gaming industry's revenue is this?"

3. Stock Market Math:
   "Find Apple's current stock price and calculate how much 1000 shares would cost, including a 2% trading fee."

4. Climate Data:
   "What's the average temperature difference between Miami and Seattle in January?"

5. Economic Comparison:
   "Compare the GDP per capita of Japan vs South Korea. What's the percentage difference?"

6. Sports Statistics:
   "Who scored the most goals in the 2024 FIFA season? How many more than the second place?"

7. Tech Company Valuation:
   "What are the current market caps of Google and Microsoft? Calculate the ratio."

8. Real Estate Analysis:
   "What's the average home price in Austin, Texas? How many homes could you buy with $10 million?"

9. Space Exploration:
   "How much did the James Webb Space Telescope cost? Compare that to NASA's annual budget."

10. Reflection Challenge:
    "Based on the data you've gathered, what insights can you draw about market trends?"
"""

import inspect
import os
from typing import Annotated, List

import requests
from dotenv import load_dotenv
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langsmith import traceable
from typing_extensions import TypedDict

# Load environment variables
load_dotenv()

# Define our agent's state


def create_empty_research_document() -> dict:
    """Create an empty research document with proper structure"""
    return {
        # List of finding objects: {"content": str, "source": str, "confidence": str, "related_questions": List[str], "timestamp": str}
        "findings": [],
        "open_questions": [],  # List of question strings: "What is the population of NYC?"
        # List of closed question objects: {"question": str, "status": str, "answer": str, "evidence": List[str], "confidence": str, "closed": str}
        "closed_questions": []
    }


class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage |
                             ToolMessage], add_messages]
    # Memory agent's document store - initialized with create_empty_research_document()
    research_document: dict

# Data Analysis Tool - CONVERTED TO NODE-TO-NODE ROUTING


@traceable
def data_analysis_node(state: AgentState) -> AgentState:
    """Perform mathematical calculations and data analysis operations"""

    # Extract calculation request from the executor's decision
    last_message = state["messages"][-1]
    content = last_message.content

    # Parse the CALCULATION section
    expression = ""
    if "CALCULATION:" in content:
        calc_part = content.split("CALCULATION:")[1].strip()
        expression = calc_part.split("\n")[0].strip()
    elif "calculate" in content.lower():
        # Try to extract expression from natural language
        import re

        # Look for mathematical expressions in the content
        math_pattern = r'[\d+\-*/().%\s]+'
        matches = re.findall(math_pattern, content)
        if matches:
            expression = max(matches, key=len).strip()

    if expression:
        try:
            # Clean the expression - remove any non-mathematical characters except basic operators
            import re

            # Allow numbers, operators, parentheses, decimal points, and spaces
            cleaned = re.sub(r'[^0-9+\-*/(). ]', '', expression)

            # Evaluate the mathematical expression safely
            result = eval(cleaned)

            result_message = f"📊 Calculation: {expression} = {result}"
            print(f"   🔢 {result_message}")

            return {
                "messages": [AIMessage(content=result_message)]
            }
        except Exception as e:
            error_message = f"❌ Error calculating '{expression}': {str(e)}"
            print(f"   🔢 {error_message}")
            return {
                "messages": [AIMessage(content=error_message)]
            }
    else:
        error_message = "❌ Could not extract calculation from executor decision"
        print(f"   🔢 {error_message}")
        return {
            "messages": [AIMessage(content=error_message)]
        }

# Search Tool - CONVERTED TO NODE-TO-NODE ROUTING


@traceable
def search_node(state: AgentState) -> AgentState:
    """Search the web for information using Perplexity API"""

    # Extract search query from the executor's decision
    last_message = state["messages"][-1]
    content = last_message.content

    # Parse the SEARCH section
    query = ""
    if "SEARCH:" in content:
        search_part = content.split("SEARCH:")[1].strip()
        query = search_part.split("\n")[0].strip()
    elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Handle tool call format for backward compatibility
        tool_args = last_message.tool_calls[0].get('args', {})
        query = tool_args.get('query', '')

    if query:
        try:
            url = "https://api.perplexity.ai/chat/completions"

            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant. Provide accurate, up-to-date information based on web search results. Be concise and include relevant details like dates or sources when available."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.1,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            search_info = result['choices'][0]['message']['content']

            result_message = f"🔍 Search results for '{query}': {search_info}"
            print(f"   🌐 Searched: {query}")

            return {
                "messages": [AIMessage(content=result_message)]
            }

        except Exception as e:
            error_message = f"❌ Error searching for '{query}': {str(e)}"
            print(f"   🌐 {error_message}")
            return {
                "messages": [AIMessage(content=error_message)]
            }
    else:
        error_message = "❌ Could not extract search query from executor decision"
        print(f"   🌐 {error_message}")
        return {
            "messages": [AIMessage(content=error_message)]
        }


# Reflection Tool - CONVERTED TO NODE-TO-NODE ROUTING

@traceable
def reflection_node(state: AgentState) -> AgentState:
    """Reflect on information and reasoning without external tools"""

    # Extract reflection request from the executor's decision
    last_message = state["messages"][-1]
    content = last_message.content

    # Parse the REFLECTION section
    thoughts = ""
    if "REFLECTION:" in content:
        reflection_part = content.split("REFLECTION:")[1].strip()
        thoughts = reflection_part.split("\n")[0].strip()
    elif "reflect" in content.lower():
        # Use the entire content as thoughts to reflect on
        thoughts = content
    elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Handle tool call format for backward compatibility
        tool_args = last_message.tool_calls[0].get('args', {})
        thoughts = tool_args.get('thoughts', '')

    if thoughts:
        # This is just an LLM call for pure reasoning
        reflection_prompt = f"""You are reflecting on the following thoughts and information:

    {thoughts}

    Based on this, provide your analysis, insights, or conclusions. Think step by step and be thorough in your reasoning."""

        try:
            reflection_response = llm.invoke(
                [SystemMessage(content=reflection_prompt)])

            result_message = f"🤔 Reflection: {reflection_response.content}"
            print(f"   💭 Reflecting on current information...")

            return {
                "messages": [AIMessage(content=result_message)]
            }
        except Exception as e:
            error_message = f"❌ Error during reflection: {str(e)}"
            print(f"   💭 {error_message}")
            return {
                "messages": [AIMessage(content=error_message)]
            }
    else:
        error_message = "❌ Could not extract reflection thoughts from executor decision"
        print(f"   💭 {error_message}")
        return {
            "messages": [AIMessage(content=error_message)]
        }


# Conclusion Tool - CONVERTED TO NODE-TO-NODE ROUTING

@traceable
def conclusion_node(state: AgentState) -> AgentState:
    """Provide final research conclusion and end the graph"""

    # Extract conclusion request from the executor's decision
    last_message = state["messages"][-1]
    content = last_message.content

    # Parse the CONCLUSION section
    findings = ""
    limitations = ""

    if "CONCLUSION:" in content:
        conclusion_part = content.split("CONCLUSION:")[1].strip()
        # Look for FINDINGS and LIMITATIONS sections
        if "FINDINGS:" in conclusion_part:
            findings_part = conclusion_part.split("FINDINGS:")[1]
            if "LIMITATIONS:" in findings_part:
                parts = findings_part.split("LIMITATIONS:")
                findings = parts[0].strip()
                limitations = parts[1].strip()
            else:
                findings = findings_part.strip()
        else:
            findings = conclusion_part
    elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Handle tool call format for backward compatibility
        tool_args = last_message.tool_calls[0].get('args', {})
        findings = tool_args.get('findings', '')
        limitations = tool_args.get('limitations', '')
    else:
        # Use all available context as findings
        findings = "Based on our research and analysis from the conversation"

    if findings:
        if limitations.strip():
            conclusion_prompt = f"""You are completing a research task. Provide a comprehensive final answer based on:

    FINDINGS:
    {findings}

    LIMITATIONS:
    {limitations}

    Create a helpful response that:
    1. Presents your key discoveries and analysis
    2. Provides clear answers to the user's questions
    3. Acknowledges any data gaps or limitations honestly
    4. Offers reasonable estimates where exact data wasn't available
    5. Summarizes the overall insights from your research

    Be thorough, professional, and provide maximum value to the user."""
        else:
            conclusion_prompt = f"""You are completing a research task. Provide a comprehensive final answer based on:

    FINDINGS:
    {findings}

    Create a helpful response that:
    1. Presents your key discoveries and analysis clearly
    2. Provides direct answers to the user's questions
    3. Summarizes calculations and comparisons you performed
    4. Highlights the most important insights from your research
    5. Ensures the user has a complete understanding of the topic

    Be thorough, professional, and deliver a high-quality research conclusion."""

        try:
            conclusion_response = llm.invoke(
                [SystemMessage(content=conclusion_prompt)])

            result_message = f"🎯 CONCLUSION: {conclusion_response.content}"
            print(f"   ✅ Research completed - delivering final conclusion")

            return {
                "messages": [AIMessage(content=result_message)]
            }
        except Exception as e:
            error_message = f"❌ Error creating conclusion: {str(e)}"
            print(f"   ✅ {error_message}")
            return {
                "messages": [AIMessage(content=error_message)]
            }
    else:
        error_message = "❌ Could not extract conclusion findings from executor decision"
        print(f"   ✅ {error_message}")
        return {
            "messages": [AIMessage(content=error_message)]
        }


# Memory Subagent Tool - REMOVED
# Now using direct orchestrator → memory_agent_reasoner routing instead of tool calls


# ============================================================================
# ORCHESTRATOR AGENT TOOLS & NODES
# ============================================================================

# Orchestrator tools - for main research agent
# orchestrator_analysis_tools removed - using direct routing to data_analysis_node
# orchestrator_search_tools removed - using direct routing to search_node
# orchestrator_reflection_tools removed - using direct routing to reflection_node
# orchestrator_conclusion_tools removed - using direct routing to conclusion_node
# No more memory tools - direct routing to memory subagent instead
# ALL TOOLS NOW USE NODE-TO-NODE ROUTING!
all_orchestrator_tools = []

# Create orchestrator tool nodes
# data_analysis_tool_node removed - using direct data_analysis_node
# search_tool_node removed - using direct search_node
# reflection_tool_node removed - using direct reflection_node
# conclusion_tool_node removed - using direct conclusion_node
# ALL TOOL NODES REMOVED - COMPLETE NODE-TO-NODE ROUTING!
# trigger_memory_subagent_tool_node removed - using direct routing now


# ============================================================================
# MEMORY OPERATIONS (TOOLS)
# ============================================================================

@tool
def memory_add_open_question(question: str) -> str:
    """Add a new research question to investigate.

    Args:
        question: The research question to add (e.g. "What is the population of NYC?")

    Returns:
        Confirmation message about the question being added
    """
    return f"Adding open question: {question}"


# Memory operations - tools for memory agent
memory_operations = [memory_add_open_question]

# Create custom memory operations tool node that can modify state


@traceable
def memory_operations_tool_node(state: AgentState):
    """Custom memory operations tool node that can access and modify research document"""

    # Get the last message with tool calls
    last_message = state["messages"][-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": [AIMessage(content="No memory operations found")]}

    # Process each tool call and modify the research document
    results = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "memory_add_open_question":
            question = tool_args.get("question", "").strip()

            if question:
                # Simply add to open_questions list in research_document
                open_questions = state["research_document"]["open_questions"]
                open_questions.append(question)

                result = f"✅ Added open question: '{question}'"
                print(f"   📝 {result}")
                results.append(result)

    # Return tool message with results
    summary = "; ".join(
        results) if results else "No memory operations performed"
    return {"messages": [ToolMessage(content=summary, tool_call_id=last_message.tool_calls[0]["id"])]}


# Initialize LLM for memory agent
memory_agent_llm = ChatOpenAI(model="gpt-4o", temperature=0.1,
                              api_key=os.getenv("OPENAI_API_KEY"))
memory_agent_llm_with_tools = memory_agent_llm.bind_tools(memory_operations)

# Initialize LLM for orchestrator
llm = ChatOpenAI(model="gpt-4o", temperature=0,
                 api_key=os.getenv("OPENAI_API_KEY"))
orchestrator_llm_with_tools = llm.bind_tools(all_orchestrator_tools)


# ============================================================================
# INITIALIZATION NODE
# ============================================================================

@traceable
def initialization_node(state: AgentState) -> AgentState:
    """Initialize the agent state with proper research document structure"""

    # Ensure research document is properly initialized
    if not state.get("research_document") or not state["research_document"]:
        print("📋 Initializing research document...")
        return {
            "research_document": create_empty_research_document()
        }

    print(
        f"📋 Research document already initialized with {len(state['research_document'].get('open_questions', []))} open questions")
    return {}  # No changes needed


# ============================================================================
# MEMORY AGENT NODES
# ============================================================================

@traceable
def memory_agent_reasoner_node(state: AgentState) -> AgentState:
    """Memory agent reasoner - decides what memory operations to perform"""

    # Build tool descriptions for memory operations dynamically
    tool_descriptions = []
    for tool in memory_operations:
        sig = inspect.signature(tool.func)
        tool_descriptions.append(f"- {tool.name}{sig}: {tool.description}")

    memory_tools_text = "\n".join(tool_descriptions)

    # Get full research document
    doc = state.get("research_document", {})

    reasoning_prompt = f"""
    You are the Memory Agent's reasoner. Your job is to analyze memory requests and decide what memory operations to perform.
    
    Current conversation: {[msg.content for msg in state['messages']]}
    Current research document: {doc}

    Available memory operations:
    {memory_tools_text}
    
    Your role:
    1. Analyze the request to understand what memory operations are needed
    2. Break down complex requests into specific tool calls
    3. You CAN recommend multiple tool calls in one response
    4. Be specific about each operation needed
    
    Decide what memory operations to perform. Be specific about each tool call needed.
    """

    reasoning_response = memory_agent_llm.invoke(
        [SystemMessage(content=reasoning_prompt)])
    print(f"🧠 Memory Agent Reasoning: {reasoning_response.content}")

    return {
        "messages": [AIMessage(content=reasoning_response.content)]
    }


@traceable
def memory_agent_executor_node(state: AgentState) -> AgentState:
    """Memory agent executor - decides which memory operation to execute"""

    executor_prompt = """You are the Memory Agent's executor. Your job is to decide which memory operation to execute based on the reasoner's analysis.

Look at the most recent reasoning message and decide what memory operation to perform.

Available operations:
- ADD_OPEN_QUESTION: Add a new research question to track

Respond with your decision in this format:
OPERATION: [operation_name]
DETAILS: [what you want to do]

For example:
OPERATION: ADD_OPEN_QUESTION  
DETAILS: What are the top 3 highest grossing video games?"""

    # Combine the executor prompt with the conversation
    messages_with_guidance = [SystemMessage(
        content=executor_prompt)] + state["messages"]
    action_response = memory_agent_llm.invoke(messages_with_guidance)

    print(f"🔧 Memory Agent Executor Decision: {action_response.content}")

    return {
        "messages": [action_response]
    }


# Memory operation router
def memory_operation_router(state: AgentState) -> str:
    """Route memory agent to specific memory operations based on executor decision"""
    last_message = state["messages"][-1]
    content = last_message.content.lower()

    if "add_open_question" in content:
        return "add_open_question_node"

    # Default fallback
    print("⚠️ Memory operation router: No clear operation found, returning to orchestrator")
    return "orchestrator_reasoner"


# ============================================================================
# MEMORY OPERATION NODES
# ============================================================================

@traceable
def add_open_question_node(state: AgentState) -> AgentState:
    """Add an open question to the research document"""

    # Extract the question from the executor's decision
    last_message = state["messages"][-1]
    content = last_message.content

    # Parse the DETAILS section
    question = ""
    if "DETAILS:" in content:
        details_part = content.split("DETAILS:")[1].strip()
        question = details_part.split("\n")[0].strip()

    if question:
        # Add to research document
        open_questions = state["research_document"]["open_questions"]
        open_questions.append(question)

        result_message = f"✅ Added open question: '{question}'"
        print(f"   📝 {result_message}")

        return {
            "messages": [AIMessage(content=result_message)]
        }
    else:
        error_message = "❌ Could not extract question from executor decision"
        print(f"   📝 {error_message}")
        return {
            "messages": [AIMessage(content=error_message)]
        }


# ============================================================================
# ORCHESTRATOR AGENT NODES
# ============================================================================

def orchestrator_reasoner_node(state: AgentState) -> AgentState:
    """Main research orchestrator reasoner - analyzes the situation and decides what to do next"""

    # Build tool descriptions for the orchestrator
    tool_descriptions = []
    for tool in all_orchestrator_tools:
        sig = inspect.signature(tool.func)
        tool_descriptions.append(f"- {tool.name}{sig}: {tool.description}")

    tools_text = "\n".join(tool_descriptions)

    # Get full research document
    doc = state.get("research_document", {})

    reasoning_prompt = f"""
    You are a general research agent designed as an educational demonstration of how agentic systems work.
    Your purpose is to show how agents decompose problems and use tools strategically.
    
    Current conversation: {[msg.content for msg in state['messages']]}
    Current research document: {doc}

    Available tools:
    {tools_text}
    
    Think through step by step:
    1. What is the user asking for?
    2. What information do I have so far?
    3. What am I still missing?
    4. What are the options for what I could do next?
    5. What's my decision on what I should do next?
    6. Do I need to use a tool for this, or am I done?
    
    DEMONSTRATION GUIDELINES:
    - This is an educational demo - show clear step-by-step problem decomposition
    - Break complex tasks into smaller, focused searches (search for one specific piece of information at a time)
    - ALWAYS use data analysis tools for any mathematical operations, calculations, or data comparisons
    - Don't try to do math in your head or ask other tools to do calculations
    - Make searches specific and targeted rather than broad
    - Use multiple tool calls to demonstrate the agentic workflow
    - The goal is for viewers to watch you flow through different states and see how agents think
    
    RESEARCH COMPLETION:
    - Use conclusion_tool to deliver your final research results - this is how all research tasks should end
    - When you have sufficient information to answer the user's question, it's time to conclude
    - Present comprehensive findings through the conclusion_tool
    - If some data wasn't available, that's normal - include what you found and note any limitations
    - Professional research includes both discoveries and honest acknowledgment of data gaps
    - Don't keep searching indefinitely - provide value with what you've gathered
    - If you want to give the search one more go, feel free to do so, but then conclude after that if you still cant find the information
    
    MEMORY MANAGEMENT WORKFLOW:
    - For NEW research tasks, consider first logging your research questions for tracking
    - Recommend the executor use "MEMORY_MANAGEMENT" routing to organize research questions
    - This helps demonstrate systematic problem decomposition and planning
    - Example: "I recommend logging questions: What are the top games? What's their revenue?"
    
    Work through the problem systematically. Just provide your reasoning about what to do next.
    """

    reasoning_response = llm.invoke([SystemMessage(content=reasoning_prompt)])
    reasoning_msg = AIMessage(content=reasoning_response.content)

    return {
        "messages": [reasoning_msg]
    }


def orchestrator_executor_node(state: AgentState) -> AgentState:
    """Main research orchestrator executor - executes the reasoner's decision"""

    executor_prompt = """You are the executor for a general research agent. Your job is to follow the reasoning and execute the recommended action.

Look at the most recent reasoning message and decide what to do:

1. If the reasoner recommends MEMORY MANAGEMENT (logging questions, organizing research), respond with:
   "ROUTING: MEMORY_MANAGEMENT - [describe what memory operations are needed]"

2. If the reasoner recommends DATA ANALYSIS (calculations, math), respond with:
   "ROUTING: DATA_ANALYSIS - CALCULATION: [mathematical expression]"

3. If the reasoner recommends SEARCH (web research, finding information), respond with:
   "ROUTING: SEARCH - SEARCH: [search query]"

4. If the reasoner recommends REFLECTION (internal thinking, analysis), respond with:
   "ROUTING: REFLECTION - REFLECTION: [thoughts to reflect on]"

5. If the reasoner recommends CONCLUSION (final answer, task completion), respond with:
   "ROUTING: CONCLUSION - CONCLUSION: [summary of findings]"

6. If the reasoner recommends using a TOOL, make the appropriate tool call.

7. Follow the reasoner's guidance precisely. Only do one action at a time.

Examples:
- "ROUTING: MEMORY_MANAGEMENT - Need to log research questions about video game revenue"
- "ROUTING: DATA_ANALYSIS - CALCULATION: 1200000000 + 800000000 + 600000000"
- "ROUTING: SEARCH - SEARCH: top grossing video games 2024"
- "ROUTING: REFLECTION - REFLECTION: I have revenue data for three games, need to analyze what this tells us"
- "ROUTING: CONCLUSION - CONCLUSION: Found total revenue of $2.6B across top 3 games with detailed breakdown"
- [No more tool calls needed - all routing is direct!]"""

    # Combine the executor prompt with the conversation
    messages_with_guidance = [SystemMessage(
        content=executor_prompt)] + state["messages"]
    action_response = orchestrator_llm_with_tools.invoke(
        messages_with_guidance)

    return {
        "messages": [action_response]
    }

# ============================================================================
# GRAPH SETUP & ROUTING
# ============================================================================


def orchestrator_router(state: AgentState) -> str:
    """Route orchestrator to different tools and subagents based on executor decisions"""
    last_message = state["messages"][-1]
    content = last_message.content.lower()

    # Check for direct routing decisions first
    if "routing: memory_management" in content or "memory_management" in content:
        return "memory_agent_reasoner"
    elif "routing: data_analysis" in content or "calculation:" in content:
        return "data_analysis_node"
    elif "routing: search" in content or "search:" in content:
        return "search_node"
    elif "routing: reflection" in content or "reflection:" in content:
        return "reflection_node"
    elif "routing: conclusion" in content or "conclusion:" in content:
        return "conclusion_node"

    # Legacy tool call handling (for backward compatibility)
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_name = last_message.tool_calls[0].get('name', '')
        # All tools converted to direct nodes
        if tool_name == 'data_analysis_tool':
            return "data_analysis_node"
        elif tool_name == 'search_tool':
            return "search_node"
        elif tool_name == 'reflection_tool':
            return "reflection_node"
        elif tool_name == 'conclusion_tool':
            return "conclusion_node"

    # If no clear routing decision, go back to reasoner
    # The only way to END is through conclusion_node
    return "orchestrator_reasoner"


# Build the graph
graph = StateGraph(AgentState)

# Add initialization node
graph.add_node("initialization", initialization_node)

# Add orchestrator nodes
graph.add_node("orchestrator_reasoner", orchestrator_reasoner_node)
graph.add_node("orchestrator_executor", orchestrator_executor_node)
graph.add_node("data_analysis_node", data_analysis_node)
graph.add_node("search_node", search_node)
graph.add_node("reflection_node", reflection_node)
graph.add_node("conclusion_node", conclusion_node)
# trigger_memory_subagent_tool node removed - using direct routing

# Add memory agent nodes
graph.add_node("memory_agent_reasoner", memory_agent_reasoner_node)
graph.add_node("memory_agent_executor", memory_agent_executor_node)

# Add memory operation nodes
graph.add_node("add_open_question_node", add_open_question_node)

# Add initialization edges
graph.add_edge(START, "initialization")
graph.add_edge("initialization", "orchestrator_reasoner")

# Add orchestrator edges
graph.add_edge("orchestrator_reasoner", "orchestrator_executor")
graph.add_conditional_edges("orchestrator_executor", orchestrator_router, {
    "memory_agent_reasoner": "memory_agent_reasoner",
    "data_analysis_node": "data_analysis_node",
    "search_node": "search_node",
    "reflection_node": "reflection_node",
    "conclusion_node": "conclusion_node",
    "orchestrator_reasoner": "orchestrator_reasoner"
})

# Memory subagent flow (direct orchestrator → memory routing)
graph.add_edge("memory_agent_reasoner", "memory_agent_executor")
graph.add_conditional_edges("memory_agent_executor", memory_operation_router, {
    "add_open_question_node": "add_open_question_node",
    "orchestrator_reasoner": "orchestrator_reasoner"
})
# Back to orchestrator from memory operations
graph.add_edge("add_open_question_node", "orchestrator_reasoner")

# All nodes go back to the orchestrator reasoner EXCEPT conclusion_node which ends
graph.add_edge("data_analysis_node", "orchestrator_reasoner")
graph.add_edge("search_node", "orchestrator_reasoner")
graph.add_edge("reflection_node", "orchestrator_reasoner")
graph.add_edge("conclusion_node", END)

# Compile the graph
app = graph.compile()

# Test function


def test_agent():
    """Test the orchestrator agent with population comparison"""
    test_query = "What is the population of New York City divided by the population of San Francisco?"

    print(f"🌍 Testing orchestrator agent with: {test_query}")
    print("-" * 50)

    # Let the initialization node handle research document setup
    initial_state = {
        "messages": [HumanMessage(content=test_query)]
    }

    result = app.invoke(initial_state)

    print("\n📊 Final result:")
    print(result["messages"][-1].content)

    return result


if __name__ == "__main__":
    test_agent()
