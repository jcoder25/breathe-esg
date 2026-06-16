# Digital Heroes ESG Platform

A full-stack emissions ingestion and review platform built with React, Django REST Framework, and PostgreSQL.

## Live Demo

Frontend:
https://breathe-esg-1-o9is.onrender.com/

Backend API:
https://breathe-esg-e40y.onrender.com/

Admin Console:
https://breathe-esg-e40y.onrender.com/admin/

## Demo Credentials

Username: admin

Password: admin123

## Features

* Upload emissions and activity data from multiple sources
* Data normalization and validation
* Scope 1, Scope 2, and Scope 3 classification
* Analyst review workflow
* Audit trail tracking
* Dashboard analytics and reporting
* Multi-tenant architecture

## Technology Stack

### Frontend

* React
* Vite
* Axios
* Recharts

### Backend

* Django
* Django REST Framework
* PostgreSQL

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Developer

Jashan Jindal

Email: [jashanjindal25@gmail.com](mailto:jashanjindal25@gmail.com)

## Digital Heroes

This project was submitted as part of the Digital Heroes Developer Trial Task.

https://digitalheroesco.com
