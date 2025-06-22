#!/usr/bin/env python3
"""
Test script for Chores.ai Desktop POC

This script tests the core functionality of the POC to ensure everything works correctly.
"""

import os
import tempfile
from datetime import datetime, timedelta
from chore_model import Chore
from chore_manager import ChoreManager


def test_chore_model():
    """Test the Chore model functionality."""
    print("Testing Chore Model...")
    
    # Test basic chore creation
    chore = Chore("Test Chore", "daily", 1, "Test description")
    assert chore.name == "Test Chore"
    assert chore.frequency_type == "daily"
    assert chore.frequency_value == 1
    assert chore.description == "Test description"
    assert chore.is_due_today() == True
    print("✓ Basic chore creation works")
    
    # Test completion
    chore.mark_completed()
    assert chore.completed_today == True
    assert chore.streak_counter == 1
    assert chore.miss_counter == 0
    print("✓ Chore completion works")
    
    # Test serialization
    chore_dict = chore.to_dict()
    restored_chore = Chore.from_dict(chore_dict)
    assert restored_chore.name == chore.name
    assert restored_chore.frequency_type == chore.frequency_type
    print("✓ Serialization/deserialization works")
    
    print("✓ Chore Model tests passed!\n")


def test_chore_manager():
    """Test the ChoreManager functionality."""
    print("Testing Chore Manager...")
    
    # Use a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = tmp.name
    
    try:
        # Test manager creation
        cm = ChoreManager(test_file)
        assert len(cm.chores) == 0
        print("✓ Manager creation works")
        
        # Test adding chores
        chore1 = Chore("Daily Task", "daily", 1)
        chore2 = Chore("Weekly Task", "weekly", 1)
        cm.add_chore(chore1)
        cm.add_chore(chore2)
        assert len(cm.chores) == 2
        print("✓ Adding chores works")
        
        # Test filtering
        due_today = cm.get_chores_due_today()
        assert len(due_today) == 2  # Both should be due today initially
        print("✓ Filtering chores works")
        
        # Test statistics
        stats = cm.get_statistics()
        assert stats['total_chores'] == 2
        assert stats['due_today'] == 2
        assert stats['completion_rate_today'] == 0.0
        print("✓ Statistics calculation works")
        
        # Test completion
        cm.mark_chore_completed(chore1)
        assert chore1.completed_today == True
        assert chore1.streak_counter == 1
        print("✓ Marking chores complete works")
        
        # Test persistence
        cm2 = ChoreManager(test_file)
        assert len(cm2.chores) == 2
        assert cm2.chores[0].name == "Daily Task"
        assert cm2.chores[1].name == "Weekly Task"
        print("✓ Data persistence works")
        
        print("✓ Chore Manager tests passed!\n")
        
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)


def test_sample_data():
    """Test the sample data creation."""
    print("Testing Sample Data...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = tmp.name
    
    try:
        cm = ChoreManager(test_file)
        cm.create_sample_chores()
        
        assert len(cm.chores) == 11  # Should create 11 sample chores
        print(f"✓ Created {len(cm.chores)} sample chores")
        
        # Check that sample chores have different frequencies
        freq_types = set(chore.frequency_type for chore in cm.chores)
        assert 'daily' in freq_types
        assert 'weekly' in freq_types
        assert 'monthly' in freq_types
        assert 'specific_days' in freq_types
        print("✓ Sample chores have varied frequencies")
        
        print("✓ Sample data tests passed!\n")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_category_management():
    print("Testing Category Management...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = tmp.name
    try:
        cm = ChoreManager(test_file)
        assert cm.add_category("Work")
        assert "Work" in cm.get_all_categories()
        assert not cm.add_category("Work")  # Duplicate
        assert cm.edit_category("Work", "Office")
        assert "Office" in cm.get_all_categories()
        assert not cm.edit_category("Work", "Office")  # Old doesn't exist
        assert cm.delete_category("Office")
        assert "Office" not in cm.get_all_categories()
        print("✓ Category add/edit/delete works")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_advanced_frequencies():
    print("Testing Advanced Frequency Types...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = tmp.name
    try:
        cm = ChoreManager(test_file)
        # Every X Days
        c1 = Chore("Every 3 Days", "every_x_days", 3)
        cm.add_chore(c1)
        # Every X Weeks
        c2 = Chore("Every 2 Weeks", "every_x_weeks", 2)
        cm.add_chore(c2)
        # Every X Months
        c3 = Chore("Every 6 Months", "every_x_months", 6)
        cm.add_chore(c3)
        # Specific Days
        c4 = Chore("Monday and Friday", "specific_days", 1, specific_days=["monday", "friday"])
        cm.add_chore(c4)
        # Check frequency descriptions
        assert "3 days" in c1.get_frequency_description().lower()
        assert "2 weeks" in c2.get_frequency_description().lower()
        assert "6 months" in c3.get_frequency_description().lower()
        assert "Monday" in c4.get_frequency_description() or "Friday" in c4.get_frequency_description()
        print("✓ Frequency descriptions correct")
        # Check next due date logic
        c1.mark_completed()
        assert (c1.next_due_date - c1.last_completed_date).days == 3
        c2.mark_completed()
        assert (c2.next_due_date - c2.last_completed_date).days == 14
        c3.mark_completed()
        assert (c3.next_due_date - c3.last_completed_date).days == 180
        print("✓ Frequency due date logic correct")
        # Specific days logic
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        c4.last_completed_date = today
        c4._calculate_next_due_date()
        assert c4.next_due_date.weekday() in [0, 4]  # Monday=0, Friday=4
        print("✓ Specific days due date logic correct")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_streak_and_miss_logic():
    print("Testing Streak and Miss Counters...")
    c = Chore("Test Streak", "daily", 1)
    # Mark complete
    c.mark_completed()
    assert c.streak_counter == 1
    assert c.miss_counter == 0
    # Unmark
    c.unmark_completed()
    assert c.streak_counter == 0
    # Mark missed
    c.mark_missed()
    assert c.miss_counter == 1
    assert c.streak_counter == 0
    print("✓ Streak and miss logic correct")


def test_category_statistics():
    print("Testing Category Statistics...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = tmp.name
    try:
        cm = ChoreManager(test_file)
        cm.add_category("Home")
        cm.add_category("Work")
        c1 = Chore("Chore1", "daily", 1, category="Home")
        c2 = Chore("Chore2", "daily", 1, category="Work")
        c3 = Chore("Chore3", "daily", 1, category="Work")
        cm.add_chore(c1)
        cm.add_chore(c2)
        cm.add_chore(c3)
        c2.mark_completed()
        stats = cm.get_category_statistics()
        assert stats["Home"]["total"] == 1
        assert stats["Work"]["total"] == 2
        assert stats["Work"]["completed_today"] == 1
        print("✓ Category statistics correct")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def run_all_tests():
    test_chore_model()
    test_chore_manager()
    test_sample_data()
    test_category_management()
    test_advanced_frequencies()
    test_streak_and_miss_logic()
    test_category_statistics()
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all_tests() 