# Setup Instructions

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/lottery-analyzer.git
cd lottery-analyzer
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Data Directory
```bash
mkdir -p data
# Copy your NCELLuckyForLife__2_.csv file to the data/ directory
cp /path/to/NCELLuckyForLife__2_.csv data/
```

### 5. Run the Application

**Command Line Interface:**
```bash
# Get recommendations
python tracker.py recommend

# Add a ticket
python tracker.py add

# Check tickets
python tracker.py check

# Run backtest
python tracker.py backtest
```

**Web Dashboard:**
```bash
python web_app.py
# Then open http://localhost:5000 in your browser
```

**Generate Visualizations:**
```bash
python visualizations.py
# Visualizations will be saved to visualizations/ directory
```

### 6. Run Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # On Mac
# Or: xdg-open htmlcov/index.html  # On Linux
```

## Project Structure

```
lottery-analyzer/
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── SETUP.md                     # This file
│
├── lucky_for_life_analyzer.py   # Core analysis engine
├── tracker.py                    # CLI interface
├── visualizations.py             # Data visualization module
├── web_app.py                    # Flask web dashboard
│
├── data/                         # Data directory
│   └── NCELLuckyForLife__2_.csv # Historical drawing data
│
├── templates/                    # HTML templates for Flask
│   └── index.html
│
├── static/                       # CSS/JS for web app
│   └── style.css
│
├── tests/                        # Unit tests
│   └── test_analyzer.py
│
├── visualizations/               # Generated charts (created on first run)
│   ├── hot_cold_numbers.png
│   ├── strategy_performance.png
│   └── ...
│
└── my_tickets.json              # Your saved tickets (created on first save)
```

## Troubleshooting

### "No module named 'pandas'"
Install dependencies: `pip install -r requirements.txt`

### "FileNotFoundError: data/NCELLuckyForLife__2_.csv"
Make sure to create the `data/` directory and copy your CSV file there.

### "Port 5000 is already in use"
Change the port in `web_app.py` line 103: `app.run(debug=True, port=5001)`

### Permission denied when running scripts
Make scripts executable: `chmod +x *.py`

## Development

### Adding New Strategies
1. Open `lucky_for_life_analyzer.py`
2. Add new strategy case in `generate_recommendations()` method
3. Add tests in `tests/test_analyzer.py`
4. Run tests: `pytest`

### Updating Data
Replace `data/NCELLuckyForLife__2_.csv` with updated drawing data.
The format must match: Date, Number 1-5, Lucky Ball

### Contributing
Pull requests are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Data Sources

Drawing data from: North Carolina Education Lottery
https://www.nclottery.com/

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: [your email]
- Portfolio: https://briabytes.com

## License

MIT License - see LICENSE file for details
