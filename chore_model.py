"""
Chore Data Model for Chores.ai Desktop POC

This module defines the Chore class which represents a single chore/task
with all its properties like name, frequency, completion status, etc.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


class Chore:
    """
    Represents a single chore/task in the Chores.ai application.
    
    A chore has:
    - Basic info: name, description
    - Frequency: type (daily, weekly, monthly, custom) and value
    - Status: completion tracking, due dates, streak counter
    - Metadata: creation date, last modified
    """
    
    def __init__(self, 
                 name: str, 
                 frequency_type: str = "daily",
                 frequency_value: int = 1,
                 description: str = "",
                 created_date: Optional[datetime] = None):
        """
        Initialize a new Chore instance.
        
        Args:
            name: The name/title of the chore
            frequency_type: How often the chore repeats ("daily", "weekly", "monthly", "custom")
            frequency_value: The frequency value (e.g., every 2 days, every 3 weeks)
            description: Optional description of the chore
            created_date: When the chore was created (defaults to now)
        """
        self.name = name
        self.description = description
        self.frequency_type = frequency_type
        self.frequency_value = frequency_value
        
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
        - If never completed: due today
        - If completed: due date = last_completed + frequency
        """
        if self.last_completed_date is None:
            # Never completed, due today
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
            else:  # custom
                self.next_due_date = self.last_completed_date + timedelta(days=self.frequency_value)
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chore to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the chore
        """
        return {
            'name': self.name,
            'description': self.description,
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
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
            description=data.get('description', '')
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
        return f"{status} {self.name} ({due_text})"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"Chore(name='{self.name}', frequency='{self.frequency_type}', due='{self.next_due_date}')" 