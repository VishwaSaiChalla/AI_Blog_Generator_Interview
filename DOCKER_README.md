# Docker Deployment Guide for AI Blog Generator with Nginx

This guide explains how to deploy the AI Blog Generator application using Docker with Nginx reverse proxy for production-ready, end-to-end containerized deployment.

## 🐳 Prerequisites

- **Docker** installed and running
- **Docker Compose** installed
- **Git** for cloning the repository

## 📁 Project Structure

```
ai-blog-generator/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container orchestration
├── nginx.conf             # Nginx configuration
├── nginx/ssl/             # SSL certificates directory
├── .dockerignore          # Files to exclude from Docker build
├── requirements.txt       # Python dependencies
├── app.py                # Main Flask application
├── ai_generator.py       # AI blog generation logic
├── seo_fetcher.py        # SEO data fetching
├── templates/            # HTML templates
├── deploy.sh             # Linux/Mac deployment script
├── deploy.bat            # Windows deployment script
└── .env                  # Environment variables (create this)
```

## 🚀 Quick Start

### Option 1: Using Deployment Scripts (Recommended)

#### For Linux/Mac:
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

#### For Windows:
```cmd
# Run deployment
deploy.bat
```

### Option 2: Manual Docker Commands

1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build -d
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   ```

## ⚙️ Configuration

### Environment Variables (.env file)

Create a `.env` file in the project root:

```env
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
```

### Port Configuration

- **Nginx**: Port 80 (HTTP) and 443 (HTTPS)
- **Flask App**: Port 5000 (internal, not exposed)
- **Access**: Use `http://localhost` or `https://localhost`

## 🏗️ Docker Architecture

### Services

- **nginx**: Reverse proxy server (ports 80/443)
- **ai-blog-generator**: Main Flask application (port 5000, internal)
- **redis** (optional): Caching layer (commented out)

### Network Flow

```
Internet → Nginx (80/443) → Flask App (5000)
```

### Volumes

- `./nginx.conf:/etc/nginx/nginx.conf:ro` - Nginx configuration
- `./nginx/ssl:/etc/nginx/ssl:ro` - SSL certificates
- `./generated_posts:/app/generated_posts` - Blog post storage
- `./reviews:/app/reviews` - User reviews storage
- `./blog_posts_db.json:/app/blog_posts_db.json` - Database file

### Networks

- `ai-blog-network`: Isolated network for services

## 🌟 Nginx Features

### Performance Optimizations
- **Gzip compression** for text-based content
- **Static file caching** with long expiration
- **Keep-alive connections** for better performance
- **Buffer optimization** for proxy requests

### Security Features
- **Rate limiting** (30 req/s general, 10 req/s API)
- **Security headers** (XSS protection, CSRF, etc.)
- **Request size limits** (10MB max)
- **Health check endpoint** at `/health`

### SSL/HTTPS Support
- **Port 443** ready for SSL certificates
- **HTTP/2** support when SSL is enabled
- **HSTS headers** for security
- **Modern cipher suites**

## 📊 Monitoring and Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f ai-blog-generator
```

### Check Health
```bash
# Service status
docker-compose ps

# Nginx health check
curl http://localhost/health

# Flask app through Nginx
curl http://localhost/
```

### Scale Services
```bash
# Scale Flask app (Nginx will load balance)
docker-compose up -d --scale ai-blog-generator=3
```

## 🔒 SSL Configuration

### Enable HTTPS

1. **Place SSL certificates:**
   ```bash
   # Copy your certificates to nginx/ssl/
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

2. **Uncomment HTTPS section** in `nginx.conf`

3. **Restart services:**
   ```bash
   docker-compose restart nginx
   ```

### Self-Signed Certificates (Development)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

## 🛠️ Development

### Build Image Only
```bash
docker-compose build
```

### Run in Development Mode
```bash
# Override environment for development
FLASK_ENV=development docker-compose up
```

### Access Container Shell
```bash
# Nginx container
docker-compose exec nginx sh

# Flask container
docker-compose exec ai-blog-generator bash
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 80 already in use:**
   ```bash
   # Check what's using port 80
   sudo lsof -i :80
   
   # Kill process or change port in docker-compose.yml
   ```

2. **Nginx won't start:**
   ```bash
   # Check Nginx logs
   docker-compose logs nginx
   
   # Validate nginx.conf
   docker-compose exec nginx nginx -t
   ```

3. **Flask app not accessible:**
   ```bash
   # Check if Flask is running
   docker-compose logs ai-blog-generator
   
   # Test direct connection
   docker-compose exec nginx wget -qO- http://ai-blog-generator:5000/
   ```

### Reset Everything
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## 🚀 Production Deployment

### Production Considerations

1. **Use proper SSL certificates** (Let's Encrypt, etc.)
2. **Configure domain names** in nginx.conf
3. **Set up monitoring** (Prometheus, Grafana)
4. **Implement logging aggregation**
5. **Use external database services**

### Example Production nginx.conf
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... rest of configuration
}
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Docker Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/docker/)

## 🤝 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify Docker is running: `docker info`
3. Check environment variables in `.env` file
4. Validate Nginx configuration: `docker-compose exec nginx nginx -t`
5. Test health endpoints: `curl http://localhost/health`

---

**Happy Containerizing with Nginx! 🐳✨🚀**
