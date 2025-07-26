# 🚀 دليل النشر الشامل - بوت الوظائف الذكي

## 📋 نظرة عامة

هذا الدليل يوضح جميع طرق نشر بوت الوظائف الذكي على منصات مختلفة، من البيئات المحلية إلى الخدمات السحابية المتقدمة. سنغطي كل خطوة بالتفصيل مع أمثلة عملية وحلول للمشاكل الشائعة.

---

## 🎯 خيارات النشر

### 1. النشر المحلي (Development)
- **الاستخدام**: التطوير والاختبار
- **المتطلبات**: جهاز محلي مع Python
- **التكلفة**: مجاني
- **الاستقرار**: متوسط

### 2. الخوادم الافتراضية (VPS)
- **الاستخدام**: الإنتاج الصغير إلى المتوسط
- **المتطلبات**: خادم Linux مع SSH
- **التكلفة**: $5-50/شهر
- **الاستقرار**: عالي

### 3. المنصات السحابية (PaaS)
- **الاستخدام**: الإنتاج مع سهولة الإدارة
- **المتطلبات**: حساب على المنصة
- **التكلفة**: $0-100/شهر
- **الاستقرار**: عالي جداً

### 4. الحاويات (Containers)
- **الاستخدام**: الإنتاج المتقدم
- **المتطلبات**: معرفة Docker/Kubernetes
- **التكلفة**: متغيرة
- **الاستقرار**: عالي جداً

---

## 🏠 النشر المحلي

### المتطلبات الأساسية

```bash
# التحقق من إصدار Python
python3 --version  # يجب أن يكون 3.8+

# التحقق من pip
pip3 --version

# التحقق من Git
git --version
```

### خطوات النشر

#### 1. تحضير البيئة

```bash
# إنشاء مجلد المشروع
mkdir ~/telegram-jobs-bot
cd ~/telegram-jobs-bot

# استنساخ المشروع
git clone https://github.com/your-username/telegram-jobs-bot.git .

# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows
```

#### 2. تثبيت المتطلبات

```bash
# تحديث pip
pip install --upgrade pip

# تثبيت المتطلبات
pip install -r requirements.txt

# التحقق من التثبيت
pip list
```

#### 3. إعداد قاعدة البيانات

```bash
# إنشاء مشروع Supabase جديد
# 1. اذهب إلى https://supabase.com
# 2. أنشئ حساب جديد
# 3. أنشئ مشروع جديد
# 4. احصل على URL و API Key

# تشغيل SQL Schema
# انسخ محتوى database_schema.sql
# الصقه في SQL Editor في Supabase
# اضغط Run
```

#### 4. إعداد البوت

```bash
# إنشاء بوت جديد مع BotFather
# 1. ابحث عن @BotFather في تليجرام
# 2. أرسل /newbot
# 3. اتبع التعليمات
# 4. احصل على Bot Token
```

#### 5. إعداد متغيرات البيئة

```bash
# نسخ ملف البيئة النموذجي
cp .env.example .env

# تعديل الملف
nano .env
```

```env
# إعدادات البوت
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_ID=123456789

# إعدادات Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# إعدادات البيئة
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

#### 6. اختبار البوت

```bash
# تشغيل الاختبارات
python test_bot.py

# تشغيل البوت
python run_bot.py
```

### إدارة العملية

#### تشغيل البوت في الخلفية

```bash
# استخدام nohup
nohup python main.py > bot.log 2>&1 &

# أو استخدام screen
screen -S telegram-bot
python main.py
# اضغط Ctrl+A ثم D للخروج

# العودة للجلسة
screen -r telegram-bot
```

#### مراقبة البوت

```bash
# عرض السجلات المباشرة
tail -f bot.log

# عرض حالة العملية
ps aux | grep python

