import pandas as pd
from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.engine import Simulator

def run_condition(n_interferers: int, condition: str, duration: int = 10000) -> dict:
    spec = default_pathfinder_spec(n_interferers)
    sim = Simulator(spec, condition, duration)
    return sim.run()

def calculate_pip_bound(spec) -> float:
    res = spec.resources[0]
    return res.critical_section_ms

def calculate_pcp_bound(spec) -> float:
    # Max single critical section among tasks whose ceiling >= bc_sched's priority
    # Here, info_bus_mutex ceiling is HIGH (3). bc_sched priority is 3. 
    # ASI_MET locks it for 30ms.
    res = spec.resources[0]
    return res.critical_section_ms

def run_m4_experiments():
    results = []
    
    for n in range(1, 6):
        spec = default_pathfinder_spec(n)
        pip_bound = calculate_pip_bound(spec)
        pcp_bound = calculate_pcp_bound(spec)
        
        for cond in ["baseline", "pip", "pcp"]:
            res = run_condition(n, cond, duration=10000)
            results.append({
                "N": n,
                "Condition": cond,
                "Worst-case Blocking (ms)": res["worst_case_blocking_bc"],
                "Mean Blocking (ms)": res["mean_blocking_bc"],
                "Missed Deadlines": res["deadline_misses"],
                "Inheritance Active (ms)": res["inheritance_active_ms"],
                "Bound (ms)": pip_bound if cond != "pcp" else pcp_bound
            })
            
    df = pd.DataFrame(results)
    print("\n--- Milestone 4 Results: Baseline vs PIP vs PCP ---")
    print(df.to_string(index=False))
    
    # Verification
    print("\n--- Verification ---")
    for n in range(1, 6):
        pip_r = df[(df["N"] == n) & (df["Condition"] == "pip")].iloc[0]
        pcp_r = df[(df["N"] == n) & (df["Condition"] == "pcp")].iloc[0]
        
        print(f"N={n}:")
        print(f"  PIP worst-case blocking: {pip_r['Worst-case Blocking (ms)']} ms")
        print(f"  PCP worst-case blocking: {pcp_r['Worst-case Blocking (ms)']} ms (Bound: {pcp_r['Bound (ms)']} ms)")
        assert pcp_r["Worst-case Blocking (ms)"] <= pip_r["Worst-case Blocking (ms)"], "PCP blocking exceeded PIP blocking!"
        assert pcp_r["Worst-case Blocking (ms)"] <= pcp_r["Bound (ms)"], "PCP bound violated!"
        
if __name__ == "__main__":
    run_m4_experiments()
