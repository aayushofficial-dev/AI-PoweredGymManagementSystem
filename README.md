# AI-Powered Gym Management System

An AI-powered web-based gym management system built with Django, Python, HTML, CSS, Bootstrap, and AI technologies.

## Problem Statement

Many gyms still manage members, payments, attendance, and workout plans manually.
This can lead to:

- Difficulty maintaining member records
- Manual attendance tracking
- Payment management problems
- Difficulty monitoring membership expiry
- Lack of personalized workout recommendations
- Difficulty analyzing food and nutrition

## Objectives

- To digitize gym management processes
- To manage gym members efficiently
- To track memberships and payments
- To manage attendance digitally
- To provide AI-generated workout recommendations
- To provide AI-based food and nutrition analysis
- To provide separate dashboards for administrators and members
- To improve communication between gym staff and members

## Features

### Admin Features

- Admin authentication
- Admin dashboard
- Add, edit, and delete members
- Manage membership plans
- Manage trainers
- Track member attendance
- Manage payments
- View active and expired memberships
- Activate/deactivate member accounts
- Send member login credentials through WhatsApp

### Member Features

- Member login
- Member dashboard
- View membership information
- View payment information
- View attendance
- View workout plans
- Generate personalized AI workout plans
- Analyze food using AI

### AI Features

- AI-powered workout plan generation
- Personalized workout recommendations
- AI food image analysis
- Nutrition information and recommendations

## Technology Stack

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

### Backend
- Python
- Django

### Database
- SQLite

### AI
- Ollama / Llama

### Tools
- Visual Studio Code
- Git
- GitHub


## Installation

### 1. Clone the repository

git clone https://github.com/aayushofficial-dev/AI-PoweredGymManagementSystem

### 2. Navigate to the project

cd Ai-PoweredGymManagementSystem

### 3. Create a virtual environment

python3 -m venv venv

### 4. Activate the virtual environment

#### macOS/Linux

source venv/bin/activate

#### Windows

venv\Scripts\activate

### 5. Install dependencies

pip install -r requirements.txt


## Database Setup

Run Django migrations:

python manage.py makemigrations
python manage.py migrate

### Create an Admin Account

python manage.py createsuperuser

### Run the Server

python manage.py runserver

Then open:
        http://127.0.0.1:8000/

## AI Integration

The system uses AI to provide intelligent features for gym members.

### AI Workout Planner

The member provides information such as:

- Fitness goal
- Experience level
- Number of workout days
- Workout duration
- Available equipment

The system sends this information to the AI service and generates a personalized workout plan.

### AI Food Analyzer

The member uploads an image of food.

The system processes the image and sends it to the configured AI service for analysis.

The AI provides information such as:

- Food identification
- Estimated nutritional information
- Calories
- Protein
- Carbohydrates
- Fat
- Dietary recommendations

## User Roles

### Administrator

The administrator can:

- Manage members
- Manage trainers
- Manage membership plans
- Manage payments
- Monitor attendance
- Manage membership status
- Access administrative dashboards

### Member

Members can:

- View their profile
- View membership details
- View payments
- View attendance
- Generate workout plans
- Analyze food
- View their fitness information


## Future Improvements

- Mobile application
- Online membership payment
- Advanced AI fitness assistant
- AI-based exercise form detection
- Automated membership renewal notifications
- Email/SMS notifications
- Advanced fitness progress analytics
- Cloud deployment
- Multi-gym support

## Limitations

- AI-generated workout plans may require professional verification.
- AI nutritional analysis provides estimates rather than exact nutritional values.
- Some AI features require an internet connection.
- AI API usage may be subject to usage limits or costs.
- The current system is primarily designed for web browsers.

## License

This project was developed for educational and academic purposes.