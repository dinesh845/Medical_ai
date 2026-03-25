# Deployment Guide for Medical AI System

## Quick Start (Development)

### Windows
1. Double-click `run.bat`
2. Wait for the server to start
3. Open browser to http://localhost:5000

### Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

## Manual Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

## Production Deployment

### Using Gunicorn (Linux/Mac)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Using Waitress (Windows)

1. **Install Waitress**
   ```bash
   pip install waitress
   ```

2. **Create production.py**
   ```python
   from waitress import serve
   from app import app
   
   if __name__ == '__main__':
       serve(app, host='0.0.0.0', port=5000)
   ```

3. **Run**
   ```bash
   python production.py
   ```

## Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/images uploads/audio data

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Build and Run
```bash
docker build -t medical-ai .
docker run -p 5000:5000 medical-ai
```

## Environment Variables

Create `.env` file:
```env
FLASK_ENV=production
SECRET_KEY=your-secure-random-secret-key-here
MAX_UPLOAD_SIZE=16777216
```

## Nginx Configuration (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 16M;
}
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set FLASK_ENV=production
- [ ] Use HTTPS (SSL/TLS)
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Regular security updates
- [ ] Secure file uploads
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection

## Performance Optimization

1. **Use Redis for caching**
2. **Enable gzip compression**
3. **Use CDN for static files**
4. **Database query optimization**
5. **Load balancing with multiple workers**

## Monitoring

- Set up logging
- Monitor server resources
- Track API response times
- Monitor error rates
- Set up alerts

## Backup Strategy

- Regular database backups
- Backup uploaded files
- Version control for code
- Disaster recovery plan

## Scaling

### Horizontal Scaling
- Multiple application servers
- Load balancer (Nginx, HAProxy)
- Shared file storage (S3, NFS)
- Distributed caching (Redis)

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Code profiling and optimization

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Kill the process or use different port
```

### Module Not Found
```bash
pip install -r requirements.txt --force-reinstall
```

### Upload Errors
- Check file permissions
- Verify MAX_CONTENT_LENGTH setting
- Ensure upload directories exist

## Support

For issues or questions:
- Check README.md
- Review logs in console
- Check GitHub issues
- Contact: support@mediai.com
