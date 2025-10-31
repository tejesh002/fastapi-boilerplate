# FastAPI Boilerplate

A production-ready FastAPI boilerplate with Docker support, health checks, and basic routing.

## Features

- 🚀 FastAPI with automatic API documentation
- 🐳 Docker and Docker Compose support
- ❤️ Health check and status endpoints
- 📦 Pre-configured dependencies
- 🔧 Development-ready structure

## Project Structure

```
fastapi-bp/
├── src/
│   └── main.py          # Main application file
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image configuration
├── docker-compose.yml  # Docker Compose configuration
├── .dockerignore       # Docker ignore file
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Quick Start

### Using Docker (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Local Development

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   uvicorn src.main:app --reload
   ```

## API Endpoints

### Base Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check for monitoring systems
- `GET /status` - Detailed status information

### Documentation

- `GET /docs` - Swagger UI (Interactive API documentation)
- `GET /redoc` - ReDoc (Alternative API documentation)
- `GET /openapi.json` - OpenAPI schema

## Docker Commands

```bash
# Build the Docker image
docker build -t fastapi-boilerplate .

# Run the container
docker run -p 8000:8000 fastapi-boilerplate

# Stop Docker Compose
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build
```

## Makefile Commands

The project includes a Makefile with convenient commands for development:

```bash
# Format code with Black (src/ and tests/ directories)
make format

# Format all Python files in the project
make format-all

# Check code formatting without making changes
make lint

# Run test suite
make test

# Run pre-PR checks (linting and tests)
make pre-pr

# Format code and run tests
make format-and-test
```


## Running TestCases and TestCoverage 
```
black . && pypyr pre-pr
```

## Environment Variables

- `ENVIRONMENT` - Application environment (development/production)

## Health Monitoring

The application includes built-in health check endpoints:

- `/health` - Returns health status (healthy/unhealthy)
- `/status` - Returns detailed application status

## Development

### Adding New Routes

Edit `src/main.py` to add your routes:

```python
@app.get("/api/example")
async def example():
    return {"message": "This is an example endpoint"}
```

### Hot Reload

When running with `uvicorn --reload` or Docker Compose with volume mounting, changes to the code will automatically reload.

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!

