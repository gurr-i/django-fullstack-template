# Django Fullstack Project

## Overview
This project is a full-stack web application built using Django. It includes features such as user registration, task management, notifications, and more.

## Features
- User registration and authentication
- Task creation, update, and deletion
- Task assignment and notifications
- User profile management
- Responsive design using Bootstrap

## Installation

### Prerequisites
- Python 3.13 or higher
- Django 5.1.6
- SQLite (or another database supported by Django)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/gurr-i/django-fullstack-template.git
```

2. Navigate to the project directory:

   ```bash
   cd DjangoFullstack
   ```
3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations to set up the database:

   ```bash
   python manage.py migrate
   ```
5. Create a superuser account to access the admin panel:

   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:

   ```bash
   python manage.py runserver
   ```
7. Access the application at `http://127.0.0.1:8000/`.

## Usage

- Register a new account or log in with an existing account.
- Create and manage tasks from the dashboard.
- View and update your profile information.
- Receive notifications for task updates and comments.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please contact [your email address].
