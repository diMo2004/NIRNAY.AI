from pydantic import BaseModel
from typing import List
from app.utils.schemas import SynthOutput
from app.config.settings import settings
from openai import OpenAI


client = OpenAI(
    api_key=settings.GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


class WebIntelState(BaseModel):
    """State for the web intelligence agent"""
    query: str = ""
    search_results: List[str] = []
    analysis: str = ""


def run_web_intel_agent(query: str) -> SynthOutput:
    """
    Web Intelligence Agent - Gathers and analyzes information from web sources.
    
    Args:
        query: The user query to search for
        
    Returns:
        SynthOutput with gathered information and analysis
    """
    try:
        # Create prompt for web intelligence gathering
        message = f"""You are a web intelligence expert. For the following user query, 
provide a comprehensive analysis of what information would be gathered from web sources.

Query: {query}

Provide:
1. Key information sources that would be relevant
2. Summary of findings
3. Recommendations for further research

Format your response as structured data."""
        
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        analysis = response.choices[0].message.content
        
        return SynthOutput(
            final_summary=analysis,
            recommendations="Further investigate the sources mentioned above for more detailed information.",
            tables=[],
            charts=[]
        )
        
    except Exception as e:
        print(f"Error in web intelligence agent: {str(e)}")
        return SynthOutput(
            final_summary=f"Error gathering web intelligence: {str(e)}",
            recommendations="Please try again.",
            tables=[],
            charts=[]
        )
