# Phase 1: Simple Agent Demo

## Goal

Create a single LangGraph agent that demonstrates basic tool orchestration through population comparison and division.

## Problem Statement

"Find the population of New York City, find the population of San Francisco, then divide NYC by SF."

## In Scope

- Single agent with two tools (Perplexity search + calculator)
- LangGraph Studio visualization working
- Sequential tool execution (search → search → calculate)
- Clean demo flow for live audience

## Out of Scope

- Multi-agent architecture (that's Phase 2)
- Error handling beyond basic cases
- Complex reasoning or planning
- Real-time interaction during demo

## Core Tasks

1. Create basic LangGraph agent structure
2. Build Perplexity search tool
3. Build calculator tool
4. Test agent execution flow
5. Launch LangGraph Studio visualization
6. Validate demo timing and clarity

## Success Criteria

- Agent completes the population comparison problem
- Visualization clearly shows tool calls and reasoning
- Demo runs reliably without technical issues
- Audience can follow the step-by-step execution

## Key Files

- `agent.py` - Main agent implementation
- `.env` - API keys (OpenAI, Perplexity)
- `requirements.txt` - Dependencies

## Execution Steps

### Step 1: Minimal Agent + Immediate Visualization

- Create simplest possible LangGraph agent (maybe just returns "Hello World")
- Launch LangGraph Studio
- **Checkpoint**: Can we see the agent running in the visualization?

### Step 2: Add Mock Tools

- Add two mock tools (fake search, fake calculator)
- Agent calls both tools in sequence
- **Checkpoint**: Visualization shows tool calling flow

### Step 3: Real Tool Integration

- Replace mock search with actual Perplexity API
- Replace mock calculator with real math
- **Checkpoint**: End-to-end demo works with real data

### Step 4: Demo Polish

- Test timing and flow
- Ensure reliability for live demo

---

## Step 1 Deep Dive: Calculator Agent v0

**Goal**: Get to visualization ASAP with a working agent

**Approach**:

- Build calculator/mathematician agent with OpenAI integration
- Use built-in calculator tool (no external APIs to debug)
- Real LLM reasoning + tool usage for visualization
- Test with complex calculation like "What's 2847 \* 193 + 4521 / 7?"

**Why This Works**:

- Shows actual agent reasoning (not just "Hello World")
- Demonstrates tool calling flow in visualization
- No external dependencies to fail during demo
- Clear, understandable problem for audience

## **Implementation**: Create `agent.py` with LangGraph + OpenAI + calculator tool

---

add here
