# ServEase Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the ServEase microservices architecture.

## 📁 Directory Structure

```
kubernetes/
├── namespace.yaml                    # ServEase namespace
├── configmap.yaml                    # Application configuration
├── secrets.yaml                      # Sensitive data (passwords, API keys)
├── persistent-volumes.yaml           # Storage for Redis, RabbitMQ
├── ingress.yaml                      # Ingress routing rules
├── redis/
│   └── deployment.yaml              # Redis cache service
├── rabbitmq/
│   └── deployment.yaml              # RabbitMQ message queue
├── pgadmin/
│   └── deployment.yaml              # PgAdmin database management
├── nginx/
│   ├── configmap.yaml               # Nginx configuration
│   └── deployment.yaml              # Nginx API Gateway
└── microservices/
    ├── authentication-service.yaml   # Authentication microservice
    ├── customer-service.yaml         # Customer management
    ├── employee-service.yaml         # Employee management
    ├── vehicleandproject-service.yaml # Vehicle & Project management
    ├── appointment-service.yaml      # Appointment scheduling
    ├── notification-service.yaml     # Notifications
    ├── admin-service.yaml            # Admin operations
    └── chatbot-service.yaml          # AI Chatbot
```

**Note:** PostgreSQL is not deployed in the cluster. The application uses **AWS RDS PostgreSQL** at `servease.ctaauyqe60k6.eu-north-1.rds.amazonaws.com`.

## 🚀 Prerequisites

1. **Kubernetes Cluster** (one of the following):
   - Minikube (local development)
   - Docker Desktop with Kubernetes
   - Kind (Kubernetes in Docker)
   - Cloud provider (GKE, EKS, AKS)

2. **kubectl** installed and configured

3. **AWS RDS PostgreSQL** - The application uses an external AWS RDS database at:
   - Host: `servease.ctaauyqe60k6.eu-north-1.rds.amazonaws.com`
   - Ensure your Kubernetes cluster can access this RDS instance (configure security groups/network policies)

4. **Docker images** built and pushed to a registry (or available locally):
   ```bash
   # Build all service images
   cd servease-backend
   docker-compose build
   
   # Tag images for your registry (if using remote cluster)
   docker tag servease/authentication-service:latest your-registry/authentication-service:latest
   # Repeat for all services...
   
   # Push to registry (if using remote cluster)
   docker push your-registry/authentication-service:latest
   # Repeat for all services...
   ```

4. **Ingress Controller** (optional but recommended):
   ```bash
   # For Minikube
   minikube addons enable ingress
   
   # For other clusters
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

## 🔧 Configuration

### 1. Update Secrets

**IMPORTANT:** Edit `secrets.yaml` before deployment and replace placeholder values:

```bash
nano kubernetes/secrets.yaml
```

Update these values:
- `DB_PASSWORD`: Strong PostgreSQL password
- `GEMINI_API_KEY`: Your Google Gemini API key
- `JWT_SECRET_KEY`: Strong JWT secret
- Other credentials as needed

### 2. Update Image References

If using a private registry, update image names in all microservice YAML files:

```yaml
# Example: microservices/authentication-service.yaml
image: your-registry/authentication-service:latest
```

Replace `servease/` with your registry URL in:
- `microservices/authentication-service.yaml`
- `microservices/customer-service.yaml`
- `microservices/employee-service.yaml`
- `microservices/vehicleandproject-service.yaml`
- `microservices/appointment-service.yaml`
- `microservices/notification-service.yaml`
- `microservices/admin-service.yaml`
- `microservices/chatbot-service.yaml`

### 3. Configure Domain (Optional)

Edit `ingress.yaml` to set your domain:

```yaml
spec:
  rules:
  - host: servease.local  # Change to your domain
```

For local testing, add to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
```
127.0.0.1 servease.local
```

## 📦 Deployment Steps

### Option 1: Deploy All at Once

```bash
# Navigate to backend directory
cd servease-backend

# Apply all Kubernetes manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/persistent-volumes.yaml
kubectl apply -f kubernetes/redis/
kubectl apply -f kubernetes/rabbitmq/
kubectl apply -f kubernetes/pgadmin/
kubectl apply -f kubernetes/microservices/
kubectl apply -f kubernetes/nginx/
kubectl apply -f kubernetes/ingress.yaml
```

**Note:** PostgreSQL deployment is skipped since the application uses AWS RDS.

### Option 2: Deploy Step by Step

```bash
# 1. Create namespace
kubectl apply -f kubernetes/namespace.yaml

# 2. Create configuration and secrets
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml

# 3. Create persistent storage
kubectl apply -f kubernetes/persistent-volumes.yaml

# 4. Deploy infrastructure services
kubectl apply -f kubernetes/redis/deployment.yaml
kubectl apply -f kubernetes/rabbitmq/deployment.yaml
kubectl apply -f kubernetes/pgadmin/deployment.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=redis -n servease --timeout=120s
kubectl wait --for=condition=ready pod -l app=rabbitmq -n servease --timeout=120s

# Note: PostgreSQL is not deployed - using AWS RDS

# 5. Deploy microservices
kubectl apply -f kubernetes/microservices/authentication-service.yaml
kubectl apply -f kubernetes/microservices/customer-service.yaml
kubectl apply -f kubernetes/microservices/employee-service.yaml
kubectl apply -f kubernetes/microservices/vehicleandproject-service.yaml
kubectl apply -f kubernetes/microservices/appointment-service.yaml
kubectl apply -f kubernetes/microservices/notification-service.yaml
kubectl apply -f kubernetes/microservices/admin-service.yaml
kubectl apply -f kubernetes/microservices/chatbot-service.yaml

