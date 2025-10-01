# Danov Music Studio - Production Setup Guide

## 🚀 Quick Deployment Steps

### 1. Upload Files to VPS
```bash
# From your local machine
scp -r . nikit@51.75.72.122:/home/nikit/danov-studio/
```

### 2. Setup on VPS
```bash
# SSH into VPS
ssh nikit@51.75.72.122

# Navigate to project directory
cd /home/nikit/danov-studio

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

### 3. Configure Nginx (Optional)
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/danovstudio
sudo ln -s /etc/nginx/sites-available/danovstudio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Setup Systemd Service (Optional)
```bash
# Copy service file
sudo cp danovstudio.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable danovstudio
sudo systemctl start danovstudio
```

## 🔧 Configuration Files

- `production.env` - Environment variables for production
- `requirements.txt` - Python dependencies
- `deploy.sh` - Automated deployment script
- `nginx.conf` - Nginx configuration
- `danovstudio.service` - Systemd service configuration

## 🌐 Access URLs

- **Website**: http://51.75.72.122:8000
- **Admin Panel**: http://51.75.72.122:8000/admin/
- **Admin Login**: admin / admin123

## 🔐 Security Notes

1. Change default admin password immediately
2. Update SECRET_KEY in production.env
3. Replace reCAPTCHA test keys with real ones
4. Setup SSL certificates for HTTPS
5. Configure firewall rules

## 📝 Environment Variables

Copy `production.env` to `.env` on the VPS:
```bash
cp production.env .env
```

## 🚨 Troubleshooting

- Check logs: `tail -f logs/security.log`
- Check service status: `sudo systemctl status danovstudio`
- Check nginx status: `sudo systemctl status nginx`
- Restart service: `sudo systemctl restart danovstudio`
