# Traffic Signal Optimization 🚦

An algorithmic approach to adaptive traffic light scheduling at a 4-way intersection. We implement three strategies — Greedy, Sorting-Based Heuristic, and Dynamic Programming — benchmark them against each other, and visualize the best two in a real-time Pygame simulation with animated vehicles, signal state, and live metrics.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![Pygame](https://img.shields.io/badge/Pygame-Simulation-green?style=flat-square) ![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 📌 Overview

Fixed-cycle traffic lights ignore real-time demand — a lane with 30 queued cars gets the same green window as an empty one. This project frames traffic light scheduling as an optimization problem: given stochastic vehicle arrivals across four directions, find a signal timing policy that minimizes total queue length and wait time while respecting constraints like minimum/maximum green durations and mandatory yellow intervals.

The project has two parts: an analytical notebook that implements and benchmarks all three algorithms, and a Pygame simulation that brings the intersection to life.

## 🧠 Algorithms

### Greedy Heuristic
At each decision point, compute a weighted queue score per direction (trucks and buses cost more time than bikes) and give green time to the heaviest queue. Fast and reactive, but myopic — it can't anticipate downstream congestion and can starve low-traffic lanes.

**Time Complexity:** O(n) per decision

### Sorting-Based Heuristic
Scores each lane with a weighted linear combination:

```
score = α · queue_length + β · arrival_rate + γ · time_since_last_service
```

The γ parameter prevents lane starvation. Tunable weights let the policy balance urgency, demand forecasting, and fairness.

**Time Complexity:** O(n log n) per decision

### Dynamic Programming (Lookahead)
Uses a rolling-horizon approach. At each decision point, it explores multiple possible green-time allocations and simulates their impact over a configurable lookahead window. It picks the allocation that minimizes total projected queue across all directions — accounting for vehicles cleared *and* vehicles accumulating in waiting lanes.

**Time Complexity:** O(n · horizon · actions) per decision

## ✨ Features

- 🧪 **Three algorithms benchmarked** — Greedy, Sorting Heuristic, and DP compared on queue length, throughput, fairness, and computational cost
- 🎮 **Real-time Pygame simulation** — animated 4-way intersection with vehicles queuing, crossing, and turning
- 🚗 **Five vehicle types** — cars, buses, trucks, rickshaws, and bikes, each with distinct speeds and crossing times
- 📊 **Live HUD** — signal state, countdown timers, vehicles crossed per lane, and current queue length displayed in real time
- 🔀 **Algorithm switching** — toggle between Greedy and DP in the visual simulation with a single variable change
- 📈 **Metrics export** — saves per-run performance data to a text file for offline comparison
- ✅ **Unit tested** — lane arrivals, signal transitions, and metric calculations validated before experiments run

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| Visual Simulation | Pygame |
| Analysis & Benchmarking | Jupyter Notebook |
| Visualization | Matplotlib |

## 📁 Project Structure

```
traffic-signal-optimization/
├── CS5800_Final_Project_Code_Steve_Kaushal.ipynb   # Full analytical pipeline — all 3 algorithms, metrics, plots
├── traffic_simulation_enhanced.py                  # Pygame visual simulation (Greedy & DP)
├── LICENSE
└── README.md
```

## 🚀 Getting Started

### Run the analytical notebook

1. Clone the repo:

```bash
git clone https://github.com/<your-username>/traffic-signal-optimization.git
cd traffic-signal-optimization
```

2. Install dependencies:

```bash
pip install pygame matplotlib
```

3. Run the notebook:

```bash
jupyter notebook CS5800_Final_Project_Code_Steve_Kaushal.ipynb
```

The notebook runs unit tests first, then executes the full simulation comparing all three algorithms with visualization.

### Run the Pygame simulation

After running the notebook, launch the visual simulation:

```bash
python traffic_simulation_enhanced.py
```

Make sure the `images/` folder is in the same directory as the script.

To switch algorithms, change line 42:

```python
ALGORITHM = "dp"      # Options: "greedy" or "dp"
```

## 📊 Key Comparisons

| Metric | Greedy | Sorting-Based | DP (Lookahead) |
|--------|--------|---------------|----------------|
| Reactivity | High | High | Moderate |
| Fairness | Can starve low-traffic lanes | γ parameter prevents starvation | Depends on horizon |
| Queue Optimization | Local only | Weighted local | Global (within horizon) |
| Computational Cost | O(n) | O(n log n) | O(n · horizon · actions) |

## 👥 Authors

- **Kaushal Nair** · MS Data Science — [GitHub](https://github.com/<your-username>)
- **Steve George** · MS Computer Science — [GitHub](https://github.com/<steve-username>)

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Final project for CS 5800: Algorithms — Northeastern University, Khoury College of Computer Sciences, Fall 2025*
