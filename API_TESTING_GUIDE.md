# PayMaur API Testing Guide

## Server Information
- **Base URL:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/api/docs/` (Swagger UI)
- **ReDoc:** `http://localhost:8000/api/redoc/`

## Authentication Endpoints

### 1. Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "36600100",
    "username": "testuser",
    "password": "1234",
    "password_confirm": "1234",
    "role": "CUSTOMER"
  }'
```

**Response:**
- Status: 201 Created
- Returns: User object + JWT tokens (access & refresh)
- Automatically creates wallet with 0 balance

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "36600100",
    "password": "1234"
  }'
```

**Response:**
- Status: 200 OK
- Returns: User object + new JWT tokens

### 3. Get Profile
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### 5. Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Wallet Endpoints

### 1. Get Wallet Balance
```bash
curl -X GET http://localhost:8000/api/wallet/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
    "id": "uuid",
    "username": "testuser",
    "phone": "36600100",
    "balance": "900.00",
    "is_locked": false,
    "last_updated": "2025-11-07T13:53:26.770287Z"
}
```

## Transfer Endpoints

### 1. Create Transfer
```bash
curl -X POST http://localhost:8000/api/transfers/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_username": "receiver",
    "amount": "100.00",
    "note": "Payment for services"
  }'
```

**Or transfer by phone:**
```bash
curl -X POST http://localhost:8000/api/transfers/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_phone": "46600200",
    "amount": "50.00",
    "note": "Test transfer"
  }'
```

**Features:**
- ✅ Atomic database transactions
- ✅ Balance validation
- ✅ Wallet lock checking
- ✅ Self-transfer prevention
- ✅ Dual transaction recording (sender & receiver)

### 2. List Transfers
```bash
curl -X GET http://localhost:8000/api/transfers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:** Returns both sent and received transfers

## Transaction Endpoints

### 1. List All Transactions
```bash
curl -X GET http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Filter by Type
```bash
curl -X GET "http://localhost:8000/api/transactions/?type=TRANSFER" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Available Types:** TOPUP, TRANSFER, WITHDRAW, BILLPAY

### 3. Filter by Status
```bash
curl -X GET "http://localhost:8000/api/transactions/?status=SUCCESS" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Available Statuses:** PENDING, SUCCESS, FAILED

## Testing Workflow

### Complete Test Flow
```bash
# 1. Register first user (sender)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"36600100","username":"sender","password":"1234","password_confirm":"1234"}'

# Save the access token from response as SENDER_TOKEN

# 2. Register second user (receiver)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"46600200","username":"receiver","password":"5678","password_confirm":"5678"}'

# 3. Add balance to sender (via Django shell)
python manage.py shell -c "from wallet.models import Wallet; from users.models import User; user = User.objects.get(username='sender'); wallet = user.wallet; wallet.balance = 1000; wallet.save(); print(f'Balance: {wallet.balance}')"

# 4. Check sender wallet
curl -X GET http://localhost:8000/api/wallet/ \
  -H "Authorization: Bearer SENDER_TOKEN"

# 5. Transfer money
curl -X POST http://localhost:8000/api/transfers/create/ \
  -H "Authorization: Bearer SENDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_username":"receiver","amount":"100.00","note":"Test payment"}'

# 6. Check balances again
curl -X GET http://localhost:8000/api/wallet/ \
  -H "Authorization: Bearer SENDER_TOKEN"

# 7. View transaction history
curl -X GET http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer SENDER_TOKEN"
```

## Error Testing

### Invalid Phone Format
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"12345678","username":"test","password":"1234","password_confirm":"1234"}'
# Expected: 400 Bad Request - "Must start with 2, 3, or 4"
```

### PIN Mismatch
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"36600100","username":"test","password":"1234","password_confirm":"5678"}'
# Expected: 400 Bad Request - "PINs do not match"
```

### Insufficient Balance
```bash
curl -X POST http://localhost:8000/api/transfers/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_username":"receiver","amount":"999999.00"}'
# Expected: 400 Bad Request - "Insufficient balance"
```

### Invalid Credentials
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"36600100","password":"9999"}'
# Expected: 401 Unauthorized - "Invalid credentials"
```

## Implementation Status

### ✅ Completed
- Authentication (register, login, logout, profile, token refresh)
- Wallet management (balance checking)
- Money transfers (P2P with atomic transactions)
- Transaction history (with filtering)
- Input validation (phone format, PIN validation, balance checks)
- API documentation (Swagger UI)
- Error handling

### 📋 Pending Implementation
- Top-up service (mobile recharge)
- Bill payment service
- Agent services (cash-in/cash-out)
- KYC verification
- Fee calculation
- Notifications

## Database Schema

### Key Models
- **User:** Authentication + profile (UUID, phone, username, PIN)
- **Wallet:** Balance tracking (OneToOne with User)
- **Transfer:** P2P transfer records
- **Transaction:** Ledger for all financial operations
- **Agent:** Cash-in/cash-out operators
- **BillPayment:** Utility bill payments
- **Topup:** Mobile recharge records
- **SimpleKYC:** Identity verification

### Security Features
- Argon2 password hashing for PINs
- JWT authentication with token rotation
- Token blacklisting on logout
- Atomic database transactions
- Wallet locking capability
- Balance validation before transfers

## Development Commands

### Start Server
```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Admin Panel
Navigate to: `http://localhost:8000/admin/`

### Django Shell (for manual testing)
```bash
python manage.py shell
```

```python
# Example: Add balance to wallet
from wallet.models import Wallet
from users.models import User

user = User.objects.get(username='testuser')
wallet = user.wallet
wallet.balance = 1000
wallet.save()
```

## Notes

- All amounts are in MRU (Mauritanian Ouguiya)
- Phone numbers must be 8 digits starting with 2, 3, or 4
- PINs must be exactly 4 digits
- JWT access tokens expire after 60 minutes
- Refresh tokens expire after 7 days
- Database: SQLite (development) / PostgreSQL (production)
