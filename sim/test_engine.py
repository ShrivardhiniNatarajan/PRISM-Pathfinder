import pytest
from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.conditions import calculate_pip_bound, calculate_pcp_bound, Simulator

def test_pip_pcp_bounds():
    spec = default_pathfinder_spec(3)
    pip_bound = calculate_pip_bound(spec)
    pcp_bound = calculate_pcp_bound(spec)
    
    # In M4, we found that PIP worst case blocking is 26ms (30ms ASI_MET crit - 4ms base execution before bc_sched arrives)
    sim_pip = Simulator(spec, "pip", duration=2000)
    res_pip = sim_pip.run()
    
    sim_pcp = Simulator(spec, "pcp", duration=2000)
    res_pcp = sim_pcp.run()
    
    assert res_pip["worst_case_blocking_bc"] <= pip_bound, "PIP worst-case blocking exceeded analytical bound"
    assert res_pcp["worst_case_blocking_bc"] <= pcp_bound, "PCP worst-case blocking exceeded analytical bound"
    
    # PCP worst case blocking should be less than or equal to PIP
    assert res_pcp["worst_case_blocking_bc"] <= res_pip["worst_case_blocking_bc"], "PCP blocking exceeded PIP blocking"
