from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from datetime import datetime
from app.agents.master_agent import run_master_agent

app = FastAPI(
    title="NIRNAY.AI Backend API",
    description="Backend API for NIRNAY.AI Analysis System",
    version="1.0.0"
)

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results (temporary solution)
analysis_store = {}
analysis_history = []

# Request models
class AnalysisRequest(BaseModel):
    query: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str

class ReportResponse(BaseModel):
    analysis_id: str
    query: str
    result: str
    timestamp: str

class HistoryItem(BaseModel):
    analysis_id: str
    query: str
    timestamp: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "NIRNAY.AI Backend API is running", "status": "active"}

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Submit a problem for analysis
    
    Returns:
        - analysis_id: Unique ID for tracking the analysis
        - status: Status of the analysis request
        - message: Confirmation message
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    try:
        # Run the master agent with the query
        result = await run_master_agent(request.query)
        
        # Store the result
        analysis_data = {
            "analysis_id": analysis_id,
            "query": request.query,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        analysis_store[analysis_id] = analysis_data
        analysis_history.append({
            "analysis_id": analysis_id,
            "query": request.query,
            "timestamp": datetime.now().isoformat()
        })
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message="Analysis completed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/report/{analysis_id}", response_model=ReportResponse)
async def get_report(analysis_id: str):
    """
    Retrieve the report for a specific analysis
    
    Args:
        analysis_id: The unique ID of the analysis
    
    Returns:
        - analysis_id: The analysis ID
        - query: The original query
        - result: The analysis result
        - timestamp: When the analysis was performed
    """
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    return ReportResponse(
        analysis_id=analysis["analysis_id"],
        query=analysis["query"],
        result=analysis["result"],
        timestamp=analysis["timestamp"]
    )

@app.get("/history", response_model=list[HistoryItem])
async def get_history():
    """
    Get the history of all analyses performed
    
    Returns:
        List of analysis history items with ID, query, and timestamp
    """
    return analysis_history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
