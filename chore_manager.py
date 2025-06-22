"""
Chore Manager for Chores.ai Desktop POC

This module manages the collection of chores, handles persistence,
and provides business logic for the application.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from chore_model import Chore


class ChoreManager:
    """
    Manages a collection of chores and handles persistence.
    
    This class is responsible for:
    - Storing and retrieving chores
    - Filtering chores by status (due today, overdue, completed, etc.)
    - Managing categories
    - Saving/loading chores to/from file
    - Managing chore lifecycle
    """
    
    def __init__(self, data_file: str = "chores.json"):
        """
        Initialize the ChoreManager.
        
        Args:
            data_file: Path to the JSON file for storing chore data
        """
        self.chores: List[Chore] = []
        self.data_file = data_file
        self.last_save_date: Optional[datetime] = None
        
        # Load existing chores from file if it exists
        self.load_chores()
    
    def add_chore(self, chore: Chore) -> None:
        """
        Add a new chore to the collection.
        
        Args:
            chore: The Chore instance to add
        """
        self.chores.append(chore)
        self.save_chores()
    
    def remove_chore(self, chore: Chore) -> None:
        """
        Remove a chore from the collection.
        
        Args:
            chore: The Chore instance to remove
        """
        if chore in self.chores:
            self.chores.remove(chore)
            self.save_chores()
    
    def get_chores_due_today(self) -> List[Chore]:
        """
        Get all chores that are due today.
        
        Returns:
            List of chores due today, sorted by category then name
        """
        due_today = [chore for chore in self.chores if chore.is_due_today()]
        return sorted(due_today, key=lambda x: (x.category, x.name))
    
    def get_overdue_chores(self) -> List[Chore]:
        """
        Get all chores that are overdue (past their due date).
        
        Returns:
            List of overdue chores, sorted by due date (oldest first)
        """
        overdue = [chore for chore in self.chores if chore.is_overdue()]
        return sorted(overdue, key=lambda x: x.next_due_date or datetime.max)
    
    def get_completed_chores_today(self) -> List[Chore]:
        """
        Get all chores that were completed today.
        
        Returns:
            List of chores completed today, sorted by completion time
        """
        completed = [chore for chore in self.chores if chore.completed_today]
        return sorted(completed, key=lambda x: x.last_completed_date or datetime.min)
    
    def get_all_chores(self) -> List[Chore]:
        """
        Get all chores in the collection.
        
        Returns:
            List of all chores, sorted by category then name
        """
        return sorted(self.chores, key=lambda x: (x.category, x.name))
    
    def get_chores_by_category(self, category: str) -> List[Chore]:
        """
        Get all chores in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of chores in the specified category, sorted by name
        """
        category_chores = [chore for chore in self.chores if chore.category.lower() == category.lower()]
        return sorted(category_chores, key=lambda x: x.name)
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories used by chores.
        
        Returns:
            List of category names, sorted alphabetically
        """
        categories = set(chore.category for chore in self.chores)
        return sorted(list(categories))
    
    def get_category_statistics(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics broken down by category.
        
        Returns:
            Dictionary with category statistics
        """
        stats = {}
        categories = self.get_categories()
        
        for category in categories:
            category_chores = self.get_chores_by_category(category)
            due_today = [c for c in category_chores if c.is_due_today()]
            completed_today = [c for c in category_chores if c.completed_today]
            overdue = [c for c in category_chores if c.is_overdue()]
            
            stats[category] = {
                'total': len(category_chores),
                'due_today': len(due_today),
                'completed_today': len(completed_today),
                'overdue': len(overdue)
            }
        
        return stats
    
    def get_chore_by_name(self, name: str) -> Optional[Chore]:
        """
        Find a chore by its name.
        
        Args:
            name: The name of the chore to find
            
        Returns:
            The Chore instance if found, None otherwise
        """
        for chore in self.chores:
            if chore.name.lower() == name.lower():
                return chore
        return None
    
    def mark_chore_completed(self, chore: Chore) -> None:
        """
        Mark a chore as completed and save the changes.
        
        Args:
            chore: The Chore instance to mark as completed
        """
        if chore in self.chores:
            chore.mark_completed()
            self.save_chores()
    
    def reset_daily_status(self) -> None:
        """
        Reset the daily status for all chores (called at start of new day).
        
        This method:
        - Calls reset_daily_status() on all chores
        - Saves the changes to file
        """
        for chore in self.chores:
            chore.reset_daily_status()
        self.save_chores()
    
    def save_chores(self) -> None:
        """
        Save all chores to the JSON file.
        
        This method:
        - Converts all chores to dictionaries
        - Writes the data to the JSON file
        - Updates the last_save_date
        """
        try:
            # Convert chores to dictionaries
            chore_data = [chore.to_dict() for chore in self.chores]
            
            # Create the data structure to save
            data = {
                'chores': chore_data,
                'last_save_date': datetime.now().isoformat(),
                'version': '1.1'  # Updated version for new features
            }
            
            # Write to file
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.last_save_date = datetime.now()
            print(f"Saved {len(self.chores)} chores to {self.data_file}")
            
        except Exception as e:
            print(f"Error saving chores: {e}")
    
    def load_chores(self) -> None:
        """
        Load chores from the JSON file.
        
        This method:
        - Reads the JSON file if it exists
        - Converts the data back to Chore instances
        - Handles errors gracefully (creates empty list if file doesn't exist)
        """
        try:
            if not os.path.exists(self.data_file):
                print(f"No existing data file found at {self.data_file}. Starting with empty chore list.")
                return
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load chores from the data
            chore_data_list = data.get('chores', [])
            self.chores = [Chore.from_dict(chore_data) for chore_data in chore_data_list]
            
            # Load last save date if available
            if 'last_save_date' in data:
                self.last_save_date = datetime.fromisoformat(data['last_save_date'])
            
            print(f"Loaded {len(self.chores)} chores from {self.data_file}")
            
        except Exception as e:
            print(f"Error loading chores: {e}")
            print("Starting with empty chore list.")
            self.chores = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the chores.
        
        Returns:
            Dictionary containing various statistics
        """
        total_chores = len(self.chores)
        due_today = len(self.get_chores_due_today())
        overdue = len(self.get_overdue_chores())
        completed_today = len(self.get_completed_chores_today())
        categories = len(self.get_categories())
        
        # Calculate completion rate for today
        completion_rate = 0
        if due_today > 0:
            completion_rate = (completed_today / due_today) * 100
        
        # Find longest streak
        longest_streak = max([chore.streak_counter for chore in self.chores]) if self.chores else 0
        
        return {
            'total_chores': total_chores,
            'due_today': due_today,
            'overdue': overdue,
            'completed_today': completed_today,
            'completion_rate_today': completion_rate,
            'longest_streak': longest_streak,
            'categories': categories,
            'last_save_date': self.last_save_date
        }
    
    def create_sample_chores(self) -> None:
        """
        Create some sample chores for testing/demo purposes.
        
        This method creates a few example chores with different categories and frequencies.
        """
        sample_chores = [
            # Daily chores
            Chore("Make bed", "daily", 1, "Start the day with a tidy bedroom", "Bedroom"),
            Chore("Wash dishes", "daily", 1, "Keep the kitchen clean", "Kitchen"),
            Chore("Water plants", "daily", 2, "Keep plants healthy and hydrated", "Garden"),
            
            # Weekly chores
            Chore("Take out trash", "weekly", 1, "Empty all trash bins", "Household"),
            Chore("Vacuum floors", "weekly", 1, "Clean carpets and hard floors", "Cleaning"),
            Chore("Laundry", "weekly", 1, "Wash and fold clothes", "Laundry"),
            
            # Monthly chores
            Chore("Pay bills", "monthly", 1, "Review and pay monthly bills", "Finance"),
            Chore("Clean refrigerator", "monthly", 1, "Deep clean the fridge", "Kitchen"),
            
            # Specific days chores
            Chore("Grocery shopping", "specific_days", 1, "Buy groceries for the week", "Shopping", ["monday", "friday"]),
            Chore("Gym workout", "specific_days", 1, "Exercise routine", "Health", ["monday", "wednesday", "friday"]),
            Chore("Call family", "specific_days", 1, "Check in with family members", "Personal", ["sunday"]),
        ]
        
        for chore in sample_chores:
            self.add_chore(chore)
        
        print(f"Created {len(sample_chores)} sample chores with categories")
    
    def clear_all_chores(self) -> None:
        """
        Remove all chores from the collection.
        
        Warning: This will permanently delete all chore data!
        """
        self.chores.clear()
        self.save_chores()
        print("All chores have been cleared.") 