# OpenDOGE (Open Data on Government Expenditure)

<p align="center">
  <img src="banner.png" alt="OpenDOGE Banner" width="100%">
</p>

An open-source platform for analyzing and visualizing government spending data.

## Features

- Integration with USAspending.gov API
- Federal spending analysis and visualization
- Contract and grant award tracking
- Agency spending patterns analysis
- State-by-state spending breakdown
- Anomaly detection in spending patterns

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/opendoge.git
cd opendoge
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Project Structure

```
opendoge/
├── app/                    # Main application package
│   ├── api/               # API endpoints and dependencies
│   │   ├── endpoints/     # API route handlers
│   │   └── dependencies.py
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   └── logging.py     # Logging setup
│   ├── models/            # Database models and schemas
│   │   └── schemas/       # Pydantic models
│   ├── services/          # Business logic
│   │   ├── scrapers/      # Data collection services
│   │   └── analysis/      # Data analysis services
│   └── utils/             # Utility functions
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── data/                 # Data storage
    ├── raw/              # Raw data
    └── processed/        # Processed data
```

## Development

1. Run tests:
```bash
pytest
```

2. Format code:
```bash
black .
isort .
```

3. Type checking:
```bash
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
