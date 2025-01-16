# FastAPI Supabase App

This project covers the challenge handling authentication and the following

User signup (creation).
User login (authentication).
User logout (authentication).
User session management. (check if user is logged in)
Test coverage for the above endpoints.
User stored in postegres (supabase with RLS)
User Session stored in postegres (supabase with RLS)

## Project Structure

```
fastapi-supabase-app
├── src
│   ├── main.py          # Entry point of the FastAPI application
│   ├── config
│   │   └── settings.py  # Configuration settings for the application
│   ├── routes
│   │   └── api.py       # API routes for the application
│   ├── models
│   │   └── models.py     # Data models used in the application
│   └── database
│       └── client.py     # Database connection and interactions with Supabase
│   └── utils
│       └── utils.py     # utility functions
├── tests
│   └── test_api.py      # Unit tests for the API endpoints
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd fastapi-supabase-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file.

## Docs

http://localhost:8000/docs

## Running the Application

To run the FastAPI application, use the following command:

```
uvicorn src.main:app --reload
```

## Testing

To run the tests, use the following command:

```
pytest tests/test_api.py
```

## License

This project is licensed under the MIT License.
