import pandas as pd
from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.engine import Simulator

def run_condition(n_interferers: int, condition: str, duration: int = 10000) -> dict:
    spec = default_pathfinder_spec(n_interferers)
    sim = Simulator(spec, condition, duration)
    return sim.run()

def calculate_pip_bound(spec) -> float:
    # Max single critical section among tasks locking the mutex
    # For this task set, info_bus_mutex is held by ASI_MET for 30ms.
    # PIP bound for a task sharing m resources is sum of max critical sections.
    # Here, bc_sched shares 1 resource, so bound is 30ms.
    res = spec.resources[0]
    return res.critical_section_ms

def run_m3_experiments():
    results = []
    
    for n in range(1, 6):
        spec = default_pathfinder_spec(n)
        pip_bound = calculate_pip_bound(spec)
        
        for cond in ["baseline", "pip"]:
            res = run_condition(n, cond, duration=10000)
            results.append({
                "N": n,
                "Condition": cond,
                "Worst-case Blocking (ms)": res["worst_case_blocking_bc"],
                "Mean Blocking (ms)": res["mean_blocking_bc"],
                "Missed Deadlines": res["deadline_misses"],
                "Inheritance Active (ms)": res["inheritance_active_ms"],
                "PIP Bound (ms)": pip_bound
            })
            
    df = pd.DataFrame(results)
    print("\n--- Milestone 3 Results: Baseline vs PIP ---")
    print(df.to_string(index=False))
    
    # Verify bounds programmatically
    print("\n--- Verification ---")
    for n in range(1, 6):
        base = df[(df["N"] == n) & (df["Condition"] == "baseline")].iloc[0]
        pip_r = df[(df["N"] == n) & (df["Condition"] == "pip")].iloc[0]
        
        print(f"N={n}:")
        print(f"  Baseline worst-case blocking: {base['Worst-case Blocking (ms)']} ms")
        print(f"  PIP worst-case blocking: {pip_r['Worst-case Blocking (ms)']} ms (Bound: {pip_r['PIP Bound (ms)']} ms)")
        assert pip_r["Worst-case Blocking (ms)"] <= pip_r["PIP Bound (ms)"], "PIP bound violated!"
        
    base_worst = df[df["Condition"] == "baseline"]["Worst-case Blocking (ms)"].tolist()
    print("\nBaseline worst-case blocking over N=1..5:", base_worst)
    
if __name__ == "__main__":
    run_m3_experiments()
