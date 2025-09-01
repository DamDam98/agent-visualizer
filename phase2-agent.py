"""
Phase 2 Enhanced Agent - General Research Agent
Goal: Multi-capability research agent with search, calculator, and reflection tools

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


class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage |
                             ToolMessage], add_messages]

# Data Analysis Tool


@tool
def data_analysis_tool(expression: str) -> str:
    """
    Perform mathematical calculations and data analysis operations.
    Supports basic arithmetic: addition (+), subtraction (-), multiplication (*), 
    division (/), exponentiation (**), parentheses for grouping.

    Examples:
    - "1200000000 + 800000000 + 600000000" 
    - "10000000 / 500000"
    - "1000 * 150.50 * 1.02"
    - "2 ** 10"
    """
    try:
        # Clean the expression - remove any non-mathematical characters except basic operators
        import re

        # Allow numbers, operators, parentheses, decimal points, and spaces
        cleaned = re.sub(r'[^0-9+\-*/(). ]', '', expression)

        # Evaluate the mathematical expression safely
        result = eval(cleaned)

        return f"Calculation: {expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}. Please check the mathematical expression format."

# Search Tool


@tool
def search_tool(query: str) -> str:
    """
    Search the web for information on any topic using Perplexity API.
    Args:
        query: The search query (e.g., "population of New York City", "GDP of Japan", "weather in Paris")
    """
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

        return f"Search results for '{query}': {search_info}"

    except Exception as e:
        return f"Error searching for '{query}': {str(e)}. Please check your PERPLEXITY_API_KEY in .env file."


# Reflection Tool


@tool
def reflection_tool(thoughts: str) -> str:
    """
    Reflect on information and reasoning without external tools. Use this to think through problems, 
    analyze information you already have, or plan your next steps.
    Args:
        thoughts: Your current thoughts or reasoning that you want to reflect on
    """
    # This is just an LLM call for pure reasoning
    reflection_prompt = f"""You are reflecting on the following thoughts and information:

{thoughts}

Based on this, provide your analysis, insights, or conclusions. Think step by step and be thorough in your reasoning."""

    try:
        reflection_response = llm.invoke(
            [SystemMessage(content=reflection_prompt)])
        return f"Reflection: {reflection_response.content}"
    except Exception as e:
        return f"Error during reflection: {str(e)}"


# Conclusion Tool


@tool
def conclusion_tool(findings: str, limitations: str = "") -> str:
    """
    Provide your final research conclusion with comprehensive findings.
    This is the standard way to complete any research task - use this when you're ready to deliver your final answer.
    Args:
        findings: What you discovered and analyzed during your research
        limitations: Any gaps in data or information you couldn't find (optional - leave empty if no significant limitations)
    """
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
        return f"CONCLUSION: {conclusion_response.content}"
    except Exception as e:
        return f"Error creating conclusion: {str(e)}"


# All tools
analysis_tools = [data_analysis_tool]
search_tools = [search_tool]
reflection_tools = [reflection_tool]
conclusion_tools = [conclusion_tool]
all_tools = analysis_tools + search_tools + reflection_tools + conclusion_tools

# Create consolidated tool nodes
data_analysis_tool_node = ToolNode(analysis_tools)
search_tool_node = ToolNode(search_tools)
reflection_tool_node = ToolNode(reflection_tools)
conclusion_tool_node = ToolNode(conclusion_tools)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0,
                 api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(all_tools)


def coordinator_reasoner_node(state: AgentState) -> AgentState:
    """Research agent reasoner - analyzes the situation and decides what to do next"""

    # Build tool descriptions for the coordinator
    tool_descriptions = []
    for tool in all_tools:
        sig = inspect.signature(tool.func)
        tool_descriptions.append(f"- {tool.name}{sig}: {tool.description}")

    tools_text = "\n".join(tool_descriptions)

    reasoning_prompt = f"""
    You are a general research agent designed as an educational demonstration of how agentic systems work.
    Your purpose is to show how agents decompose problems and use tools strategically.
    
    Current conversation: {[msg.content for msg in state['messages']]}

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
    
    Work through the problem systematically. Just provide your reasoning about what to do next.
    """

    reasoning_response = llm.invoke([SystemMessage(content=reasoning_prompt)])
    reasoning_msg = AIMessage(content=reasoning_response.content)

    return {
        "messages": [reasoning_msg]
    }


def coordinator_executor_node(state: AgentState) -> AgentState:
    """Research agent executor - executes the reasoner's decision"""

    executor_prompt = """You are the executor for a general research agent. Your job is to follow the reasoning and execute the recommended action.

Look at the most recent reasoning message and execute the recommended action with the tools you have available.

Follow the reasoner's guidance precisely. Only do one action at a time. Do not use a tool that is not recommended by the reasoner. The reasoner should only be recommending one tool at a time. if it recommends using multiple tools, only use the first tool it recommends. Thank you."""

    # Combine the executor prompt with the conversation
    messages_with_guidance = [SystemMessage(
        content=executor_prompt)] + state["messages"]
    action_response = llm_with_tools.invoke(messages_with_guidance)

    return {
        "messages": [action_response]
    }

# Define routing logic


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_name = last_message.tool_calls[0].get('name', '')
        # Route to consolidated tool nodes
        if tool_name == 'data_analysis_tool':
            return "data_analysis_tool"
        elif tool_name == 'search_tool':
            return "search_tool"
        elif tool_name == 'reflection_tool':
            return "reflection_tool"
        elif tool_name == 'conclusion_tool':
            return "conclusion_tool"

    # If no tool calls, force the agent to go back to reasoner
    # The only way to END is through conclusion_tool
    return "research_agent_reasoner"


# Build the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("research_agent_reasoner", coordinator_reasoner_node)
graph.add_node("research_agent_executor", coordinator_executor_node)
graph.add_node("data_analysis_tool", data_analysis_tool_node)
graph.add_node("search_tool", search_tool_node)
graph.add_node("reflection_tool", reflection_tool_node)
graph.add_node("conclusion_tool", conclusion_tool_node)

# Add edges
graph.add_edge(START, "research_agent_reasoner")
graph.add_edge("research_agent_reasoner", "research_agent_executor")
graph.add_conditional_edges("research_agent_executor", should_continue)

# All tool nodes go back to the reasoner EXCEPT conclusion_tool which ends
graph.add_edge("data_analysis_tool", "research_agent_reasoner")
graph.add_edge("search_tool", "research_agent_reasoner")
graph.add_edge("reflection_tool", "research_agent_reasoner")
graph.add_edge("conclusion_tool", END)

# Compile the graph
app = graph.compile()

# Test function


def test_agent():
    """Test the multi-agent system with population comparison"""
    test_query = "What is the population of New York City divided by the population of San Francisco?"

    print(f"🌍 Testing multi-agent system with: {test_query}")
    print("-" * 50)

    result = app.invoke({
        "messages": [HumanMessage(content=test_query)]
    })

    print("\n📊 Final result:")
    print(result["messages"][-1].content)

    return result


if __name__ == "__main__":
    test_agent()
