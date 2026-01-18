from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import Annotated
import json
import operator
from app.utils.schemas import RouterOutput, SynthOutput
from app.utils.prompts import MASTER_AGENT_ROUTER_PROMPT, SYNTH_PROMPT
from app.agents import (report_generator_agent, web_intel_agent)
from app.config.settings import settings
from openai import OpenAI


client = OpenAI(
    api_key=settings.GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


class MasterState(BaseModel):
    """State for the master agent workflow"""
    query: str = ""
    selected_agents: list = []
    routing_reason: str = ""
    results: dict = {}
    final_output: SynthOutput | None = None


def router_node(state: MasterState) -> dict:
    """
    Routes the query to appropriate agents based on content analysis.
    Returns selected agents and reasoning.
    """
    message = f"""You are an intelligent router agent. Analyze the following user query and determine which agents should handle it.

Available agents:
1. Web Intelligence Agent - Gathers and analyzes information from web sources
2. Report Generator Agent - Creates comprehensive reports based on data

User Query: {state.query}

{MASTER_AGENT_ROUTER_PROMPT}

Respond in JSON format with:
{{"selected_agents": ["agent_name1", "agent_name2"], "reason": "explanation"}}
"""
    
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    
    try:
        content = response.choices[0].message.content
        # Extract JSON from response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        result = json.loads(json_str)
        
        return {
            "selected_agents": result.get("selected_agents", []),
            "routing_reason": result.get("reason", "")
        }
    except (json.JSONDecodeError, AttributeError, ValueError):
        # Fallback if parsing fails
        return {
            "selected_agents": ["Web Intelligence Agent", "Report Generator Agent"],
            "routing_reason": "Default routing due to parsing error"
        }


def web_intel_node(state: MasterState) -> dict:
    """
    Calls the web intelligence agent to gather web-based information.
    """
    if "Web Intelligence Agent" not in state.selected_agents:
        return {"results": state.results}
    
    # Call web intelligence agent
    web_result = web_intel_agent.run_web_intel_agent(state.query)
    
    results = state.results.copy()
    results["web_intel"] = web_result
    
    return {"results": results}


def report_generator_node(state: MasterState) -> dict:
    """
    Calls the report generator agent to create a comprehensive report.
    """
    if "Report Generator Agent" not in state.selected_agents:
        return {"results": state.results}
    
    # Prepare context from previous results
    context = json.dumps(state.results) if state.results else "No previous data"
    
    # Call report generator agent
    report_result = report_generator_agent.run_report_generator_agent(
        state.query, 
        context
    )
    
    results = state.results.copy()
    results["report"] = report_result
    
    return {"results": results}


def synthesizer_node(state: MasterState) -> dict:
    """
    Synthesizes results from all agents into final output.
    """
    results_context = json.dumps(state.results) if state.results else "No data available"
    
    message = f"""You are a synthesis agent. Combine the following agent outputs into a comprehensive final response.

User Query: {state.query}

Agent Results:
{results_context}

{SYNTH_PROMPT}

Create a final summary with recommendations and any relevant tables or charts in JSON format.
"""
    
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    
    try:
        content = response.choices[0].message.content
        # Try to extract JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            final_output = SynthOutput(
                final_summary=result.get("final_summary", content),
                recommendations=result.get("recommendations", ""),
                tables=result.get("tables", []),
                charts=result.get("charts", [])
            )
        else:
            final_output = SynthOutput(
                final_summary=content,
                recommendations="",
                tables=[],
                charts=[]
            )
        
        return {"final_output": final_output}
    except (json.JSONDecodeError, ValueError):
        return {
            "final_output": SynthOutput(
                final_summary=response.choices[0].message.content,
                recommendations="",
                tables=[],
                charts=[]
            )
        }


# Build the graph
graph = StateGraph(MasterState)

# Add nodes
graph.add_node("router", router_node)
graph.add_node("web_intel", web_intel_node)
graph.add_node("report_generator", report_generator_node)
graph.add_node("synthesizer", synthesizer_node)

# Add edges
graph.set_entry_point("router")
graph.add_edge("router", "web_intel")
graph.add_edge("web_intel", "report_generator")
graph.add_edge("report_generator", "synthesizer")
graph.add_edge("synthesizer", END)

# Compile the graph
master_chain = graph.compile()


# PUBLIC ENTRY FUNCTION
async def run_master_agent(query: str):
    """
    Main entry point for the master agent.
    
    Args:
        query: The user query to process
        
    Returns:
        Final SynthOutput with results
    """
    state = MasterState(query=query)
    
    try:
        # Run the workflow
        final_state = master_chain.invoke(state)
        return final_state.final_output
    except Exception as e:
        print(f"Error in master agent: {str(e)}")
        return SynthOutput(
            final_summary=f"Error processing query: {str(e)}",
            recommendations="Please try again with a different query.",
            tables=[],
            charts=[]
        )

