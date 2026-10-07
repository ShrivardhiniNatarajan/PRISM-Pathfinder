import pytest
import pandas as pd
import numpy as np
from task_spec.pathfinder_spec import default_pathfinder_spec
from forecast.monte_carlo import run_forecast

def test_forecast_censoring():
    spec = default_pathfinder_spec(3)
    
    # Under PIP, there are 0 deadline misses, so 100% of trials should be censored (NaN)
    s_pip = run_forecast(spec, "pip", n_trials=100)
    
    # Check that all trials are censored
    assert s_pip.isna().all(), "PIP forecast should have 100% censoring rate"
    assert len(s_pip) == 100
    
    # For baseline with very high lambda, it should fail and NOT be censored
    # Very high lambda means guaranteed failure in the first period.
    s_base = run_forecast(spec, "baseline", n_trials=100, arrival_rate_lambda=0.5)
    
    assert not s_base.isna().any(), "Baseline with very high lambda should have 0% censoring rate"
    assert len(s_base) == 100
