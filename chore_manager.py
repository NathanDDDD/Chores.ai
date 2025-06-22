"""
Chore Manager for Chores.ai Desktop POC

This module manages the collection of chores, handles persistence,
and provides business logic for the application.
"""

import json
import os
from datetime import datetime, timedelta
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
        self.categories: Set[str] = {"General"}  # Default category
        
        # Load existing chores from file if it exists
        self.load_chores()
    
    def add_chore(self, chore: Chore) -> None:
        """
        Add a new chore to the collection.
        
        Args:
            chore: The Chore instance to add
        """
        self.chores.append(chore)
        self.categories.add(chore.category)  # Add category if new
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
                'categories': list(self.categories),
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
            
            # Load categories
            self.categories = set(data.get('categories', ["General"]))
            
            # Load last save date if available
            if 'last_save_date' in data:
                self.last_save_date = datetime.fromisoformat(data['last_save_date'])
            
            print(f"Loaded {len(self.chores)} chores from {self.data_file}")
            
        except Exception as e:
            print(f"Error loading chores: {e}")
            print("Starting with empty chore list.")
            self.chores = []
            self.categories = {"General"}
    
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
    
    def add_category(self, category_name: str) -> bool:
        """
        Add a new category.
        
        Args:
            category_name: Name of the new category
            
        Returns:
            True if added successfully, False if category already exists
        """
        if category_name not in self.categories:
            self.categories.add(category_name)
            self.save_chores()
            return True
        return False
    
    def edit_category(self, old_name: str, new_name: str) -> bool:
        """
        Edit a category name.
        
        Args:
            old_name: Current category name
            new_name: New category name
            
        Returns:
            True if edited successfully, False if old category doesn't exist or new name already exists
        """
        if old_name not in self.categories or new_name in self.categories:
            return False
        
        # Update category for all chores
        for chore in self.chores:
            if chore.category == old_name:
                chore.category = new_name
        
        # Update categories set
        self.categories.remove(old_name)
        self.categories.add(new_name)
        
        self.save_chores()
        return True
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a category and move its chores to General category.
        
        Args:
            category_name: Name of the category to delete
            
        Returns:
            True if deleted successfully, False if category doesn't exist or is General
        """
        if category_name not in self.categories or category_name == "General":
            return False
        
        # Move all chores in this category to General
        for chore in self.chores:
            if chore.category == category_name:
                chore.category = "General"
        
        # Remove category
        self.categories.remove(category_name)
        
        self.save_chores()
        return True
    
    def get_all_categories(self) -> List[str]:
        """
        Get all available categories.
        
        Returns:
            List of all category names
        """
        return sorted(list(self.categories))
    
    def update_daily_status(self) -> None:
        """
        Update the daily status of all chores.
        
        This method:
        - Resets completed_today flags
        - Updates streak/miss counters for overdue chores
        - Should be called at the start of each day
        """
        for chore in self.chores:
            chore.reset_daily_status()
        self.save_chores()
    
    def get_chores_for_date(self, target_date: datetime) -> Dict[str, List[Chore]]:
        """
        Get chores for a specific date, categorized by status.
        
        Args:
            target_date: The date to get chores for
            
        Returns:
            Dictionary with 'active', 'missed', 'completed' lists
        """
        # This is a simplified version - in a real implementation,
        # you'd need to calculate which chores were due on the target date
        # based on their frequency and start dates
        
        active_chores = []
        missed_chores = []
        completed_chores = []
        
        # For now, return today's chores
        # TODO: Implement proper date-based filtering
        for chore in self.chores:
            if chore.is_due_today():
                if chore.completed_today:
                    completed_chores.append(chore)
                elif chore.is_overdue():
                    missed_chores.append(chore)
                else:
                    active_chores.append(chore)
        
        return {
            'active': active_chores,
            'missed': missed_chores,
            'completed': completed_chores
        }
    
    def get_overall_statistics(self) -> Dict[str, int]:
        """
        Get overall statistics for all chores.
        
        Returns:
            Dictionary with overall statistics
        """
        total_chores = len(self.chores)
        completed_today = len([c for c in self.chores if c.completed_today])
        due_today = len([c for c in self.chores if c.is_due_today()])
        overdue = len([c for c in self.chores if c.is_overdue()])
        
        # Calculate average streak
        total_streak = sum(c.streak_counter for c in self.chores)
        avg_streak = total_streak / total_chores if total_chores > 0 else 0
        
        return {
            'total_chores': total_chores,
            'completed_today': completed_today,
            'due_today': due_today,
            'overdue': overdue,
            'avg_streak': round(avg_streak, 1)
        }
    
    def search_chores(self, query: str) -> List[Chore]:
        """
        Search chores by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching chores
        """
        query_lower = query.lower()
        return [
            chore for chore in self.chores
            if query_lower in chore.name.lower() or 
               query_lower in chore.description.lower() or
               query_lower in chore.category.lower()
        ]
    
    def get_chore_by_index(self, index: int) -> Optional[Chore]:
        """
        Get a chore by its index.
        
        Args:
            index: Index of the chore
            
        Returns:
            The chore at the specified index, or None if invalid
        """
        if 0 <= index < len(self.chores):
            return self.chores[index]
        return None
    
    def get_chore_index(self, chore: Chore) -> Optional[int]:
        """
        Get the index of a chore in the list.
        
        Args:
            chore: The chore to find
            
        Returns:
            Index of the chore, or None if not found
        """
        try:
            return self.chores.index(chore)
        except ValueError:
            return None
    
    def get_chores_for_today(self) -> List[Chore]:
        """
        Alias for get_chores_due_today, for UI compatibility.
        """
        return self.get_chores_due_today() 