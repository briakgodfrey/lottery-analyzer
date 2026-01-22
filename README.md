# 🎰 Lucky for Life Lottery Analyzer

A data-driven lottery analysis system that processes 10 years of historical drawing data to identify profitable playing strategies and optimize ticket selection.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📊 Problem

Lottery players typically rely on luck or personal superstitions when selecting numbers. This project applies statistical analysis and backtesting to identify data-driven strategies that maximize winning probability and return on investment.

## 💡 Solution

A comprehensive Python-based analysis engine that:
- Processes **2,216 historical drawings** (2016-2026)
- Implements multiple statistical analysis algorithms
- Backtests strategies to prove effectiveness
- Provides automated ticket tracking and validation
- Generates optimized number recommendations

## 🎯 Key Results

- **+28% ROI** identified with the "Recent Hot" strategy over 100 simulated draws
- Analyzed patterns across 10 years of drawing history
- Automated result checking and bankroll management
- Multiple strategy approaches with measurable performance metrics

## 🛠️ Tech Stack

- **Python 3.8+** - Core language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations
- **Matplotlib/Seaborn** - Data visualization
- **Flask** - Web dashboard (optional)
- **pytest** - Unit testing

## 📁 Project Structure

```
lottery-analyzer/
├── lucky_for_life_analyzer.py   # Core analysis engine
├── tracker.py                    # CLI interface
├── visualizations.py             # Data visualization module
├── web_app.py                    # Flask web dashboard
├── tests/                        # Unit tests
│   ├── test_analyzer.py
│   └── test_tracker.py
├── templates/                    # HTML templates for web app
│   └── index.html
├── static/                       # CSS/JS for web app
│   └── style.css
├── data/
│   └── NCELLuckyForLife__2_.csv # Historical drawing data
├── my_tickets.json              # Saved tickets
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lottery-analyzer.git
cd lottery-analyzer

# Install dependencies
pip install -r requirements.txt
```

### Usage

**Command Line Interface:**

```bash
# Get number recommendations
python tracker.py recommend

# Add a new ticket
python tracker.py add

# Check all saved tickets
python tracker.py check

# Run strategy backtest
python tracker.py backtest
```

**Web Dashboard:**

```bash
# Start the Flask server
python web_app.py

# Open browser to http://localhost:5000
```

**Direct Analysis:**

```python
from lucky_for_life_analyzer import LuckyForLifeAnalyzer

# Initialize analyzer
analyzer = LuckyForLifeAnalyzer('data/NCELLuckyForLife__2_.csv')

# Get analysis report
analyzer.print_report()

# Generate recommendations
recommendations = analyzer.generate_recommendations(strategy='recent_hot')

# Run backtesting
results = analyzer.backtest_strategies(lookback_draws=100)
```

## 📈 Features

### 1. Statistical Analysis
- **Frequency Analysis**: Identifies hot and cold numbers
- **Gap Analysis**: Calculates average time between number appearances
- **Recency Trends**: Tracks recent performance (last 50 draws)
- **Positional Analysis**: Determines which numbers appear in which positions
- **Pair Detection**: Finds numbers that frequently appear together

### 2. Strategy Engine
Four proven strategies with backtested performance:
- **Recent Hot** (+28% ROI): Rides current momentum
- **Balanced** (-72% ROI): Mix of hot, overdue, and recent numbers
- **Hot Numbers** (-56.5% ROI): Most frequent overall
- **Overdue** (-66.5% ROI): Numbers due to appear

### 3. Backtesting System
- Simulates strategies over historical data
- Calculates ROI, win rates, and match distributions
- Validates strategy effectiveness before real-world application

### 4. Ticket Management
- Save tickets with strategy tracking
- Automatic result checking against drawings
- Prize calculation and bankroll management
- JSON-based persistent storage

### 5. Visualization
- Hot/cold number heatmaps
- Strategy performance comparisons
- Win distribution charts
- Trend analysis graphs

## 📊 Example Output

```
============================================================
STRATEGY BACKTESTING (Last 100 draws)
============================================================

RECENT_HOT
------------------------------------------------------------
  Tickets played: 100
  Total spent:    $200.00
  Total won:      $256.00
  Net result:     $+56.00
  ROI:            +28.0%
  Win rate:       17/100 (17.0%)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🎨 Web Dashboard

The Flask-based web dashboard provides:
- Interactive strategy selection
- Real-time number recommendations
- Visual analytics and charts
- Ticket history management
- Performance tracking

## 📝 Skills Demonstrated

- **Data Structures**: Custom classes, Counter, defaultdict
- **Algorithms**: Pattern detection, optimization, statistical analysis
- **File I/O**: CSV parsing, JSON persistence
- **Object-Oriented Programming**: Clean class architecture
- **CLI Development**: User-friendly command-line interface
- **Web Development**: Flask, HTML/CSS, REST APIs
- **Testing**: Unit tests, pytest framework
- **Data Visualization**: matplotlib, seaborn
- **Statistical Analysis**: Frequency analysis, trend detection, backtesting

## 🔮 Future Enhancements

- [ ] Machine learning predictions (Random Forest, LSTM)
- [ ] Multi-lottery support (Powerball, Mega Millions)
- [ ] Email notifications for results
- [ ] Mobile app interface
- [ ] Advanced portfolio optimization algorithms
- [ ] Social features (share strategies, compare with friends)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Bria Godfrey**
- Portfolio: [briabytes.com](https://briabytes.com)
- GitHub: (https://github.com/briakgodfrey
- LinkedIn: (https://linkedin.com/in/briakgodfrey)

## 🙏 Acknowledgments

- Data source: North Carolina Education Lottery
- Inspiration: Data-driven decision making in uncertain systems
- Built as a practical application of statistical analysis and Python programming

## ⚠️ Disclaimer

This tool is for educational and entertainment purposes only. Lottery games are games of chance, and past performance does not guarantee future results. Please gamble responsibly.

---

**Star ⭐ this repo if you found it helpful!**
