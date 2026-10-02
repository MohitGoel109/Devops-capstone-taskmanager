# Kubernetes Deployment

The local deployment uses kind and the `capstone` cluster. The kind config maps host ports 30080, 30300, and 30900 for the app and monitoring services.

Create the cluster, load the local app image, and create the namespace:

```powershell
kind create cluster --name capstone --config k8s/kind-config.yaml
kind load docker-image taskmanager:local --name capstone
kubectl --context kind-capstone apply -f k8s/namespace.yaml
```

Create the real Kubernetes Secret interactively in PowerShell. Do not apply `k8s/secret.example.yaml`; it contains placeholders only. The real `k8s/secret.yaml` path is git-ignored.

```powershell
$passwordSecure = Read-Host "Postgres password" -AsSecureString
$keySecure = Read-Host "Flask SECRET_KEY" -AsSecureString
$password = [System.Net.NetworkCredential]::new("", $passwordSecure).Password
$secretKey = [System.Net.NetworkCredential]::new("", $keySecure).Password
$escapedPassword = [uri]::EscapeDataString($password)
$databaseUrl = "postgresql+psycopg2://taskmanager:$escapedPassword@postgres:5432/taskmanager"
kubectl --context kind-capstone create secret generic taskmanager-secret -n taskmanager `
  --from-literal="POSTGRES_PASSWORD=$password" `
  --from-literal="SECRET_KEY=$secretKey" `
  --from-literal="DATABASE_URL=$databaseUrl"
Remove-Variable passwordSecure,keySecure,password,secretKey,escapedPassword,databaseUrl
```

Deploy PostgreSQL and the app, then verify the namespace resources and health endpoint:

```powershell
kubectl --context kind-capstone apply -f k8s/postgres.yaml -f k8s/taskmanager.yaml
kubectl --context kind-capstone rollout status deployment/postgres -n taskmanager
kubectl --context kind-capstone rollout status deployment/taskmanager -n taskmanager
kubectl --context kind-capstone get pods,pvc,service -n taskmanager
curl.exe -fS http://localhost:30080/health
```

Demonstrate scaling and a rolling image update with rollback:

```powershell
kubectl --context kind-capstone scale deployment/taskmanager --replicas=4 -n taskmanager
kubectl --context kind-capstone rollout status deployment/taskmanager -n taskmanager
kubectl --context kind-capstone scale deployment/taskmanager --replicas=2 -n taskmanager
docker build -f docker/Dockerfile -t taskmanager:v2 .
kind load docker-image taskmanager:v2 --name capstone
kubectl --context kind-capstone set image deployment/taskmanager taskmanager=taskmanager:v2 -n taskmanager
kubectl --context kind-capstone rollout status deployment/taskmanager -n taskmanager
kubectl --context kind-capstone rollout undo deployment/taskmanager -n taskmanager
kubectl --context kind-capstone rollout status deployment/taskmanager -n taskmanager
```

For the PVC persistence check, create a probe row in PostgreSQL, delete the PostgreSQL pod, wait for its replacement, and query the row again:

```powershell
kubectl --context kind-capstone exec -n taskmanager deployment/postgres -- psql -U taskmanager -d taskmanager -c "CREATE TABLE k8s_volume_probe (value text PRIMARY KEY); INSERT INTO k8s_volume_probe VALUES ('persisted');"
kubectl --context kind-capstone delete pod -n taskmanager -l app=postgres
kubectl --context kind-capstone rollout status deployment/postgres -n taskmanager
kubectl --context kind-capstone exec -n taskmanager deployment/postgres -- psql -U taskmanager -d taskmanager -Atc "SELECT value FROM k8s_volume_probe;"
```