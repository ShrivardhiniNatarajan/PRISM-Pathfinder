from typing import Dict

def guard_decision(resource_name: str, scan_scores: Dict, threshold: float, current_phase_high_interference: bool) -> bool:
    """
    GUARD gating logic.
    - below threshold -> inactive
    - at/above threshold AND high-interference phase -> active
    - at/above threshold but not high-interference phase -> inactive
    """
    if resource_name not in scan_scores:
        return False
        
    score = scan_scores[resource_name]["score"]
    
    if score < threshold:
        return False
        
    if current_phase_high_interference:
        return True
        
    return False
