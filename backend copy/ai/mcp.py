import httpx
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

# Simulated MCP endpoints. In a real environment, this might be a dedicated 
# Model Context Protocol server exposing endpoints for WHO/CDC fact-checking.
MCP_SERVICE_URL = settings.mcp_service_endpoint

async def fetch_authoritative_guidelines(symptom_keywords: str) -> Optional[str]:
    """
    Simulates an MCP retrieval tool that fetches official public health guidance
    (e.g., from WHO or CDC) based on detected symptom keywords.
    """
    # For Phase 9, since we don't have a live MCP server hosted externally,
    # we return a static, verified health fact block based on keyword matching
    # to ground the LLM and reduce hallucinations.
    
    symptoms = symptom_keywords.lower()
    
    if "fever" in symptoms or "cough" in symptoms:
        return (
            "[MCP FACT: According to general CDC guidance, mild fever and cough can often be "
            "managed at home with rest and fluids. However, if breathing becomes difficult "
            "or fever exceeds 103°F (39.4°C), professional medical evaluation is required.]"
        )
    
    if "rash" in symptoms:
         return (
             "[MCP FACT: Skin rashes have many causes ranging from allergic reactions to infections. "
             "The WHO advises that any rash accompanied by difficulty breathing or swelling of the face/throat "
             "is a medical emergency.]"
         )
         
    if "headache" in symptoms:
         return (
             "[MCP FACT: While most headaches are benign, public health guidelines stress that a "
             "'thunderclap' headache (sudden and severe) or a headache accompanied by fever, stiff neck, "
             "or neurological symptoms requires immediate emergency care.]"
         )
         
    # Default generic grounding fact
    return (
        "[MCP FACT: Always prioritize official guidance from your local health authority or a "
        "registered physician. Symptom checkers only provide awareness, not definitive medical answers.]"
    )

def inject_mcp_context(original_prompt: str, mcp_facts: Optional[str]) -> str:
    """
    Appends the retrieved MCP facts into the LLM prompt to ground its response.
    """
    if not mcp_facts:
        return original_prompt
        
    return f"{original_prompt}\n\n--- AUTHORITATIVE CONTEXT ---\n{mcp_facts}\n---------------------------\n"
