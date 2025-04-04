import subprocess
import sys

def get_running_containers():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}:::{{.Image}}"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split("\n") if result.stdout else []
    containers = []
    for line in lines:
        if ":::" in line:
            name, image = line.split(":::")
            containers.append((name.strip(), image.strip()))
    return containers

def select_containers(containers, already_selected):
    selected = []

    while True:
        remaining = [c for i, c in enumerate(containers) if i not in already_selected]
        if not remaining:
            print("✔️ All containers have been selected.")
            break

        print("\nRunning containers:")
        for idx, (name, image) in enumerate(remaining, start=1):
            print(f"{idx}. {name} ({image})")

        choice = input("\nSelect a container by number (ENTER to finish): ").strip()
        if choice == "":
            break

        try:
            index = int(choice) - 1
            if index < 0 or index >= len(remaining):
                print("❌ Invalid selection.")
                continue

            selected_container = remaining[index]
            print(f"Selected: {selected_container[0]} ({selected_container[1]})")
            selected.append(selected_container)
            already_selected.add(containers.index(selected_container))
        except ValueError:
            print("❌ Please enter a valid number.")

    return selected

def confirm_selection(containers):
    if not containers:
        print("❌ No containers selected.")
        return False

    print("\nSelected containers:")
    for idx, (name, image) in enumerate(containers, start=1):
        print(f"{idx}. {name} ({image})")
    choice = input("Press ENTER to continue, or 0 to exit: ").strip()
    return choice != "0"

def choose_action():
    print("\nWhat would you like to do?")
    print("0. Exit")
    print("1. Stop")
    print("2. Restart")
    print("3. Rebuild (docker compose build --remove-orphans && up -d)")
    return input("--> ").strip()

def run_tasks(task_list, rebuild=False):
    print("\n Pending tasks:")
    for action, (name, image) in task_list:
        print(f"- {action.upper()} → {name} ({image})")

    if rebuild:
        print("- REBUILD → docker compose build --remove-orphans && up -d")

    confirm = input("Do you want to execute these tasks? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Execution cancelled.")
        sys.exit(0)

    for action, (name, _) in task_list:
        if action == "stop":
            print(f"→ Stopping: {name}")
            res = subprocess.run(["docker", "stop", name])
            if res.returncode != 0:
                print(f"⚠️ Failed to stop container: {name}")
        elif action == "restart":
            print(f"→ Restarting: {name}")
            res = subprocess.run(["docker", "restart", name])
            if res.returncode != 0:
                print(f"⚠️ Failed to restart container: {name}")

    if rebuild:
        try:
            with open("docker-compose.yml", "r"):
                print("→ Rebuilding via Docker Compose...")
                subprocess.run(["docker", "compose", "build", "--remove-orphans"], check=True)
                subprocess.run(["docker", "compose", "up", "-d"], check=True)
        except FileNotFoundError:
            print("❌ docker-compose.yml not found in current directory.")
        except subprocess.CalledProcessError:
            print("❌ Docker Compose rebuild failed.")

    show_current_containers()

def show_current_containers():
    print("\n Currently running containers:")
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}:::{{.Image}}"],
        capture_output=True, text=True
    )
    containers = result.stdout.strip().split("\n") if result.stdout else []

    if not containers or containers == ['']:
        print("⚠️  No containers are currently running.")
    else:
        for line in containers:
            if ":::" in line:
                name, image = line.split(":::")
                print(f"- {name.strip()} ({image.strip()})")

def main():
    all_containers = get_running_containers()
    if not all_containers:
        print("⚠️ No running containers found.")
        sys.exit(0)

    task_list = []
    used_indices = set()

    while True:
        selected = select_containers(all_containers, used_indices)
        if not confirm_selection(selected):
            print("Exiting without executing any tasks.")
            sys.exit(0)

        action = choose_action()
        if action == "0":
            print("Exiting without executing any tasks.")
            sys.exit(0)
        elif action == "1":
            for item in selected:
                task_list.append(("stop", item))
        elif action == "2":
            for item in selected:
                task_list.append(("restart", item))
        elif action == "3":
            task_list.append(("rebuild", ("compose-project", "docker-compose")))
        else:
            print("❌ Unknown action. Starting over.")
            continue

        cont = input("Do you want to add another task? (y/n): ").strip().lower()
        if cont != "y":
            break

    # Separate rebuild flag
    rebuild = any(task[0] == "rebuild" for task in task_list)
    task_list = [task for task in task_list if task[0] != "rebuild"]

    run_tasks(task_list, rebuild)

if __name__ == "__main__":
    main()
