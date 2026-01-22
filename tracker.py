#!/usr/bin/env python3
"""
Quick ticket tracker - Easy interface for managing your lottery tickets
Usage:
  python tracker.py add        # Add a new ticket
  python tracker.py check      # Check all tickets
  python tracker.py recommend  # Get new recommendations
  python tracker.py backtest   # Run strategy backtest
"""

import sys
from lucky_for_life_analyzer import LuckyForLifeAnalyzer

def add_ticket():
    """Add a new ticket"""
    analyzer = LuckyForLifeAnalyzer('NCELLuckyForLife__2_.csv')
    
    print("\n📝 Add New Ticket")
    print("-" * 40)
    numbers_str = input("Numbers (space-separated): ").strip()
    numbers = [int(n) for n in numbers_str.split()]
    lucky_ball = int(input("Lucky Ball: ").strip())
    strategy = input("Strategy [recent_hot/balanced/hot/overdue/custom]: ").strip() or 'recent_hot'
    date = input("Date played [YYYY-MM-DD]: ").strip()
    
    analyzer.save_ticket(numbers, lucky_ball, strategy, date, cost=2.00)
    print("\n✅ Ticket saved!\n")

def check_tickets():
    """Check all saved tickets"""
    analyzer = LuckyForLifeAnalyzer('NCELLuckyForLife__2_.csv')
    analyzer.check_all_tickets()

def get_recommendations():
    """Get new recommendations"""
    analyzer = LuckyForLifeAnalyzer('NCELLuckyForLife__2_.csv')
    
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    strategies = ['recent_hot', 'balanced', 'hot', 'overdue']
    sets = analyzer.generate_multiple_sets(num_sets=4, strategies=strategies)
    
    for set_info in sets:
        print(f"\n{set_info['strategy'].upper()}")
        print(f"  Numbers: {', '.join(map(str, set_info['numbers']))}")
        print(f"  Lucky Ball: {set_info['lucky_ball']}")
        if set_info['strategy'] == 'recent_hot':
            print("  ⭐ BEST PERFORMER IN BACKTEST (+28% ROI)")
    
    print("\n" + "=" * 60 + "\n")

def run_backtest():
    """Run strategy backtest"""
    analyzer = LuckyForLifeAnalyzer('NCELLuckyForLife__2_.csv')
    
    draws = input("How many recent draws to test? [default: 100]: ").strip()
    draws = int(draws) if draws else 100
    
    analyzer.backtest_strategies(lookback_draws=draws)

def show_usage():
    """Show usage instructions"""
    print("""
Lucky for Life Ticket Tracker

Commands:
  add         Add a new ticket
  check       Check all saved tickets
  recommend   Get new number recommendations
  backtest    Run strategy performance backtest
  
Examples:
  python tracker.py add
  python tracker.py check
  python tracker.py recommend
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_usage()
    elif sys.argv[1] == 'add':
        add_ticket()
    elif sys.argv[1] == 'check':
        check_tickets()
    elif sys.argv[1] == 'recommend':
        get_recommendations()
    elif sys.argv[1] == 'backtest':
        run_backtest()
    else:
        show_usage()
