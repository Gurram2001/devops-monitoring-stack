# Complete Guide: Flask WebApp with GitHub Actions, Docker, Azure Deployment & Monitoring

This repository contains a Flask-based web application with CI/CD pipeline configured through GitHub Actions, Docker, and deployment to Azure VM with prometheus, grafana monitoring

## Getting Started

### Clone the Repository
```bash
git clone https://github.com/gurram2001/webapp.git
cd webapp
```

## CI/CD Configuration

### Secrets to Add in GitHub Repository
Go to your GitHub repo → Settings → Secrets and Variables → Actions and add:

| Name | Description |
|------|-------------|
| DOCKER_USERNAME | Your Docker Hub username |
| DOCKER_PASSWORD | Your Docker Hub password or token |
| VM_HOST | Public IP of your Azure VM |
| VM_USER | SSH username (usually azureuser) |
| VM_KEY | Your private SSH key |
### Note: Update VM_USER, VM_HOST, VM password accordingly
## Set Up Azure VM

### Create an Azure VM (Ubuntu)
1. Open port 22 (SSH) and 80 (HTTP) in Network Security Group (NSG)
2. SSH into VM and install Docker:
```bash
sudo apt install docker.io
sudo usermod -aG docker azureuser
```
3. Logout VM and Login again
4. CHeck with below command
```bash
docker run hello-world
```

## Test the Full Flow
1. Commit and push code → GitHub Action triggers
2. Image builds → pushed to Docker Hub
3. Azure VM pulls latest image → runs container
4. Open browser: http://<Azure-VM-IP> to see your app

## Monitoring Setup

### Step 1: SSH into your Azure VM
```bash
ssh azureuser@<your-azure-vm-ip>
```

### Step 2: Go to prometheus folder
```bash
cd prometheus
```

### Step 3: Create Prometheus config file
Observe file named `prometheus.yml`: 
Importance of prometheus.yml: 
1. Its is main configuration file for prometheus
2. Prometheus doesn't magically know what to monitor - it needs this configure to define:
   * Which target(apps/container/hosts) to scrape
   * Howfrequently to scrape them
3. Tells prometheus what to monitor.
   
Thus file place crucial role. It helps 
See example from my prometheus folder
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'flask-app'
    static_configs:
      - targets: ['web-app:5000']
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:9323']
```
### Step 4: Docker Network
Docker network helps the containers in docker to communicate with each, this docker network is used among all. It is used of service discovery, as containers can reach each other by name.
Create docker network if not created. It is created in `Github Actions` ci-cd pipeline. Check with this command. 
```bash
docker network ls
```
You will output like
```
NETWORK ID     NAME           DRIVER    SCOPE
2c0c2e5e7a0b   bridge         bridge    local
d38e6e1e8abc   host           host      local
8f3e7f6ef02f   none           null      local
3c1e6fc7d0de   devops-net     bridge    local
```
If it is not created, create one
```bash
docker network create docker-net
```
### Step 5: Run Prometheus and Grafana in Docker
```bash
# Run Prometheus
docker run -d --name prometheus \
  --network devops-net \
  -p 9090:9090 \
  -v ~/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Run Grafana
docker run -d --name grafana \
  --network devops-net \
  -p 3000:3000 \
  grafana/grafana
```

### Step 6: (Optional) Install Docker Metrics Exporter
Prometheus needs metrics from Docker – install this exporter:
```bash
docker run -d --name cadvisor \
  --network devops-net \
  -p 9323:9323 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  google/cadvisor:latest
```

### Step 7: Access Grafana on Browser
Open: http://<your-azure-vm-ip>:3000

Default login:
- User: admin
- Password: admin (you'll be prompted to change)

Confirm Everything Works
1. http://<vm-ip>:5000/metrics → Should show Flask app metrics
2. http://<vm-ip>:9090/targets → Prometheus should show flask-app:5000 and cadvisor:9323 as UP
3. http://<vm-ip>:3000 → Grafana dashboard

### Step 8: Connect Prometheus as Grafana Data Source
In Grafana:
1. Go to Settings → Data Sources → Add Prometheus
2. URL: http://<az-vm-ip>:9090
3. Click Save & Test

### Step 9: Import a Dashboard
1. Go to + → Import
2. Paste Dashboard ID: 193 (Docker metrics)
3. Click Load → Select Prometheus as data source → Import

## Notes

### Understanding Prometheus Configuration
- **prometheus.yml**: This configuration file tells Prometheus what to monitor (targets) and how often (scrape interval)
  - The `scrape_interval` defines how frequently Prometheus collects metrics (15s = every 15 seconds)
  - The `scrape_configs` section defines what services to monitor and where to find them
  - The `targets` field specifies the host:port where metrics can be collected

### About Exporters
- Exporters are components that collect and expose metrics from various services in a format Prometheus can understand
- **cAdvisor** (Container Advisor) is an exporter that collects container metrics from Docker
- The exporter exposes Docker metrics on port 9323, which Prometheus then scrapes based on the configuration

