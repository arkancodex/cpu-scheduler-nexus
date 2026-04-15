"""
SRTF - Shortest Remaining Time First (Preemptive SJF)
Har time unit pe check hota hai - agar koi naya process aaya jiska
remaining time kam hai toh current process ruk jaati hai.
"""


def merge_gantt(gantt):
    """Consecutive same-process blocks ko ek mein merge karo."""
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


def run_srtf(processes):
    # Remaining burst time track karte hain har process ka
    remaining = {p["pid"]: p["burst_time"] for p in processes}
    first_run = {}      # pehli baar CPU kab mila
    completion_time = {}

    current_time = 0
    done_count = 0
    total = len(processes)

    raw_gantt = []      # merge se pehle wala gantt
    prev_pid = None
    segment_start = 0

    while done_count < total:
        # Abhi available processes (jo aa chuki hain aur khatam nahi hui)
        available = [
            p for p in processes
            if p["arrival_time"] <= current_time and remaining[p["pid"]] > 0
        ]

        if not available:
            # CPU idle hai - agar koi ongoing segment tha usse close karo
            if prev_pid is not None:
                raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})
                prev_pid = None
            current_time += 1
            continue

        # Sabse kam remaining time wali process choose karo
        chosen = min(
            available,
            key=lambda p: (remaining[p["pid"]], p["arrival_time"], p["pid"])
        )

        # Pehli baar run ho rahi hai toh response time note karo
        if chosen["pid"] not in first_run:
            first_run[chosen["pid"]] = current_time

        # Agar process badli toh pehle wala segment close karo, naya open karo
        if chosen["pid"] != prev_pid:
            if prev_pid is not None:
                raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})
            segment_start = current_time
            prev_pid = chosen["pid"]

        # Ek unit execute karo
        remaining[chosen["pid"]] -= 1
        current_time += 1

        # Process khatam?
        if remaining[chosen["pid"]] == 0:
            completion_time[chosen["pid"]] = current_time
            done_count += 1

    # Last segment close karo agar bacha ho
    if prev_pid is not None:
        raw_gantt.append({"pid": prev_pid, "start": segment_start, "end": current_time})

    # Metrics calculate karo har process ke liye
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
    return gantt, metrics, "SRTF (Preemptive SJF)"
