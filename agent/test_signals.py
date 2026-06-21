from agent.planner_tools import get_pending_signals

signals = get_pending_signals()

print(f"\nFound {len(signals)} signals\n")

for signal in signals:
    print(signal)