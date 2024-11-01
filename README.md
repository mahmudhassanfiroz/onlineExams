# Online Exam System
Live Link: https://onlineexams-firoz.onrender.com/

**Online Exam System** is a Django Web web app designed for students and teachers to take online exams and share educational resources. It provides encouragement in a blog where users can share their experiences and newcomers can learn from them. There are also notable books.

## Table of Contents
- [Features](#Features)
- [tech](#tech)
- [installation](#installation)
- [usage](#usage)
- [contributing](#contributing)
- [license](#license)

## Features
- **home**: A home page where project parts and various symbols are located.
- **Exams**: Facility to add various subject exams.
- **Live test**: Live test in a specific object.
- **Book**: problems, so they can be used as a reference.
- **Experience Blog**: A discussion forum for students to share their experiences.

## technology
- **Backend**: Django, the Django REST framework
- **Database**: PostgreSQL
- **FriendEnd**: HTML, CSS, JavaScript, Bootstrap 
- **API**: REST API, JSON Web Token (JWT) authentication

## Installation
Follow the pressing steps to setup Project on your local machine:

1. Clone the project
 bash
 git clone https://github.com/mahmudhassanfiroz/onlineExams
 CD Online Test

2. Create and activate the virtual environment:
python3 -m venv venv
source venv/bin/activate # Linux/macOS
venv\script\activate # Windows

3. Install the package:
pip install -r requirements.txt

4. Running the database migration:
python management.py migrate

5. Create admin user:
python manage.py createsuperuser

6. Manage local servers:
python manage.py runserver
Click on the link: http://127.0.0.1:8000

Live Link: https://onlineexams-firoz.onrender.com/
