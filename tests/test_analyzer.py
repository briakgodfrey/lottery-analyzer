#!/usr/bin/env python3
"""
Unit tests for Lucky for Life Analyzer
"""

import pytest
import pandas as pd
import json
import os
from lucky_for_life_analyzer import LuckyForLifeAnalyzer


@pytest.fixture
def analyzer():
    """Fixture to create analyzer instance"""
    csv_path = 'data/NCELLuckyForLife__2_.csv'
    if not os.path.exists(csv_path):
        # Create a minimal test dataset
        test_data = {
            'Date': ['01/21/2026', '01/20/2026', '01/19/2026'],
            'Number 1': [3, 6, 5],
            'Number 2': [10, 9, 17],
            'Number 3': [22, 28, 22],
            'Number 4': [32, 41, 42],
            'Number 5': [38, 45, 48],
            'Lucky Ball': [11, 8, 16]
        }
        df = pd.DataFrame(test_data)
        os.makedirs('data', exist_ok=True)
        df.to_csv(csv_path, index=False)
    
    return LuckyForLifeAnalyzer(csv_path)


class TestAnalyzer:
    """Test cases for the main analyzer"""
    
    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert len(analyzer.df) > 0
        assert analyzer.main_numbers_range == range(1, 49)
        assert analyzer.lucky_ball_range == range(1, 19)
    
    def test_frequency_analysis(self, analyzer):
        """Test frequency analysis returns correct data"""
        main_freq, lucky_freq = analyzer.frequency_analysis()
        
        assert isinstance(main_freq, dict) or hasattr(main_freq, 'items')
        assert isinstance(lucky_freq, dict) or hasattr(lucky_freq, 'items')
        assert len(main_freq) > 0
        assert len(lucky_freq) > 0
        
        # Check all values are positive integers
        for count in main_freq.values():
            assert count > 0
            assert isinstance(count, int)
    
    def test_recent_analysis(self, analyzer):
        """Test recent analysis with default window"""
        recent_main, recent_lucky = analyzer.recent_analysis(last_n_draws=10)
        
        assert isinstance(recent_main, dict) or hasattr(recent_main, 'items')
        assert isinstance(recent_lucky, dict) or hasattr(recent_lucky, 'items')
    
    def test_gap_analysis(self, analyzer):
        """Test gap analysis calculations"""
        avg_gaps, current_gaps = analyzer.gap_analysis()
        
        assert isinstance(avg_gaps, dict)
        assert isinstance(current_gaps, dict)
        
        # Check gaps are positive numbers
        for gap in avg_gaps.values():
            assert gap > 0 or gap == float('inf')
    
    def test_overdue_numbers(self, analyzer):
        """Test overdue number detection"""
        overdue = analyzer.get_overdue_numbers(threshold_multiplier=1.5)
        
        assert isinstance(overdue, dict)
        
        # Each overdue number should have required fields
        for num, data in overdue.items():
            assert 'current_gap' in data
            assert 'avg_gap' in data
            assert 'ratio' in data
            assert data['ratio'] > 1.5


class TestRecommendations:
    """Test cases for recommendation generation"""
    
    def test_balanced_strategy(self, analyzer):
        """Test balanced recommendation strategy"""
        rec = analyzer.generate_recommendations(strategy='balanced')
        
        assert 'main_numbers' in rec
        assert 'lucky_ball' in rec
        assert 'reasoning' in rec
        assert len(rec['main_numbers']) == 5
        assert len(rec['lucky_ball']) == 1
        
        # Numbers should be in valid range
        for num in rec['main_numbers']:
            assert 1 <= num <= 48
        assert 1 <= rec['lucky_ball'][0] <= 18
    
    def test_hot_strategy(self, analyzer):
        """Test hot numbers strategy"""
        rec = analyzer.generate_recommendations(strategy='hot')
        
        assert len(rec['main_numbers']) == 5
        assert len(rec['lucky_ball']) == 1
        
        # Verify numbers are valid
        for num in rec['main_numbers']:
            assert 1 <= num <= 48
    
    def test_recent_hot_strategy(self, analyzer):
        """Test recent hot strategy"""
        rec = analyzer.generate_recommendations(strategy='recent_hot')
        
        assert len(rec['main_numbers']) == 5
        assert len(rec['lucky_ball']) == 1
    
    def test_overdue_strategy(self, analyzer):
        """Test overdue numbers strategy"""
        rec = analyzer.generate_recommendations(strategy='overdue')
        
        assert len(rec['main_numbers']) == 5
        assert len(rec['lucky_ball']) == 1


