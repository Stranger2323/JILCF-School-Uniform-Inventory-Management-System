# Feather Login

A modern, secure authentication system with a beautiful UI built with Flask.

## Features

- Modern and responsive UI design
- Secure user authentication
- Password strength validation
- Social login options (UI ready)
- Beautiful animations and transitions
- Flash messages for user feedback
- SQLAlchemy database integration

## Tech Stack

- Backend: Flask
- Database: SQLAlchemy with SQLite
- Frontend: HTML, CSS, JavaScript
- Deployment: Render-ready

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/feather-login.git
cd feather-login
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:8080`

## Deployment

This application is configured for deployment on Render. Simply connect your GitHub repository to Render and it will automatically deploy using the configuration in `render.yaml`.

## Environment Variables

For production deployment, set the following environment variables:
- `FLASK_ENV`: Set to 'production'
- `DATABASE_URL`: Your database URL (optional, defaults to SQLite)

## License

MIT License
