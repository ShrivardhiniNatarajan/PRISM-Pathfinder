import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_spec.pathfinder_spec import default_pathfinder_spec
from sim.engine import Simulator

def run_m8_sweep():
    n = 3
    spec = default_pathfinder_spec(n)
    thresholds = [0.2, 0.4, 0.6, 0.8]
    
    overheads = []
    misses = []
    
    # Generate phases for GUARD
    duration = 10000
    phases = []
    for i in range(duration // 1000 + 1):
        start = i * 1000 + 19
        end = i * 1000 + 140
        phases.append((start, end, {"info_bus_mutex": True}))
        
    for tau in thresholds:
        sim = Simulator(spec, "guard", duration=duration, guard_phases=phases, guard_threshold=tau)
        res = sim.run()
        overheads.append(res["inheritance_active_ms"])
        misses.append(res["deadline_misses"])
        
    print("Thresholds:", thresholds)
    print("Overheads:", overheads)
    print("Misses:", misses)
    
    # Plot
    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = 'tab:blue'
    ax1.set_xlabel('GUARD Threshold (τ)')
    ax1.set_ylabel('Overhead (ms)', color=color)
    ax1.plot(thresholds, overheads, marker='o', color=color, label="Overhead")
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Deadline Misses', color=color)  
    ax2.plot(thresholds, misses, marker='x', linestyle='--', color=color, label="Misses")
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  
    plt.title("GUARD Threshold Sensitivity Sweep (N=3)")
    plt.savefig("results/figures/guard_threshold_sensitivity.png")
    plt.close()
    
    print("Saved results/figures/guard_threshold_sensitivity.png")

if __name__ == "__main__":
    run_m8_sweep()
