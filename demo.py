#!/usr/bin/env python3
"""
Quick Demo Script - Shows off all features
Run this to see the analyzer in action!
"""

from lucky_for_life_analyzer import LuckyForLifeAnalyzer
from visualizations import LotteryVisualizer
import os


def print_banner(text):
    """Print a fancy banner"""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")


def main():
    print_banner("🎰 LUCKY FOR LIFE ANALYZER DEMO")
    
    # Initialize
    print("📊 Loading historical data...")
    analyzer = LuckyForLifeAnalyzer('data/NCELLuckyForLife__2_.csv')
    print(f"✅ Loaded {len(analyzer.df)} drawings\n")
    
    # Show basic stats
    print_banner("QUICK STATISTICS")
    main_freq, lucky_freq = analyzer.frequency_analysis()
    
    print("🔥 Top 5 Hot Numbers:")
    for num, count in main_freq.most_common(5):
        print(f"   {num:2d} - appeared {count} times")
    
    print("\n❄️  Bottom 5 Cold Numbers:")
    for num, count in sorted(main_freq.items(), key=lambda x: x[1])[:5]:
        print(f"   {num:2d} - appeared {count} times")
    
    # Get recommendations
    print_banner("NUMBER RECOMMENDATIONS")
    
    strategies = ['recent_hot', 'balanced', 'hot']
    for strategy in strategies:
        rec = analyzer.generate_recommendations(strategy)
        print(f"📌 {strategy.upper().replace('_', ' ')}:")
        print(f"   Numbers: {', '.join(map(str, rec['main_numbers']))}")
        print(f"   Lucky Ball: {rec['lucky_ball'][0]}")
        print()
    
    # Run quick backtest
    print_banner("STRATEGY PERFORMANCE")
    print("⏳ Running backtest on last 100 draws...\n")
    
    results = analyzer.backtest_strategies(lookback_draws=100, strategies=['recent_hot', 'balanced'])
    
    print("\n📊 Results:")
    for strategy in ['recent_hot', 'balanced']:
        data = results[strategy]
        total_cost = data['tickets'] * 2.00
        net = data['total_prize'] - total_cost
        roi = ((data['total_prize'] / total_cost - 1) * 100) if total_cost > 0 else 0
        
        print(f"\n{strategy.upper().replace('_', ' ')}:")
        print(f"   ROI: {roi:+.1f}%")
        print(f"   Net: ${net:+.2f}")
        print(f"   Wins: {data['wins']}/{data['tickets']}")
    
    # Generate visualizations
    print_banner("GENERATING VISUALIZATIONS")
    print("🎨 Creating charts and graphs...\n")
    
    visualizer = LotteryVisualizer(analyzer)
    
    # Generate a few key visualizations
    print("📊 Hot/Cold numbers chart...")
    visualizer.plot_hot_cold_numbers()
    
    print("📈 Recent trends...")
    visualizer.plot_recent_trends()
    
    print("🍀 Lucky ball distribution...")
    visualizer.plot_lucky_ball_distribution()
    
    print_banner("DEMO COMPLETE!")
    
    print("✅ All done! Check out:")
    print("   • visualizations/ directory for charts")
    print("   • Run 'python tracker.py recommend' for new picks")
    print("   • Run 'python web_app.py' for web dashboard")
    print("   • Run 'pytest' to verify everything works\n")
    
    print("🚀 Ready to add to your portfolio!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
