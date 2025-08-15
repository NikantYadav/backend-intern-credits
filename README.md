# Credits API

A FastAPI-based credits management system with user management, automated daily credits, and dynamic schema management.

## Features

- User management with email validation
- Credits system with balance tracking
- Automated daily credit distribution (5 credits at midnight UTC)
- Dynamic database schema management
- MySQL database with async operations
- Background job scheduling

## Setup

### Prerequisites

- Python 3.10+
- MySQL database
- pip or uv package manager

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name
```

3. Run the application:
```bash
python src/main.py
```

The server will start on `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000
```

## User Management

### Create User
**POST** `/users/`

Create a new user with email and name.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Get User
**GET** `/users/{user_id}`

Retrieve user information by ID.

**Response:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

## Credits Management

### Get Credits
**GET** `/api/credits/{user_id}`

Retrieve current credit balance and last update timestamp.

**Response:**
```json
{
  "user_id": 1,
  "credits": 150,
  "last_updated": "2025-01-14T12:30:45.123456"
}
```

### Add Credits
**POST** `/api/credits/{user_id}/add`

Add credits to a user's account.

**Request Body:**
```json
{
  "amount": 100
}
```

**Response:**
```json
{
  "message": "Added 100 credits",
  "user_id": 1,
  "new_balance": 250,
  "last_updated": "2025-01-14T12:35:20.654321"
}
```

### Deduct Credits
**POST** `/api/credits/{user_id}/deduct`

Subtract credits from a user's account (prevents negative balances).

**Request Body:**
```json
{
  "amount": 50
}
```

**Response:**
```json
{
  "message": "Deducted 50 credits",
  "user_id": 1,
  "new_balance": 200,
  "last_updated": "2025-01-14T12:40:15.789012"
}
```

**Error Response (Insufficient Credits):**
```json
{
  "detail": "Insufficient credits"
}
```

### Reset Credits
**PATCH** `/api/credits/{user_id}/reset`

Reset user's credits to zero.

**Response:**
```json
{
  "message": "Credits reset to zero",
  "user_id": 1,
  "credits": 0,
  "last_updated": "2025-01-14T12:45:30.345678"
}
```

## Admin Operations

### Trigger Daily Credits
**POST** `/admin/trigger-daily-credits`

Manually trigger the daily credits job (adds 5 credits to all users).

**Response:**
```json
{
  "message": "Daily credits job triggered successfully"
}
```

## Schema Management

### List Tables
**GET** `/api/schema/tables`

Get all tables in the database.

**Response:**
```json
{
  "tables": ["users", "credits", "products"]
}
```

### Describe Table
**GET** `/api/schema/tables/{table_name}/columns`

Get column information for a specific table.

**Response:**
```json
{
  "table": "users",
  "columns": [
    {
      "field": "user_id",
      "type": "int",
      "null": "NO",
      "key": "PRI",
      "default": null,
      "extra": "auto_increment"
    },
    {
      "field": "email",
      "type": "varchar(255)",
      "null": "NO",
      "key": "UNI",
      "default": null,
      "extra": ""
    }
  ]
}
```

### Create Table
**POST** `/api/schema/tables`

Create a new table dynamically.

**Request Body:**
```json
{
  "table_name": "products",
  "columns": [
    {
      "name": "id",
      "type": "INT AUTO_INCREMENT PRIMARY KEY",
      "nullable": false
    },
    {
      "name": "name",
      "type": "VARCHAR(255)",
      "nullable": false
    },
    {
      "name": "price",
      "type": "DECIMAL(10,2)",
      "nullable": true,
      "default": "0.00"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Table 'products' created successfully"
}
```

### Add Column
**POST** `/api/schema/columns`

Add a new column to an existing table.

**Request Body:**
```json
{
  "table_name": "users",
  "column": {
    "name": "phone",
    "type": "VARCHAR(20)",
    "nullable": true
  }
}
```

**Response:**
```json
{
  "message": "Column 'phone' added to table 'users' successfully"
}
```

### Drop Column
**DELETE** `/api/schema/columns/{table_name}/{column_name}`

Remove a column from a table.

**Response:**
```json
{
  "message": "Column 'phone' dropped from table 'users' successfully"
}
```

### Drop Table
**DELETE** `/api/schema/tables/{table_name}`

Remove a table from the database.

**Response:**
```json
{
  "message": "Table 'products' dropped successfully"
}
```

### Reflect Schema
**POST** `/api/schema/reflect`

Get the complete database schema structure.

**Response:**
```json
{
  "schema": {
    "users": [
      {
        "name": "user_id",
        "type": "int",
        "nullable": false,
        "key": "PRI",
        "default": null,
        "extra": "auto_increment"
      }
    ],
    "credits": [
      {
        "name": "id",
        "type": "int",
        "nullable": false,
        "key": "PRI",
        "default": null,
        "extra": "auto_increment"
      }
    ]
  }
}
```

## Health Check

### Root Endpoint
**GET** `/`

Basic API status check.

**Response:**
```json
{
  "message": "Hello World"
}
```

### Health Check
**GET** `/health`

API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

## Background Jobs

### Daily Credits Distribution

The system automatically adds 5 credits to all users:
- **Startup**: Immediately when the server starts
- **Daily**: Every day at midnight UTC (00:00)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Credits Table
```sql
CREATE TABLE credits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    credits INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```