# إيقاف البوت
pkill -f "python main.py"
```

---

## 🖥️ النشر على VPS

### اختيار مزود الخدمة

#### الخيارات الشائعة:
- **DigitalOcean**: سهل الاستخدام، $5/شهر
- **Linode**: أداء جيد، $5/شهر
- **Vultr**: خيارات متنوعة، $2.50/شهر
- **AWS EC2**: مرن ولكن معقد، متغير
- **Google Cloud**: قوي ومتقدم، متغير

### إعداد الخادم

#### 1. إنشاء الخادم

```bash
# المواصفات المقترحة:
# - نظام التشغيل: Ubuntu 20.04 LTS
# - الذاكرة: 1GB RAM (الحد الأدنى)
# - التخزين: 25GB SSD
# - المعالج: 1 vCPU
```

#### 2. الاتصال بالخادم

```bash
# الاتصال عبر SSH
ssh root@your-server-ip

# أو باستخدام مفتاح SSH
ssh -i ~/.ssh/your-key.pem root@your-server-ip
```

#### 3. تحديث النظام

```bash
# تحديث قوائم الحزم
apt update

# ترقية النظام
apt upgrade -y

# تثبيت الأدوات الأساسية
apt install -y curl wget git vim htop unzip
```

#### 4. تثبيت Python

```bash
# تثبيت Python 3.9
apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# إنشاء رابط رمزي
ln -sf /usr/bin/python3.9 /usr/bin/python3
ln -sf /usr/bin/python3.9 /usr/bin/python

# التحقق من التثبيت
python3 --version
pip3 --version
```

#### 5. إعداد المستخدم

```bash
# إنشاء مستخدم جديد
adduser botuser

# إضافة المستخدم لمجموعة sudo
usermod -aG sudo botuser

# التبديل للمستخدم الجديد
su - botuser
```

#### 6. نشر البوت

```bash
# إنشاء مجلد المشروع
mkdir ~/telegram-jobs-bot
cd ~/telegram-jobs-bot

# استنساخ المشروع
git clone https://github.com/your-username/telegram-jobs-bot.git .

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt
```

#### 7. إعداد متغيرات البيئة

```bash
# إنشاء ملف البيئة
cp .env.example .env
nano .env
```

#### 8. إعداد خدمة systemd

```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/telegram-jobs-bot.service
```

```ini
[Unit]
Description=Telegram Jobs Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram-jobs-bot
Environment=PATH=/home/botuser/telegram-jobs-bot/venv/bin
ExecStart=/home/botuser/telegram-jobs-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 9. تشغيل الخدمة

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة
sudo systemctl enable telegram-jobs-bot

# تشغيل الخدمة
sudo systemctl start telegram-jobs-bot

# التحقق من الحالة
sudo systemctl status telegram-jobs-bot
```

### إعداد Nginx (اختياري)

```bash
# تثبيت Nginx
sudo apt install -y nginx

# إنشاء ملف التكوين
sudo nano /etc/nginx/sites-available/telegram-jobs-bot
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        return 404;
    }
}
```

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/telegram-jobs-bot /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تشغيل Nginx
sudo systemctl restart nginx
```

### إعداد SSL (اختياري)

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com

# تجديد تلقائي
sudo crontab -e
# أضف هذا السطر:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ☁️ النشر على المنصات السحابية

### Render.com

#### المزايا:
- سهولة الاستخدام
- نشر تلقائي من Git
- SSL مجاني
- قاعدة بيانات PostgreSQL مجانية

#### خطوات النشر:

##### 1. إعداد المستودع

```bash
# إنشاء مستودع Git
git init
git add .
git commit -m "Initial commit"

# رفع إلى GitHub
git remote add origin https://github.com/your-username/telegram-jobs-bot.git
git push -u origin main
```

##### 2. إنشاء خدمة Render

