import json
TICK = "RUN-20260530-150539"
ops = [
  {"op":"clear_session","idempotency_key":f"{TICK}:4390025997776432846:clear",
   "data":{"session_id":"4390025997776432846"}},
  {"op":"set_status","idempotency_key":f"{TICK}:TASK-OPS-auto-rescue:done",
   "data":{"collection":"tasks","id":"TASK-OPS-auto-rescue","status":"DONE"}},
  {"op":"update_session","idempotency_key":f"{TICK}:12749140667475037666:state",
   "data":{"session_id":"12749140667475037666","state":"IN_PROGRESS"}},
]
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"clear auto-rescue (operator-rescued); steer FIX-kernel-metadata (use competition_sources + inline corpus build)",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_clear.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "ops")
