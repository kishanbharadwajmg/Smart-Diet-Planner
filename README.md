# Smart Diet Planner

A comprehensive AI-powered web application built with Flask for personalized nutrition tracking, meal planning, and dietary recommendations.

## Features

- **User Authentication**: Secure registration and login system
- **Personalized Dashboard**: Track daily nutrition intake and progress
- **AI-Powered Recommendations**: Get personalized diet plans using AI integration
- **Food Logging**: Easy meal tracking with nutritional information
- **Progress Tracking**: Monitor your dietary goals and achievements
- **Admin Panel**: Administrative interface for managing users and food database
- **Export Functionality**: Export your dietary data for analysis
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **AI Integration**: Google Gemini API
- **Forms**: WTForms with Flask-WTF

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kishanbharadwajmg/Smart-Diet-Planner.git
   cd Smart-Diet-Planner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   FLASK_CONFIG=development
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Project Structure

```
Smart-Diet-Planner/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── database/
│   ├── schema.sql        # Database schema
│   └── seed_data.py      # Initial data setup
├── models/               # Database models
│   ├── user.py
│   ├── food.py
│   ├── food_log.py
│   └── user_preferences.py
├── routes/               # Application routes
│   ├── auth.py          # Authentication routes
│   ├── dashboard.py     # User dashboard
│   ├── admin.py         # Admin panel
│   ├── api.py           # API endpoints
│   └── ai_agent.py      # AI integration
├── services/             # Business logic services
│   ├── ai_agent.py
│   ├── gemini_client.py
│   └── ollama_client.py
├── templates/            # HTML templates
├── static/              # CSS, JS, and static assets
└── screenshots/         # Application screenshots
```

## Usage

1. **Register** a new account or login with existing credentials
2. **Set up your profile** with dietary preferences and goals
3. **Log meals** throughout the day using the food diary
4. **Get AI recommendations** for personalized meal plans
5. **Track progress** towards your nutritional goals
6. **Export data** for further analysis

## API Keys Setup

To use the AI features, you'll need to obtain API keys:

1. **Google Gemini API**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key
2. Add the API key to your `.env` file as `GEMINI_API_KEY`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Screenshots

The `screenshots/` directory contains images showing the application's key features:
- User registration and login
- Dashboard overview
- Food logging interface
- AI-powered diet plan generation

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

**Kishan Bharadwaj MG**
- Email: kishanbharadwajmg@gmail.com
- GitHub: [@kishanbharadwajmg](https://github.com/kishanbharadwajmg)

---

*Built with ❤️ using Flask and AI technology*