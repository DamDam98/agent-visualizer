# Agent Visualizer for Maker Faire Orlando

## Vision & Goal

Create an educational demo for Maker Faire that "peels back the curtain" on what AI agents actually are. Combat the misconception that agents are magical black boxes you "train" - instead show that they're intelligent orchestration systems that break down problems and use tools strategically.

**Target Audience**: Kids and families at Maker Faire - needs to be accessible, visual, and engaging.

## Core Message

Agents aren't magic - they're just smart problem decomposition + tool usage + orchestration.

## Three-Stage Demo Structure

### Stage 1: Single Agent (DECIDED)

- **Problem**: "Get weather in San Francisco and divide by weather in Seattle"
- **Architecture**: One agent with two tools (weather API + calculator)
- **Purpose**: Show basic tool calling and sequencing
- **Flow**: Get SF weather → Get Seattle weather → Divide
- **Key Learning**: Even simple problems require multiple tools and reasoning

### Stage 2: Specialized Sub-Agents (DECIDED)

- **Problem**: Same exact weather/calculator problem
- **Architecture**: WeatherAgent + CalculatorAgent
- **Purpose**: Show how you can decompose even simple problems into specialized agents
- **Key Learning**: Inter-agent communication and specialization

### Stage 3: Complex Multi-Level System (PENCILED IN)

- **Problem**: TBD - needs to be kid-friendly and engaging
- **Ideas Discussed**: Santa's route planning, multi-layered marketing agents
- **Architecture**: Multiple layers of sub-agents with hierarchical decomposition
- **Purpose**: Show how agents scale to complex, real-world problems
- **Key Learning**: Sophisticated orchestration and state management

## Technology Stack (DECIDED)

### Primary Tools

- **LangGraph**: Framework for building the actual agents
- **LangGraph Studio**: Visual IDE for debugging and demonstration
- **LangSmith Developer Plan**: Free tier with 5k traces/month

### Key Benefits

- ✅ Completely free during beta
- ✅ Out-of-the-box visualization
- ✅ Step-by-step debugging mode
- ✅ Real-time agent state inspection
- ✅ Professional-quality visual interface

### Setup Time

~30 minutes total:

- Sign up for free LangSmith account
- Install LangGraph (`pip install langgraph`)
- Build weather/calculator agents (2 Python files)
- Launch with `langgraph dev`

## Demo Experience Design

### Visualization Features

- Live graph showing active nodes
- State panels showing gathered information
- Tool call logs (weather API, calculator operations)
- "Debugger-like" step-through capability
- Slow, controlled pacing for audience comprehension

### Interactive Elements

- Pause/play execution
- Step-through mode
- State modification capabilities
- Real-time agent reasoning display

## What Makes This Powerful

- Shows the evolution from simple → complex agent architectures
- Uses the same problem across Stage 1 & 2 to highlight the difference
- Demonstrates that agents are just intelligent orchestration, not magic
- Kid-friendly but technically accurate
- Professional tools that developers actually use

## Next Steps for Development

1. Set up LangGraph Studio environment
2. Build Stage 1 weather/calculator agent
3. Refactor into Stage 2 specialized sub-agents
4. Test visualization and pacing
5. Decide on Stage 3 use case and implement
6. Practice demo presentation flow

## Success Metrics

- Kids can explain "what an agent does" after seeing the demo
- Adults understand that agents = problem decomposition + tools
- Audience sees the clear progression from simple → sophisticated systems
- Demo runs reliably without technical hiccups
