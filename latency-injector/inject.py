import subprocess
import sys
import time

# Profile definitions: name -> list of (node_number, delay_ms)
# 5 nodes: fast nodes get 1ms, slow nodes get the higher delay
PROFILES = {
    "mild": [
        ("node1", 1),
        ("node2", 1),
        ("node3", 1),
        ("node4", 2),
        ("node5", 2),
    ],
    "moderate": [
        ("node1", 1),
        ("node2", 1),
        ("node3", 1),
        ("node4", 5),
        ("node5", 5),
    ],
    "severe": [
        ("node1", 1),
        ("node2", 1),
        ("node3", 1),
        ("node4", 10),
        ("node5", 10),
    ],
}

def get_container_name(node_id):
    """Returns the Docker container name for a node."""
    return f"raft-{node_id}-1"

def run_in_container(container, cmd):
    """Runs a shell command inside a Docker container."""
    full_cmd = ["docker", "exec", container, "sh", "-c", cmd]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result

def clear_delay(container):
    """Removes any existing tc netem rule (ignore error if none exists)."""
    run_in_container(container, "tc qdisc del dev eth0 root 2>/dev/null || true")

def apply_delay(container, delay_ms):
    """Applies a netem delay to eth0 inside the container."""
    cmd = f"tc qdisc add dev eth0 root netem delay {delay_ms}ms"
    result = run_in_container(container, cmd)
    if result.returncode != 0:
        print(f"  ⚠️  Warning applying delay to {container}: {result.stderr.strip()}")
    else:
        print(f"  ✅ Applied {delay_ms}ms delay to {container}")

def show_current(container):
    """Shows current tc rules for a container."""
    result = run_in_container(container, "tc qdisc show dev eth0")
    return result.stdout.strip()

def inject_profile(profile_name):
    """Applies a named latency profile to all 5 nodes."""
    if profile_name not in PROFILES:
        print(f"❌ Unknown profile '{profile_name}'. Choose: mild, moderate, severe")
        sys.exit(1)

    profile = PROFILES[profile_name]
    spreads = {"mild": "2×", "moderate": "5×", "severe": "10×"}

    print(f"\n🔧 Injecting profile: {profile_name.upper()} ({spreads[profile_name]} spread)")
    print("─" * 50)

    for node_id, delay_ms in profile:
        container = get_container_name(node_id)
        print(f"\n[{node_id}] → {delay_ms}ms delay")
        clear_delay(container)
        apply_delay(container, delay_ms)

    print("\n✅ Profile applied. Waiting 5 seconds for rules to take effect...")
    time.sleep(5)
    print("\n📋 Verification — current tc rules per node:")
    print("─" * 50)
    for node_id, delay_ms in profile:
        container = get_container_name(node_id)
        status = show_current(container)
        print(f"  {node_id}: {status}")

def reset_all():
    """Removes all tc rules from all nodes."""
    print("\n🔄 Resetting all nodes to no delay...")
    for node_id in ["node1", "node2", "node3", "node4", "node5"]:
        container = get_container_name(node_id)
        clear_delay(container)
        print(f"  ✅ Cleared {node_id}")
    print("\n✅ All nodes reset.")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python inject.py mild        # Apply mild profile (2x spread)")
        print("  python inject.py moderate    # Apply moderate profile (5x spread)")
        print("  python inject.py severe      # Apply severe profile (10x spread)")
        print("  python inject.py reset       # Remove all delays")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "reset":
        reset_all()
    else:
        inject_profile(command)

if __name__ == "__main__":
    main()