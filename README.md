# cafe_backend# ☕️ Cafe Backend (Django REST API)

## 📌 Project Description
This backend is part of a full web application for a cafe system.  
It provides REST APIs for meals, categories, cart, orders, and reports.  
Frontend (React) and another backend (Spring Boot) will consume these APIs.

---

## ⚙️ Installation Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your_repo>/cafe_backend.git
cd cafe_backend
2️⃣ Create and Activate Virtual Environment
bash
Копировать код
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
3️⃣ Install Dependencies
bash
Копировать код
pip install -r requirements.txt
4️⃣ Apply Migrations
bash
Копировать код
python manage.py makemigrations
python manage.py migrate
5️⃣ Create Superuser
bash
Копировать код
python manage.py createsuperuser
6️⃣ Run the Server
bash
Копировать код
python manage.py runserver
🔑 Authentication (JWT)
Obtain token:

bash
Копировать код
POST /api/token/
{
  "username": "admin",
  "password": "123"
}
Use in headers:

makefile
Копировать код
Authorization: Bearer <access_token>
🧾 API Endpoints
Endpoint	Method	Description
/api/meals/	GET, POST	Manage meals
/api/categories/	GET, POST	Manage categories
/api/cart/	GET	View cart
/api/cart/add/	POST	Add item to cart
/api/order/create/	POST	Create order
/api/reports/sales/	GET	Get sales report
/api/reports/pdf/	GET	Download sales report as PDF

🧱 Tech Stack
Backend: Django, Django REST Framework

Database: PostgreSQL (can use SQLite for local)

Auth: JWT (SimpleJWT)

PDF Generator: reportlab

External API: open.er-api.com for currency rates

🤝 Integration
Frontend: React

Backend #2: Spring Boot
Both can consume Django REST endpoints.

👨‍💻 Developer
Xojiakbar Asomov

yaml
Копировать код

---

## 🧩 2️⃣ `requirements.txt` 



**`requirements.txt`**
```txt
Django==4.2.23
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
requests==2.31.0
reportlab==4.1.0
psycopg2-binary==2.9.9
