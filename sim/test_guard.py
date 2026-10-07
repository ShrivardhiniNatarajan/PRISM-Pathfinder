import pytest
from sim.guard import guard_decision

def test_guard_truth_table():
    res_name = "test_mutex"
    
    # 1. Score < Threshold
    scores = {res_name: {"score": 0.4}}
    assert not guard_decision(res_name, scores, threshold=0.5, current_phase_high_interference=False)
    assert not guard_decision(res_name, scores, threshold=0.5, current_phase_high_interference=True)
    
    # 2. Score >= Threshold, but Not high interference
    scores = {res_name: {"score": 0.8}}
    assert not guard_decision(res_name, scores, threshold=0.5, current_phase_high_interference=False)
    
    # 3. Score >= Threshold, AND high interference
    assert guard_decision(res_name, scores, threshold=0.5, current_phase_high_interference=True)
