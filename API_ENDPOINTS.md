# PayMaur Backend - API Endpoints Documentation

 

## 🎯 First 3 Core Modules Implemented

 

### 1. **Users Module** (`/api/v1/users/`)

### 2. **Wallet Module** (`/api/v1/wallet/`)

### 3. **Transactions Module** (`/api/v1/transactions/`)

 

---

 

## 🔐 Authentication Endpoints

 

**Base URL:** `/api/v1/auth/`

 

### Register User

```http

POST /api/v1/auth/register/

Content-Type: application/json

 

{

  "username": "johndoe",

  "phone": "36600100",

  "password": "1234"

}

```

 

### Login

```http

POST /api/v1/auth/login/

Content-Type: application/json

 

{

  "phone": "36600100",

  "password": "1234"

}

```

 

**Response:**

```json

{

  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",

  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."

}

```

 

### Refresh Token

```http

POST /api/v1/auth/token/refresh/

Content-Type: application/json

 

{

  "refresh": "your-refresh-token"

}

```

 

### Verify OTP

```http

POST /api/v1/auth/verify-otp/

Content-Type: application/json

 

{

  "phone": "36600100",

  "otp": "123456"

}

```

 

---

 

## 👤 Users Module

 

**Base URL:** `/api/v1/users/`

 

### Get Current User Profile

```http

GET /api/v1/users/profile/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "id": "uuid-here",

  "username": "johndoe",

  "phone": "36600100",

  "role": "CUSTOMER",

  "is_verified": true,

  "is_active": true,

  "date_joined": "2025-01-15T10:30:00Z",

  "wallet_balance": "1500.00"

}

```

 

### Update Profile

```http

PATCH /api/v1/users/profile/update/

Authorization: Bearer <access_token>

Content-Type: application/json

 

{

  "username": "newusername"

}

```

 

### Search Users

```http

GET /api/v1/users/search/?q=john

Authorization: Bearer <access_token>

```

 

**Response:**

```json

[

  {

    "id": "uuid",

    "username": "johndoe",

    "phone": "36600100",

    "role": "CUSTOMER",

    "is_verified": true

  }

]

```

 

### Get User by Username

```http

GET /api/v1/users/username/johndoe/

Authorization: Bearer <access_token>

```

 

---

 

## 💰 Wallet Module

 

**Base URL:** `/api/v1/wallet/`

 

### Get Wallet Details

```http

GET /api/v1/wallet/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "id": "uuid",

  "user_info": {

    "id": "user-uuid",

    "username": "johndoe",

    "phone": "36600100"

  },

  "balance": "1500.00",

  "is_locked": false,

  "last_updated": "2025-01-15T12:00:00Z"

}

```

 

### Get Balance Only

```http

GET /api/v1/wallet/balance/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "balance": "1500.00",

  "is_locked": false,

  "last_updated": "2025-01-15T12:00:00Z"

}

```

 

### Lock Wallet

```http

POST /api/v1/wallet/lock/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "detail": "Wallet locked successfully.",

  "is_locked": true

}

```

 

### Unlock Wallet

```http

POST /api/v1/wallet/unlock/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "detail": "Wallet unlocked successfully.",

  "is_locked": false

}

```

 

---

 

## 📊 Transactions Module

 

**Base URL:** `/api/v1/transactions/`

 

### List All Transactions

```http

GET /api/v1/transactions/

Authorization: Bearer <access_token>

```

 

**Query Parameters:**

- `type` - Filter by type: TOPUP, TRANSFER, WITHDRAW, BILLPAY

- `status` - Filter by status: PENDING, SUCCESS, FAILED

 

**Example:**

```http

GET /api/v1/transactions/?type=TRANSFER&status=SUCCESS

```

 

**Response:**

```json

[

  {

    "id": "uuid",

    "type": "TRANSFER",

    "amount": "100.00",

    "status": "SUCCESS",

    "reference": "TXN123456789",

    "created_at": "2025-01-15T10:30:00Z"

  }

]

```

 

### Get Transaction Details

