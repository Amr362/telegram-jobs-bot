# 🤖 Telegram Jobs Bot - بوت الوظائف الذكي

<div align="center">

![Bot Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

**بوت تليجرام ذكي ومتقدم للباحثين عن الوظائف**

[الميزات](#-الميزات) • [التثبيت](#-التثبيت) • [الاستخدام](#-الاستخدام) • [التوثيق](#-التوثيق) • [المساهمة](#-المساهمة)

</div>

---

## 📋 نظرة عامة

بوت الوظائف الذكي هو حل شامل ومتطور للباحثين عن الوظائف، مصمم خصيصاً للمتحدثين بالعربية والإنجليزية. يوفر البوت إشعارات يومية مخصصة، بحث متقدم عن الوظائف، تحليل الآراء، والعديد من الميزات الذكية التي تساعد المستخدمين في العثور على الوظيفة المثالية.

### 🎯 الهدف الرئيسي

تسهيل عملية البحث عن الوظائف من خلال:
- **الأتمتة الذكية**: إشعارات يومية مخصصة حسب تفضيلات المستخدم
- **البحث الشامل**: جمع الوظائف من مصادر متعددة محلية وعالمية
- **التحليل المتقدم**: تحليل آراء الموظفين والشركات
- **الدعم الشامل**: نظام دعم ذكي مرتبط بالوظائف

---

## ✨ الميزات

### 🔔 الإشعارات الذكية
- **إشعارات يومية مخصصة** حسب المهارات والموقع المفضل
- **إشعارات عاجلة** للوظائف ذات المواعيد النهائية القريبة
- **ملخصات أسبوعية** مع إحصائيات وتوصيات شخصية
- **تنبيهات مخصصة** للوظائف المطابقة لمعايير محددة

### 🔍 البحث المتقدم
- **8 مصادر وظائف** محلية وعالمية:
  - Google Jobs
  - RemoteOK
  - Remotive  
  - AngelList
  - WeWorkRemotely
  - Wuzzuf (وظف)
  - Bayt (بيت)
  - Tanqeeb (تنقيب)

### 🧠 الذكاء الاصطناعي
- **تحليل المشاعر** للآراء والمراجعات
- **مطابقة ذكية** بين الوظائف وتفضيلات المستخدم
- **توصيات شخصية** بناءً على النشاط والاهتمامات
- **تحليل الصلة** لترتيب الوظائف حسب الأهمية

### 💬 نظام الدعم المتقدم
- **دعم مرتبط بالوظائف** مع نصائح مخصصة
- **9 فئات دعم** تشمل التقديم والمقابلات والمهارات
- **بحث بالكلمات المفتاحية** في قاعدة المعرفة
- **أسئلة شائعة ذكية** حسب نوع الوظيفة

### 🔗 فحص الروابط
- **فحص تلقائي** لحالة روابط التقديم
- **مراقبة دورية** للروابط المحفوظة
- **تقارير صحة الروابط** مع إحصائيات مفصلة

### 📊 التحليلات والإحصائيات
- **إحصائيات شخصية** للمستخدم
- **تتبع النشاط** والتفاعل مع الوظائف
- **تحليلات النظام** للمطورين والإداريين

---

## 🛠 التقنيات المستخدمة

### Backend
- **Python 3.8+** - لغة البرمجة الأساسية
- **python-telegram-bot** - مكتبة بوت تليجرام
- **Supabase** - قاعدة البيانات والمصادقة
- **APScheduler** - جدولة المهام
- **BeautifulSoup4** - تحليل HTML
- **aiohttp** - طلبات HTTP غير متزامنة

### AI & Analysis
- **NLTK/TextBlob** - معالجة اللغة الطبيعية
- **Transformers** - نماذج الذكاء الاصطناعي
- **scikit-learn** - تعلم الآلة

### Database
- **PostgreSQL** (عبر Supabase) - قاعدة البيانات الرئيسية
- **Row Level Security** - أمان البيانات
- **Real-time subscriptions** - التحديثات الفورية

### Infrastructure
- **Docker** - الحاويات
- **GitHub Actions** - CI/CD
- **Render/Heroku** - النشر السحابي

---

## 📦 التثبيت

### المتطلبات الأساسية

```bash
# Python 3.8 أو أحدث
python --version

# Git
git --version

# pip
pip --version
```

### 1. استنساخ المشروع

```bash
git clone https://github.com/your-username/telegram-jobs-bot.git
cd telegram-jobs-bot
```

### 2. إعداد البيئة الافتراضية

```bash
# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# على Linux/Mac:
source venv/bin/activate
# على Windows:
venv\Scripts\activate
```

### 3. تثبيت المتطلبات

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات

#### إنشاء مشروع Supabase

1. اذهب إلى [supabase.com](https://supabase.com)
2. أنشئ حساب جديد أو سجل الدخول
3. أنشئ مشروع جديد
4. احصل على `Project URL` و `anon public key`

#### تشغيل SQL Schema

```bash
# في لوحة تحكم Supabase، اذهب إلى SQL Editor
# انسخ والصق محتوى ملف database_schema.sql
# اضغط Run لتنفيذ الأوامر
```

### 5. إعداد بوت تليجرام

#### إنشاء البوت

1. ابحث عن `@BotFather` في تليجرام
2. أرسل `/newbot`
3. اتبع التعليمات لإنشاء البوت
4. احصل على `Bot Token`

#### إعداد الأوامر

```bash
# أرسل هذا الأمر لـ BotFather:
/setcommands

# ثم انسخ والصق:
start - بدء استخدام البوت وإعداد التفضيلات
help - عرض المساعدة والأوامر المتاحة
profile - عرض الملف الشخصي
settings - إعدادات البوت والتفضيلات
search - البحث عن الوظائف
jobs - عرض أحدث الوظائف
saved - الوظائف المحفوظة
stats - الإحصائيات الشخصية
notifications - إدارة الإشعارات
support - مركز الدعم والمساعدة
job_support - دعم مخصص للوظائف
```

### 6. إعداد متغيرات البيئة

```bash
# انسخ ملف البيئة النموذجي
cp .env.example .env

# عدل الملف وأضف قيمك الفعلية
nano .env
```

#### متغيرات البيئة المطلوبة

```env
# إعدادات البوت
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_USER_ID=your_telegram_user_id

# إعدادات Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# إعدادات البيئة
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 🚀 الاستخدام

### تشغيل البوت

#### الطريقة البسيطة

```bash
# تشغيل البوت مباشرة
python run_bot.py
```

#### الطريقة المتقدمة

```bash
# تشغيل البوت الرئيسي
python main.py
```

#### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
python test_bot.py

# تشغيل اختبار محدد
python -m pytest tests/ -v
```

### استخدام البوت

#### للمستخدمين الجدد

1. **ابدأ المحادثة**: أرسل `/start` للبوت
2. **اختر نوع الوظائف**: عربي، عالمي، أو كلاهما
3. **حدد الموقع**: بلد محدد، عن بُعد، أو كلاهما
4. **أدخل مهاراتك**: اكتب المهارات المطلوبة (مفصولة بفواصل)
5. **اختر تكرار الإشعارات**: يومي، أسبوعي، أو حسب الطلب

#### الأوامر الأساسية

```
/help - عرض جميع الأوامر المتاحة
/profile - عرض ملفك الشخصي وتفضيلاتك
/settings - تعديل الإعدادات والتفضيلات
/search - البحث اليدوي عن الوظائف
/jobs - عرض أحدث الوظائف المناسبة لك
/saved - عرض الوظائف المحفوظة
/stats - عرض إحصائياتك الشخصية
/notifications - إدارة إعدادات الإشعارات
/support - الحصول على المساعدة والدعم
```

#### للمطورين والإداريين

```
/admin - لوحة تحكم الإدارة
/system_stats - إحصائيات النظام المفصلة
/force_scrape - فرض جمع الوظائف فوراً
/broadcast - إرسال إعلان لجميع المستخدمين
```

---

## 📁 هيكل المشروع

```
telegram-jobs-bot/
├── 📁 src/                          # الكود المصدري
│   ├── 📁 bot/                      # منطق البوت الأساسي
│   │   ├── __init__.py
│   │   ├── main.py                  # البوت الرئيسي
│   │   ├── handlers.py              # معالجات الأوامر
│   │   ├── conversation.py          # إدارة المحادثات
│   │   ├── support_handlers.py     # معالجات الدعم
│   │   └── admin_handlers.py       # معالجات الإدارة
│   ├── 📁 database/                 # إدارة قاعدة البيانات
│   │   ├── __init__.py
│   │   ├── models.py                # نماذج البيانات
│   │   ├── manager.py               # مدير قاعدة البيانات
│   │   └── queries.py               # الاستعلامات المتخصصة
│   ├── 📁 scrapers/                 # أدوات جمع الوظائف
│   │   ├── __init__.py
│   │   ├── base.py                  # الفئة الأساسية
│   │   ├── google_jobs.py           # Google Jobs
│   │   ├── remote_sites.py          # مواقع العمل عن بُعد
│   │   ├── arabic_sites.py          # المواقع العربية
│   │   └── manager.py               # مدير الجمع
│   ├── 📁 scheduler/                # جدولة المهام
│   │   ├── __init__.py
│   │   ├── job_scheduler.py         # جدولة الوظائف
│   │   └── notification_manager.py # مدير الإشعارات
│   └── 📁 utils/                    # الأدوات المساعدة
│       ├── __init__.py
│       ├── config.py                # إدارة التكوين
│       ├── logger.py                # نظام التسجيل
│       ├── link_checker.py          # فحص الروابط
│       ├── link_monitor.py          # مراقب الروابط
│       ├── opinion_collector.py     # جمع الآراء
│       ├── sentiment_analyzer.py    # تحليل المشاعر
│       └── support_system.py        # نظام الدعم
├── 📁 tests/                        # الاختبارات
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_scrapers.py
│   ├── test_notifications.py
│   └── test_integration.py
├── 📁 docs/                         # الوثائق
│   ├── api.md                       # توثيق API
│   ├── deployment.md               # دليل النشر
│   ├── configuration.md            # دليل التكوين
│   └── troubleshooting.md          # حل المشاكل
├── 📁 config/                       # ملفات التكوين
│   ├── logging.yaml
│   └── scheduler.yaml
├── 📄 main.py                       # الملف الرئيسي
├── 📄 run_bot.py                    # ملف التشغيل المبسط
├── 📄 test_bot.py                   # نظام الاختبار الشامل
├── 📄 database_schema.sql           # هيكل قاعدة البيانات
├── 📄 requirements.txt              # المتطلبات
├── 📄 .env.example                  # نموذج متغيرات البيئة
├── 📄 .env                          # متغيرات البيئة (لا يُرفع لـ Git)
├── 📄 .gitignore                    # ملفات Git المتجاهلة
├── 📄 Dockerfile                    # ملف Docker
├── 📄 docker-compose.yml            # Docker Compose
├── 📄 README.md                     # هذا الملف
└── 📄 LICENSE                       # رخصة المشروع
```

---


## ⚙️ التكوين المتقدم

### إعدادات الجمع (Scraping)

```env
# عدد الوظائف القصوى لكل بحث
MAX_JOBS_PER_SEARCH=50

# التأخير بين طلبات الجمع (بالثواني)
SCRAPING_DELAY=2

# مهلة انتظار الطلبات (بالثواني)
REQUEST_TIMEOUT=30
```

### إعدادات الإشعارات

```env
# عدد الإشعارات اليومية القصوى لكل مستخدم
MAX_DAILY_NOTIFICATIONS=3

# حجم دفعة الإشعارات
NOTIFICATION_BATCH_SIZE=10

# التأخير بين الإشعارات (بالثواني)
NOTIFICATION_DELAY=0.5
```

### إعدادات قاعدة البيانات

```env
# حجم مجموعة الاتصالات
DB_POOL_SIZE=10

# مهلة انتظار قاعدة البيانات (بالثواني)
DB_TIMEOUT=30
```

### إعدادات الأمان

```env
# حد الطلبات في الدقيقة الواحدة
RATE_LIMIT_PER_MINUTE=30

# الحد الأقصى لطول الرسالة
MAX_MESSAGE_LENGTH=4096
```

### مفاتيح API الاختيارية

```env
# OpenAI لتحليل المشاعر المتقدم
OPENAI_API_KEY=your_openai_api_key

# Reddit لجمع الآراء
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Twitter لجمع الآراء
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

---

## 🚀 النشر

### النشر على Render

#### 1. إعداد المستودع

```bash
# إنشاء مستودع Git جديد
git init
git add .
git commit -m "Initial commit"

# رفع إلى GitHub
git remote add origin https://github.com/your-username/telegram-jobs-bot.git
git push -u origin main
```

#### 2. إنشاء خدمة Render

1. اذهب إلى [render.com](https://render.com)
2. سجل الدخول أو أنشئ حساب جديد
3. اضغط "New +" ثم "Web Service"
4. اربط مستودع GitHub الخاص بك
5. اختر المستودع `telegram-jobs-bot`

#### 3. إعدادات النشر

```yaml
# في إعدادات Render:
Name: telegram-jobs-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

#### 4. متغيرات البيئة

أضف جميع متغيرات البيئة في قسم "Environment Variables":

```
BOT_TOKEN=your_actual_bot_token
SUPABASE_URL=your_actual_supabase_url
SUPABASE_KEY=your_actual_supabase_key
ADMIN_USER_ID=your_telegram_user_id
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### النشر على Heroku

#### 1. تثبيت Heroku CLI

```bash
# على macOS
brew tap heroku/brew && brew install heroku

# على Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. إنشاء تطبيق Heroku

```bash
# تسجيل الدخول
heroku login

# إنشاء التطبيق
heroku create telegram-jobs-bot-your-name

# إضافة PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev
```

#### 3. إعداد متغيرات البيئة

```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_KEY=your_supabase_key
heroku config:set ADMIN_USER_ID=your_user_id
heroku config:set ENVIRONMENT=production
```

#### 4. النشر

```bash
# إضافة ملف Procfile
echo "worker: python main.py" > Procfile

# رفع التطبيق
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# تشغيل العامل
heroku ps:scale worker=1
```

### النشر باستخدام Docker

#### 1. إنشاء Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# تثبيت المتطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# إنشاء مستخدم غير جذر
RUN useradd --create-home --shell /bin/bash app
USER app

# تشغيل البوت
CMD ["python", "main.py"]
```

#### 2. إنشاء docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ADMIN_USER_ID=${ADMIN_USER_ID}
      - ENVIRONMENT=production
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

#### 3. تشغيل الحاوية

```bash
# بناء الصورة
docker build -t telegram-jobs-bot .

# تشغيل الحاوية
docker run -d --name jobs-bot \
  --env-file .env \
  telegram-jobs-bot

# أو باستخدام docker-compose
docker-compose up -d
```

---

## 🔧 الصيانة والمراقبة

### مراقبة السجلات

```bash
# عرض السجلات المباشرة
tail -f logs/bot.log

# البحث في السجلات
grep "ERROR" logs/bot.log

# عرض إحصائيات السجلات
awk '/ERROR/ {errors++} /WARNING/ {warnings++} /INFO/ {info++} END {print "Errors:", errors, "Warnings:", warnings, "Info:", info}' logs/bot.log
```

### النسخ الاحتياطي

#### نسخ احتياطي لقاعدة البيانات

```bash
# تصدير البيانات من Supabase
# (يتم عبر لوحة التحكم أو API)

# نسخ احتياطي للملفات
tar -czf backup-$(date +%Y%m%d).tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=.git \
  .
```

### تحديث البوت

```bash
# إيقاف البوت
pkill -f "python main.py"

# سحب التحديثات
git pull origin main

# تحديث المتطلبات
pip install -r requirements.txt --upgrade

# تشغيل الاختبارات
python test_bot.py

# إعادة تشغيل البوت
python main.py &
```

### مراقبة الأداء

#### استخدام htop

```bash
# تثبيت htop
sudo apt install htop

# مراقبة العمليات
htop
```

#### مراقبة استخدام الذاكرة

```bash
# عرض استخدام الذاكرة
free -h

# مراقبة عملية البوت
ps aux | grep python
```

#### مراقبة مساحة القرص

```bash
# عرض مساحة القرص
df -h

# عرض حجم المجلدات
du -sh logs/ database/ src/
```

---

## 🐛 حل المشاكل الشائعة

### مشاكل الاتصال

#### خطأ في توكن البوت

```
Error: Unauthorized (401)
```

**الحل:**
1. تأكد من صحة `BOT_TOKEN` في ملف `.env`
2. تأكد من أن البوت لم يتم حذفه من BotFather
3. جرب إنشاء بوت جديد إذا لزم الأمر

#### خطأ في الاتصال بـ Supabase

```
Error: Could not connect to Supabase
```

**الحل:**
1. تحقق من `SUPABASE_URL` و `SUPABASE_KEY`
2. تأكد من أن المشروع نشط في Supabase
3. تحقق من إعدادات الشبكة والجدار الناري

### مشاكل الجمع (Scraping)

#### عدم العثور على وظائف

```
Warning: No jobs found for criteria
```

**الحل:**
1. تحقق من اتصال الإنترنت
2. قد تكون المواقع قد غيرت هيكلها
3. جرب معايير بحث مختلفة
4. تحقق من السجلات للحصول على تفاصيل أكثر

#### بطء في الجمع

**الحل:**
1. زيادة `SCRAPING_DELAY` في إعدادات البيئة
2. تقليل `MAX_JOBS_PER_SEARCH`
3. تحسين اتصال الإنترنت

### مشاكل الإشعارات

#### عدم وصول الإشعارات

**الحل:**
1. تحقق من أن المستخدم لم يحظر البوت
2. تأكد من تشغيل الجدولة بشكل صحيح
3. تحقق من السجلات لمعرفة أخطاء الإرسال

#### إشعارات مكررة

**الحل:**
1. تحقق من إعدادات الجدولة
2. تأكد من عدم تشغيل عدة نسخ من البوت
3. راجع منطق منع التكرار في الكود

### مشاكل الأداء

#### استهلاك عالي للذاكرة

**الحل:**
1. إعادة تشغيل البوت دورياً
2. تحسين استعلامات قاعدة البيانات
3. تنظيف البيانات القديمة

#### بطء في الاستجابة

**الحل:**
1. تحسين استعلامات قاعدة البيانات
2. إضافة فهارس جديدة
3. تحسين خوارزميات البحث

---

## 📊 الإحصائيات والتحليلات

### إحصائيات المستخدمين

يمكن للمطورين الوصول إلى إحصائيات شاملة عبر:

```bash
# عرض إحصائيات النظام
/system_stats

# عرض إحصائيات المستخدمين
/admin -> إحصائيات المستخدمين
```

### مؤشرات الأداء الرئيسية (KPIs)

- **معدل النشاط**: نسبة المستخدمين النشطين
- **معدل النجاح في الجمع**: نسبة نجاح عمليات جمع الوظائف
- **معدل التفاعل**: نسبة التفاعل مع الإشعارات
- **معدل الاحتفاظ**: نسبة المستخدمين الذين يواصلون الاستخدام

### تقارير دورية

يتم إنشاء تقارير تلقائية تشمل:
- تقرير يومي للنشاط
- تقرير أسبوعي للإحصائيات
- تقرير شهري للأداء العام

---

## 🔒 الأمان والخصوصية

### حماية البيانات

- **تشفير البيانات**: جميع البيانات الحساسة مشفرة
- **Row Level Security**: حماية على مستوى الصفوف في قاعدة البيانات
- **التحقق من الهوية**: نظام مصادقة آمن
- **تسجيل العمليات**: تسجيل جميع العمليات الحساسة

### الامتثال للقوانين

- **GDPR**: امتثال لقانون حماية البيانات الأوروبي
- **حق النسيان**: إمكانية حذف البيانات نهائياً
- **الشفافية**: وضوح في جمع واستخدام البيانات
- **الموافقة**: الحصول على موافقة صريحة من المستخدمين

### أفضل الممارسات الأمنية

```bash
# تحديث المتطلبات بانتظام
pip install --upgrade -r requirements.txt

# فحص الثغرات الأمنية
pip audit

# استخدام متغيرات البيئة للمعلومات الحساسة
# عدم تخزين كلمات المرور في الكود
# استخدام HTTPS لجميع الاتصالات
```

---

## 🤝 المساهمة

نرحب بمساهماتكم في تطوير البوت! إليكم كيفية المساهمة:

### إرشادات المساهمة

1. **Fork المشروع** على GitHub
2. **إنشاء فرع جديد** للميزة أو الإصلاح
3. **كتابة الكود** مع اتباع معايير المشروع
4. **إضافة الاختبارات** للكود الجديد
5. **تشغيل الاختبارات** للتأكد من عدم كسر شيء
6. **إرسال Pull Request** مع وصف واضح

### معايير الكود

```python
# استخدام Type Hints
def process_job(job: Job) -> bool:
    """Process a job and return success status."""
    pass

# التوثيق الواضح
class JobScraper:
    """
    Base class for job scrapers.
    
    This class provides the basic interface for all job scrapers
    and includes common functionality like rate limiting and error handling.
    """
    pass

# معالجة الأخطاء
try:
    result = await scrape_jobs()
except ScrapingError as e:
    logger.error(f"Scraping failed: {e}")
    return []
```

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
python test_bot.py

# تشغيل اختبارات محددة
python -m pytest tests/test_scrapers.py -v

# تشغيل اختبارات التغطية
python -m pytest --cov=src tests/
```

### الإبلاغ عن المشاكل

عند الإبلاغ عن مشكلة، يرجى تضمين:

1. **وصف المشكلة**: ما الذي حدث؟
2. **خطوات الإعادة**: كيف يمكن إعادة إنتاج المشكلة؟
3. **السلوك المتوقع**: ما الذي كان يجب أن يحدث؟
4. **البيئة**: نظام التشغيل، إصدار Python، إلخ
5. **السجلات**: أي رسائل خطأ أو سجلات ذات صلة

---

## 📚 الموارد الإضافية

### الوثائق التقنية

- [دليل API المفصل](docs/api.md)
- [دليل النشر المتقدم](docs/deployment.md)
- [دليل التكوين الشامل](docs/configuration.md)
- [دليل حل المشاكل](docs/troubleshooting.md)

### الروابط المفيدة

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Supabase Documentation](https://supabase.com/docs)
- [Python-telegram-bot Library](https://python-telegram-bot.readthedocs.io/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

### المجتمع والدعم

- **GitHub Issues**: للإبلاغ عن المشاكل والاقتراحات
- **Discussions**: للنقاشات العامة والأسئلة
- **Wiki**: للوثائق التعاونية
- **Telegram Group**: @TelegramJobsBotSupport (إذا متاح)

---

## 📄 الرخصة

هذا المشروع مرخص تحت رخصة MIT. راجع ملف [LICENSE](LICENSE) للتفاصيل.

```
MIT License

Copyright (c) 2024 Manus AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 شكر وتقدير

نشكر جميع المساهمين والمطورين الذين ساعدوا في إنجاز هذا المشروع:

### المكتبات والأدوات المستخدمة

- **python-telegram-bot**: مكتبة ممتازة لتطوير بوتات تليجرام
- **Supabase**: منصة قواعد البيانات السحابية المتقدمة
- **BeautifulSoup**: أداة قوية لتحليل HTML
- **APScheduler**: مكتبة جدولة المهام المرنة
- **NLTK**: مكتبة معالجة اللغة الطبيعية

### المصادر والمراجع

- [Telegram Bot Best Practices](https://core.telegram.org/bots/faq)
- [Web Scraping Ethics](https://blog.apify.com/web-scraping-ethics/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)

---

## 📞 التواصل

للأسئلة والاستفسارات:

- **البريد الإلكتروني**: support@manusai.com
- **GitHub**: [github.com/manus-ai/telegram-jobs-bot](https://github.com/manus-ai/telegram-jobs-bot)
- **الموقع الرسمي**: [manusai.com](https://manusai.com)

---

<div align="center">

**صُنع بـ ❤️ بواسطة [Manus AI](https://manusai.com)**

⭐ إذا أعجبك المشروع، لا تنس إعطاؤه نجمة على GitHub!

</div>

