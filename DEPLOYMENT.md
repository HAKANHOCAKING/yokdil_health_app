# Deployment Guide

## Backend Deployment (FastAPI)

### Production Checklist

1. **Environment Variables**
```bash
# Update .env with production values
DATABASE_URL=postgresql://user:pass@prod-db:5432/yokdil_db
SECRET_KEY=<generate-strong-secret-min-32-chars>
MINIO_ENDPOINT=s3.amazonaws.com  # Or your S3 endpoint
OPENAI_API_KEY=<your-production-key>
ALLOWED_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
```

2. **Database Migration**
```bash
cd backend
alembic upgrade head
```

3. **Run with Gunicorn (Production)**
```bash
pip install gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment Options

#### AWS (Recommended)
- **Backend**: AWS Elastic Beanstalk or ECS
- **Database**: AWS RDS (PostgreSQL)
- **Storage**: AWS S3
- **Caching**: AWS ElastiCache (Redis)

#### DigitalOcean
- **Backend**: App Platform
- **Database**: Managed PostgreSQL
- **Storage**: Spaces (S3-compatible)

#### Heroku
```bash
# Install Heroku CLI and login
heroku create yokdil-health-api

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-api-key

# Deploy
git push heroku main
```

## Flutter App Deployment

### Android

1. **Update app signing**
```bash
cd flutter_app
keytool -genkey -v -keystore ~/yokdil-keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias yokdil
```

2. **Configure key.properties**
```properties
# android/key.properties
storePassword=<password>
keyPassword=<password>
keyAlias=yokdil
storeFile=<path-to-keystore>
```

3. **Build APK/AAB**
```bash
flutter build apk --release
# or for Google Play
flutter build appbundle --release
```

4. **Upload to Google Play Console**
- Create app in Google Play Console
- Upload AAB file
- Complete store listing
- Submit for review

### iOS

1. **Prerequisites**
- Apple Developer account ($99/year)
- Xcode on macOS
- Provisioning profiles and certificates

2. **Update Bundle ID**
```bash
# In ios/Runner.xcodeproj
# Update Bundle Identifier to: com.yourcompany.yokdil
```

3. **Build IPA**
```bash
flutter build ios --release
# Then archive and upload via Xcode
```

4. **Upload to App Store Connect**
- Open project in Xcode
- Product > Archive
- Upload to App Store Connect
- Submit for review

### Web (Admin Panel)

1. **Build for web**
```bash
cd admin_web
flutter build web --release
```

2. **Deploy to hosting**
```bash
# Firebase Hosting
firebase init hosting
firebase deploy

# Netlify
netlify deploy --dir=build/web --prod

# Vercel
vercel --prod
```

## Database Backup

### Automated Backups
```bash
# Daily backup cron job
0 2 * * * pg_dump -U postgres yokdil_db | gzip > /backups/yokdil_$(date +\%Y\%m\%d).sql.gz
```

### Manual Backup
```bash
# Backup
pg_dump -U postgres -h localhost yokdil_db > yokdil_backup.sql

# Restore
psql -U postgres -h localhost -d yokdil_db < yokdil_backup.sql
```

## Monitoring & Logging

### Sentry Integration (Recommended)
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Checks
```bash
# Check API health
curl https://api.yourdomain.com/health

# Expected response:
# {"status":"healthy","service":"YÖKDİL Health App","version":"1.0.0"}
```

## Scaling Considerations

### Backend Scaling
- Use load balancer (AWS ALB, Nginx)
- Horizontal scaling with multiple workers
- Connection pooling for database
- Redis for caching frequently accessed data

### Database Optimization
- Add indexes on frequently queried columns
- Use materialized views for analytics
- Implement read replicas for heavy read operations

### CDN for Assets
- Use CloudFlare or AWS CloudFront
- Serve static files (PDFs, images) from CDN
- Enable caching headers

## Security Hardening

1. **SSL/TLS Certificates**
```bash
# Use Let's Encrypt (free)
certbot --nginx -d api.yourdomain.com
```

2. **Firewall Rules**
```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

3. **Rate Limiting**
- Implemented via SlowAPI in backend
- Additional protection via CloudFlare

4. **CORS Configuration**
```python
# Only allow production domains
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

## Cost Estimation (Monthly)

### Minimal Setup (Small Scale)
- AWS EC2 t3.small: $15
- AWS RDS db.t3.micro: $15
- AWS S3: $5
- Domain + SSL: $2
- **Total: ~$40/month**

### Medium Scale (10K+ users)
- AWS ECS (2 instances): $60
- AWS RDS db.t3.medium: $65
- AWS S3 + CloudFront: $20
- Redis: $15
- **Total: ~$160/month**

### Enterprise Scale (100K+ users)
- AWS ECS (4+ instances): $200
- AWS RDS db.r5.xlarge: $300
- AWS S3 + CloudFront: $50
- Redis Cluster: $50
- OpenAI API: $100-500 (based on usage)
- **Total: ~$700-1100/month**

## CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to AWS
        run: |
          # Deploy script here
  
  deploy-flutter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - name: Build and deploy
        run: |
          flutter build apk --release
          # Upload to Play Store
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
# Check connectivity
psql -h <host> -U <user> -d <database>

# Verify environment variables
echo $DATABASE_URL
```

2. **CORS Errors**
```python
# Add domain to ALLOWED_ORIGINS in backend/.env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

3. **Flutter Build Errors**
```bash
# Clean and rebuild
flutter clean
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter build apk --release
```

## Support & Maintenance

- Monitor error rates via Sentry
- Review logs daily
- Update dependencies monthly
- Security patches: immediate
- Feature updates: bi-weekly sprint cycle

---

For questions or issues, contact: [your-email@domain.com]