# 6. Deploy API Gateway
kubectl apply -f kubernetes/nginx/configmap.yaml
kubectl apply -f kubernetes/nginx/deployment.yaml

# 7. Create Ingress (optional)
kubectl apply -f kubernetes/ingress.yaml
```

## 🔍 Verification

### Check Deployment Status

```bash
# View all resources in servease namespace
kubectl get all -n servease

# Check pod status
kubectl get pods -n servease

# Check services
kubectl get svc -n servease

# Check ingress
kubectl get ingress -n servease
```

### View Logs

```bash
# View logs for a specific service
kubectl logs -f deployment/authentication-service -n servease
kubectl logs -f deployment/customer-service -n servease

# View logs for all pods of a service
kubectl logs -f -l app=appointment-service -n servease
```

### Access Services

```bash
# Port forward to test individual services
kubectl port-forward svc/authentication-service 8001:8001 -n servease
kubectl port-forward svc/nginx-service 8080:80 -n servease

# Access PgAdmin
kubectl port-forward svc/pgadmin-service 5050:80 -n servease
# Then open http://localhost:5050

# Access RabbitMQ Management
kubectl port-forward svc/rabbitmq-service 15672:15672 -n servease
# Then open http://localhost:15672
```

### Get Service URL (if using LoadBalancer)

```bash
# Get external IP for nginx service
kubectl get svc nginx-service -n servease

# For Minikube
minikube service nginx-service -n servease --url
```

## 🧪 Testing

Test the API through the Nginx gateway:

```bash
# Health check
curl http://servease.local/health

# Authentication endpoint
curl -X POST http://servease.local/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Customer endpoint
curl http://servease.local/api/customers/
```

## 📊 Monitoring

### Resource Usage

```bash
# View resource usage
kubectl top nodes
kubectl top pods -n servease

# Describe a pod for detailed info
kubectl describe pod <pod-name> -n servease
```

### Scaling

```bash
# Scale a deployment
kubectl scale deployment authentication-service --replicas=3 -n servease

# Auto-scale based on CPU
kubectl autoscale deployment authentication-service \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n servease
```

## 🔄 Updates

### Rolling Update

```bash
# Update image version
kubectl set image deployment/authentication-service \
  authentication-service=servease/authentication-service:v2 \
  -n servease

# Check rollout status
kubectl rollout status deployment/authentication-service -n servease

# Rollback if needed
kubectl rollout undo deployment/authentication-service -n servease
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap servease-config -n servease

# Restart deployments to pick up changes
kubectl rollout restart deployment/authentication-service -n servease
```

## 🗑️ Cleanup

### Delete All Resources

```bash
# Delete entire namespace (removes everything)
kubectl delete namespace servease

# Or delete selectively
kubectl delete -f kubernetes/microservices/
kubectl delete -f kubernetes/nginx/
kubectl delete -f kubernetes/rabbitmq/
kubectl delete -f kubernetes/redis/
kubectl delete -f kubernetes/pgadmin/
kubectl delete -f kubernetes/persistent-volumes.yaml
kubectl delete -f kubernetes/secrets.yaml
kubectl delete -f kubernetes/configmap.yaml
kubectl delete -f kubernetes/ingress.yaml

# Note: PostgreSQL data in AWS RDS will NOT be deleted
```

## 🛠️ Troubleshooting

### Pod Not Starting

```bash
# Get pod details
kubectl describe pod <pod-name> -n servease

# Check events
kubectl get events -n servease --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n servease
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n servease

# Test internal connectivity
kubectl run -it --rm debug --image=alpine --restart=Never -n servease -- sh
# Inside pod: wget -O- http://authentication-service:8001/health
```

### Database Connection Issues

```bash
# Test AWS RDS connection from a pod
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -n servease -- sh
# Inside pod: psql -h servease.ctaauyqe60k6.eu-north-1.rds.amazonaws.com -U postgres -d servease_authentication

# Check if RDS is accessible (ensure security groups allow traffic from your cluster)
kubectl run -it --rm netcat --image=busybox --restart=Never -n servease -- nc -zv servease.ctaauyqe60k6.eu-north-1.rds.amazonaws.com 5432
```

**Important:** Ensure your Kubernetes cluster's security group or VPC allows outbound traffic to your AWS RDS instance.

### Image Pull Errors

If using a private registry:

```bash
# Create docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n servease

# Add to deployment spec
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
```

## 📝 Notes

- **Database**: Using **AWS RDS PostgreSQL** (external managed database) - no PostgreSQL deployment needed in cluster
- **Network Access**: Ensure your Kubernetes cluster can reach the RDS instance at `servease.ctaauyqe60k6.eu-north-1.rds.amazonaws.com:5432`
- **Security Groups**: Configure AWS security groups to allow inbound traffic from your Kubernetes cluster
- **Local Development**: Use Minikube or Docker Desktop Kubernetes
- **Production**: Use managed Kubernetes (GKE, EKS, AKS) with proper secrets management (Vault, AWS Secrets Manager, etc.)
- **Storage**: Update `persistentVolumeReclaimPolicy` and storage classes based on your environment
- **Security**: In production, use proper SSL/TLS certificates with cert-manager
- **High Availability**: Increase replicas for critical services
- **Monitoring**: Consider adding Prometheus + Grafana for observability

## 🔐 Security Best Practices

1. **Never commit secrets.yaml with real credentials**
2. Use Kubernetes secrets encryption at rest
3. Implement network policies to restrict pod-to-pod communication
4. Use RBAC for access control
5. Scan images for vulnerabilities before deployment
6. Enable Pod Security Policies/Standards
7. Use non-root containers where possible

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
