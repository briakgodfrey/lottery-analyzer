#!/usr/bin/env python3
"""
Data Visualization Module for Lucky for Life Analyzer
Creates charts and graphs for analysis results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class LotteryVisualizer:
    """Generates visualizations for lottery analysis"""
    
    def __init__(self, analyzer):
        """Initialize with LuckyForLifeAnalyzer instance"""
        self.analyzer = analyzer
        self.output_dir = 'visualizations'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def plot_hot_cold_numbers(self, save=True):
        """Plot hot and cold numbers as a bar chart"""
        main_freq, _ = self.analyzer.frequency_analysis()
        
        # Sort by frequency
        sorted_numbers = sorted(main_freq.items(), key=lambda x: x[1], reverse=True)
        numbers = [n for n, _ in sorted_numbers]
        frequencies = [f for _, f in sorted_numbers]
        
        # Create color gradient (hot = red, cold = blue)
        colors = plt.cm.RdYlBu_r(np.linspace(0, 1, len(numbers)))
        
        plt.figure(figsize=(14, 6))
        bars = plt.bar(range(len(numbers)), frequencies, color=colors)
        
        plt.xlabel('Numbers (sorted by frequency)', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title('Hot vs Cold Numbers (All Time)', fontsize=14, fontweight='bold')
        plt.xticks(range(0, len(numbers), 5), [numbers[i] for i in range(0, len(numbers), 5)])
        
        # Add value labels on top of bars for top 10 and bottom 10
        for i in range(10):
            plt.text(i, frequencies[i], str(numbers[i]), 
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        for i in range(len(numbers)-10, len(numbers)):
            plt.text(i, frequencies[i], str(numbers[i]), 
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/hot_cold_numbers.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/hot_cold_numbers.png")
        
        plt.close()
    
    def plot_strategy_performance(self, backtest_results, save=True):
        """Plot strategy performance comparison"""
        strategies = list(backtest_results.keys())
        
        # Calculate metrics
        net_results = []
        roi_percentages = []
        win_rates = []
        
        for strategy in strategies:
            results = backtest_results[strategy]
            tickets = results['tickets']
            total_cost = tickets * 2.00
            total_prize = results['total_prize']
            net = total_prize - total_cost
            roi = ((total_prize / total_cost - 1) * 100) if total_cost > 0 else 0
            win_rate = (results['wins'] / tickets * 100) if tickets > 0 else 0
            
            net_results.append(net)
            roi_percentages.append(roi)
            win_rates.append(win_rate)
        
        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Net Results
        colors = ['green' if x > 0 else 'red' for x in net_results]
        axes[0].bar(strategies, net_results, color=colors, alpha=0.7)
        axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        axes[0].set_title('Net Results ($)', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Dollars', fontsize=11)
        axes[0].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for i, v in enumerate(net_results):
            axes[0].text(i, v, f'${v:+.0f}', ha='center', 
                        va='bottom' if v > 0 else 'top', fontweight='bold')
        
        # ROI Percentage
        colors = ['green' if x > 0 else 'red' for x in roi_percentages]
        axes[1].bar(strategies, roi_percentages, color=colors, alpha=0.7)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        axes[1].set_title('Return on Investment (%)', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('ROI %', fontsize=11)
        axes[1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for i, v in enumerate(roi_percentages):
            axes[1].text(i, v, f'{v:+.1f}%', ha='center', 
                        va='bottom' if v > 0 else 'top', fontweight='bold')
        
        # Win Rates
        axes[2].bar(strategies, win_rates, color='steelblue', alpha=0.7)
        axes[2].set_title('Win Rate (%)', fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Win %', fontsize=11)
        axes[2].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for i, v in enumerate(win_rates):
            axes[2].text(i, v, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Strategy Performance Comparison (Last 100 Draws)', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/strategy_performance.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/strategy_performance.png")
        
        plt.close()
    
    def plot_recent_trends(self, last_n_draws=50, save=True):
        """Plot recent number trends"""
        recent_main, _ = self.analyzer.recent_analysis(last_n_draws=last_n_draws)
        
        # Get top 15 recent hot numbers
        top_recent = recent_main.most_common(15)
        numbers = [n for n, _ in top_recent]
        counts = [c for _, c in top_recent]
        
        plt.figure(figsize=(12, 6))
        bars = plt.barh(range(len(numbers)), counts, color='coral')
        
        plt.yticks(range(len(numbers)), [f'#{n}' for n in numbers])
        plt.xlabel(f'Appearances in Last {last_n_draws} Draws', fontsize=12, fontweight='bold')
        plt.ylabel('Number', fontsize=12, fontweight='bold')
        plt.title(f'Recent Hot Numbers (Last {last_n_draws} Draws)', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, v in enumerate(counts):
            plt.text(v, i, f' {v}', va='center', fontweight='bold')
        
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/recent_trends.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/recent_trends.png")
        
        plt.close()
    
    def plot_lucky_ball_distribution(self, save=True):
        """Plot Lucky Ball frequency distribution"""
        _, lucky_freq = self.analyzer.frequency_analysis()
        
        numbers = sorted(lucky_freq.keys())
        frequencies = [lucky_freq[n] for n in numbers]
        
        # Create color map
        colors = plt.cm.YlOrRd(np.array(frequencies) / max(frequencies))
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(numbers, frequencies, color=colors, edgecolor='black', linewidth=0.5)
        
        plt.xlabel('Lucky Ball Number', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title('Lucky Ball Distribution', fontsize=14, fontweight='bold')
        plt.xticks(numbers)
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels for top 5 and bottom 5
        sorted_indices = sorted(range(len(frequencies)), key=lambda i: frequencies[i], reverse=True)
        for i in sorted_indices[:5] + sorted_indices[-5:]:
            plt.text(numbers[i], frequencies[i], str(frequencies[i]), 
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/lucky_ball_distribution.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/lucky_ball_distribution.png")
        
        plt.close()
    
    def plot_number_heatmap(self, save=True):
        """Plot number frequency as a heatmap"""
        main_freq, _ = self.analyzer.frequency_analysis()
        
        # Create 6x8 grid (48 numbers)
        grid = np.zeros((6, 8))
        for num in range(1, 49):
            row = (num - 1) // 8
            col = (num - 1) % 8
            grid[row][col] = main_freq.get(num, 0)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(grid, annot=True, fmt='.0f', cmap='RdYlGn', 
                   cbar_kws={'label': 'Frequency'}, linewidths=0.5)
        
        # Create labels
        labels = [[str(i * 8 + j + 1) for j in range(8)] for i in range(6)]
        
        ax = plt.gca()
        for i in range(6):
            for j in range(8):
                text = ax.texts[i * 8 + j]
                num = int(labels[i][j])
                text.set_text(f'{num}\n({int(grid[i][j])})')
                text.set_fontsize(9)
                text.set_fontweight('bold')
        
        plt.title('Number Frequency Heatmap', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('', fontsize=12)
        plt.ylabel('', fontsize=12)
        plt.xticks([])
        plt.yticks([])
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/number_heatmap.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/number_heatmap.png")
        
        plt.close()
    
    def plot_match_distribution(self, backtest_results, save=True):
        """Plot distribution of matches for each strategy"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Match Distribution by Strategy', fontsize=14, fontweight='bold')
        
        strategies = list(backtest_results.keys())
        
        for idx, strategy in enumerate(strategies):
            ax = axes[idx // 2, idx % 2]
            
            matches_dist = backtest_results[strategy]['matches_dist']
            matches = list(range(6))
            counts = [matches_dist[m] for m in matches]
            
            colors = ['#d62728', '#ff7f0e', '#ffbb78', '#98df8a', '#2ca02c', '#1f77b4']
            bars = ax.bar(matches, counts, color=colors, alpha=0.7, edgecolor='black')
            
            ax.set_title(strategy.upper(), fontsize=12, fontweight='bold')
            ax.set_xlabel('Number of Matches', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_xticks(matches)
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(counts):
                if v > 0:
                    ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/match_distribution.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: {self.output_dir}/match_distribution.png")
        
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualizations at once"""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60 + "\n")
        
        # Hot/Cold numbers
        print("📊 Creating hot/cold numbers chart...")
        self.plot_hot_cold_numbers()
        
        # Recent trends
        print("📈 Creating recent trends chart...")
        self.plot_recent_trends()
        
        # Lucky ball distribution
        print("🍀 Creating lucky ball distribution...")
        self.plot_lucky_ball_distribution()
        
        # Number heatmap
        print("🔥 Creating number frequency heatmap...")
        self.plot_number_heatmap()
        
        # Strategy performance (requires backtesting)
        print("🎯 Running backtest and creating performance charts...")
        backtest_results = self.analyzer.backtest_strategies(
            lookback_draws=100, 
            strategies=['balanced', 'hot', 'overdue', 'recent_hot']
        )
        
        print("📊 Creating strategy performance comparison...")
        self.plot_strategy_performance(backtest_results)
        
        print("📉 Creating match distribution charts...")
        self.plot_match_distribution(backtest_results)
        
        print("\n" + "="*60)
        print(f"✅ All visualizations saved to '{self.output_dir}/' directory")
        print("="*60 + "\n")


def main():
    """Generate all visualizations"""
    from lucky_for_life_analyzer import LuckyForLifeAnalyzer
    
    # Initialize analyzer
    analyzer = LuckyForLifeAnalyzer('data/NCELLuckyForLife__2_.csv')
    
    # Create visualizer
    visualizer = LotteryVisualizer(analyzer)
    
    # Generate all visualizations
    visualizer.generate_all_visualizations()


if __name__ == '__main__':
    main()