class TestTicketManagement:
    """Test cases for ticket saving and checking"""
    
    def test_save_ticket(self, analyzer):
        """Test saving a ticket"""
        test_file = 'test_tickets.json'
        
        # Clean up if exists
        if os.path.exists(test_file):
            os.remove(test_file)
        
        ticket = analyzer.save_ticket(
            numbers=[1, 2, 3, 4, 5],
            lucky_ball=10,
            strategy='test',
            date_played='2026-01-22',
            cost=2.00,
            ticket_file=test_file
        )
        
        assert os.path.exists(test_file)
        assert ticket['numbers'] == [1, 2, 3, 4, 5]
        assert ticket['lucky_ball'] == 10
        assert ticket['strategy'] == 'test'
        
        # Clean up
        os.remove(test_file)
    
    def test_check_ticket(self, analyzer):
        """Test checking ticket against a drawing"""
        # Use a recent drawing date from the data
        result, error = analyzer.check_ticket(
            numbers=[3, 10, 22, 32, 38],
            lucky_ball=11,
            drawing_date='2026-01-21'
        )
        
        if result:
            assert 'main_matches' in result
            assert 'lucky_match' in result
            assert 'prize' in result
            assert result['main_matches'] >= 0
            assert isinstance(result['lucky_match'], bool)
            assert result['prize'] >= 0


class TestBacktesting:
    """Test cases for strategy backtesting"""
    
    def test_backtest_strategies(self, analyzer):
        """Test strategy backtesting with small sample"""
        # Use small lookback for faster testing
        results = analyzer.backtest_strategies(
            lookback_draws=10,
            strategies=['balanced', 'hot']
        )
        
        assert isinstance(results, dict)
        assert 'balanced' in results
        assert 'hot' in results
        
        # Check result structure
        for strategy, data in results.items():
            assert 'wins' in data
            assert 'total_prize' in data
            assert 'tickets' in data
            assert data['tickets'] > 0


class TestDataIntegrity:
    """Test cases for data integrity"""
    
    def test_no_duplicate_numbers(self, analyzer):
        """Test that no drawing has duplicate numbers"""
        for idx, row in analyzer.df.iterrows():
            numbers = [int(row[f'Number {i}']) for i in range(1, 6)]
            assert len(numbers) == len(set(numbers)), f"Duplicate numbers in row {idx}"
    
    def test_numbers_in_range(self, analyzer):
        """Test all numbers are in valid range"""
        for idx, row in analyzer.df.iterrows():
            # Check main numbers
            for i in range(1, 6):
                num = int(row[f'Number {i}'])
                assert 1 <= num <= 48, f"Number {num} out of range in row {idx}"
            
            # Check lucky ball
            lb = int(row['Lucky Ball'])
            assert 1 <= lb <= 18, f"Lucky ball {lb} out of range in row {idx}"
    
    def test_dates_are_valid(self, analyzer):
        """Test all dates are valid and sorted"""
        dates = analyzer.df['Date'].tolist()
        
        # Check all dates are datetime objects
        for date in dates:
            assert isinstance(date, pd.Timestamp)
        
        # Check dates are in descending order (most recent first)
        for i in range(len(dates) - 1):
            assert dates[i] >= dates[i + 1], "Dates not in descending order"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_recommendations(self, analyzer):
        """Test recommendation with invalid strategy"""
        rec = analyzer.generate_recommendations(strategy='invalid_strategy')
        
        # Should fall back to balanced
        assert 'main_numbers' in rec
        assert len(rec['main_numbers']) == 5
    
    def test_check_nonexistent_date(self, analyzer):
        """Test checking ticket against non-existent date"""
        result, error = analyzer.check_ticket(
            numbers=[1, 2, 3, 4, 5],
            lucky_ball=1,
            drawing_date='2099-12-31'
        )
        
        assert result is None
        assert error == "Drawing date not found"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
