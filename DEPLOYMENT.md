# 🚀 Deployment Guide

Complete guide for deploying the Demand Forecasting application to various platforms.

## Table of Contents
1. [Docker Deployment](#docker-deployment)
2. [Render Deployment](#render-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [AWS EC2 Deployment](#aws-ec2-deployment)
5. [Production Considerations](#production-considerations)

---

## 🐳 Docker Deployment

### Prerequisites
- Docker installed on your system
- Docker Hub account (optional, for pushing images)

### Build Docker Image

```bash
cd demand_forecasting
docker build -t demand-forecasting:latest .
```

### Run Container Locally

```bash
docker run -d -p 5000:5000 --name demand-app demand-forecasting:latest
```

### Access Application
```
http://localhost:5000
```

### Stop Container
```bash
docker stop demand-app
docker rm demand-app
```

### Push to Docker Hub (Optional)

```bash
docker tag demand-forecasting:latest yourusername/demand-forecasting:latest
docker push yourusername/demand-forecasting:latest
```

---

## ☁️ Render Deployment

### Method 1: Via GitHub

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/demand-forecasting.git
git push -u origin main
```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up or log in

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `demand-forecasting` repository

4. **Configure Service**
   - Name: `demand-forecasting`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Instance Type: Free or Starter

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Access via provided URL

### Method 2: Via Docker

1. **Build and push Docker image**
```bash
docker build -t yourusername/demand-forecasting .
docker push yourusername/demand-forecasting
```

2. **Create Web Service on Render**
   - Select "Docker" as environment
   - Provide Docker image URL
   - Set port to 5000

---

## 🟣 Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Installation

**Windows:**
Download from https://devcenter.heroku.com/articles/heroku-cli

**Mac:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Deployment Steps

1. **Login to Heroku**
```bash
heroku login
```

2. **Create Heroku App**
```bash
heroku create your-demand-forecasting-app
```

3. **Verify Files**
Ensure these files exist:
- `Procfile` (contains: `web: python app.py`)
- `runtime.txt` (contains: `python-3.10.12`)
- `requirements.txt`

4. **Initialize Git (if not done)**
```bash
git init
git add .
git commit -m "Initial commit"
```

5. **Deploy to Heroku**
```bash
git push heroku main
```

Or if using master branch:
```bash
git push heroku master
```

6. **Open Application**
```bash
heroku open
```

### Heroku Commands

**View logs:**
```bash
heroku logs --tail
```

**Restart app:**
```bash
heroku restart
```

**Scale dynos:**
```bash
heroku ps:scale web=1
```

**Set environment variables:**
```bash
heroku config:set SECRET_KEY=your-secret-key
```

---

## 🟠 AWS EC2 Deployment

### 1. Launch EC2 Instance

1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Choose Ubuntu Server 22.04 LTS
4. Select t2.micro (free tier eligible)
5. Configure security group:
   - SSH (port 22) - Your IP
   - HTTP (port 80) - Anywhere
   - Custom TCP (port 5000) - Anywhere
6. Create/select key pair
7. Launch instance

### 2. Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx -y
```

### 4. Clone/Upload Project

**Option A: Clone from GitHub**
```bash
git clone https://github.com/yourusername/demand-forecasting.git
cd demand-forecasting
```

**Option B: Upload via SCP**
```bash
scp -i your-key.pem -r demand_forecasting ubuntu@your-ec2-ip:~
```

### 5. Setup Application

```bash
cd demand-forecasting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Run with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 7. Setup as Service (Optional)

Create `/etc/systemd/system/demand-forecasting.service`:

```ini
[Unit]
Description=Demand Forecasting Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/demand-forecasting
Environment="PATH=/home/ubuntu/demand-forecasting/venv/bin"
ExecStart=/home/ubuntu/demand-forecasting/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable demand-forecasting
sudo systemctl start demand-forecasting
sudo systemctl status demand-forecasting
```

### 8. Configure Nginx (Optional)

Create `/etc/nginx/sites-available/demand-forecasting`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/demand-forecasting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Production Considerations

### Security

1. **Change Secret Key**
```python
# In app.py
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')
```

Set environment variable:
```bash
export SECRET_KEY='your-random-secret-key-here'
```

2. **Disable Debug Mode**
```python
# In app.py
app.run(debug=False, host='0.0.0.0', port=5000)
```

3. **Use HTTPS**
   - Get SSL certificate (Let's Encrypt)
   - Configure Nginx with SSL
   - Redirect HTTP to HTTPS

4. **Environment Variables**
Create `.env` file:
```
SECRET_KEY=your-secret-key
FLASK_ENV=production
MAX_CONTENT_LENGTH=16777216
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Load in app.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Performance

1. **Use Production WSGI Server**
   - Gunicorn (recommended)
   - uWSGI
   - Waitress

2. **Enable Caching**
   - Redis for session storage
   - Cache model predictions

3. **Database**
   - Use PostgreSQL/MySQL instead of CSV files
   - Implement proper data persistence

4. **Load Balancing**
   - Use multiple workers
   - Implement load balancer (Nginx, AWS ELB)

### Monitoring

1. **Logging**
```python
import logging
logging.basicConfig(level=logging.INFO)
```

2. **Error Tracking**
   - Sentry
   - Rollbar
   - AWS CloudWatch

3. **Performance Monitoring**
   - New Relic
   - DataDog
   - Prometheus + Grafana

### Backup

1. **Regular Backups**
   - Backup `uploads/` folder
   - Backup `models/` folder
   - Backup database (if using)

2. **Automated Backups**
```bash
# Cron job for daily backup
0 2 * * * tar -czf /backup/demand-forecasting-$(date +\%Y\%m\%d).tar.gz /path/to/demand-forecasting
```

---

## 📊 Cost Estimates

### Free Tier Options
- **Render**: Free tier available (limited resources)
- **Heroku**: Free tier discontinued, starts at $5/month
- **AWS EC2**: t2.micro free for 12 months

### Paid Options
- **Render Starter**: $7/month
- **Heroku Basic**: $7/month
- **AWS EC2 t2.small**: ~$17/month
- **DigitalOcean Droplet**: $6/month

---

## 🆘 Troubleshooting

### Application won't start
- Check logs: `heroku logs --tail` or `docker logs container-name`
- Verify all dependencies installed
- Check port configuration

### Out of memory
- Increase instance size
- Optimize model loading
- Use model caching

### Slow performance
- Use Gunicorn with multiple workers
- Enable caching
- Optimize database queries

---

## ✅ Deployment Checklist

- [ ] Code tested locally
- [ ] Dependencies listed in requirements.txt
- [ ] Secret key changed
- [ ] Debug mode disabled
- [ ] Environment variables configured
- [ ] Database configured (if applicable)
- [ ] Static files configured
- [ ] HTTPS enabled
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Documentation updated

---

**Ready to deploy? Choose your platform and follow the guide above!**
