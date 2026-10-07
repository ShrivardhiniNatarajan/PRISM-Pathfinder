# PRISM-Pathfinder

PRISM-Pathfinder is a Python-based project that numerically reconstructs the 1997 Mars Pathfinder priority-inversion incident and evaluates **PRISM**, a novel three-module framework (SCAN, GUARD, FORECAST) for cost-aware adaptive priority-inheritance protection.

## Modules

1. **SCAN**: A transparent, auditable static risk scoring module that evaluates resources based on priority span, interferer count, critical section duration, and inheritance penalty.
2. **GUARD**: A gating logic module that evaluates the SCAN score and temporal high-interference phases to dynamically apply Priority Inheritance Protocol (PIP) only when necessary, minimizing RTOS overhead.
3. **FORECAST**: A classical Monte Carlo simulation module relying on Poisson task arrivals to forecast the time-to-first-deadline-miss (system reset) over mission horizons stretching millions of milliseconds (Martian sols).

## Installation

Ensure you have Python 3.12+ installed. Clone the repository and install the dependencies:

```bash
git clone <repository_url>
cd PRISM
pip install -r requirements.txt
```

## Running the Simulation & Experiments

To run the full discrete-event simulation and Monte Carlo forecasting experiment matrix (sweeping across N=1..5 interferers and 4 conditions: Baseline, PIP, PCP, GUARD):

```bash
python experiments/run_experiment_matrix.py
```

This will automatically generate the experiment summary at `results/raw/experiment_matrix.csv` and output all plots into the `results/figures/` directory.

To run the test suite to validate bounds and truth tables:

```bash
pytest
```

## Results Summary

Our results validate the PRISM framework against the classic Pathfinder scenario:

- **Baseline Vulnerability**: Under the baseline condition (no protection), the system misses deadlines strictly when $N \ge 4$ interferers are present, and the FORECAST module correctly predicts a median time-to-first-reset of $\approx 2.88$ Sols (matching historical accounts).
- **Protocol Bounds**: Traditional PIP and PCP completely eliminate deadline misses. PCP perfectly matches PIP's $26\text{ ms}$ worst-case blocking time, but applies priority boosts overly pessimistically.
- **GUARD Efficiency**: GUARD successfully achieves $0$ deadline misses (identical to PIP and PCP) but maintains a strictly lower cumulative inheritance-active time ($\approx 231\text{ ms}$ vs PIP's $241\text{ ms}$) by dynamically disengaging protection when high-priority tasks are not immediately threatened.
- **Survival**: Under GUARD, the survival curve remains perfectly flat at $100\%$ censoring (no system resets) across the entire 3-Sol mission horizon.

### Plots

* [Worst-case Blocking Time vs N](results/figures/blocking_time_vs_N.png)
* [Overhead vs N](results/figures/overhead_vs_N.png)
* [Deadline Misses vs N](results/figures/deadline_misses_vs_N.png)
* [Mission Survival Curve](results/figures/forecast_survival_curve.png)

## License
MIT
