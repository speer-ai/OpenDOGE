# OpenDOGE (Open Data on Government Expenditure)

OpenDOGE is a comprehensive platform for analyzing and visualizing government spending data. It aggregates data from multiple federal sources including USAspending.gov, Treasury.gov, SEC EDGAR, and more.

## Features

- Real-time contract award tracking
- Federal spending analysis
- National debt monitoring
- Economic indicators dashboard
- Company filing analysis
- Smart search capabilities
- RESTful API access
- Interactive data visualizations

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL, Redis
- **Infrastructure**: Docker, Nginx
- **APIs**: USAspending.gov, Treasury.gov, FRED, SEC EDGAR, and more

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/speer-ai/OpenDOGE.git
   cd OpenDOGE
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Production Deployment

1. Configure your domain DNS to point to your server.

2. SSH into your server and clone the repository:
   ```bash
   git clone https://github.com/speer-ai/OpenDOGE.git
   cd OpenDOGE
   ```

3. Run the deployment script:
   ```bash
   sudo ./scripts/setup_droplet.sh
   ```

4. The script will:
   - Install all necessary dependencies
   - Set up SSL certificates with Let's Encrypt
   - Configure Nginx as a reverse proxy
   - Start all services with Docker Compose
   - Set up automatic SSL renewal

## API Documentation

Once running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Data Sources

OpenDOGE integrates with multiple government data sources:
- USAspending.gov API
- Treasury Fiscal Data API
- Federal Reserve Economic Data (FRED)
- SEC EDGAR
- SAM.gov
- Federal Procurement Data System (FPDS)
- Federal Subaward Reporting System (FSRS)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
black .
isort .
flake8
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository.
