import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.conditions import run_condition
from forecast.monte_carlo import run_forecast

def main():
    os.makedirs("results/raw", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    
    results = []
    
    # Run the experiment matrix
    print("Running Experiment Matrix...")
    conditions = ["baseline", "pip", "pcp", "guard"]
    
    # Store series for survival curve
    survival_data = {}
    
    for n in range(1, 6):
        spec = default_pathfinder_spec(n)
        for cond in conditions:
            print(f"Running N={n}, Condition={cond}...")
            # 1. Discrete Event Simulation (for blocking, overhead, misses)
            sim_res = run_condition(n, cond, duration=10000)
            
            # 2. Monte Carlo Forecast (for TTF)
            s_ttf = run_forecast(spec, cond, n_trials=10000, arrival_rate_lambda=0.000130, mission_horizon_ms=266325732, seed=42+n)
            
            if n == 5 and cond in ["baseline", "guard"]:
                survival_data[cond] = s_ttf
                
            censoring_rate = s_ttf.isna().sum() / 10000.0
            s_inf = s_ttf.fillna(np.inf)
            median_ttf = s_inf.median()
            p95_ttf = s_inf.quantile(0.05) # time by which 5% fail = 95% survival
            
            results.append({
                "condition": cond,
                "N": n,
                "worst_case_blocking_ms": sim_res["worst_case_blocking_bc"],
                "mean_blocking_ms": sim_res["mean_blocking_bc"],
                "deadline_misses": sim_res["deadline_misses"],
                "inheritance_active_ms": sim_res["inheritance_active_ms"],
                "median_ttf_ms": median_ttf,
                "p95_ttf_ms": p95_ttf,
                "censoring_rate": censoring_rate
            })
            
    df = pd.DataFrame(results)
    df.to_csv("results/raw/experiment_matrix.csv", index=False)
    print("Saved results/raw/experiment_matrix.csv")
    
    # Generate Plots
    print("Generating figures...")
    
    # 1. blocking_time_vs_N.png
    plt.figure(figsize=(8, 5))
    for cond in conditions:
        subset = df[df["condition"] == cond]
        plt.plot(subset["N"], subset["worst_case_blocking_ms"], marker='o', label=cond.upper())
    plt.title("Worst-Case Blocking Time vs Interferers (N)")
    plt.xlabel("Number of Interferers (N)")
    plt.ylabel("Worst-Case Blocking Time (ms)")
    plt.xticks(range(1, 6))
    plt.grid(True)
    plt.legend()
    plt.savefig("results/figures/blocking_time_vs_N.png")
    plt.close()
    
    # 2. overhead_vs_N.png
    plt.figure(figsize=(8, 5))
    for cond in conditions:
        subset = df[df["condition"] == cond]
        plt.plot(subset["N"], subset["inheritance_active_ms"], marker='o', label=cond.upper())
    plt.title("Inheritance Protocol Overhead vs Interferers (N)")
    plt.xlabel("Number of Interferers (N)")
    plt.ylabel("Cumulative Inheritance-Active Time (ms)")
    plt.xticks(range(1, 6))
    plt.grid(True)
    plt.legend()
    plt.savefig("results/figures/overhead_vs_N.png")
    plt.close()
    
    # 3. deadline_misses_vs_N.png
    plt.figure(figsize=(8, 5))
    for cond in conditions:
        subset = df[df["condition"] == cond]
        plt.plot(subset["N"], subset["deadline_misses"], marker='o', label=cond.upper())
    plt.title("Deadline Misses vs Interferers (N)")
    plt.xlabel("Number of Interferers (N)")
    plt.ylabel("Deadline Miss Count (over 10,000ms)")
    plt.xticks(range(1, 6))
    plt.grid(True)
    plt.legend()
    plt.savefig("results/figures/deadline_misses_vs_N.png")
    plt.close()
    
    # 4. forecast_survival_curve.png
    plt.figure(figsize=(8, 5))
    t_base = np.sort(survival_data["baseline"].dropna().values)
    surv_base = 1.0 - np.arange(1, len(t_base) + 1) / 10000.0
    
    # Append the horizon point
    horizon = 266325732
    if len(t_base) > 0:
        t_base = np.append(t_base, horizon)
        surv_base = np.append(surv_base, surv_base[-1])
    else:
        t_base = np.array([0, horizon])
        surv_base = np.array([1.0, 1.0])
        
    t_guard = np.sort(survival_data["guard"].dropna().values)
    surv_guard = 1.0 - np.arange(1, len(t_guard) + 1) / 10000.0
    if len(t_guard) > 0:
        t_guard = np.append(t_guard, horizon)
        surv_guard = np.append(surv_guard, surv_guard[-1])
    else:
        t_guard = np.array([0, horizon])
        surv_guard = np.array([1.0, 1.0])
        
    # Convert ms to Sols for plot
    ms_to_sols = 88775244.0
    plt.step(t_base / ms_to_sols, surv_base, where='post', label='BASELINE (Unprotected)', color='red')
    plt.step(t_guard / ms_to_sols, surv_guard, where='post', label='GUARD (Protected)', color='green')
    
    # Reference line at actual approximate mission reset time (e.g., 3 sols)
    plt.axvline(x=2.88, color='black', linestyle='--', label='Pathfinder Reset (~2.88 sols)')
    
    plt.title("Mission Survival Curve (N=5 Forecast)")
    plt.xlabel("Time Since Landing (Sols)")
    plt.ylabel("Probability of System Survival")
    plt.ylim(0, 1.05)
    plt.xlim(0, horizon / ms_to_sols)
    plt.grid(True)
    plt.legend()
    plt.savefig("results/figures/forecast_survival_curve.png")
    plt.close()
    
    print("All experiments and plotting completed successfully.")

if __name__ == "__main__":
    main()
