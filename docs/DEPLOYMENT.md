# Deployment Guide

This guide covers deploying the Freqtrade trading bot using Docker for production environments.

## Deployment Options

### 1. Docker Deployment (Recommended)

Docker provides:
- **Consistent environment** across development and production
- **Easy scaling** and management
- **Isolation** from host system
- **Simplified updates** and rollbacks

### 2. Direct Python Deployment

For advanced users who prefer direct Python installation.

## Docker Deployment

### 1. Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM
- 10GB free disk space

### 2. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start paper trading
docker-compose up freqtrade-dry-run

# Start live trading (after configuration)
docker-compose up freqtrade

# Run in background
docker-compose up -d freqtrade-dry-run
```

### 3. Configuration for Production

#### Environment Variables

Create a production `.env` file:

```bash
# Production environment variables
MEXC_API_KEY=your_production_api_key
MEXC_SECRET_KEY=your_production_secret_key
MEXC_PASSPHRASE=your_production_passphrase

# Database configuration
DATABASE_URL=sqlite:///user_data/tradesv3.sqlite

# Logging
LOG_LEVEL=INFO

# Risk management
MAX_OPEN_TRADES=3
STAKE_AMOUNT=100
STAKE_CURRENCY=USDT
```

#### Production Configuration

Update `config/config.json` for production:

```json
{
    "dry_run": false,
    "exchange": {
        "name": "mexc",
        "key": "${MEXC_API_KEY}",
        "secret": "${MEXC_SECRET_KEY}"
    },
    "telegram": {
        "enabled": true,
        "token": "${TELEGRAM_TOKEN}",
        "chat_id": "${TELEGRAM_CHAT_ID}"
    },
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "username": "${API_USERNAME}",
        "password": "${API_PASSWORD}"
    }
}
```

### 4. Docker Compose Services

#### Main Trading Service

```yaml
freqtrade:
  build: .
  container_name: traderbot
  restart: unless-stopped
  volumes:
    - ./user_data:/app/user_data
    - ./config:/app/config
    - ./strategies:/app/strategies
    - ./logs:/app/logs
  environment:
    - FREQTRADE_CONFIG=/app/config/config.json
  env_file:
    - .env
  ports:
    - "8080:8080"
  command: freqtrade trade --config config/config.json
```

#### Paper Trading Service

```yaml
freqtrade-dry-run:
  build: .
  container_name: traderbot-dry-run
  restart: unless-stopped
  volumes:
    - ./user_data:/app/user_data
    - ./config:/app/config
    - ./strategies:/app/strategies
    - ./logs:/app/logs
  environment:
    - FREQTRADE_CONFIG=/app/config/config_dry_run.json
  env_file:
    - .env
  ports:
    - "8081:8080"
  command: freqtrade trade --config config/config_dry_run.json
```

### 5. Production Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 2. Deploy Application

```bash
# Clone repository
git clone <repository-url> traderbot
cd traderbot

# Create production environment
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose build
docker-compose up -d freqtrade-dry-run
```

#### 3. Monitor Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs freqtrade-dry-run

# Follow logs in real-time
docker-compose logs -f freqtrade-dry-run

# Check container health
docker-compose exec freqtrade-dry-run freqtrade status
```

### 6. Scaling and Management

#### Multiple Strategy Instances

```yaml
# docker-compose.yml
services:
  strategy-1:
    build: .
    container_name: traderbot-strategy-1
    restart: unless-stopped
    volumes:
      - ./user_data:/app/user_data
      - ./config:/app/config
      - ./strategies:/app/strategies
    environment:
      - FREQTRADE_CONFIG=/app/config/config_strategy_1.json
    command: freqtrade trade --config config/config_strategy_1.json

  strategy-2:
    build: .
    container_name: traderbot-strategy-2
    restart: unless-stopped
    volumes:
      - ./user_data:/app/user_data
      - ./config:/app/config
      - ./strategies:/app/strategies
    environment:
      - FREQTRADE_CONFIG=/app/config/config_strategy_2.json
    command: freqtrade trade --config config/config_strategy_2.json
```

#### Load Balancing

```yaml
# nginx.conf
upstream freqtrade_api {
    server freqtrade:8080;
    server freqtrade-dry-run:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://freqtrade_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Cloud Deployment

### 1. AWS EC2 Deployment

#### Launch EC2 Instance

```bash
# Create security group
aws ec2 create-security-group --group-name freqtrade-sg --description "Freqtrade trading bot"

# Add inbound rules
aws ec2 authorize-security-group-ingress --group-name freqtrade-sg --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name freqtrade-sg --protocol tcp --port 8080 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --instance-type t3.medium --security-groups freqtrade-sg --key-name your-key
```

#### Deploy Application

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy application
git clone <repository-url> traderbot
cd traderbot
docker-compose up -d
```

### 2. Google Cloud Platform

#### Create VM Instance

```bash
# Create instance
gcloud compute instances create freqtrade-bot \
    --image-family ubuntu-2004-lts \
    --image-project ubuntu-os-cloud \
    --machine-type e2-medium \
    --zone us-central1-a

# Configure firewall
gcloud compute firewall-rules create allow-freqtrade \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0
```

