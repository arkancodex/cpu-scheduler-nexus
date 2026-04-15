"""
CPU Scheduler - Flask Backend
Ye file frontend se request receive karti hai aur sahi algorithm call karti hai.
Run karo: python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from fcfs import run_fcfs
from sjf import run_sjf
from srtf import run_srtf
from rr import run_rr
from priority import run_priority, run_priority_preemptive

app = Flask(__name__)

# CORS allow (frontend connect ke liye)
CORS(app, resources={r"/*": {"origins": "*"}})


# 🔥 Health check route (Render ke liye important)
@app.route("/", methods=["GET"])
def home():
    return "CPU Scheduler Backend Running 🚀"


def calculate_averages(metrics, gantt, processes):
    """
    Common stats calculate karo - average WT, TAT, RT aur CPU utilization.
    """
    n = len(metrics)
    if n == 0:
        return 0, 0, 0, 0

    avg_wt = round(sum(m["wt"] for m in metrics) / n, 2)
    avg_tat = round(sum(m["tat"] for m in metrics) / n, 2)
    avg_rt = round(sum(m["rt"] for m in metrics) / n, 2)

    total_burst = sum(p["burst_time"] for p in processes)

    # Safe handling (empty gantt avoid crash)
    end_time = max((block["end"] for block in gantt), default=0)
    start_time = min((p["arrival_time"] for p in processes), default=0)

    span = end_time - start_time
    cpu_util = round(min(100.0, (total_burst / span) * 100), 2) if span > 0 else 100.0

    return avg_wt, avg_tat, avg_rt, cpu_util


@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body JSON nahi hai"}), 400

    algorithm = data.get("algorithm")
    processes = data.get("processes", [])
    quantum = data.get("quantum", 2)

    if not algorithm:
        return jsonify({"error": "Algorithm specify karo"}), 400

    if not processes:
        return jsonify({"error": "Koi bhi process nahi diya"}), 400

    # Validation
    for proc in processes:
        if "pid" not in proc or "arrival_time" not in proc or "burst_time" not in proc:
            return jsonify({"error": "Process mein pid, arrival_time, burst_time hona chahiye"}), 400
        if proc["burst_time"] < 1:
            return jsonify({"error": f"{proc['pid']} ka burst time 1 se kam nahi ho sakta"}), 400

    try:
        print("Algorithm:", algorithm)
        print("Processes:", processes)

        # Algorithm selection
        if algorithm == "fcfs":
            gantt, metrics, algo_name = run_fcfs(processes)

        elif algorithm == "sjf":
            gantt, metrics, algo_name = run_sjf(processes)

        elif algorithm == "srtf":
            gantt, metrics, algo_name = run_srtf(processes)

        elif algorithm == "rr":
            if quantum < 1:
                return jsonify({"error": "Quantum 1 se kam nahi ho sakta"}), 400
            gantt, metrics, algo_name = run_rr(processes, quantum)

        elif algorithm == "priority":
            gantt, metrics, algo_name = run_priority(processes)

        elif algorithm == "priority_preemptive":
            gantt, metrics, algo_name = run_priority_preemptive(processes)

        else:
            return jsonify({"error": f"Unknown algorithm: {algorithm}"}), 400

        avg_wt, avg_tat, avg_rt, cpu_util = calculate_averages(metrics, gantt, processes)

        response = {
            "algorithm": algo_name,
            "gantt": gantt,
            "metrics": metrics,
            "avg_wt": avg_wt,
            "avg_tat": avg_tat,
            "avg_rt": avg_rt,
            "cpu_util": cpu_util
        }

        return jsonify(response), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run()