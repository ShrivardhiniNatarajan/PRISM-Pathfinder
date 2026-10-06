import pytest
from task_spec.pathfinder_spec import default_pathfinder_spec, SharedResource
from scan.scoring import scan_score

def test_scan_score_comparative():
    # Build a spec with N=3 interferers
    spec = default_pathfinder_spec(3)
    
    # We already have info_bus_mutex in spec.resources (held by ASI_MET, crit=30, inh=False)
    # ASI_MET has priority LOW (1). Interferers are MEDIUM (2). bc_sched is HIGH (3).
    # So info_bus_mutex should have priority_span = 2, interferer_count = 3.
    info_bus = spec.resources[0]
    
    # Add a synthetic resource
    # Held by a MEDIUM priority task, meaning priority_span = 1, interferers = 0.
    # Inheritance enabled, and shorter critical section.
    synth_mutex = SharedResource(
        name="synth_mutex",
        held_by="comm_task_1",
        critical_section_ms=10.0,
        inheritance_enabled=True
    )
    spec.resources.append(synth_mutex)
    
    info_score_data = scan_score(info_bus, spec)
    synth_score_data = scan_score(synth_mutex, spec)
    
    info_score = info_score_data["score"]
    synth_score = synth_score_data["score"]
    
    # Assert info_bus_mutex scores strictly higher
    assert info_score > synth_score, f"Expected info_bus ({info_score}) > synth_mutex ({synth_score})"
    
    # Verify raw components for auditability (and correctness)
    info_raw = info_score_data["raw"]
    synth_raw = synth_score_data["raw"]
    
    assert info_raw["priority_span"] == 2.0
    assert info_raw["interferer_count"] == 3.0
    assert info_raw["critical_section_duration"] == 30.0
    assert info_raw["inheritance_penalty"] == 1.0
    
    assert synth_raw["priority_span"] == 1.0
    assert synth_raw["interferer_count"] == 0.0
    assert synth_raw["critical_section_duration"] == 10.0
    assert synth_raw["inheritance_penalty"] == 0.0
