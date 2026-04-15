"""
Priority Scheduling - Non-Preemptive aur Preemptive dono versions.
Lower priority number = higher priority (0 sabse important hai).
"""


def merge_gantt(gantt):
    """Consecutive same-process blocks ko ek mein merge karo (preemptive ke liye)."""
    if not gantt:
        return []
    merged = [dict(gantt[0])]
    for block in gantt[1:]:
        last = merged[-1]
        if block["pid"] == last["pid"] and block["start"] == last["end"]:
            last["end"] = block["end"]
        else:
            merged.append(dict(block))
    return merged


def run_priority(processes):
    """
    Non-Preemptive Priority Scheduling.
    Ek baar CPU mila toh process poora burst time leke hi jaayegi.
    """
    completed = set()
    first_run = {}

    current_time = 0
    gantt = []
    metrics = []
    total = len(processes)

    while len(completed) < total:
        # Available processes: arrival ho chuki ho, complete nahi hui ho
        available = [
            p for p in processes
            if p["arrival_time"] <= current_time and p["pid"] not in completed
        ]

        if not available:
            # CPU idle - agle process ke aane tak jump karo
            next_time = min(
                p["arrival_time"] for p in processes if p["pid"] not in completed
            )
            current_time = next_time
            continue

        # Sabse high priority (lowest number) wali process
        # Tie-break: arrival time, phir PID
        chosen = min(
            available,
            key=lambda p: (p["priority"], p["arrival_time"], p["pid"])
        )

        first_run[chosen["pid"]] = current_time
        start_time = current_time
        current_time += chosen["burst_time"]
        completion_time = current_time

        tat = completion_time - chosen["arrival_time"]
        wt  = tat - chosen["burst_time"]
        rt  = first_run[chosen["pid"]] - chosen["arrival_time"]

        gantt.append({"pid": chosen["pid"], "start": start_time, "end": completion_time})
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

    return gantt, metrics, "Priority (Non-Preemptive)"


def run_priority_preemptive(processes):
    """
    Preemptive Priority Scheduling.
    Har time unit pe check - agar koi higher priority process aa gayi
    toh current wali ruk jaayegi.
    """
    remaining = {p["pid"]: p["burst_time"] for p in processes}
    first_run = {}
    completion_time = {}

    current_time = 0
    done_count = 0
    total = len(processes)

    raw_gantt = []
    prev_pid = None
    segment_start = 0

    while done_count < total:
        # Available: aa chuki hain aur remaining time > 0
        available = [
            p for p in processes
            if p["arrival_time"] <= current_time and remaining[p["pid"]] > 0
        ]

        if not available:
            if prev_pid is not None:
                raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})
                prev_pid = None
            current_time += 1
            continue

        # Highest priority process (lowest number wali)
        chosen = min(
            available,
            key=lambda p: (p["priority"], p["arrival_time"], p["pid"])
        )

        if chosen["pid"] not in first_run:
            first_run[chosen["pid"]] = current_time

        # Naya segment shuru hua toh pehle wala close karo
        if chosen["pid"] != prev_pid:
            if prev_pid is not None:
                raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})
            segment_start = current_time
            prev_pid = chosen["pid"]

        remaining[chosen["pid"]] -= 1
        current_time += 1

        if remaining[chosen["pid"]] == 0:
            completion_time[chosen["pid"]] = current_time
            done_count += 1

    # Agar last segment bacha ho
    if prev_pid is not None:
        raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})

    # Metrics
    metrics = []
    for proc in processes:
        ct  = completion_time[proc["pid"]]
        tat = ct - proc["arrival_time"]
        wt  = tat - proc["burst_time"]
        rt  = first_run[proc["pid"]] - proc["arrival_time"]

        metrics.append({
            "pid": proc["pid"],
            "at":  proc["arrival_time"],
            "bt":  proc["burst_time"],
            "ct":  ct,
            "tat": tat,
            "wt":  wt,
            "rt":  rt
        })

    gantt = merge_gantt(raw_gantt)
    return gantt, metrics, "Priority (Preemptive)"