1. اذهب إلى [render.com](https://render.com)
2. سجل الدخول أو أنشئ حساب
3. اضغط "New +" ثم "Web Service"
4. اربط مستودع GitHub
5. اختر المستودع

##### 3. إعدادات النشر

```yaml
Name: telegram-jobs-bot
Environment: Python 3
Region: Oregon (US West)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

##### 4. متغيرات البيئة

```env
BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_USER_ID=your_user_id
ENVIRONMENT=production
LOG_LEVEL=INFO
```

##### 5. إعداد قاعدة البيانات (اختياري)

```bash
# إنشاء قاعدة بيانات PostgreSQL
# في Render Dashboard:
# New + -> PostgreSQL
# Name: telegram-jobs-bot-db
# Database: telegram_jobs_bot
# User: bot_user
```

### Heroku

#### المزايا:
- منصة ناضجة ومستقرة
- إضافات متنوعة
- سهولة التوسع
- دعم ممتاز للـ CI/CD

#### خطوات النشر:

##### 1. تثبيت Heroku CLI

```bash
# على macOS
brew tap heroku/brew && brew install heroku

# على Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# على Windows
# تحميل من https://devcenter.heroku.com/articles/heroku-cli
```

##### 2. تسجيل الدخول

```bash
heroku login
```

##### 3. إنشاء التطبيق

```bash
# إنشاء تطبيق جديد
heroku create telegram-jobs-bot-your-name

# إضافة قاعدة بيانات PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# إضافة Redis (اختياري)
heroku addons:create heroku-redis:hobby-dev
```

##### 4. إعداد متغيرات البيئة

```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_KEY=your_supabase_key
heroku config:set ADMIN_USER_ID=your_user_id
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO
```

##### 5. إعداد ملفات النشر

```bash
# إنشاء Procfile
echo "worker: python main.py" > Procfile

# إنشاء runtime.txt
echo "python-3.9.16" > runtime.txt

# إنشاء app.json (اختياري)
cat > app.json << EOF
{
  "name": "Telegram Jobs Bot",
  "description": "Smart Telegram bot for job seekers",
  "keywords": ["telegram", "bot", "jobs", "python"],
  "env": {
    "BOT_TOKEN": {
      "description": "Telegram Bot Token from BotFather"
    },
    "SUPABASE_URL": {
      "description": "Supabase Project URL"
    },
    "SUPABASE_KEY": {
      "description": "Supabase Anon Key"
    }
  },
  "addons": [
    "heroku-postgresql:hobby-dev"
  ]
}
EOF
```

##### 6. النشر

```bash
# إضافة الملفات
git add .
git commit -m "Deploy to Heroku"

# رفع إلى Heroku
git push heroku main

# تشغيل العامل
heroku ps:scale worker=1

# عرض السجلات
heroku logs --tail
```

### Railway

#### المزايا:
- واجهة حديثة وسهلة
- نشر سريع
- أسعار تنافسية
- دعم ممتاز للـ Git

#### خطوات النشر:

##### 1. إعداد المشروع

1. اذهب إلى [railway.app](https://railway.app)
2. سجل الدخول بـ GitHub
3. اضغط "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر المستودع

##### 2. إعداد متغيرات البيئة

```env
BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_USER_ID=your_user_id
ENVIRONMENT=production
```

##### 3. إعداد أمر البدء

```bash
# في إعدادات المشروع:
Start Command: python main.py
```

---

## 🐳 النشر باستخدام Docker

### إنشاء Dockerfile

```dockerfile
# استخدام Python 3.9 slim كصورة أساسية
FROM python:3.9-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت متطلبات Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# إنشاء مستخدم غير جذر
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# فتح المنفذ (اختياري للمراقبة)
EXPOSE 8000

# فحص صحة الحاوية
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# تشغيل البوت
CMD ["python", "main.py"]
```

### إنشاء docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: telegram-jobs-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ADMIN_USER_ID=${ADMIN_USER_ID}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - bot-network
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: telegram-jobs-bot-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - bot-network
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    container_name: telegram-jobs-bot-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - bot-network
    depends_on:
      - bot

volumes:
  redis_data:

networks:
  bot-network:
    driver: bridge
```

### إنشاء .dockerignore

```dockerignore
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
venv/
ENV/
env/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/
data/
test_results.json
*.log
```

### بناء وتشغيل الحاوية

```bash
# بناء الصورة
docker build -t telegram-jobs-bot .

# تشغيل الحاوية
docker run -d \
  --name telegram-jobs-bot \
  --env-file .env \
  --restart unless-stopped \
  telegram-jobs-bot

# أو باستخدام docker-compose
docker-compose up -d

# عرض السجلات
docker logs -f telegram-jobs-bot

# دخول الحاوية
docker exec -it telegram-jobs-bot bash
```

### إدارة الحاويات

```bash
# عرض الحاويات الجارية
docker ps

# إيقاف الحاوية
docker stop telegram-jobs-bot

# إعادة تشغيل الحاوية
docker restart telegram-jobs-bot

# حذف الحاوية
docker rm telegram-jobs-bot

# عرض استخدام الموارد
docker stats telegram-jobs-bot
```

---

## 🔧 إعدادات الإنتاج المتقدمة

### مراقبة الأداء

#### إعداد Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'telegram-bot'
    static_configs:
      - targets: ['localhost:8000']
```

#### إعداد Grafana

```bash
# تشغيل Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# الوصول عبر http://localhost:3000
# admin/admin
```

### إعداد التنبيهات

#### Alertmanager

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourcompany.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@yourcompany.com'
        subject: 'Bot Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

### النسخ الاحتياطي التلقائي

```bash
#!/bin/bash
# backup.sh

# إعدادات النسخ الاحتياطي
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BOT_DIR="/home/botuser/telegram-jobs-bot"

# إنشاء مجلد النسخ الاحتياطي
mkdir -p $BACKUP_DIR

# نسخ احتياطي للكود
tar -czf $BACKUP_DIR/bot_code_$DATE.tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=.git \
  $BOT_DIR

# نسخ احتياطي لقاعدة البيانات (إذا كانت محلية)
# pg_dump telegram_jobs_bot > $BACKUP_DIR/database_$DATE.sql

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# إضافة إلى crontab
crontab -e

# نسخ احتياطي يومي في الساعة 2 صباحاً
0 2 * * * /home/botuser/backup.sh >> /var/log/backup.log 2>&1
```

### إعداد Load Balancer

#### Nginx Load Balancer

```nginx
upstream telegram_bot {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name bot.yourcompany.com;

    location / {
        proxy_pass http://telegram_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔍 مراقبة ومتابعة النشر

### مراقبة السجلات

```bash
# عرض السجلات المباشرة
tail -f /var/log/telegram-jobs-bot.log

# البحث في السجلات
grep "ERROR" /var/log/telegram-jobs-bot.log

# تحليل السجلات
awk '/ERROR/ {errors++} /WARNING/ {warnings++} /INFO/ {info++} END {
    print "Errors:", errors, "Warnings:", warnings, "Info:", info
}' /var/log/telegram-jobs-bot.log
```

### مراقبة الموارد

```bash
# مراقبة استخدام المعالج والذاكرة
htop

# مراقبة مساحة القرص
df -h

# مراقبة الشبكة
iftop

# مراقبة العمليات
ps aux | grep python
```

### فحص صحة النظام

```bash
#!/bin/bash
# health_check.sh

# فحص حالة البوت
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Bot is running"
else
    echo "❌ Bot is not running"
    # إعادة تشغيل البوت
    systemctl restart telegram-jobs-bot
fi

# فحص استخدام الذاكرة
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "⚠️ High memory usage: $MEMORY_USAGE%"
fi

# فحص مساحة القرص
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ High disk usage: $DISK_USAGE%"
fi

# فحص الاتصال بالإنترنت
if ping -c 1 google.com &> /dev/null; then
    echo "✅ Internet connection is working"
else
    echo "❌ No internet connection"
fi
```

### إعداد التنبيهات

```bash
# إضافة فحص صحة دوري
crontab -e

# فحص كل 5 دقائق
*/5 * * * * /home/botuser/health_check.sh >> /var/log/health_check.log 2>&1
```

---

## 🚨 حل مشاكل النشر

### مشاكل شائعة وحلولها

#### 1. خطأ في توكن البوت

```
Error: Unauthorized (401)
```

**الحل:**
```bash
# التحقق من متغير البيئة
echo $BOT_TOKEN

# التحقق من صحة التوكن
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe"

# إعادة إنشاء البوت إذا لزم الأمر
```

#### 2. مشاكل الاتصال بقاعدة البيانات

```
Error: Could not connect to Supabase
```

**الحل:**
```bash
# التحقق من متغيرات البيئة
echo $SUPABASE_URL
echo $SUPABASE_KEY

# اختبار الاتصال
curl -H "apikey: $SUPABASE_KEY" "$SUPABASE_URL/rest/v1/"

# التحقق من إعدادات الشبكة
```

#### 3. نفاد الذاكرة

```
Error: MemoryError
```

**الحل:**
```bash
# زيادة الذاكرة المتاحة
# أو تحسين الكود لاستخدام ذاكرة أقل

# مراقبة استخدام الذاكرة
free -h
ps aux --sort=-%mem | head

# إعادة تشغيل البوت دورياً
# إضافة إلى crontab:
# 0 4 * * * systemctl restart telegram-jobs-bot
```

#### 4. مشاكل الشبكة

```
Error: Connection timeout
```

**الحل:**
```bash
# التحقق من الاتصال
ping google.com

# التحقق من DNS
nslookup api.telegram.org

# التحقق من الجدار الناري
sudo ufw status

# فتح المنافذ المطلوبة
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

#### 5. مشاكل الأذونات

```
Error: Permission denied
```

**الحل:**
```bash
# التحقق من أذونات الملفات
ls -la /home/botuser/telegram-jobs-bot/

# إصلاح الأذونات
sudo chown -R botuser:botuser /home/botuser/telegram-jobs-bot/
chmod +x /home/botuser/telegram-jobs-bot/main.py
```

### أدوات التشخيص

```bash
#!/bin/bash
# diagnose.sh

echo "=== System Information ==="
uname -a
cat /etc/os-release

echo "=== Python Information ==="
python3 --version
pip3 --version

echo "=== Bot Process ==="
ps aux | grep python

echo "=== Memory Usage ==="
free -h

echo "=== Disk Usage ==="
df -h

echo "=== Network ==="
ping -c 3 api.telegram.org

echo "=== Bot Logs (last 20 lines) ==="
tail -20 /var/log/telegram-jobs-bot.log
```

---

## 📈 تحسين الأداء

### تحسين قاعدة البيانات

```sql
-- إضافة فهارس لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at);

-- تحليل الاستعلامات البطيئة
EXPLAIN ANALYZE SELECT * FROM jobs WHERE posted_date > NOW() - INTERVAL '7 days';
```

### تحسين الكود

```python
# استخدام connection pooling
import asyncpg

async def create_pool():
    return await asyncpg.create_pool(
        database_url,
        min_size=5,
        max_size=20,
        command_timeout=60
    )

# استخدام caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_job_categories():
    # كود جلب الفئات
    pass

# تحسين الذاكرة
import gc

def cleanup_memory():
    gc.collect()
```

### تحسين الشبكة

```python
# استخدام session مع connection pooling
import aiohttp

async def create_session():
    connector = aiohttp.TCPConnector(
        limit=100,
        limit_per_host=30,
        ttl_dns_cache=300,
        use_dns_cache=True
    )
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    return aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    )
```

---

## 🔐 أمان النشر

### تأمين الخادم

```bash
# تحديث النظام
apt update && apt upgrade -y

# تثبيت fail2ban
apt install -y fail2ban

# إعداد fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl restart fail2ban

# تغيير منفذ SSH
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
systemctl restart ssh

# إعداد الجدار الناري
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### تأمين التطبيق

```python
# تشفير البيانات الحساسة
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

# التحقق من المدخلات
import re

def validate_input(text: str) -> bool:
    # منع SQL injection
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)"
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True

# Rate limiting
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=30, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        user_requests = self.requests[user_id]
        
        # إزالة الطلبات القديمة
        user_requests[:] = [req_time for req_time in user_requests 
                           if now - req_time < self.window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        return True
```

### مراقبة الأمان

```bash
#!/bin/bash
# security_check.sh

echo "=== Security Check Report ==="
echo "Date: $(date)"

# فحص محاولات تسجيل الدخول الفاشلة
echo "=== Failed Login Attempts ==="
grep "Failed password" /var/log/auth.log | tail -10

# فحص الاتصالات المشبوهة
echo "=== Suspicious Connections ==="
netstat -tuln | grep LISTEN

# فحص العمليات المشبوهة
echo "=== Running Processes ==="
ps aux | grep -v "\[" | sort -k3 -nr | head -10

# فحص استخدام الموارد
echo "=== Resource Usage ==="
top -bn1 | head -20

# فحص سجلات fail2ban
echo "=== Fail2ban Status ==="
fail2ban-client status
```

---

## 📊 مراقبة الأداء والإحصائيات

### إعداد مراقبة شاملة

```python
# metrics.py
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
message_counter = Counter('bot_messages_total', 'Total messages processed')
response_time = Histogram('bot_response_time_seconds', 'Response time')
active_users = Gauge('bot_active_users', 'Number of active users')
memory_usage = Gauge('bot_memory_usage_bytes', 'Memory usage in bytes')

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_message(self):
        message_counter.inc()
    
    def record_response_time(self, duration):
        response_time.observe(duration)
    
    def update_active_users(self, count):
        active_users.set(count)
    
    def update_system_metrics(self):
        # Memory usage
        process = psutil.Process()
        memory_usage.set(process.memory_info().rss)
    
    def start_metrics_server(self, port=8000):
        start_http_server(port)

# استخدام في البوت
metrics = MetricsCollector()
metrics.start_metrics_server()
```

### Dashboard للمراقبة

```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Telegram Jobs Bot Dashboard</h1>
    
    <div class="metrics">
        <div class="metric">
            <h3>Active Users</h3>
            <span id="active-users">Loading...</span>
        </div>
        
        <div class="metric">
            <h3>Messages Today</h3>
            <span id="messages-today">Loading...</span>
        </div>
        
        <div class="metric">
            <h3>Jobs Scraped</h3>
            <span id="jobs-scraped">Loading...</span>
        </div>
    </div>
    
    <canvas id="responseTimeChart"></canvas>
    
    <script>
        // كود JavaScript لجلب وعرض البيانات
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                document.getElementById('active-users').textContent = data.active_users;
                document.getElementById('messages-today').textContent = data.messages_today;
                document.getElementById('jobs-scraped').textContent = data.jobs_scraped;
                
                updateChart(data.response_times);
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }
        
        // تحديث كل 30 ثانية
        setInterval(updateMetrics, 30000);
        updateMetrics();
    </script>
</body>
</html>
```

---

## 🎯 الخلاصة

هذا الدليل يغطي جميع جوانب نشر بوت الوظائف الذكي من البيئة المحلية إلى الإنتاج المتقدم. اختر الطريقة التي تناسب احتياجاتك:

- **للتطوير**: النشر المحلي
- **للمشاريع الصغيرة**: VPS بسيط
- **للمشاريع المتوسطة**: Render أو Heroku
- **للمشاريع الكبيرة**: Docker مع Kubernetes

تذكر دائماً:
- ✅ اختبر قبل النشر
- ✅ راقب الأداء باستمرار
- ✅ احتفظ بنسخ احتياطية
- ✅ حدث النظام بانتظام
- ✅ راجع السجلات دورياً

للمساعدة والدعم، راجع [دليل حل المشاكل](troubleshooting.md) أو تواصل معنا عبر GitHub Issues.

---

**تم إنشاء هذا الدليل بواسطة Manus AI - نحو مستقبل أذكى للتوظيف! 🚀**

