"""
FCFS - First Come First Serve Scheduling Algorithm
Non-preemptive: jab process aata hai, woh apna poora burst time leke jaata hai.
"""


def run_fcfs(processes):
    # Arrival time ke hisaab se sort karo, agar same arrival time toh PID se
    sorted_procs = sorted(processes, key=lambda p: (p["arrival_time"], p["pid"]))

    current_time = 0
    gantt = []
    metrics = []

    for proc in sorted_procs:
        # Agar CPU idle hai toh directly process ke arrival time pe jump karo
        if current_time < proc["arrival_time"]:
            current_time = proc["arrival_time"]

        start_time = current_time
        current_time += proc["burst_time"]
        completion_time = current_time

        tat = completion_time - proc["arrival_time"]       # Turnaround Time
        wt  = tat - proc["burst_time"]                    # Waiting Time
        rt  = start_time - proc["arrival_time"]           # Response Time (FCFS mein same as wt)

        gantt.append({
            "pid":   proc["pid"],
            "start": start_time,
            "end":   completion_time
        })

        metrics.append({
            "pid": proc["pid"],
            "at":  proc["arrival_time"],
            "bt":  proc["burst_time"],
            "ct":  completion_time,
            "tat": tat,
            "wt":  wt,
            "rt":  rt
        })

    return gantt, metrics, "FCFS"
