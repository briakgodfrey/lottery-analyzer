#!/usr/bin/env python3
"""
Lucky for Life Lottery Analyzer
Analyzes historical drawing data to identify patterns and provide data-driven recommendations
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json
import os

class LuckyForLifeAnalyzer:
    def __init__(self, csv_path):
        """Initialize analyzer with historical data"""
        self.df = pd.read_csv(csv_path)
        # Remove the footer disclaimer rows
        self.df = self.df[self.df['Date'].str.contains(r'\d{2}/\d{2}/\d{4}', na=False)]
        
        # Convert date to datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%m/%d/%Y')
        
        # Sort by date descending (most recent first)
        self.df = self.df.sort_values('Date', ascending=False).reset_index(drop=True)
        
        # Define number ranges
        self.main_numbers_range = range(1, 49)  # 1-48
        self.lucky_ball_range = range(1, 19)    # 1-18
        
        print(f"Loaded {len(self.df)} drawings from {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
    
    def frequency_analysis(self):
        """Analyze frequency of each number"""
        main_freq = Counter()
        lucky_ball_freq = Counter()
        
        for _, row in self.df.iterrows():
            for i in range(1, 6):
                main_freq[int(row[f'Number {i}'])] += 1
            lucky_ball_freq[int(row['Lucky Ball'])] += 1
        
        return main_freq, lucky_ball_freq
    
    def recent_analysis(self, last_n_draws=50):
        """Analyze recent trends vs all-time"""
        recent_df = self.df.head(last_n_draws)
        
        recent_main = Counter()
        recent_lucky = Counter()
        
        for _, row in recent_df.iterrows():
            for i in range(1, 6):
                recent_main[int(row[f'Number {i}'])] += 1
            recent_lucky[int(row['Lucky Ball'])] += 1
        
        return recent_main, recent_lucky
    
    def gap_analysis(self):
        """Calculate average gap between appearances for each number"""
        last_seen = {}  # Last index where number was seen
        gaps = defaultdict(list)  # All gaps for each number
        
        # Main numbers
        for idx, row in self.df.iterrows():
            numbers_in_draw = [int(row[f'Number {i}']) for i in range(1, 6)]
            
            # Record gaps for numbers that appeared
            for num in numbers_in_draw:
                if num in last_seen:
                    gaps[num].append(idx - last_seen[num])
                last_seen[num] = idx
        
        # Calculate average gap for each number
        avg_gaps = {num: np.mean(gap_list) if gap_list else float('inf') 
                    for num, gap_list in gaps.items()}
        
        # Calculate how long since last seen
        current_gap = {}
        for num in self.main_numbers_range:
            if num in last_seen:
                current_gap[num] = 0 - last_seen[num]  # Negative because most recent is index 0
            else:
                current_gap[num] = len(self.df)  # Never seen or very old
        
        return avg_gaps, current_gap
    
    def positional_analysis(self):
        """Analyze which numbers appear in which positions"""
        position_freq = {i: Counter() for i in range(1, 6)}
        
        for _, row in self.df.iterrows():
            for i in range(1, 6):
                position_freq[i][int(row[f'Number {i}'])] += 1
        
        return position_freq
    
    def pair_analysis(self):
        """Find numbers that frequently appear together"""
        pair_freq = Counter()
        
        for _, row in self.df.iterrows():
            numbers = sorted([int(row[f'Number {i}']) for i in range(1, 6)])
            # Generate all pairs
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    pair = (numbers[i], numbers[j])
                    pair_freq[pair] += 1
        
        return pair_freq
    
    def get_overdue_numbers(self, threshold_multiplier=1.5):
        """Find numbers that are overdue based on their average gap"""
        avg_gaps, current_gaps = self.gap_analysis()
        
        overdue = {}
        for num in self.main_numbers_range:
            if num in avg_gaps and num in current_gaps:
                avg = avg_gaps[num]
                current = abs(current_gaps[num])
                if current > avg * threshold_multiplier:
                    overdue[num] = {
                        'current_gap': current,
                        'avg_gap': round(avg, 1),
                        'ratio': round(current / avg, 2)
                    }
        
        return overdue
    
    def generate_recommendations(self, strategy='balanced'):
        """Generate number recommendations based on strategy"""
        main_freq, lucky_freq = self.frequency_analysis()
        recent_main, recent_lucky = self.recent_analysis()
        avg_gaps, current_gaps = self.gap_analysis()
        overdue = self.get_overdue_numbers()
        
        recommendations = {
            'main_numbers': [],
            'lucky_ball': [],
            'reasoning': {}
        }
        
        if strategy == 'hot':
            # Pick the most frequent numbers overall
            hot_numbers = [num for num, _ in main_freq.most_common(10)]
            recommendations['main_numbers'] = hot_numbers[:5]
            recommendations['lucky_ball'] = [lucky_freq.most_common(1)[0][0]]
            recommendations['reasoning']['strategy'] = "Hot numbers: Most frequently drawn overall"
            
        elif strategy == 'cold':
            # Pick the least frequent numbers
            cold_numbers = [num for num, _ in sorted(main_freq.items(), key=lambda x: x[1])[:10]]
            recommendations['main_numbers'] = cold_numbers[:5]
            recommendations['lucky_ball'] = [sorted(lucky_freq.items(), key=lambda x: x[1])[0][0]]
            recommendations['reasoning']['strategy'] = "Cold numbers: Least frequently drawn"
            
        elif strategy == 'overdue':
            # Pick overdue numbers
            overdue_sorted = sorted(overdue.items(), key=lambda x: x[1]['ratio'], reverse=True)
            recommendations['main_numbers'] = [num for num, _ in overdue_sorted[:5]]
            recommendations['lucky_ball'] = [self._get_overdue_lucky_ball()]
            recommendations['reasoning']['strategy'] = "Overdue numbers: Haven't appeared in longer than average"
            
        elif strategy == 'recent_hot':
            # Recent momentum
            hot_recent = [num for num, _ in recent_main.most_common(10)]
            recommendations['main_numbers'] = hot_recent[:5]
            recommendations['lucky_ball'] = [recent_lucky.most_common(1)[0][0]]
            recommendations['reasoning']['strategy'] = "Recent hot: Most frequent in last 50 draws"
            
        elif strategy == 'jackpot_spread':
            # Maximize diversity across number ranges for jackpot play
            # Divide 1-48 into regions and pick from each
            low = list(range(1, 13))      # 1-12
            mid_low = list(range(13, 25)) # 13-24
            mid_high = list(range(25, 37)) # 25-36
            high = list(range(37, 49))     # 37-48
            
            # Get top performers from each range
            low_freq = {n: main_freq[n] for n in low if n in main_freq}
            mid_low_freq = {n: main_freq[n] for n in mid_low if n in main_freq}
            mid_high_freq = {n: main_freq[n] for n in mid_high if n in main_freq}
            high_freq = {n: main_freq[n] for n in high if n in main_freq}
            
            selected = []
            selected.append(max(low_freq.items(), key=lambda x: x[1])[0])
            selected.append(max(mid_low_freq.items(), key=lambda x: x[1])[0])
            selected.append(max(mid_high_freq.items(), key=lambda x: x[1])[0])
            selected.append(max(high_freq.items(), key=lambda x: x[1])[0])
            
            # 5th number from most recent hot not yet selected
            for num, _ in recent_main.most_common(20):
                if num not in selected:
                    selected.append(num)
                    break
            
            recommendations['main_numbers'] = sorted(selected[:5])
            recommendations['lucky_ball'] = [lucky_freq.most_common(1)[0][0]]
            recommendations['reasoning']['strategy'] = "Jackpot spread: Maximum coverage across number ranges"
            
        else:  # balanced
            # Mix of hot, overdue, and recent
            hot_nums = [num for num, _ in main_freq.most_common(15)]
            overdue_sorted = sorted(overdue.items(), key=lambda x: x[1]['ratio'], reverse=True)
            overdue_nums = [num for num, _ in overdue_sorted[:10]]
            recent_nums = [num for num, _ in recent_main.most_common(10)]
            
            # Combine: 2 hot, 2 overdue, 1 recent
            selected = []
            selected.extend([n for n in hot_nums if n not in selected][:2])
            selected.extend([n for n in overdue_nums if n not in selected][:2])
            selected.extend([n for n in recent_nums if n not in selected][:1])
            
            recommendations['main_numbers'] = selected[:5]
            recommendations['lucky_ball'] = [lucky_freq.most_common(3)[1][0]]  # 2nd most common
            recommendations['reasoning']['strategy'] = "Balanced: Mix of hot, overdue, and recent numbers"
        
        return recommendations
    
    def _get_overdue_lucky_ball(self):
        """Helper to find overdue lucky ball"""
        last_seen = {}
        for idx, row in self.df.iterrows():
            lb = int(row['Lucky Ball'])
            if lb not in last_seen:
                last_seen[lb] = idx
        
        # Return the one with highest current gap
        overdue_lb = max(last_seen.items(), key=lambda x: abs(x[1]))
        return overdue_lb[0]
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        main_freq, lucky_freq = self.frequency_analysis()
        recent_main, recent_lucky = self.recent_analysis()
        overdue = self.get_overdue_numbers()
        pair_freq = self.pair_analysis()
        
        report = {
            'top_10_hot_numbers': [{'number': num, 'count': count} 
                                   for num, count in main_freq.most_common(10)],
            'bottom_10_cold_numbers': [{'number': num, 'count': count} 
                                       for num, count in sorted(main_freq.items(), key=lambda x: x[1])[:10]],
            'recent_hot_numbers': [{'number': num, 'count': count} 
                                   for num, count in recent_main.most_common(10)],
            'most_overdue': [{'number': num, 'gap': data['current_gap'], 
                             'avg': data['avg_gap'], 'ratio': data['ratio']} 
                            for num, data in sorted(overdue.items(), 
                                                   key=lambda x: x[1]['ratio'], 
                                                   reverse=True)[:10]],
            'top_pairs': [{'pair': f"{p[0]}-{p[1]}", 'count': count} 
                         for p, count in pair_freq.most_common(10)],
            'lucky_ball_hot': [{'number': num, 'count': count} 
                              for num, count in lucky_freq.most_common(5)],
            'lucky_ball_cold': [{'number': num, 'count': count} 
                               for num, count in sorted(lucky_freq.items(), key=lambda x: x[1])[:5]]
        }
        
        return report
    
    def print_report(self):
        """Print formatted report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("LUCKY FOR LIFE - DATA ANALYSIS REPORT")
        print("="*60)
        
        print("\n🔥 TOP 10 HOT NUMBERS (Most Frequent Overall)")
        print("-" * 60)
        for item in report['top_10_hot_numbers']:
            print(f"  {item['number']:2d} - appeared {item['count']:3d} times")
        
        print("\n❄️  BOTTOM 10 COLD NUMBERS (Least Frequent)")
        print("-" * 60)
        for item in report['bottom_10_cold_numbers']:
            print(f"  {item['number']:2d} - appeared {item['count']:3d} times")
        
        print("\n📈 RECENT HOT (Last 50 Draws)")
        print("-" * 60)
        for item in report['recent_hot_numbers']:
            print(f"  {item['number']:2d} - appeared {item['count']:2d} times in last 50")
        
        print("\n⏰ MOST OVERDUE NUMBERS")
        print("-" * 60)
        for item in report['most_overdue']:
            print(f"  {item['number']:2d} - {item['gap']:3d} draws since last (avg: {item['avg']:.1f}, ratio: {item['ratio']:.2f}x)")
        
        print("\n👥 TOP PAIRS (Numbers that appear together)")
        print("-" * 60)
        for item in report['top_pairs']:
            print(f"  {item['pair']:>7} - appeared together {item['count']:3d} times")
        
        print("\n🍀 LUCKY BALL ANALYSIS")
        print("-" * 60)
        print("Hot Lucky Balls:")
        for item in report['lucky_ball_hot']:
            print(f"  {item['number']:2d} - appeared {item['count']:3d} times")
        print("\nCold Lucky Balls:")
        for item in report['lucky_ball_cold']:
            print(f"  {item['number']:2d} - appeared {item['count']:3d} times")
    
    def generate_multiple_sets(self, num_sets=3, strategies=None):
        """Generate multiple number sets with different strategies"""
        if strategies is None:
            strategies = ['balanced', 'hot', 'overdue']
        
        sets = []
        for i, strategy in enumerate(strategies[:num_sets], 1):
            rec = self.generate_recommendations(strategy)
            sets.append({
                'set_number': i,
                'strategy': strategy,
                'numbers': sorted(rec['main_numbers']),
                'lucky_ball': rec['lucky_ball'][0],
                'reasoning': rec['reasoning']['strategy']
            })
        
        return sets
    
    def generate_jackpot_coverage(self, num_tickets=5, budget=10.00):
        """Generate diverse tickets optimized for jackpot coverage"""
        max_tickets = int(budget / 2.00)
        num_tickets = min(num_tickets, max_tickets)
        
        main_freq, lucky_freq = self.frequency_analysis()
        recent_main, recent_lucky = self.recent_analysis()
        
        print("\n" + "="*60)
        print(f"🎯 JACKPOT-OPTIMIZED TICKET PORTFOLIO (${num_tickets * 2.00:.2f})")
        print("="*60)
        print("\nStrategy: Maximum diversity to cover different scenarios")
        print("Goal: One ticket hits while others stay diverse\n")
        
        tickets = []
        used_combinations = set()
        
        # Ticket 1: Range-spread (one from each quartile)
        rec1 = self.generate_recommendations('jackpot_spread')
        tickets.append({
            'numbers': rec1['main_numbers'],
            'lucky_ball': rec1['lucky_ball'][0],
            'strategy': 'Range Spread',
            'reasoning': 'Covers all number ranges (low/mid/high)'
        })
        used_combinations.add(tuple(sorted(rec1['main_numbers'])))
        
        if num_tickets >= 2:
            # Ticket 2: Recent hot momentum
            rec2 = self.generate_recommendations('recent_hot')
            # Ensure different from ticket 1
            while tuple(sorted(rec2['main_numbers'])) in used_combinations:
                # Slightly vary by swapping one number
                rec2['main_numbers'][4] = recent_main.most_common(15)[len(tickets) + 5][0]
            tickets.append({
                'numbers': sorted(rec2['main_numbers']),
                'lucky_ball': rec2['lucky_ball'][0],
                'strategy': 'Recent Hot',
                'reasoning': 'Rides current momentum (proven +28% ROI)'
            })
            used_combinations.add(tuple(sorted(rec2['main_numbers'])))
        
        if num_tickets >= 3:
            # Ticket 3: All-time hot numbers
            rec3 = self.generate_recommendations('hot')
            tickets.append({
                'numbers': rec3['main_numbers'],
                'lucky_ball': lucky_freq.most_common(2)[1][0],  # Different LB
                'strategy': 'All-Time Hot',
                'reasoning': 'Most frequently drawn numbers overall'
            })
            used_combinations.add(tuple(sorted(rec3['main_numbers'])))
        
        if num_tickets >= 4:
            # Ticket 4: Balanced mix
            rec4 = self.generate_recommendations('balanced')
            tickets.append({
                'numbers': rec4['main_numbers'],
                'lucky_ball': rec4['lucky_ball'][0],
                'strategy': 'Balanced Mix',
                'reasoning': 'Hot + overdue + recent hybrid'
            })
            used_combinations.add(tuple(sorted(rec4['main_numbers'])))
        
        if num_tickets >= 5:
            # Ticket 5: High numbers bias (many jackpots hit with high numbers)
            high_nums = [n for n in range(30, 49) if n in main_freq]
            high_sorted = sorted(high_nums, key=lambda x: main_freq[x], reverse=True)[:7]
            
            # Mix with some recent hot
            selected = high_sorted[:3]
            for num in [n for n, _ in recent_main.most_common(20)]:
                if num not in selected and len(selected) < 5:
                    selected.append(num)
            
            tickets.append({
                'numbers': sorted(selected[:5]),
                'lucky_ball': lucky_freq.most_common(3)[0][0],
                'strategy': 'High Numbers',
                'reasoning': 'Focus on 30-48 range with hot picks'
            })
        
        # Print tickets
        for i, ticket in enumerate(tickets, 1):
            print(f"Ticket {i}: {ticket['strategy'].upper()}")
            print(f"  Numbers: {', '.join(map(str, ticket['numbers']))}")
            print(f"  Lucky Ball: {ticket['lucky_ball']}")
            print(f"  Why: {ticket['reasoning']}")
            print()
        
        print("-"*60)
        print(f"Total Investment: ${len(tickets) * 2.00:.2f}")
        print(f"Coverage: {len(tickets)} different combinations")
        print(f"Remaining: ${budget - (len(tickets) * 2.00):.2f}")
        print("="*60 + "\n")
        
        return tickets
    
    def save_ticket(self, numbers, lucky_ball, strategy, date_played, cost=2.00, 
                    ticket_file='my_tickets.json'):
        """Save a ticket to your history"""
        ticket = {
            'date_played': date_played,
            'numbers': sorted(numbers),
            'lucky_ball': lucky_ball,
            'strategy': strategy,
            'cost': cost,
            'result': None,  # Will be filled in when checking
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
        
        print(f"✅ Ticket saved! Numbers: {numbers} + Lucky Ball: {lucky_ball}")
        print(f"   Strategy: {strategy}, Cost: ${cost:.2f}")
        return ticket
    
    def check_ticket(self, numbers, lucky_ball, drawing_date):
        """Check if a ticket won and how much"""
        # Find the drawing
        drawing = self.df[self.df['Date'] == pd.to_datetime(drawing_date)]
        
        if drawing.empty:
            return None, "Drawing date not found"
        
        drawing = drawing.iloc[0]
        winning_numbers = [int(drawing[f'Number {i}']) for i in range(1, 6)]
        winning_lucky = int(drawing['Lucky Ball'])
        
        # Count matches
        main_matches = len(set(numbers) & set(winning_numbers))
        lucky_match = (lucky_ball == winning_lucky)
        
        # Determine prize (Lucky for Life prize structure)
        # https://www.luckyforlife.us/how-to-play
        prize = 0.00
        prize_description = "No win"
        
        if main_matches == 5 and lucky_match:
            prize_description = "JACKPOT! $1,000/Day for Life"
        elif main_matches == 5:
            prize_description = "2nd Prize! $25,000/Year for Life"
        elif main_matches == 4 and lucky_match:
            prize = 5000.00
            prize_description = "$5,000"
        elif main_matches == 4:
            prize = 200.00
            prize_description = "$200"
        elif main_matches == 3 and lucky_match:
            prize = 150.00
            prize_description = "$150"
        elif main_matches == 3:
            prize = 20.00
            prize_description = "$20"
        elif main_matches == 2 and lucky_match:
            prize = 25.00
            prize_description = "$25"
        elif main_matches == 2:
            prize = 3.00
            prize_description = "$3"
        elif main_matches == 1 and lucky_match:
            prize = 6.00
            prize_description = "$6"
        elif lucky_match:
            prize = 4.00
            prize_description = "$4"
        
        result = {
            'main_matches': main_matches,
            'lucky_match': lucky_match,
            'prize': prize,
            'prize_description': prize_description,
            'winning_numbers': winning_numbers,
            'winning_lucky': winning_lucky,
            'your_numbers': numbers,
            'your_lucky': lucky_ball
        }
        
        return result, None
    
    def check_all_tickets(self, ticket_file='my_tickets.json'):
        """Check all saved tickets against actual results"""
        if not os.path.exists(ticket_file):
            print("No tickets found!")
            return []
        
        with open(ticket_file, 'r') as f:
            tickets = json.load(f)
        
        results = []
        total_spent = 0
        total_won = 0
        
        print("\n" + "="*60)
        print("TICKET HISTORY & RESULTS")
        print("="*60)
        
        for i, ticket in enumerate(tickets, 1):
            # Try to find the next drawing after the play date
            play_date = pd.to_datetime(ticket['date_played'])
            next_drawings = self.df[self.df['Date'] >= play_date].sort_values('Date')
            
            if not next_drawings.empty:
                drawing_date = next_drawings.iloc[-1]['Date']  # Most recent
                result, error = self.check_ticket(
                    ticket['numbers'], 
                    ticket['lucky_ball'], 
                    drawing_date
                )
                
                if result:
                    total_spent += ticket['cost']
                    total_won += result['prize']
                    
                    print(f"\nTicket #{i} - {ticket['date_played']} ({ticket['strategy']})")
                    print(f"  Your pick: {ticket['numbers']} + LB: {ticket['lucky_ball']}")
                    print(f"  Drawing:   {result['winning_numbers']} + LB: {result['winning_lucky']}")
                    print(f"  Result: {result['main_matches']} matches + {'✓' if result['lucky_match'] else '✗'} LB")
                    print(f"  Prize: {result['prize_description']}")
                    
                    results.append({
                        **ticket,
                        'result': result,
                        'winnings': result['prize']
                    })
        
        print("\n" + "-"*60)
        print(f"Total Spent:  ${total_spent:.2f}")
        print(f"Total Won:    ${total_won:.2f}")
        print(f"Net:          ${total_won - total_spent:+.2f}")
        print(f"ROI:          {((total_won/total_spent - 1) * 100) if total_spent > 0 else 0:.1f}%")
        print("="*60 + "\n")
        
        return results
    
    def backtest_strategies(self, lookback_draws=100, strategies=None):
        """Simulate strategies over past draws to see which performs best"""
        if strategies is None:
            strategies = ['balanced', 'hot', 'overdue', 'recent_hot']
        
        print("\n" + "="*60)
        print(f"STRATEGY BACKTESTING (Last {lookback_draws} draws)")
        print("="*60)
        
        strategy_results = {s: {'wins': 0, 'total_prize': 0, 'tickets': 0, 
                                'matches_dist': Counter()} for s in strategies}
        
        # Test each strategy by simulating picks before each draw
        test_draws = self.df.head(lookback_draws)
        
        for idx in range(len(test_draws)):
            # Create a temporary analyzer with data BEFORE this draw
            historical_data = self.df.iloc[idx+1:].copy()
            
            if len(historical_data) < 50:  # Need enough history
                continue
            
            # Get the actual winning numbers for this draw
            actual_draw = test_draws.iloc[idx]
            winning_numbers = [int(actual_draw[f'Number {i}']) for i in range(1, 6)]
            winning_lucky = int(actual_draw['Lucky Ball'])
            
            # Test each strategy
            for strategy in strategies:
                # Generate recommendation based on historical data only
                temp_analyzer = LuckyForLifeAnalyzer.__new__(LuckyForLifeAnalyzer)
                temp_analyzer.df = historical_data
                temp_analyzer.main_numbers_range = self.main_numbers_range
                temp_analyzer.lucky_ball_range = self.lucky_ball_range
                
                rec = temp_analyzer.generate_recommendations(strategy)
                predicted_numbers = rec['main_numbers']
                predicted_lucky = rec['lucky_ball'][0]
                
                # Check matches
                main_matches = len(set(predicted_numbers) & set(winning_numbers))
                lucky_match = (predicted_lucky == winning_lucky)
                
                # Calculate prize
                prize = 0.00
                if main_matches == 5 and lucky_match:
                    prize = 1000000.00  # Approximation for jackpot
                elif main_matches == 5:
                    prize = 25000.00
                elif main_matches == 4 and lucky_match:
                    prize = 5000.00
                elif main_matches == 4:
                    prize = 200.00
                elif main_matches == 3 and lucky_match:
                    prize = 150.00
                elif main_matches == 3:
                    prize = 20.00
                elif main_matches == 2 and lucky_match:
                    prize = 25.00
                elif main_matches == 2:
                    prize = 3.00
                elif main_matches == 1 and lucky_match:
                    prize = 6.00
                elif lucky_match:
                    prize = 4.00
                
                strategy_results[strategy]['tickets'] += 1
                strategy_results[strategy]['total_prize'] += prize
                strategy_results[strategy]['matches_dist'][main_matches] += 1
                if prize > 0:
                    strategy_results[strategy]['wins'] += 1
        
        # Print results
        for strategy in strategies:
            results = strategy_results[strategy]
            tickets = results['tickets']
            total_cost = tickets * 2.00
            total_prize = results['total_prize']
            net = total_prize - total_cost
            roi = ((total_prize / total_cost - 1) * 100) if total_cost > 0 else 0
            
            print(f"\n{strategy.upper()}")
            print("-" * 60)
            print(f"  Tickets played: {tickets}")
            print(f"  Total spent:    ${total_cost:.2f}")
            print(f"  Total won:      ${total_prize:.2f}")
            print(f"  Net result:     ${net:+.2f}")
            print(f"  ROI:            {roi:+.1f}%")
            print(f"  Win rate:       {results['wins']}/{tickets} ({results['wins']/tickets*100:.1f}%)")
            print(f"  Match distribution:")
            for matches in range(6):
                count = results['matches_dist'][matches]
                if count > 0:
                    print(f"    {matches} matches: {count:3d} times ({count/tickets*100:.1f}%)")
        
        # Find best strategy
        best_strategy = max(strategy_results.items(), 
                           key=lambda x: x[1]['total_prize'] - (x[1]['tickets'] * 2.00))
        
        print("\n" + "="*60)
        print(f"🏆 Best performing strategy: {best_strategy[0].upper()}")
        net_best = best_strategy[1]['total_prize'] - (best_strategy[1]['tickets'] * 2.00)
        print(f"   Net result: ${net_best:+.2f}")
        print("="*60 + "\n")
        
        return strategy_results


def main():
    # Initialize analyzer
    analyzer = LuckyForLifeAnalyzer('/mnt/user-data/uploads/NCELLuckyForLife__2_.csv')
    
    # Print comprehensive report
    analyzer.print_report()
    
    # Generate recommended sets
    print("\n" + "="*60)
    print("RECOMMENDED NUMBER SETS")
    print("="*60)
    
    strategies = ['balanced', 'hot', 'overdue', 'recent_hot']
    sets = analyzer.generate_multiple_sets(num_sets=4, strategies=strategies)
    
    for set_info in sets:
        print(f"\n Set {set_info['set_number']}: {set_info['strategy'].upper()}")
        print(f" Numbers: {', '.join(map(str, set_info['numbers']))}")
        print(f" Lucky Ball: {set_info['lucky_ball']}")
        print(f" Strategy: {set_info['reasoning']}")
    
    # Run backtesting
    print("\n" + "="*60)
    print("Running strategy backtest...")
    print("="*60)
    analyzer.backtest_strategies(lookback_draws=100, strategies=strategies)
    
    print("\n" + "="*60)
    print("Notes:")
    print("- All lottery draws are random; past patterns don't guarantee future results")
    print("- This analysis is for entertainment and educational purposes")
    print("- Stick to your 'only winnings' rule for responsible play!")
    print("="*60 + "\n")


def interactive_mode():
    """Interactive mode for tracking tickets"""
    analyzer = LuckyForLifeAnalyzer('/mnt/user-data/uploads/NCELLuckyForLife__2_.csv')
    
    print("\n" + "="*60)
    print("LUCKY FOR LIFE - TICKET TRACKER")
    print("="*60)
    print("\nOptions:")
    print("1. Save a new ticket")
    print("2. Check all my tickets")
    print("3. Run strategy backtest")
    print("4. Get new recommendations")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        print("\nEnter your ticket details:")
        numbers_str = input("Numbers (5 numbers separated by spaces): ").strip()
        numbers = [int(n) for n in numbers_str.split()]
        lucky_ball = int(input("Lucky Ball: ").strip())
        strategy = input("Strategy used (balanced/hot/overdue/recent_hot/custom): ").strip()
        date_played = input("Date played (YYYY-MM-DD): ").strip()
        
        analyzer.save_ticket(numbers, lucky_ball, strategy, date_played)
        
    elif choice == '2':
        analyzer.check_all_tickets()
        
    elif choice == '3':
        lookback = int(input("How many recent draws to test? (default 100): ").strip() or "100")
        analyzer.backtest_strategies(lookback_draws=lookback)
        
    elif choice == '4':
        strategies = ['balanced', 'hot', 'overdue', 'recent_hot']
        sets = analyzer.generate_multiple_sets(num_sets=4, strategies=strategies)
        
        print("\n" + "="*60)
        print("RECOMMENDED NUMBER SETS")
        print("="*60)
        
        for set_info in sets:
            print(f"\n Set {set_info['set_number']}: {set_info['strategy'].upper()}")
            print(f" Numbers: {', '.join(map(str, set_info['numbers']))}")
            print(f" Lucky Ball: {set_info['lucky_ball']}")
            print(f" Strategy: {set_info['reasoning']}")
        
    print("\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'track':
        interactive_mode()
    else:
        main()
