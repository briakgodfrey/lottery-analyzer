#!/usr/bin/env python3
"""
Flask Web Application for Lucky for Life Analyzer
Provides web-based interface for lottery analysis
"""

from flask import Flask, render_template, jsonify, request
from lucky_for_life_analyzer import LuckyForLifeAnalyzer
import json
import os

app = Flask(__name__)

# Initialize analyzer
ANALYZER = LuckyForLifeAnalyzer('data/NCELLuckyForLife__2_.csv')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    main_freq, lucky_freq = ANALYZER.frequency_analysis()
    recent_main, recent_lucky = ANALYZER.recent_analysis()
    
    # Top 10 hot numbers
    hot_numbers = [{'number': num, 'count': count} 
                   for num, count in main_freq.most_common(10)]
    
    # Bottom 10 cold numbers
    cold_numbers = [{'number': num, 'count': count} 
                    for num, count in sorted(main_freq.items(), key=lambda x: x[1])[:10]]
    
    # Recent hot
    recent_hot = [{'number': num, 'count': count} 
                  for num, count in recent_main.most_common(10)]
    
    # Lucky ball stats
    lucky_hot = [{'number': num, 'count': count} 
                 for num, count in lucky_freq.most_common(5)]
    
    return jsonify({
        'hot_numbers': hot_numbers,
        'cold_numbers': cold_numbers,
        'recent_hot': recent_hot,
        'lucky_hot': lucky_hot,
        'total_draws': len(ANALYZER.df)
    })

@app.route('/api/recommendations/<strategy>')
def get_recommendations(strategy):
    """Get number recommendations for a specific strategy"""
    try:
        rec = ANALYZER.generate_recommendations(strategy)
        return jsonify({
            'success': True,
            'numbers': rec['main_numbers'],
            'lucky_ball': rec['lucky_ball'][0],
            'strategy': rec['reasoning']['strategy']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/backtest')
def run_backtest():
    """Run strategy backtesting"""
    lookback = request.args.get('lookback', default=100, type=int)
    
    strategies = ['balanced', 'hot', 'overdue', 'recent_hot']
    results = {}
    
    # Run simplified backtest for web
    backtest_results = ANALYZER.backtest_strategies(lookback_draws=lookback, strategies=strategies)
    
    for strategy in strategies:
        data = backtest_results[strategy]
        tickets = data['tickets']
        total_cost = tickets * 2.00
        total_prize = data['total_prize']
        net = total_prize - total_cost
        roi = ((total_prize / total_cost - 1) * 100) if total_cost > 0 else 0
        
        results[strategy] = {
            'tickets': tickets,
            'spent': total_cost,
            'won': total_prize,
            'net': net,
            'roi': roi,
            'wins': data['wins'],
            'win_rate': (data['wins'] / tickets * 100) if tickets > 0 else 0
        }
    
    return jsonify(results)

@app.route('/api/tickets', methods=['GET', 'POST'])
def manage_tickets():
    """Manage saved tickets"""
    ticket_file = 'my_tickets.json'
    
    if request.method == 'GET':
        # Return saved tickets
        if os.path.exists(ticket_file):
            with open(ticket_file, 'r') as f:
                tickets = json.load(f)
            return jsonify({'success': True, 'tickets': tickets})
        return jsonify({'success': True, 'tickets': []})
    
    elif request.method == 'POST':
        # Save a new ticket
        data = request.json
        
        ticket = {
            'date_played': data.get('date'),
            'numbers': sorted(data.get('numbers', [])),
            'lucky_ball': data.get('lucky_ball'),
            'strategy': data.get('strategy'),
            'cost': 2.00,
            'result': None,
            'winnings': 0.00
        }
        
        # Load existing tickets
        tickets = []
        if os.path.exists(ticket_file):
            with open(ticket_file, 'r') as f:
                tickets = json.load(f)
        
        tickets.append(ticket)
        
        # Save updated tickets
        with open(ticket_file, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        return jsonify({'success': True, 'ticket': ticket})

@app.route('/api/jackpot-coverage')
def get_jackpot_coverage():
    """Get jackpot-optimized ticket portfolio"""
    budget = request.args.get('budget', default=10.0, type=float)
    num_tickets = int(budget / 2.00)
    
    tickets = ANALYZER.generate_jackpot_coverage(num_tickets=num_tickets, budget=budget)
    
    return jsonify({
        'success': True,
        'tickets': tickets,
        'total_cost': len(tickets) * 2.00,
        'remaining': budget - (len(tickets) * 2.00)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎰 LUCKY FOR LIFE ANALYZER - WEB DASHBOARD")
    print("="*60)
    print("\n🌐 Starting server at http://localhost:5000")
    print("📊 Dashboard will open automatically\n")
    print("Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
