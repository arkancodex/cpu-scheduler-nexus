"""
SJF - Shortest Job First (Non-Preemptive)
Jo process sabse kam burst time leti hai, woh pehle run hoti hai.
Lekin ek baar CPU mil gaya toh koi interrupt nahi karega.
"""


def run_sjf(processes):
    total = len(processes)
    completed = set()   # jo processes khatam ho gayi unke PIDs
    first_run = {}      # har process pehli baar kab chali

    current_time = 0
    gantt = []
    metrics = []

    while len(completed) < total:
        # Abhi tak jo processes aa chuki hain aur complete nahi hui hain unhe dekho
        available = [
            p for p in processes
            if p["arrival_time"] <= current_time and p["pid"] not in completed
        ]

        if not available:
            # Koi process available nahi - agle arrival tak jump karo (CPU idle)
            next_arrival = min(
                p["arrival_time"] for p in processes if p["pid"] not in completed
            )
            current_time = next_arrival
            continue

        # Sabse kam burst time wali process choose karo
        # Tie-break: pehle aaya, phir PID alphabetically
        chosen = min(
            available,
            key=lambda p: (p["burst_time"], p["arrival_time"], p["pid"])
        )

        first_run[chosen["pid"]] = current_time

        start_time = current_time
        current_time += chosen["burst_time"]
        completion_time = current_time

        tat = completion_time - chosen["arrival_time"]
        wt  = tat - chosen["burst_time"]
        rt  = first_run[chosen["pid"]] - chosen["arrival_time"]

        gantt.append({
            "pid":   chosen["pid"],
            "start": start_time,
            "end":   completion_time
        })

        metrics.append({
            "pid": chosen["pid"],
            "at":  chosen["arrival_time"],
            "bt":  chosen["burst_time"],
            "ct":  completion_time,
            "tat": tat,
            "wt":  wt,
            "rt":  rt
        })

        completed.add(chosen["pid"])

    return gantt, metrics, "SJF (Non-Preemptive)"
