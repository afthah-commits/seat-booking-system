# 🚀 Quick Deployment Commands

## 📦 Push to GitHub (Do This First!)

```bash
# 1. Create a new repository on GitHub.com
#    - Go to https://github.com/new
#    - Name: seat-booking-system
#    - Don't initialize with README
#    - Click "Create repository"

# 2. Push your code (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/seat-booking-system.git
git branch -M main
git push -u origin main
```

---

## 🌐 Deploy to Render (Easiest - Recommended!)

### One-Time Setup:
1. Go to https://render.com and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Fill in:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn seat_booking.wsgi:application`
5. Add **PostgreSQL** database from dashboard
6. Add these **Environment Variables**:
   ```
   SECRET_KEY=<run command below to generate>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=<copy from PostgreSQL dashboard>
   ```

### Generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### After First Deploy:
```bash
# In Render Shell tab:
python manage.py migrate
python manage.py seed_data
```

**Your app will be live at:** `https://seat-booking-system.onrender.com`

---

## 🚂 Deploy to Railway (Fast & Simple!)

### One-Time Setup:
1. Go to https://railway.app and sign up
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
5. Add **Environment Variables**:
   ```
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=.railway.app
   ```

### After First Deploy:
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and run migrations
railway login
railway run python manage.py migrate
railway run python manage.py seed_data
```

**Your app will be live at:** `https://seat-booking-system.up.railway.app`

---

## 🔮 Deploy to Heroku (Classic Choice)

### Prerequisites:
```bash
# Install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
```

### Deploy:
```bash
# Login
heroku login

# Create app
heroku create seat-booking-system

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY="<your-secret-key>"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=".herokuapp.com"

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py seed_data

# Open app
heroku open
```

**Your app will be live at:** `https://seat-booking-system.herokuapp.com`

---

## 🔄 Update Your Deployed App

After making changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

**Render & Railway:** Auto-deploy from GitHub  
**Heroku:** Run `git push heroku main`

---

## ✅ Verify Deployment

Visit your app and test:
- [ ] Homepage loads
- [ ] Select a show
- [ ] Hold seats
- [ ] Book seats
- [ ] Check admin panel at `/admin/`

---

## 🐛 Quick Troubleshooting

**App won't start?**
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure `DATABASE_URL` is correct

**Static files missing?**
```bash
python manage.py collectstatic --noinput
```

**Database errors?**
```bash
python manage.py migrate
```

---

## 📊 View Logs

**Render:** Dashboard → Service → Logs tab  
**Railway:** Service → Deployments → View Logs  
**Heroku:** `heroku logs --tail`

---

## 🎉 You're Done!

Your seat booking system is now live and accessible worldwide! 🌍

**Share your links:**
- 📦 GitHub: `https://github.com/YOUR_USERNAME/seat-booking-system`
- 🌐 Live App: Your deployment URL
- 📖 Documentation: Link to your README.md

---

**Pro Tips:**
- Enable automatic backups in your database settings
- Set up custom domain (optional)
- Add monitoring/error tracking
- Keep your SECRET_KEY secure and never commit it to Git!
