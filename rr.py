"""
Round Robin Scheduling
Har process ko ek fixed quantum mila hai CPU pe.
Time khatam? Wapis queue mein! Fair sharing approach.
"""


def run_rr(processes, quantum):
    # Arrival time ke hisaab se sort karo pehle
    sorted_procs = sorted(processes, key=lambda p: (p["arrival_time"], p["pid"]))

    remaining = {p["pid"]: p["burst_time"] for p in processes}
    first_run = {}
    completion_time = {}

    current_time = 0
    gantt = []
    queue = []
    in_queue = set()    # duplicate entries avoid karne ke liye
    idx = 0             # sorted_procs mein position

    # Shuruaat mein jo processes already available hain unhe queue mein daalo
    while idx < len(sorted_procs) and sorted_procs[idx]["arrival_time"] <= current_time:
        queue.append(sorted_procs[idx])
        in_queue.add(sorted_procs[idx]["pid"])
        idx += 1

    while queue or idx < len(sorted_procs):
        # Agar queue empty hai toh agle process ke aane tak skip karo
        if not queue:
            current_time = sorted_procs[idx]["arrival_time"]
            while idx < len(sorted_procs) and sorted_procs[idx]["arrival_time"] <= current_time:
                if sorted_procs[idx]["pid"] not in in_queue:
                    queue.append(sorted_procs[idx])
                    in_queue.add(sorted_procs[idx]["pid"])
                idx += 1

        current_proc = queue.pop(0)
        pid = current_proc["pid"]

        # Response time: pehli baar CPU kab mila
        if pid not in first_run:
            first_run[pid] = current_time

        # Kitna execute hoga is baar - minimum of quantum or remaining time
        exec_time = min(quantum, remaining[pid])
        start_time = current_time

        gantt.append({"pid": pid, "start": start_time, "end": start_time + exec_time})
        current_time += exec_time
        remaining[pid] -= exec_time

        # Is execution ke baad jo processes aa gayi hain unhe queue mein daalo
        newly_arrived = []
        while idx < len(sorted_procs) and sorted_procs[idx]["arrival_time"] <= current_time:
            if sorted_procs[idx]["pid"] not in in_queue:
                newly_arrived.append(sorted_procs[idx])
                in_queue.add(sorted_procs[idx]["pid"])
            idx += 1
        queue.extend(newly_arrived)

        if remaining[pid] > 0:
            # Process abhi bhi baaki hai - wapis queue mein
            queue.append(current_proc)
        else:
            # Process khatam!
            completion_time[pid] = current_time

    # Final metrics
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

    return gantt, metrics, f"Round Robin (Q={quantum})"
