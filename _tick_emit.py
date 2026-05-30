import json
TICK = "RUN-20260530-135009"
ops = [
  # clear PR-43 session
  {"op":"clear_session","idempotency_key":f"{TICK}:15996892913727706506:clear",
   "data":{"session_id":"15996892913727706506"}},
  # clear E-007 session (rescued operator-side)
  {"op":"clear_session","idempotency_key":f"{TICK}:13107147469450254389:clear",
   "data":{"session_id":"13107147469450254389"}},
  # mark E-007 task DONE
  {"op":"set_status","idempotency_key":f"{TICK}:TASK-E007:done",
   "data":{"collection":"tasks","id":"TASK-E007-cryptarithm-guess-integration","status":"DONE"}},
]
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"clear PR-43 + operator-rescued E-007 sessions; mark E-007 DONE",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_clear.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "ops")
