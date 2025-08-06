# Credit Approval System

A Django REST API-based credit approval system that manages customer registration, loan eligibility checks, and loan creation with intelligent credit scoring algorithms.

## 🚀 Features

- **Customer Registration**: Register new customers with automatic approved limit calculation
- **Loan Eligibility Check**: Intelligent credit scoring based on multiple factors
- **Loan Creation**: Automated loan approval and creation process
- **Loan Management**: View loan details and customer loan history
- **Background Data Import**: Celery-based data import from Excel files
- **Credit Scoring Algorithm**: Multi-factor credit assessment including:
  - Payment history (EMI on-time percentage)
  - Number of active loans
  - Recent loan activity
  - Credit utilization ratio
  - EMI-to-income ratio

## 🏗️ Architecture

- **Backend**: Django 5.2.4 with Django REST Framework
- **Database**: PostgreSQL with dj-database-url
- **Task Queue**: Celery with Redis
- **Data Import**: Pandas for Excel file processing

## 📋 Prerequisites

- Docker & Docker Compose (recommended)
- Or: Python 3.8+, PostgreSQL, Redis (for Celery)

## 🐳 Docker Setup & Running

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django
   ```

2. **Copy or create environment variables**
   - If not present, create a `.env` file in the `django/` directory with:
     ```env
     DATABASE_URL=postgresql://postgres:postgres@db:5432/credit_approval
     SECRET_KEY=your-secret-key
     DEBUG=True
     CELERY_BROKER_URL=redis://redis:6379/0
     CELERY_RESULT_BACKEND=redis://redis:6379/1
     POSTGRES_DB=credit_approval
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=postgres
     ```

3. **Build and start all services**
   ```bash
   docker-compose up --build -d
   ```
   This will start Django, PostgreSQL, and Redis containers. **Migrations and sample data import are handled automatically.**

4. **Access the API**
   - By default, the API will be available at: [http://localhost:8000/](http://localhost:8000/)

**That's it! No need to run migrations or import data manually when using Docker.**

---

## 🛠️ Local Development (without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables** (see Docker section above)
4. **Run migrations**
   ```bash
   python manage.py migrate
   ```
5. **Import sample data**
   ```bash
   python manage.py import_data
   ```
6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

---

## 📑 API Endpoints (Quick Reference)

| Method | Endpoint                   | Description                        |
|--------|----------------------------|------------------------------------|
| POST   | `/register/`               | Register a new customer            |
| POST   | `/check-eligibility/`      | Check loan eligibility             |
| POST   | `/create-loan/`            | Create a new loan                  |
| GET    | `/view-loan/<loan_id>/`    | Get details of a specific loan     |
| GET    | `/view-loans/<customer_id>/`| List all active loans for customer |

---

## 📖 API Usage Examples

### 1. Customer Registration
```http
POST /register/
```
**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "phone_number": "1234567890",
    "monthly_income": 50000.00
}
```
**Response:**
```json
{
    "customer_id": 1,
    "name": "John Doe",
    "age": 30,
    "monthly_income": "50000.00",
    "approved_limit": "1800000.00",
    "phone_number": "1234567890"
}
```

### 2. Check Loan Eligibility
```http
POST /check-eligibility/
```
**Request Body:**
```json
{
    "customer_id": 1,
    "loan_amount": 100000.00,
    "interest_rate": 12.50,
    "tenure": 24
}
```
**Response:**
```json
{
    "customer_id": 1,
    "approved": true,
    "interest_rate": "12.50",
    "corrected_rate": "12.50",
    "tenure": 24,
    "monthly_installment": "4727.50"
}
```

### 3. Create Loan
```http
POST /create-loan/
```
**Request Body:**
```json
{
    "customer_id": 1,
    "loan_amount": 100000.00,
    "interest_rate": 12.50,
    "tenure": 24
}
```
**Response:**
```json
{
    "loan_id": 1,
    "customer_id": 1,
    "loan_approved": true,
    "message": "Loan approved successfully.",
    "monthly_installment": "4727.50"
}
```

### 4. View Loan Details
```http
GET /view-loan/{loan_id}/
```
**Response:**
```json
{
    "loan_id": 1,
    "customer": {
        "customer_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "phone_number": "1234567890",
        "monthly_salary": "50000.00",
        "approved_limit": "1800000.00"
    },
    "loan_amount": "100000.00",
    "interest_rate": "12.50",
    "monthly_installment": "4727.50",
    "tenure": 24,
    "date_of_approval": "2024-01-15",
    "end_date": "2026-01-15",
    "emis_paid_on_time": 0
}
```

### 5. View Customer Loans
```http
GET /view-loans/{customer_id}/
```
**Response:**
```json
[
    {
        "loan_id": 1,
        "loan_amount": "100000.00",
        "interest_rate": "12.50",
        "monthly_installment": "4727.50",
        "repayments_left": 24
    }
]
```

---

## 🧮 Credit Scoring Algorithm

The system uses a comprehensive credit scoring algorithm that considers:

1. **Payment History (40%)**: Percentage of EMIs paid on time
2. **Loan Factor (20%)**: Number of active loans (fewer is better)
3. **Activity Factor (20%)**: Recent loan activity in current year
4. **Volume Factor (10%)**: Credit utilization ratio
5. **EMI Factor (10%)**: EMI-to-income ratio (must be ≤50%)

**Approval Criteria:**
- Score > 50: No interest rate slab
- Score 30-50: Minimum 12% interest rate
- Score 10-30: Minimum 16% interest rate
- Score < 10: Not approved

## 📊 Data Management

### Import Sample Data
```bash
python manage.py import_data
```
This command imports customer and loan data from Excel files in the `data/` directory using Celery background tasks.

### Data Files
- `data/customer_data.xlsx`: Customer information
- `data/loan_data.xlsx`: Historical loan data

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `CELERY_BROKER_URL`: Redis connection for Celery
- `CELERY_RESULT_BACKEND`: Redis connection for Celery results
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL settings for Docker Compose

### Database Configuration
The system uses PostgreSQL with the following models:

**Customer Model:**
- customer_id (Primary Key)
- first_name, last_name
- age, phone_number
- monthly_salary, approved_limit

**Loan Model:**
- loan_id, customer (Foreign Key)
- loan_amount, tenure, interest_rate
- monthly_payment, emis_paid_on_time
- date_of_approval, end_date

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Documentation

### Error Responses

**Loan Not Approved:**
```json
{
    "loan_id": null,
    "customer_id": 1,
    "loan_approved": false,
    "message": "Loan not approved based on credit score or EMI constraints.",
    "monthly_installment": "0.00"
}
```

**Validation Errors:**
```json
{
    "field_name": ["Error message"]
}
```

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False`
2. Configure production database
3. Set secure `SECRET_KEY`
4. Configure static files
5. Set up proper logging
6. Configure CORS if needed
7. Set up SSL/TLS certificates

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.
