def classify_risk_severity(text: str, is_emergency: bool) -> str:
    """
    Classifies the symptom risk into Low, Medium, or High categories.
    In a full production scenario, this might also use a separate LLM call.
    For Phase 8, we base 'High' strictly on keyword guardrails,
    and fallback to 'Medium' or 'Low' based on heuristic length/complexity.
    """
    if is_emergency:
        return "High"
    
    # Simple heuristic: If the user is explaining multiple complex symptoms, rate Medium for caution.
    # Otherwise rate Low.
    if len(text.split()) > 30:
         return "Medium"
         
    return "Low"
