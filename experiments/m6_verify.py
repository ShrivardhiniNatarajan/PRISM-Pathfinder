import sys
sys.path.append("C:/PRISM")

from task_spec.pathfinder_spec import default_pathfinder_spec
from forecast.monte_carlo import run_forecast

def run_m6_verification():
    spec = default_pathfinder_spec(5)
    
    print("Running baseline forecast...")
    base_s = run_forecast(spec, "baseline", n_trials=10000, arrival_rate_lambda=0.000130)
    
    print("\nRunning guard forecast...")
    guard_s = run_forecast(spec, "guard", n_trials=10000, arrival_rate_lambda=0.000130)

if __name__ == "__main__":
    run_m6_verification()
