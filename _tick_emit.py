import json
TICK = "RUN-20260530-141526"
COMPLETED = ["11091484301140930622","11172407645040114728","5860122008944918375"]
ops = [{"op":"clear_session","idempotency_key":f"{TICK}:{sid}:clear","data":{"session_id":sid}} for sid in COMPLETED]
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"clear 3 COMPLETED sessions (PRs #44/#45/#46 auto-merged)",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_clear.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "ops")
