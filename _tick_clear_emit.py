import json
TICK = "RUN-20260530-124519"
COMPLETED = [
  "13013155406031425658","14674823960857717074","14769124856858592956",
  "3331869219988151080","5459254010184172264","6684794983844118444",
  "8195905385648107214","9916984275388767522",
]
ops = [{"op":"clear_session","idempotency_key":f"{TICK}:{sid}:clear","data":{"session_id":sid}} for sid in COMPLETED]
decision = {
  "tick_id":TICK,"status":"complete",
  "summary":"clear 8 COMPLETED sessions (PRs #32-#39 all auto-merged via R-007)",
  "state_patch":{"tick_id":TICK,"operations":ops},
}
with open("decision_clear.json","w",encoding="utf-8") as f: json.dump(decision,f)
print("wrote", len(ops), "clear_session ops")
