#!/usr/bin/env python3
"""
Test script for Chores.ai Desktop POC

This script tests the core functionality of the POC to ensure everything works correctly.
"""

import os
import tempfile
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
        
        assert len(cm.chores) == 6  # Should create 6 sample chores
        print(f"✓ Created {len(cm.chores)} sample chores")
        
        # Check that sample chores have different frequencies
        freq_types = set(chore.frequency_type for chore in cm.chores)
        assert 'daily' in freq_types
        assert 'weekly' in freq_types
        assert 'monthly' in freq_types
        print("✓ Sample chores have varied frequencies")
        
        print("✓ Sample data tests passed!\n")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """Run all tests."""
    print("=" * 50)
    print("Chores.ai Desktop POC - Test Suite")
    print("=" * 50)
    
    try:
        test_chore_model()
        test_chore_manager()
        test_sample_data()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The Chores.ai Desktop POC is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 