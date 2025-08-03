from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import EmailCheckRequest, EmailCheckResponse
from services import SuppressionService, OllamaService
from config import config

app = FastAPI(
    title="Suppressed Email Checker API",
    description="API to check if an email address is suppressed and get human-readable explanations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
suppression_service = SuppressionService()
ollama_service = OllamaService()

@app.get("/")
async def root():
    return {"message": "Suppressed Email Checker API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "suppressed-email-checker"}

@app.post("/check-email", response_model=EmailCheckResponse)
async def check_email_suppression(request: EmailCheckRequest):
    """
    Check if an email address is suppressed
    
    Returns:
    - is_suppressed: Boolean indicating if email is suppressed
    - reason: Reason for suppression (if suppressed)
    - last_update_time: When the suppression was last updated (if suppressed)
    - human_readable_explanation: AI-generated human-readable explanation (if suppressed)
    """
    try:
        email = request.email.lower()
        
        # Check if email is suppressed
        suppression_info = suppression_service.check_email_suppression(email)
        
        if not suppression_info:
            return EmailCheckResponse(
                email=email,
                is_suppressed=False
            )
        
        # Format datetime for human readability
        formatted_time = suppression_service._format_datetime_human_readable(
            suppression_info.last_update_time
        )
        
        # Get reason explanation
        reason_explanation = suppression_service._get_reason_explanation(
            suppression_info.reason
        )
        
        # Generate human-readable explanation using Ollama
        human_explanation = ollama_service.generate_human_explanation(
            email=email,
            reason=suppression_info.reason,
            last_update_time=suppression_info.last_update_time,
            formatted_time=formatted_time,
            reason_explanation=reason_explanation
        )
        
        return EmailCheckResponse(
            email=email,
            is_suppressed=True,
            reason=suppression_info.reason,
            last_update_time=suppression_info.last_update_time,
            human_readable_explanation=human_explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
