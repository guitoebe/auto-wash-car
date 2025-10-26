# flask-customer-app

This project is a simple Flask application that manages customer records using SQLAlchemy. It provides functionality to create and retrieve customer information.

## Project Structure

```
flask-customer-app
├── src
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── models
│   │   ├── __init__.py
│   │   └── customer.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── customer_routes.py
│   └── templates
│       └── base.html
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd flask-customer-app
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Set up the database and run the application:
   ```
   python src/app.py
   ```
2. Access the application in your web browser at `http://localhost:5000`.

## License

This project is licensed under the MIT License.