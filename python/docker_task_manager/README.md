# Docker Task Manager

An interactive CLI script for managing Docker containers.  
Allows you to select running containers and batch operations like stop, restart, or full project rebuild (via Docker Compose).

## Features

- Lists all currently running containers
- Interactive selection by number
- Prevents selecting the same container twice
- Task queuing: define multiple actions before execution
- Supports:
  - Stop
  - Restart
  - Rebuild (docker compose build + up with orphan removal)
- Final summary of currently running containers

## Requirements

- Python 3.6+
- Docker CLI
- (Optional) Docker Compose v2+

Ensure your user is part of the `docker` group or run the script with `sudo`.

## Usage

```bash
python3 docker_task_manager.py
```