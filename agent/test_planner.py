from agent.planner import generate_daily_plan
import pprint


plan = generate_daily_plan()
pprint.pprint(plan)

print("\n===== TODAY =====")

for item in plan["today"]:
    print(
        f"{item['time_slot']} | "
        f"{item['student_name']} | "
        f"{item['session_type']} | "
        f"{item['reason']}"
    )

print("\n===== DEFERRED =====")

for item in plan["deferred"]:
    print(
        f"{item['student_name']} | "
        f"{item['reason']}"
    )