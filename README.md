# 💸 PayMaur — Modern Fintech Platform for Mauritania

> **Secure. Scalable. Smart Payments Infrastructure.**

---

## 🚀 Overview

**PayMaur** is a next-generation fintech backend built with **Django REST Framework** and **PostgreSQL**, designed to power secure digital payments, money transfers, and financial services in Mauritania.  

It provides a unified wallet system, real-time transfers, and an extensible API architecture for integrating with telecom operators, billers, and merchants — built using enterprise-grade design and modern security standards.

---

## 🧱 Core Features

### 🔐 Authentication & Security
- Secure login using **phone/email + 4-digit PIN**
- **JWT-based authentication** with access and refresh tokens
- **Argon2 hashing** for PIN encryption
- **Brute-force & rate-limiting** protection
- **Environment-based configuration** using `.env`

### 💼 Wallet Management
- Real-time wallet balance tracking
- Double-entry ledger system for integrity
- Wallet top-up, refund, and withdrawal flows

### 💸 Money Transfers
- Peer-to-Peer (P2P) transfers via username or phone
- Request, accept, or decline money seamlessly
- QR-based quick transfers and merchant payments

### 📱 Airtime & Utilities
- Mobile recharge and data bundles (Mattel, Chinguitel, Mauritel)
- Utility bill payments (electricity, water, internet)
- Full idempotency and transaction reliability

### 🧾 Account Statements
- Generate detailed wallet statements
- Filter by date, type, and status
- Future export support (CSV, PDF)

### 🏦 Requests & Services
- Request **cheque books** and **debit cards**
- Secure **cash-out** via agent tokens
- Extendable service APIs for future banking partners

---

## 🧩 Tech Stack

| Layer | Technology |
|:------|:------------|
| **Backend Framework** | Django 5.2.7 + Django REST Framework |
| **Database** | PostgreSQL |
| **Authentication** | JWT (SimpleJWT), Argon2 |
| **Documentation** | drf-spectacular (OpenAPI/Swagger) |
| **Environment Management** | python-dotenv |
| **Containerization** | Docker (optional for deployment) |
| **Version Control** | Git + GitHub CI/CD Ready |
| **Deployment** | Render / Railway / AWS / Vercel (API Gateway) |

---

## ⚙️ Project Structure

```bash
paymaur-backend/
│
├── config/                 # Django settings, URLs, ASGI/WSGI configuration
│   ├── __init__.py
│   ├── settings.py         # Global Django configuration (environment, DB, REST)
│   ├── urls.py             # API route definitions
│   ├── asgi.py             # ASGI entry point for async servers
│   └── wsgi.py             # WSGI entry point for production
│
├── core/                   # Global utilities, middleware, base classes
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── utils.py
│   └── middleware.py
│
├── users/                  # Custom user model and profile management
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── authentication/         # JWT + PIN-based login & registration logic
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   └── urls.py
│
├── wallet/                 # Wallet model, balance logic, and ledger tracking
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── transactions/           # Transaction history, reconciliation, and logs
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── transfers/              # Peer-to-Peer transfers & requests
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── topup/                  # Mobile & internet recharge integrations
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── bills/                  # Bill payment services (electricity, water, etc.)
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── meta/                   # Static metadata (operators, billers)
│   ├── __init__.py
│   ├── data/
│   ├── views.py
│   └── urls.py
│
├── requirements.txt         # Python dependencies
├── manage.py                # Django management CLI
└── .env.example             # Example environment variables