```http

GET /api/v1/transactions/<transaction_id>/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "id": "uuid",

  "wallet": "wallet-uuid",

  "wallet_owner": {

    "username": "johndoe",

    "phone": "36600100"

  },

  "type": "TRANSFER",

  "amount": "100.00",

  "balance_after": "1400.00",

  "status": "SUCCESS",

  "reference": "TXN123456789",

  "metadata": {

    "recipient": "janedoe"

  },

  "created_at": "2025-01-15T10:30:00Z"

}

```

 

### Get Transaction Statistics

```http

GET /api/v1/transactions/stats/

Authorization: Bearer <access_token>

```

 

**Response:**

```json

{

  "total_transactions": 45,

  "total_spent": "2500.00",

  "total_received": "5000.00",

  "pending_count": 2,

  "success_count": 40,

  "failed_count": 3

}

```

 

### Get Recent Transactions

```http

GET /api/v1/transactions/recent/

Authorization: Bearer <access_token>

```

 

**Response:** (Last 10 transactions)

```json

[

  {

    "id": "uuid",

    "type": "TRANSFER",

    "amount": "100.00",

    "status": "SUCCESS",

    "reference": "TXN123456789",

    "created_at": "2025-01-15T10:30:00Z"

  }

]

```

 

---

 

## 📚 API Documentation (Swagger/ReDoc)

 

### Swagger UI (Interactive)

```http

GET /api/docs/

```

 

### ReDoc (Documentation)

```http

GET /api/redoc/

```

 

### OpenAPI Schema

```http

GET /api/schema/

```

 

---

 

## 🧪 Testing Endpoints

 

### Using cURL

 

**1. Register a User:**

```bash

curl -X POST http://localhost:8000/api/v1/auth/register/ \

  -H "Content-Type: application/json" \

  -d '{

    "username": "testuser",

    "phone": "36600100",

    "password": "1234"

  }'

```

 

**2. Login:**

```bash

curl -X POST http://localhost:8000/api/v1/auth/login/ \

  -H "Content-Type: application/json" \

  -d '{

    "phone": "36600100",

    "password": "1234"

  }'

```

 

**3. Get Profile (with token):**

```bash

curl -X GET http://localhost:8000/api/v1/users/profile/ \

  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

```

 

**4. Get Wallet:**

```bash

curl -X GET http://localhost:8000/api/v1/wallet/ \

  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

```

 

**5. Get Transactions:**

```bash

curl -X GET http://localhost:8000/api/v1/transactions/ \

  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

```

 

---

 

## 🚀 Running the Server

 

### 1. Set up Database (PostgreSQL)

```bash

# Make sure PostgreSQL is running

# Update .env file with your database credentials

```

 

### 2. Run Migrations

```bash

source venv/bin/activate

python manage.py makemigrations

python manage.py migrate

```

 

### 3. Create Superuser (Admin)

```bash

python manage.py createsuperuser

```

 

### 4. Start Development Server

```bash

python manage.py runserver

```

 

Server will be available at: `http://localhost:8000`

 

---

 

## 📝 Important Notes

 

### Authentication

- All endpoints (except auth endpoints) require JWT authentication

- Include the access token in the `Authorization` header as: `Bearer <token>`

- Tokens expire after 60 minutes (access) and 7 days (refresh)

 

### Phone Numbers

- Must be 8 digits

- Must start with 2 (Chinguitel), 3 (Mattel), or 4 (Mauritel)

- Example: `36600100`

 

### User Roles

- `CUSTOMER` - Regular users (default)

- `AGENT` - Agents for cash-in/cash-out

- `MERCHANT` - Business accounts

- `ADMIN` - System administrators

 

### Wallet Auto-Creation

- Wallets are automatically created when a user registers (via signals)

- Initial balance is `0.00 MRO`

 

### Transaction Types

- `TOPUP` - Add money to wallet

- `TRANSFER` - Send money to another user

- `WITHDRAW` - Withdraw money

- `BILLPAY` - Pay bills

 

### Transaction Statuses

- `PENDING` - Transaction initiated

- `SUCCESS` - Transaction completed

- `FAILED` - Transaction failed