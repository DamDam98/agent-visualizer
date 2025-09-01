"""
Phase 1 Calculator Agent - Basic LangGraph agent with calculator tool
Goal: Get to LangGraph Studio visualization ASAP
testcase: 
********** What is 2847 * 193^2 + 4521^2? **********
"""

import inspect
import os
from typing import Annotated, List

from dotenv import load_dotenv
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, create_react_agent
from langsmith import traceable
from typing_extensions import TypedDict

# Load environment variables
load_dotenv()

# Define our agent's state


class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage |
                             ToolMessage], add_messages]


@tool
def addition_tool(a: float, b: float) -> str:
    """
    Add two numbers together.
    """
    result = a + b
    return f"The result of {a} + {b} is {result}"


@tool
def subtraction_tool(a: float, b: float) -> str:
    """
    Subtract two numbers.
    """
    result = a - b
    return f"The result of {a} - {b} is {result}"


@tool
def multiplication_tool(a: float, b: float) -> str:
    """
    Multiply two numbers together.
    """
    result = a * b
    return f"The result of {a} * {b} is {result}"


@tool
def division_tool(a: float, b: float) -> str:
    """
    Divide two numbers.
    """
    result = a / b
    return f"The result of {a} / {b} is {result}"


@tool
def exponentiation_tool(a: float, b: float) -> str:
    """
    Exponentiate two numbers.
    """
    result = a ** b
    return f"The result of {a} ** {b} is {result}"


# All tools list
all_tools = [addition_tool, subtraction_tool,
             multiplication_tool, division_tool, exponentiation_tool]

# Create individual tool nodes
addition_node = ToolNode([addition_tool])
subtraction_node = ToolNode([subtraction_tool])
multiplication_node = ToolNode([multiplication_tool])
division_node = ToolNode([division_tool])
exponentiation_node = ToolNode([exponentiation_tool])


llm = ChatOpenAI(model="gpt-4o", temperature=0,
                 api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(all_tools)


def reasoner_node(state: AgentState) -> AgentState:
    """Pure reasoning node - analyzes situation and decides what to do next"""

    # Build tool descriptions for the reasoner
    tool_descriptions = []
    for tool in all_tools:
        # Get the actual function signature
        sig = inspect.signature(tool.func)
        tool_descriptions.append(f"- {tool.name}{sig}: {tool.description}")

    tools_text = "\n".join(tool_descriptions)

    # Generate reasoning about what to do next
    reasoning_prompt = f"""
    Look at this conversation and think step by step:
    
    Current conversation: {[msg.content for msg in state['messages']]}

    Available tools:
    {tools_text}
    
    What should I do next? Think through:
    1. What is the user asking?
    2. What steps have I already taken?
    3. What new information is now available?
    4. What do I need to calculate next?
    5. Should I use a tool? If so, which one?
    
    Just provide your reasoning, don't take action yet.

    One note: this is for a demonstration of simple reasoning. So please only do one tool call at a time. Let's take this one step at a time.
    """

    reasoning_response = llm.invoke([SystemMessage(content=reasoning_prompt)])
    reasoning_msg = AIMessage(
        content=reasoning_response.content)

    return {
        "messages": [reasoning_msg]
    }


def executor_node(state: AgentState) -> AgentState:
    """Executor node - takes action based on the reasoner's analysis"""

    # Add a system message to guide the executor to follow the reasoner's advice
    executor_prompt = """You are the executor part of a mathematician agent. Your job is to follow the reasoning and advice from the reasoner.

Look at the most recent reasoning message and execute the recommended action. If the reasoner suggested using a specific tool, use that tool with the suggested arguments. If the reasoner said you have enough information to provide a final answer, then provide that answer.

If the reasoner suggests using a single tool, but you think you can use multiple tools at the same time, do not do it. Just listen to the reasoner and execute the recommended action. The reasoner has a master plan. Please let the reasoner take the lead. Thank you.

Follow the reasoner's guidance closely."""

    # Combine the executor prompt with the conversation
    messages_with_guidance = [
        SystemMessage(content=executor_prompt)] + state["messages"]
    action_response = llm_with_tools.invoke(messages_with_guidance)

    return {
        "messages": [action_response],
    }


# Define routing logic - route to specific tool nodes
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_name = last_message.tool_calls[0].get('name', '')
        # Route directly to the specific tool node
        if tool_name == 'addition_tool':
            return "addition_tool"
        elif tool_name == 'subtraction_tool':
            return "subtraction_tool"
        elif tool_name == 'multiplication_tool':
            return "multiplication_tool"
        elif tool_name == 'division_tool':
            return "division_tool"
        elif tool_name == 'exponentiation_tool':
            return "exponentiation_tool"
    return END


# Build the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("mathematician_agent_reasoner", reasoner_node)
graph.add_node("mathematician_agent_executor", executor_node)
graph.add_node("addition_tool", addition_node)
graph.add_node("subtraction_tool", subtraction_node)
graph.add_node("multiplication_tool", multiplication_node)
graph.add_node("division_tool", division_node)
graph.add_node("exponentiation_tool", exponentiation_node)

# Add edges
graph.add_edge(START, "mathematician_agent_reasoner")
graph.add_edge("mathematician_agent_reasoner", "mathematician_agent_executor")
graph.add_conditional_edges("mathematician_agent_executor", should_continue)

# All tool nodes go back to the reasoner (not executor)
graph.add_edge("addition_tool", "mathematician_agent_reasoner")
graph.add_edge("subtraction_tool", "mathematician_agent_reasoner")
graph.add_edge("multiplication_tool", "mathematician_agent_reasoner")
graph.add_edge("division_tool", "mathematician_agent_reasoner")
graph.add_edge("exponentiation_tool", "mathematician_agent_reasoner")

# Compile the graph
app = graph.compile()

# Test function


def test_agent():
    """Test the agent with a complex calculation"""
    test_query = "What is 2847 * 193^2 + 4521 / 7?"

    print(f"🧮 Testing calculator agent with: {test_query}")
    print("-" * 50)

    result = app.invoke({
        "messages": [HumanMessage(content=test_query)]
    })

    print("\n📊 Final result:")
    print(result["messages"][-1].content)

    return result


if __name__ == "__main__":
    test_agent()
