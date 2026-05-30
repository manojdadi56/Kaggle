import json
TICK = "RUN-20260530-141526b"
ops = [
  # E-007 was operator-rescued earlier today (tick RUN-20260530-135009, commit bb6f8d3/ea848dd)
  {"op":"set_status","idempotency_key":f"{TICK}:TASK-E007-RESCOPE:done",
   "data":{"collection":"tasks","id":"TASK-E007-RESCOPE","status":"DONE"}},
  # Defer cron-trigger back to BACKLOG (user controls trigger cadence manually per the goal-loop pattern)
  {"op":"set_status","idempotency_key":f"{TICK}:TASK-OPS-cron-trigger:defer",
   "data":{"collection":"tasks","id":"TASK-OPS-cron-trigger","status":"BACKLOG"}},
]
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"close E007-RESCOPE (already rescued); defer cron-trigger (user controls cadence)",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_status.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "ops")
