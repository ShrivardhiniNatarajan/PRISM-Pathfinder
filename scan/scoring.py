from typing import Dict, Tuple
from task_spec.pathfinder_spec import SystemSpec, SharedResource

def scan_score(resource: SharedResource, spec: SystemSpec, weights: Tuple[float, float, float, float] = (0.3, 0.3, 0.2, 0.2)) -> Dict:
    """
    Computes SCAN static risk scoring for a specific resource, 
    normalizing against all resources in the spec.
    """
    w1, w2, w3, w4 = weights
    
    # Calculate raw components for all resources to allow min-max normalization
    raw_components = {}
    max_prio_system = max((t.priority for t in spec.tasks), default=0)
    
    for res in spec.resources:
        holder = next((t for t in spec.tasks if t.name == res.held_by), None)
        holder_prio = holder.priority if holder else max_prio_system
        
        priority_span = max_prio_system - holder_prio
        interferer_count = sum(1 for t in spec.tasks if holder_prio < t.priority < max_prio_system)
        
        raw_components[res.name] = {
            "priority_span": float(priority_span),
            "interferer_count": float(interferer_count),
            "critical_section_duration": float(res.critical_section_ms),
            "inheritance_penalty": 1.0 if not res.inheritance_enabled else 0.0
        }
        
    if not spec.resources:
        return {}
        
    spans = [raw_components[r.name]["priority_span"] for r in spec.resources]
    interferers = [raw_components[r.name]["interferer_count"] for r in spec.resources]
    durations = [raw_components[r.name]["critical_section_duration"] for r in spec.resources]
    penalties = [raw_components[r.name]["inheritance_penalty"] for r in spec.resources]
    
    def normalize(val, values):
        min_v = min(values)
        max_v = max(values)
        if max_v == min_v:
            return 1.0
        return (val - min_v) / (max_v - min_v)
        
    target_raw = raw_components[resource.name]
    
    norm_span = normalize(target_raw["priority_span"], spans)
    norm_interf = normalize(target_raw["interferer_count"], interferers)
    norm_dur = normalize(target_raw["critical_section_duration"], durations)
    norm_pen = normalize(target_raw["inheritance_penalty"], penalties)
    
    score = (
        w1 * norm_span +
        w2 * norm_interf +
        w3 * norm_dur +
        w4 * norm_pen
    )
    
    return {
        "score": score,
        "raw": target_raw
    }
