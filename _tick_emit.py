import json
TICK = "RUN-20260530-131519"
COMPLETED = ["15457649004442238545","290296703496810863","728421577080239025"]
ops = [{"op":"clear_session","idempotency_key":f"{TICK}:{sid}:clear","data":{"session_id":sid}} for sid in COMPLETED]
# also explicitly mark package-zip task DONE since we rescued its PR
ops.append({"op":"set_status","idempotency_key":f"{TICK}:TASK-SUBMIT-package-zip:done",
            "data":{"collection":"tasks","id":"TASK-SUBMIT-package-zip","status":"DONE"}})
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"clear 3 COMPLETED + mark package-zip DONE (operator-rescued patch from session that completed without PR)",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_clear.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "ops")
