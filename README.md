# MedDose UZ 🧬💊

**Dori vositalarini xavfsiz dozalash va farmakokinetik jarayonlarni monitoring qilish axborot tizimi**

[![Django](https://img.shields.io/badge/Django-5.1-green?style=flat-square)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square)](https://python.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square)](https://getbootstrap.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange?style=flat-square)](https://chartjs.org)

> ⚠️ **Eslatma:** Bu loyiha faqat ta'lim va simulyatsiya maqsadida ishlab chiqilgan. Haqiqiy tibbiy tashxis yoki davolash vositasi emas.

---

## 📋 Loyiha haqida

MedDose UZ — kasalxonalar, oilaviy shifokorlar va farmasevtlar uchun mo'ljallangan interaktiv farmakokinetik monitoring tizimi. Tizim dori vositasining inson organizmidagi dinamikasini hisoblab beradi, qondagi konsentratsiyani vaqt bo'yicha ko'rsatadi va xavfli dozalar haqida ogohlantiradi.

## ✨ Asosiy funksiyalar

- ✅ **Bemor parametrlari** — vazn, yosh, yuborish usuli
- ✅ **8 ta dori** uchun standart farmakokinetik koeffitsiyentlar
- ✅ **Bir kamerali model** — dC/dt = -k·C
- ✅ **Ikki kamerali model** — absorbsiya + eliminatsiya
- ✅ **Eyler usuli** — 1-tartibli sonli yechim
- ✅ **Runge-Kutta 4 (RK4)** — 4-tartibli aniq sonli yechim
- ✅ **Eyler vs RK4** xatoliklar solishtirmasi
- ✅ **Chart.js** grafiklar — MIC/MTC chegaralar ko'rsatilgan
- ✅ **Xavf ogohlantirish** — toksik/terapevtik/xavfsiz zonalar
- ✅ **Keyingi doza vaqti** tavsiyasi
- ✅ **Hisoblashlar tarixi** — SQLite da saqlanadi
- ✅ **MathJax** formulalar ko'rsatish

## 🛠️ Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | Django 5.1 |
| Frontend | Django Templates |
| UI | Bootstrap 5.3 |
| Grafiklar | Chart.js 4.4 |
| Formulalar | MathJax 3 |
| Ma'lumotlar bazasi | SQLite |
| Ikonlar | Bootstrap Icons |
| Shriftlar | Inter, Outfit (Google Fonts) |

## 🔬 Matematik asoslar

### Bir kamerali model
```
dC/dt = -k · C
C(t)  = C₀ · e^(-kt)
```

### Ikki kamerali model
```
dC_depo/dt = -ka · C_depo
dC_qon/dt  =  ka · C_depo - ke · C_qon
```

### Eyler usuli
```
y_{n+1} = y_n + h · f(t_n, y_n)
```

### Runge-Kutta 4-tartibli
```
k1 = f(t_n, y_n)
k2 = f(t_n + h/2, y_n + h·k1/2)
k3 = f(t_n + h/2, y_n + h·k2/2)
k4 = f(t_n + h, y_n + h·k3)
y_{n+1} = y_n + (h/6)·(k1 + 2k2 + 2k3 + k4)
```

## 📁 Loyiha tuzilmasi

```
MedDose UZ/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── db.sqlite3
├── static/
├── staticfiles/
├── meddose/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── calculator/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py            ← Input formasi
    ├── math_engine.py      ← PK modellar, Euler, RK4
    ├── models.py           ← Drug, Calculation
    ├── urls.py
    ├── views.py
    ├── templatetags/
    │   └── calculator_extras.py
    ├── migrations/
    └── templates/
        └── calculator/
            ├── base.html
            ├── index.html
            ├── result.html
            ├── history.html
            └── about.html
```

## 🚀 O'rnatish va ishga tushirish

### 1. Repozitoriyni klonlash
```bash
git clone https://github.com/yourusername/meddose-uz.git
cd meddose-uz
```

### 2. Virtual muhit yaratish (ixtiyoriy, tavsiya etiladi)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Ma'lumotlar bazasini tayyorlash
```bash
python manage.py migrate
```

### 5. Serverni ishga tushirish
```bash
python manage.py runserver
```

Brauzerda oching: **http://127.0.0.1:8000**

## 🌐 Deploy (Render.com)

### render.yaml fayli yarating:
```yaml
services:
  - type: web
    name: meddose-uz
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
    startCommand: gunicorn meddose.wsgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: meddose.settings
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
```

### Railway uchun:
1. Railway.app ga kiring
2. "New Project" → "Deploy from GitHub repo"
3. `DJANGO_SETTINGS_MODULE=meddose.settings` env var qo'shing
4. Start command: `gunicorn meddose.wsgi:application`

## 📊 Tizim modulları

### 1. `math_engine.py` — Matematik dvigatel

| Funksiya | Tavsif |
|----------|--------|
| `one_compartment_model()` | Bir kamerali analitik yechim |
| `two_compartment_model()` | Ikki kamerali analitik yechim |
| `euler_method()` | Eyler usuli (sonli) |
| `rk4_method()` | Runge-Kutta 4 (sonli) |
| `calculate_concentration()` | Asosiy hisoblash funksiyasi |
| `detect_risk_zone()` | Xavf zonasini aniqlash |
| `recommend_next_dose()` | Keyingi doza vaqtini hisoblash |
| `compare_methods()` | Eyler vs RK4 xatolarni solishtirish |

### 2. `forms.py` — Input

- Bemor vazni va yoshi
- Dori nomi (8 ta tayyor, yoki qo'lda)
- Yuborish usuli (tabletka, ukol, kapelnitsa)
- Doza (mg)
- k, ka, ke koeffitsiyentlari
- MIC/MTC chegara qiymatlari
- Vaqt oralig'i va vaqt qadami

### 3. Alert tizimi

| Holat | Ko'rinish | Shart |
|-------|-----------|-------|
| ☣️ Toksik | Qizil, pulsirlovchi | max_C > MTC |
| 📉 Past | Sariq | max_C < MIC |
| ✅ Xavfsiz | Yashil | MIC ≤ max_C ≤ MTC |

## 👥 Maqsadli foydalanuvchilar

- 🏥 Shifoxonalar va klinikalar
- 👨‍⚕️ Oilaviy shifokorlar
- 💊 Farmasevtlar
- 🎓 Tibbiyot universitetlari (ta'lim)
- 💻 Online tibbiy maslahat platformalari

## 📝 Litsenziya

MIT License — ta'lim va ilmiy maqsadlarda erkin foydalanish mumkin.

---

*MedDose UZ — Farmakokinetik monitoring tizimi | Universitet loyihasi 2025-2026*
