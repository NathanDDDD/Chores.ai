"""
Chore Data Model for Chores.ai Desktop POC

This module defines the Chore class which represents a single chore/task
with all its properties like name, frequency, completion status, etc.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json


class Chore:
    """
    Represents a single chore/task in the Chores.ai application.
    
    A chore has:
    - Basic info: name, description, category
    - Frequency: type (daily, weekly, monthly, custom, specific_days) and value
    - Status: completion tracking, due dates, streak counter
    - Metadata: creation date, last modified
    """
    
    def __init__(self, 
                 name: str, 
                 frequency_type: str = "daily",
                 frequency_value: int = 1,
                 description: str = "",
                 category: str = "General",
                 specific_days: Optional[List[str]] = None,
                 created_date: Optional[datetime] = None):
        """
        Initialize a new Chore instance.
        
        Args:
            name: The name/title of the chore
            frequency_type: How often the chore repeats ("daily", "weekly", "monthly", "custom", "specific_days")
            frequency_value: The frequency value (e.g., every 2 days, every 3 weeks)
            description: Optional description of the chore
            category: The category this chore belongs to
            specific_days: List of specific days for "specific_days" frequency (e.g., ["monday", "friday"])
            created_date: When the chore was created (defaults to now)
        """
        self.name = name
        self.description = description
        self.category = category
        self.frequency_type = frequency_type
        self.frequency_value = frequency_value
        self.specific_days = specific_days or []
        
        # Set creation date
        self.created_date = created_date or datetime.now()
        
        # Initialize completion tracking
        self.last_completed_date: Optional[datetime] = None
        self.next_due_date: Optional[datetime] = None
        self.completed_today = False
        self.streak_counter = 0  # How many times completed in a row
        self.miss_counter = 0    # How many times missed in a row
        
        # Calculate initial due date
        self._calculate_next_due_date()
    
    def _calculate_next_due_date(self) -> None:
        """
        Calculate when this chore is next due based on frequency and last completion.
        
        This method updates the next_due_date based on:
        - If never completed: due today (or next specific day)
        - If completed: due date = last_completed + frequency
        """
        if self.last_completed_date is None:
            # Never completed, calculate initial due date
            if self.frequency_type == "specific_days" and self.specific_days:
                self.next_due_date = self._get_next_specific_day()
            else:
                self.next_due_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Calculate next due date based on frequency
            if self.frequency_type == "daily":
                self.next_due_date = self.last_completed_date + timedelta(days=self.frequency_value)
            elif self.frequency_type == "weekly":
                self.next_due_date = self.last_completed_date + timedelta(weeks=self.frequency_value)
            elif self.frequency_type == "monthly":
                # Simple monthly calculation (30 days)
                self.next_due_date = self.last_completed_date + timedelta(days=30 * self.frequency_value)
            elif self.frequency_type == "specific_days":
                # For specific days, find the next occurrence after last completion
                self.next_due_date = self._get_next_specific_day_after(self.last_completed_date)
            else:  # custom
                self.next_due_date = self.last_completed_date + timedelta(days=self.frequency_value)
    
    def _get_next_specific_day(self) -> datetime:
        """
        Get the next specific day from today.
        
        Returns:
            The next datetime when this chore is due
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self._get_next_specific_day_after(today)
    
    def _get_next_specific_day_after(self, after_date: datetime) -> datetime:
        """
        Get the next specific day after a given date.
        
        Args:
            after_date: The date to find the next occurrence after
            
        Returns:
            The next datetime when this chore is due
        """
        if not self.specific_days:
            return after_date
        
        # Day name to number mapping
        day_mapping = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        # Convert specific days to numbers
        target_days = [day_mapping.get(day.lower(), 0) for day in self.specific_days]
        
        # Find the next occurrence
        current_date = after_date
        for _ in range(7):  # Check next 7 days
            if current_date.weekday() in target_days:
                return current_date
            current_date += timedelta(days=1)
        
        # If not found in next 7 days, return the first target day of next week
        return after_date + timedelta(days=7)
    
    def is_due_today(self) -> bool:
        """
        Check if this chore is due today.
        
        Returns:
            True if the chore is due today, False otherwise
        """
        if self.next_due_date is None:
            return False
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.next_due_date <= today
    
    def is_overdue(self) -> bool:
        """
        Check if this chore is overdue (past its due date).
        
        Returns:
            True if the chore is overdue, False otherwise
        """
        if self.next_due_date is None:
            return False
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.next_due_date < today
    
    def mark_completed(self) -> None:
        """
        Mark this chore as completed for today.
        
        This method:
        - Updates last_completed_date to now
        - Increments streak counter
        - Resets miss counter
        - Calculates next due date
        - Sets completed_today flag
        """
        now = datetime.now()
        self.last_completed_date = now
        self.completed_today = True
        self.streak_counter += 1
        self.miss_counter = 0  # Reset miss counter when completed
        self._calculate_next_due_date()
    
    def mark_missed(self) -> None:
        """
        Mark this chore as missed (called when day passes without completion).
        
        This method:
        - Increments miss counter
        - Resets streak counter
        - Updates completed_today flag
        """
        self.completed_today = False
        self.miss_counter += 1
        self.streak_counter = 0  # Reset streak when missed
    
    def reset_daily_status(self) -> None:
        """
        Reset the daily completion status (called at start of new day).
        
        This method:
        - Resets completed_today flag
        - Checks if chore was missed yesterday and updates counters
        """
        if not self.completed_today and self.is_overdue():
            self.mark_missed()
        self.completed_today = False
    
    def get_frequency_description(self) -> str:
        """
        Get a human-readable description of the frequency.
        
        Returns:
            String description of the frequency
        """
        if self.frequency_type == "specific_days" and self.specific_days:
            days_str = ", ".join(self.specific_days).title()
            return f"Every {days_str}"
        elif self.frequency_type == "daily":
            if self.frequency_value == 1:
                return "Daily"
            else:
                return f"Every {self.frequency_value} days"
        elif self.frequency_type == "weekly":
            if self.frequency_value == 1:
                return "Weekly"
            else:
                return f"Every {self.frequency_value} weeks"
        elif self.frequency_type == "monthly":
            if self.frequency_value == 1:
                return "Monthly"
            else:
                return f"Every {self.frequency_value} months"
        else:  # custom
            return f"Every {self.frequency_value} days"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chore to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the chore
        """
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
            'specific_days': self.specific_days,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'last_completed_date': self.last_completed_date.isoformat() if self.last_completed_date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'completed_today': self.completed_today,
            'streak_counter': self.streak_counter,
            'miss_counter': self.miss_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chore':
        """
        Create a Chore instance from a dictionary (for JSON deserialization).
        
        Args:
            data: Dictionary containing chore data
            
        Returns:
            New Chore instance
        """
        chore = cls(
            name=data['name'],
            frequency_type=data.get('frequency_type', 'daily'),
            frequency_value=data.get('frequency_value', 1),
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            specific_days=data.get('specific_days', [])
        )
        
        # Restore dates
        if data.get('created_date'):
            chore.created_date = datetime.fromisoformat(data['created_date'])
        if data.get('last_completed_date'):
            chore.last_completed_date = datetime.fromisoformat(data['last_completed_date'])
        if data.get('next_due_date'):
            chore.next_due_date = datetime.fromisoformat(data['next_due_date'])
        
        # Restore counters
        chore.completed_today = data.get('completed_today', False)
        chore.streak_counter = data.get('streak_counter', 0)
        chore.miss_counter = data.get('miss_counter', 0)
        
        return chore
    
    def __str__(self) -> str:
        """String representation of the chore for debugging."""
        status = "✓" if self.completed_today else "□"
        due_text = f"Due: {self.next_due_date.strftime('%Y-%m-%d')}" if self.next_due_date else "No due date"
        return f"{status} {self.name} ({self.category}) - {due_text}"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"Chore(name='{self.name}', category='{self.category}', frequency='{self.frequency_type}', due='{self.next_due_date}')" 