### 3. DigitalOcean Droplet

#### Create Droplet

```bash
# Create droplet
doctl compute droplet create freqtrade-bot \
    --image ubuntu-20-04-x64 \
    --size s-1vcpu-2gb \
    --region nyc1 \
    --ssh-keys your-ssh-key-id
```

## Monitoring and Logging

### 1. Log Management

#### Centralized Logging

```yaml
# docker-compose.yml
services:
  freqtrade:
    # ... existing configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Log Rotation

```bash
# /etc/logrotate.d/freqtrade
/var/lib/docker/containers/*/freqtrade*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### 2. Health Monitoring

#### Health Checks

```bash
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "freqtrade", "--version"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### Monitoring Script

```bash
#!/bin/bash
# monitor.sh

# Check if container is running
if ! docker-compose ps | grep -q "Up"; then
    echo "Container is down, restarting..."
    docker-compose restart
fi

# Check API endpoint
if ! curl -f http://localhost:8080/api/v1/ping > /dev/null 2>&1; then
    echo "API is not responding"
    exit 1
fi
```

### 3. Alerting

#### Telegram Notifications

```json
{
    "telegram": {
        "enabled": true,
        "token": "${TELEGRAM_TOKEN}",
        "chat_id": "${TELEGRAM_CHAT_ID}",
        "balance_dust_level": 0.01,
        "reload": true,
        "allow_custom_messages": true
    }
}
```

#### Email Notifications

```bash
# Install mailutils
sudo apt install mailutils

# Configure SMTP
echo "smtp.gmail.com:587" >> /etc/postfix/main.cf
```

## Backup and Recovery

### 1. Data Backup

#### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/freqtrade"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup user data
tar -czf $BACKUP_DIR/user_data_$DATE.tar.gz user_data/

# Backup configuration
cp -r config/ $BACKUP_DIR/config_$DATE/

# Backup database
cp user_data/tradesv3.sqlite $BACKUP_DIR/tradesv3_$DATE.sqlite

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

#### Cron Job

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

### 2. Recovery Procedures

#### Restore from Backup

```bash
# Stop services
docker-compose down

# Restore data
tar -xzf /backups/freqtrade/user_data_20231201_020000.tar.gz

# Restore configuration
cp -r /backups/freqtrade/config_20231201_020000/* config/

# Start services
docker-compose up -d
```

## Security Considerations

### 1. Container Security

#### Non-root User

```dockerfile
# Dockerfile
RUN useradd --create-home --shell /bin/bash ${FREQTRADE_USER}
USER ${FREQTRADE_USER}
```

#### Resource Limits

```yaml
# docker-compose.yml
services:
  freqtrade:
    # ... existing configuration
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 2. Network Security

#### Firewall Configuration

```bash
# UFW configuration
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp
sudo ufw enable
```

#### SSL/TLS

```yaml
# nginx-ssl.conf
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://freqtrade:8080;
    }
}
```

### 3. API Security

#### Authentication

```json
{
    "api_server": {
        "enabled": true,
        "username": "admin",
        "password": "secure_password",
        "jwt_secret_key": "very_secure_secret_key"
    }
}
```

## Performance Optimization

### 1. Resource Optimization

#### Memory Management

```yaml
# docker-compose.yml
services:
  freqtrade:
    # ... existing configuration
    environment:
      - PYTHONUNBUFFERED=1
      - FREQTRADE_CONFIG=/app/config/config.json
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

#### CPU Optimization

```bash
# Set CPU affinity
docker run --cpuset-cpus="0,1" traderbot
```

### 2. Database Optimization

#### PostgreSQL Configuration

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: freqtrade
      POSTGRES_USER: freqtrade
      POSTGRES_PASSWORD: freqtrade
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs freqtrade
   
   # Check configuration
   docker-compose config
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Increase memory limits
   # Update docker-compose.yml
   ```

3. **Network Issues**
   ```bash
   # Check network connectivity
   docker-compose exec freqtrade ping google.com
   
   # Check port binding
   netstat -tlnp | grep 8080
   ```

### Debugging Commands

```bash
# Container shell access
docker-compose exec freqtrade bash

# Check Freqtrade status
docker-compose exec freqtrade freqtrade status

# View configuration
docker-compose exec freqtrade freqtrade show-config

# Test strategy
docker-compose exec freqtrade freqtrade backtesting --strategy MomentumStrategy
```

## Maintenance

### 1. Regular Updates

#### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

#### Update Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Rebuild with new dependencies
docker-compose build
```

### 2. Monitoring

#### System Monitoring

```bash
# Monitor system resources
htop
iostat -x 1
df -h
```

#### Application Monitoring

```bash
# Monitor container resources
docker stats

# Monitor logs
docker-compose logs -f
```

## Support and Resources

### Documentation

- **Freqtrade Documentation**: https://www.freqtrade.io/
- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/

### Community

- **Freqtrade Discord**: https://discord.gg/freqtrade
- **Docker Community**: https://forums.docker.com/
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/freqtrade
