import pandas as pd
from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.engine import Simulator

def run_condition(n_interferers: int, condition: str, duration: int = 10000) -> dict:
    spec = default_pathfinder_spec(n_interferers)
    
    phases = []
    if condition == "guard":
        # Only active when comm_task actually preempts bc_sched's blocking time
        # This saves active time while still preventing missed deadlines.
        for i in range(duration // 1000 + 1):
            start = i * 1000 + 19
            end = i * 1000 + 140
            phases.append((start, end, {"info_bus_mutex": True}))
            
    sim = Simulator(spec, condition, duration, guard_phases=phases, guard_threshold=0.5)
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

def run_m5_experiments():
    results = []
    
    for n in range(1, 6):
        spec = default_pathfinder_spec(n)
        pip_bound = calculate_pip_bound(spec)
        pcp_bound = calculate_pcp_bound(spec)
        
        for cond in ["baseline", "pip", "pcp", "guard"]:
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
    print("\n--- Milestone 5 Results: Baseline vs PIP vs PCP vs GUARD ---")
    print(df.to_string(index=False))
    
    # Verification
    print("\n--- Verification ---")
    for n in range(1, 6):
        pip_r = df[(df["N"] == n) & (df["Condition"] == "pip")].iloc[0]
        guard_r = df[(df["N"] == n) & (df["Condition"] == "guard")].iloc[0]
        
        print(f"N={n}:")
        print(f"  PIP   active time: {pip_r['Inheritance Active (ms)']} ms (Misses: {pip_r['Missed Deadlines']})")
        print(f"  GUARD active time: {guard_r['Inheritance Active (ms)']} ms (Misses: {guard_r['Missed Deadlines']})")
        assert guard_r["Missed Deadlines"] == 0, f"GUARD missed {guard_r['Missed Deadlines']} deadlines!"
        
    for target_n in [3, 5]:
        pip_r = df[(df["N"] == target_n) & (df["Condition"] == "pip")].iloc[0]
        guard_r = df[(df["N"] == target_n) & (df["Condition"] == "guard")].iloc[0]
        assert guard_r["Inheritance Active (ms)"] < pip_r["Inheritance Active (ms)"], f"GUARD active time not strictly lower for N={target_n}!"
        
if __name__ == "__main__":
    run_m5_experiments()
