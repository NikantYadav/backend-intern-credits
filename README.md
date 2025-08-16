# Credits API

A FastAPI-based REST API for managing user credits with automated background tasks.

## Features

- User management (create, read, update, delete)
- Credits system with automatic daily credit allocation
- Background scheduler for automated tasks
- MySQL database with async SQLAlchemy
- CORS enabled for cross-origin requests
- Health check endpoint

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL with async SQLAlchemy
- **Background Tasks**: APScheduler
- **Server**: Uvicorn
- **Environment**: Python 3.8+

## Prerequisites

- Python 3.8 or higher
- MySQL server running

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  
```

### 3. Install Dependencies
```bash
cd src
pip install -r requirements.txt
```

### 4. Database Setup
Make sure MySQL is running and create a database:
```sql
CREATE DATABASE `database_name`;
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON `database_name`.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Environment Configuration
Create a `.env` file in the root directory with:
```
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name
HOST=0.0.0.0
PORT=8000
```

Replace `username`, `password`, and `database_name` with your actual database credentials.

## Running the Application

### Development Mode
```bash
python src/main.py
```

### Production Mode with Uvicorn
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /health` - Returns API health status

### Users
- `POST /users` - Create a new user
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Credits
- `GET /credits` - List all credits
- `GET /credits/{user_id}` - Get credits for specific user
- `POST /credits` - Create/update user credits
- `PUT /credits/{user_id}` - Update user credits

### Schema
- `GET /schema` - Get database schema information

## Database Schema

### Users Table
- `user_id` (Primary Key)
- `email` (Unique)
- `name`
- `created_at`
- `updated_at`

### Credits Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `credits`
- `last_updated`

## Background Tasks

The application includes a scheduler that runs background tasks for automated credit management. The scheduler starts automatically when the application launches.

