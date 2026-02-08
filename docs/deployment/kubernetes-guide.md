# NSS v3.1.1 -- Kubernetes Deployment Guide

[Back to Main Documentation](../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

This guide covers deploying NSS v3.1.1 on Kubernetes, the recommended deployment method for enterprise environments. The deployment uses GPU-enabled nodes and pod anti-affinity for high availability.

---

## Prerequisites

- Kubernetes cluster (v1.25+)
- GPU-enabled nodes with NVIDIA A100 (40GB) or equivalent
- NVIDIA device plugin for Kubernetes installed
- `kubectl` configured and authenticated
- Container images available:
  - `nss/mars:3.1.1`
  - `nss/gateway:3.1.1`
  - `nss/governance:3.1.1`

---

## Step 1: Create the Namespace

```bash
kubectl create namespace ai-infrastructure
```

---

## Step 2: Deploy NSS Guardian Shield

Apply the following deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nss-guardian-shield
  namespace: ai-infrastructure
spec:
  replicas: 3
  selector:
    matchLabels:
      app: guardian-shield
  template:
    metadata:
      labels:
        app: guardian-shield
    spec:
      containers:
      - name: mars
        image: nss/mars:3.1.1
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 8Gi
          requests:
            nvidia.com/gpu: 1
            memory: 8Gi
      - name: gateway
        image: nss/gateway:3.1.1
        ports:
        - containerPort: 11337
        livenessProbe:
          httpGet:
            path: /health
            port: 11337
          initialDelaySeconds: 30
          periodSeconds: 10
      - name: governance
        image: nss/governance:3.1.1
        ports:
        - containerPort: 11339
      nodeSelector:
        node-type: gpu-enabled
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - guardian-shield
              topologyKey: kubernetes.io/hostname
```

Save to `nss-deployment.yaml` and apply:

```bash
kubectl apply -f nss-deployment.yaml
```

---

## Step 3: Verify Deployment

```bash
kubectl get pods -n ai-infrastructure
kubectl get deployments -n ai-infrastructure
```

Check that all 3 replicas are running and the liveness probe on port 11337 is passing:

```bash
kubectl describe deployment nss-guardian-shield -n ai-infrastructure
```

---

## Step 4: Expose the Gateway (Optional)

If the Gateway needs to be accessible outside the cluster, create a Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nss-gateway
  namespace: ai-infrastructure
spec:
  selector:
    app: guardian-shield
  ports:
  - port: 11337
    targetPort: 11337
  type: ClusterIP
```

For external access, use an Ingress controller or LoadBalancer type depending on your cluster configuration. Internal-only access via ClusterIP is recommended for security.

---

## Scaling Recommendations

| Configuration | Replicas | Throughput | Latency (p95) | Notes |
|---|---|---|---|---|
| Minimum | 3 | 7,500 RPS | 540ms | Recommended starting point |
| Standard | 5 | 12,500 RPS | 545ms | For sustained production loads |
| Enterprise | 10 | 25,000 RPS | 560ms | For peak traffic handling |

### Auto-Scaling

Configure a Horizontal Pod Autoscaler to scale between 3 and 10 replicas based on CPU or custom metrics:

```bash
kubectl autoscale deployment nss-guardian-shield \
  --namespace ai-infrastructure \
  --min=3 --max=10 \
  --cpu-percent=70
```

---

## Monitoring

The Metrics endpoint runs on Port 11340 within each pod. Configure your Prometheus instance to scrape metrics:

```yaml
- job_name: 'nss-metrics'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names:
      - ai-infrastructure
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    regex: guardian-shield
    action: keep
  - source_labels: [__meta_kubernetes_pod_ip]
    target_label: __address__
    replacement: ${1}:11340
```

---

## Key Notes

- Each MARS container requires 1 NVIDIA GPU and 8Gi of memory.
- Pod anti-affinity ensures replicas are distributed across different nodes for high availability.
- The `nodeSelector` requires nodes to be labeled with `node-type: gpu-enabled`.
- The liveness probe checks the `/health` endpoint on port 11337 every 10 seconds after an initial 30-second delay.

---

## References

- [6-Layer Defense Architecture](../architecture/6-layer-defense.md)
- [Port Schema](../architecture/port-schema.md)
- [Scaling Guide](scaling-guide.md)
- [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)
