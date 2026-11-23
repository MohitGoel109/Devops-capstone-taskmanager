# Task Manager: End-to-End DevOps Pipeline

End-to-end DevOps pipeline for deploying a cloud-native Task Manager application ("Ronin Task Board"). A Flask app is containerised with Docker, built and tested by Jenkins, deployed to Kubernetes, provisioned with Terraform and Ansible, and monitored with Prometheus and Grafana.

## Features

- User registration, login and logout (hashed passwords)
- Create, edit, complete and delete tasks ("missions")
- Task priority: High, Medium or Low, shown as a colour-coded badge
- JSON REST API with validation (invalid priority returns `400`)
- `/health` endpoint for liveness and readiness probes
- Prometheus metrics exposed by the app
- Automatic schema upgrade: the `priority` column is added to an existing `tasks` table at startup, so rolling updates need no manual migration

## Tools

| Area | Tools |
|---|---|
| Version control | Git, GitHub (feature, develop, main branching) |
| CI/CD | Jenkins, ArgoCD |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes (kind cluster) |
| Configuration management | Ansible |
| Infrastructure as code | Terraform |
| Monitoring | Prometheus, Grafana |
| App stack | Python, Flask, SQLAlchemy, PostgreSQL (SQLite for local runs), pytest |

## Architecture

```
Developer -> GitHub -> Jenkins (test, build image) -> Kubernetes (rolling update)
                                                          |
                              Terraform / Ansible provision and configure
                                                          |
                                         Prometheus -> Grafana (+ alerts)
```

## Folder Structure

```
app/          Application source code (Flask app, templates, static files, tests)
docker/       Dockerfile and docker-compose.yml
jenkins/      Jenkinsfile
k8s/          Kubernetes manifests
ansible/      Playbooks
terraform/    Infrastructure code
monitoring/   Prometheus and Grafana configs (Helm values, ServiceMonitor, alert rules)
docs/         Report, diagrams, screenshots
```

## Getting Started

### Run locally (SQLite)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd app
python app.py
```

Open http://127.0.0.1:5000, register a user and add a task.

### Run with Docker Compose (PostgreSQL)

```bash
docker compose -f docker/docker-compose.yml up --build
```

The app is served on port 5000. Stop it with `docker compose -f docker/docker-compose.yml down`. Do not run Compose and `python app.py` at the same time, because both use port 5000.

### Run tests

```bash
python -m pytest app/tests/test_app.py -v
```

All 9 tests should pass.

## Kubernetes Deployment

```bash
docker build -f docker/Dockerfile -t taskmanager:v2 .
kind load docker-image taskmanager:v2 --name capstone
kubectl --context kind-capstone set image deployment/taskmanager taskmanager=taskmanager:v2 -n taskmanager
kubectl --context kind-capstone rollout status deployment/taskmanager -n taskmanager
```

Rollback:

```bash
kubectl --context kind-capstone rollout undo deployment/taskmanager -n taskmanager
```

## Service Endpoints

| Service | URL |
|---|---|
| Task Manager (Kubernetes) | http://localhost:30080 |
| Grafana | http://localhost:30300 |
| Prometheus | http://localhost:30900 |
| Jenkins | http://localhost:8080 |

## API

All `/api` routes require a logged-in session.

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/tasks` | List your tasks |
| POST | `/api/tasks` | Create a task (`title`, optional `description`, `priority`) |
| GET | `/api/tasks/<id>` | Get one task |
| PUT | `/api/tasks/<id>` | Update title, description, completed or priority |
| DELETE | `/api/tasks/<id>` | Delete a task |

`priority` must be `High`, `Medium` or `Low` (default `Medium`).

## Monitoring

Prometheus and Grafana are installed with the kube-prometheus-stack Helm chart. A ServiceMonitor scrapes the app's metrics and three alert rules are defined. Configs are in `monitoring/`.

## Git Workflow

```
feature/* -> develop -> main
```

Work is done on feature branches, merged into `develop` by pull request, and `develop` is merged into `main` for releases. Only commits on `main` count towards the GitHub contribution graph.

## Documentation

Report, architecture diagrams and screenshots are in `docs/`.
