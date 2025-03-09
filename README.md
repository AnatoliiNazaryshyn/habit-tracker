# Habit Tracker

A Django-based habit tracking application that helps users build consistent habits through tracking, goal setting, and timely reminders.

## Features

- **User Dashboard**: A personalized dashboard that displays the user's habits, including:
    - Habit details (name, frequency)
    - Reminder (if set)
    - Goal information (current streak, target streak, if set)
    - Logs for the current day (for daily habits) or the current month (for monthly habits)
- **Habit Management**: Create, update, and delete habits with customizable frequencies (daily or monthly)
- **Habit Logging**: Log completion of your habits to maintain a record of your progress
- **Goal Setting**: Set streak goals to stay motivated and track your consistency
- **Reminders**: Configure email reminders for your habits to ensure you never forget
- **User Authentication**: Secure JWT-based authentication with email login

## Tech Stack

- Django 5.1.6
- Django REST Framework
- Celery 5.4.0 (with Redis as broker)
- PostgreSQL
- Docker & Docker Compose

## Project Structure

```
habit-tracker/
├── .github/workflows/      # Linting workflow
├── docker/                 # Dockerfiles for different services
├── apps/                   # Django applications
│   ├── users/              # User authentication and management
│   └── habits/             # Habit tracking functionality
├── habit-tracker/          # Django project settings
├── .env.example            # Example environment variables
├── docker-compose.yml      # Docker compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/AnatoliiNazaryshyn/habit-tracker.git
   cd habit-tracker
   ```

2. Create your environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and replace placeholders with your actual values:

4. Start the application:
   ```bash
   docker-compose up
   ```

5. The application should now be running and accessible at `http://localhost:<API_PORT>`  
   (Check your `.env` file for the actual port)

## API Endpoints

### Authentication

- `POST /auth/register/` - Register a new user and receive JWT tokens
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

- `POST /auth/login/` - Login and receive JWT tokens
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

- `POST /auth/token/refresh/` - Refresh JWT token
  ```json
  {
    "refresh": "your_refresh_token"
  }
  ```

### Habits

- `GET /habits/habits/dashboard/` - Retrieve the user's personalized dashboard
- `GET /habits/habits/` - List all habits
- `POST /habits/habits/` - Create a new habit
  ```json
  {
    "name": "Morning Exercises",
    "frequency": "daily"
  }
  ```
- `GET /habits/habits/{id}/` - Retrieve a specific habit
- `PUT /habits/habits/{id}/` - Update a habit
- `DELETE /habits/habits/{id}/` - Delete a habit

### Goals

- `GET /habits/goals/` - List all goals
- `POST /habits/goals/` - Create a new goal
  ```json
  {
    "habit": 1,
    "target_streak": 30
  }
  ```
- `GET /habits/goals/{id}/` - Retrieve a specific goal
- `PUT /habits/goals/{id}/` - Update a goal
- `DELETE /habits/goals/{id}/` - Delete a goal

### Reminders

- `GET /habits/reminders/` - List all reminders
- `POST /habits/reminders/` - Create a new reminder
  ```json
  {
    "habit": 1,
    "reminder_time": "08:00:00"
  }
  ```
- `GET /habits/reminders/{id}/` - Retrieve a specific reminder
- `PUT /habits/reminders/{id}/` - Update a reminder
- `DELETE /habits/reminders/{id}/` - Delete a reminder

### Habit Logs

- `GET /habits/habit-logs/` - List all habit logs
- `POST /habits/habit-logs/` - Create a new habit log
  ```json
  {
    "habit": 1
  }
  ```

## Background Tasks

The application uses Celery with Redis, PostgreSQL for background task processing:

1. **Streak Reset Task**: Runs daily at 00:01 to check habits with goals that weren't logged properly:
   - For daily habits: Checks if a log is present for the previous day
   - For monthly habits: Checks if a log is present for the previous month
   - Resets the current streak to 0 for habits that failed their logging requirements

2. **Reminder Check Task**: Runs every minute to check and send email reminders for habits.

## Development

### Running Tests

```bash
docker-compose exec habit_tracker_backend pytest
```

### Accessing Admin Interface

The Django admin interface is available at `http://localhost:<API_PORT>/admin/`
