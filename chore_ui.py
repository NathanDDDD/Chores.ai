"""
Chore UI for Chores.ai Desktop POC

This module provides the Tkinter-based user interface for the Chores.ai application.
It includes all the features from the architecture diagram.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
from datetime import datetime, timedelta
import calendar
from typing import Optional, List, Dict
from chore_manager import ChoreManager
from chore_model import Chore


class ChoreUI:
    """
    Main UI class for the Chores.ai application.
    
    Features:
    - Left navigation sidebar matching architecture
    - Today's checklist with completion tracking
    - Category management (add, edit, delete)
    - Monthly calendar view
    - Right-click context menu for chores
    - Advanced frequency options
    - Proper streak/miss counter tracking
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the UI.
        
        Args:
            root: The main Tkinter window
        """
        self.root = root
        self.root.title("Chores.ai Desktop POC")
        self.root.geometry("1400x900")  # Increased size to accommodate sidebar
        
        # Initialize chore manager
        self.chore_manager = ChoreManager()
        
        # UI state
        self.selected_chore_index: Optional[int] = None
        self.selected_date = datetime.now()
        self.current_section = "chores"  # Track current navigation section
        
        # Initialize count variables for calendar view
        self.count_vars = {
            'active': tk.StringVar(),
            'missed': tk.StringVar(),
            'completed': tk.StringVar()
        }
        
        # Create UI components
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Initial load
        self.refresh_all()
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with sidebar and content
        self.main_container = ttk.Frame(self.root)
        
        # Left Navigation Sidebar
        self._create_sidebar()
        
        # Right Content Area
        self.content_frame = ttk.Frame(self.main_container)
        
        # Main notebook for tabs (only for chores section)
        self.notebook = ttk.Notebook(self.content_frame)
        
        # Today's Checklist Tab
        self.today_frame = ttk.Frame(self.notebook)
        self._create_today_tab()
        
        # Calendar Tab
        self.calendar_frame = ttk.Frame(self.notebook)
        self._create_calendar_tab()
        
        # Categories Tab
        self.categories_frame = ttk.Frame(self.notebook)
        self._create_categories_tab()
        
        # Add tabs to notebook
        self.notebook.add(self.today_frame, text="Today's Checklist")
        self.notebook.add(self.calendar_frame, text="Calendar")
        self.notebook.add(self.categories_frame, text="Categories")
        
        # Placeholder frames for other sections
        self.habits_frame = ttk.Frame(self.content_frame)
        self.goals_frame = ttk.Frame(self.content_frame)
        self.social_frame = ttk.Frame(self.content_frame)
        self.user_frame = ttk.Frame(self.content_frame)
        self.achievements_frame = ttk.Frame(self.content_frame)
        self.store_frame = ttk.Frame(self.content_frame)
        self.settings_frame = ttk.Frame(self.content_frame)
        
        # Create placeholder content for other sections
        self._create_placeholder_sections()
        
        # Add chore button (only visible in chores section)
        self.add_chore_btn = ttk.Button(self.content_frame, text="Add New Chore", command=self._show_add_chore_dialog)
        
        # FOR TESTING ONLY: Add Demo Data button (remove before production)
        self.demo_data_btn = ttk.Button(self.content_frame, text="Load Demo Data (Testing Only)", command=self._load_demo_data)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
    
    def _create_sidebar(self):
        """Create the left navigation sidebar."""
        self.sidebar = ttk.Frame(self.main_container, relief=tk.RAISED, borderwidth=2)
        
        # Sidebar header
        header_frame = ttk.Frame(self.sidebar)
        ttk.Label(header_frame, text="Chores.ai", font=("Arial", 14, "bold")).pack(pady=10)
        header_frame.pack(fill=tk.X)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("chores", "Chores", "📋"),
            ("habits", "Habits", "🔄"),
            ("goals", "Goals", "🎯"),
            ("social", "Social Network", "👥"),
            ("user", "User", "👤"),
            ("achievements", "Achievements", "🏆"),
            ("store", "Store", "🛒"),
            ("settings", "Settings", "⚙️")
        ]
        
        for section_id, label, icon in nav_items:
            btn = ttk.Button(
                self.sidebar, 
                text=f"{icon} {label}", 
                command=lambda s=section_id: self._switch_section(s),
                width=20
            )
            btn.pack(pady=2, padx=5, fill=tk.X)
            self.nav_buttons[section_id] = btn
        
        # Highlight current section
        self._highlight_current_section()
    
    def _create_placeholder_sections(self):
        """Create placeholder content for sections not yet implemented."""
        
        # Habits Section
        habits_content = ttk.Frame(self.habits_frame)
        ttk.Label(habits_content, text="Habits Module", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(habits_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(habits_content, text="Track your daily habits and build streaks").pack(pady=10)
        habits_content.pack(expand=True)
        
        # Goals Section
        goals_content = ttk.Frame(self.goals_frame)
        ttk.Label(goals_content, text="Goals Module", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(goals_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(goals_content, text="Set and track long-term goals").pack(pady=10)
        goals_content.pack(expand=True)
        
        # Social Network Section
        social_content = ttk.Frame(self.social_frame)
        ttk.Label(social_content, text="Social Network", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(social_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(social_content, text="Share progress with friends and family").pack(pady=10)
        social_content.pack(expand=True)
        
        # User Section
        user_content = ttk.Frame(self.user_frame)
        ttk.Label(user_content, text="User Profile", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(user_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(user_content, text="Manage your profile and preferences").pack(pady=10)
        user_content.pack(expand=True)
        
        # Achievements Section
        achievements_content = ttk.Frame(self.achievements_frame)
        ttk.Label(achievements_content, text="Achievements", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(achievements_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(achievements_content, text="Earn badges and rewards for your progress").pack(pady=10)
        achievements_content.pack(expand=True)
        
        # Store Section
        store_content = ttk.Frame(self.store_frame)
        ttk.Label(store_content, text="Store", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(store_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(store_content, text="Purchase premium features and themes").pack(pady=10)
        store_content.pack(expand=True)
        
        # Settings Section
        settings_content = ttk.Frame(self.settings_frame)
        ttk.Label(settings_content, text="Settings", font=("Arial", 16, "bold")).pack(pady=50)
        ttk.Label(settings_content, text="Coming Soon!", font=("Arial", 12)).pack()
        ttk.Label(settings_content, text="Customize your experience").pack(pady=10)
        settings_content.pack(expand=True)
    
    def _create_today_tab(self):
        """Create the Today's Checklist tab."""
        # Header
        header_frame = ttk.Frame(self.today_frame)
        ttk.Label(header_frame, text="Today's Checklist", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Statistics
        stats_frame = ttk.LabelFrame(header_frame, text="Today's Progress")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_vars = {
            'total': tk.StringVar(),
            'completed': tk.StringVar(),
            'due': tk.StringVar(),
            'overdue': tk.StringVar()
        }
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=5)
        
        ttk.Label(stats_grid, text="Total:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, textvariable=self.stats_vars['total']).grid(row=0, column=1, padx=5)
        
        ttk.Label(stats_grid, text="Completed:").grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, textvariable=self.stats_vars['completed']).grid(row=0, column=3, padx=5)
        
        ttk.Label(stats_grid, text="Due:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, textvariable=self.stats_vars['due']).grid(row=1, column=1, padx=5)
        
        ttk.Label(stats_grid, text="Overdue:").grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Label(stats_grid, textvariable=self.stats_vars['overdue']).grid(row=1, column=3, padx=5)
        
        header_frame.pack(fill=tk.X)
        
        # Chores list
        list_frame = ttk.Frame(self.today_frame)
        
        # Treeview for chores
        columns = ("Name", "Category", "Frequency", "Streak", "Misses", "Due Date", "Status")
        self.chores_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.chores_tree.heading("Name", text="Chore Name")
        self.chores_tree.heading("Category", text="Category")
        self.chores_tree.heading("Frequency", text="Frequency")
        self.chores_tree.heading("Streak", text="Streak")
        self.chores_tree.heading("Misses", text="Misses")
        self.chores_tree.heading("Due Date", text="Due Date")
        self.chores_tree.heading("Status", text="Status")
        
        self.chores_tree.column("Name", width=200)
        self.chores_tree.column("Category", width=100)
        self.chores_tree.column("Frequency", width=120)
        self.chores_tree.column("Streak", width=60)
        self.chores_tree.column("Misses", width=60)
        self.chores_tree.column("Due Date", width=100)
        self.chores_tree.column("Status", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.chores_tree.yview)
        self.chores_tree.configure(yscrollcommand=scrollbar.set)
        
        self.chores_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Chore", command=self._edit_selected_chore)
        self.context_menu.add_command(label="Delete Chore", command=self._delete_selected_chore)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Mark Complete", command=self._mark_selected_complete)
        self.context_menu.add_command(label="Mark Incomplete", command=self._mark_selected_incomplete)
    
    def _create_calendar_tab(self):
        """Create the Calendar tab."""
        # Header
        header_frame = ttk.Frame(self.calendar_frame)
        ttk.Label(header_frame, text="Monthly Calendar View", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Calendar widget
        self.calendar = Calendar(header_frame, selectmode='day', date_pattern='y-mm-dd')
        self.calendar.pack(pady=10)
        
        # Date selection info
        self.selected_date_var = tk.StringVar()
        ttk.Label(header_frame, textvariable=self.selected_date_var).pack(pady=5)
        
        header_frame.pack(fill=tk.X)
        
        # Chores for selected date - Enhanced to match architecture
        date_chores_frame = ttk.LabelFrame(self.calendar_frame, text="Chores for Selected Date")
        date_chores_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Notebook for different chore statuses
        self.date_notebook = ttk.Notebook(date_chores_frame)
        
        # Active chores (due today)
        self.active_frame = ttk.Frame(self.date_notebook)
        self._create_enhanced_chore_list_frame(self.active_frame, "Active Chores", "active")
        
        # Missed chores (overdue)
        self.missed_frame = ttk.Frame(self.date_notebook)
        self._create_enhanced_chore_list_frame(self.missed_frame, "Missed Chores", "missed")
        
        # Completed chores (completed today)
        self.completed_frame = ttk.Frame(self.date_notebook)
        self._create_enhanced_chore_list_frame(self.completed_frame, "Completed Chores", "completed")
        
        self.date_notebook.add(self.active_frame, text="Active")
        self.date_notebook.add(self.missed_frame, text="Missed")
        self.date_notebook.add(self.completed_frame, text="Completed")
        
        self.date_notebook.pack(fill=tk.BOTH, expand=True)
    
    def _create_enhanced_chore_list_frame(self, parent, title, list_type):
        """Create an enhanced frame with a chore list for calendar view."""
        frame = ttk.Frame(parent)
        
        # Header with count
        header_frame = ttk.Frame(frame)
        ttk.Label(header_frame, text=title, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.count_vars[list_type] = tk.StringVar()
        ttk.Label(header_frame, textvariable=self.count_vars[list_type], font=("Arial", 10)).pack(side=tk.RIGHT)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Treeview with enhanced columns matching architecture
        if list_type == "active":
            columns = ("Name", "Category", "Frequency", "Due Date", "Status", "Checkbox")
        elif list_type == "missed":
            columns = ("Name", "Category", "Frequency", "Due Date", "Miss Counter")
        else:  # completed
            columns = ("Name", "Category", "Frequency", "Completion Time", "Streak Counter")
        
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        
        # Configure columns based on type
        if list_type == "active":
            tree.heading("Name", text="Chore Name")
            tree.heading("Category", text="Category")
            tree.heading("Frequency", text="Frequency")
            tree.heading("Due Date", text="Due Date")
            tree.heading("Status", text="Status")
            tree.heading("Checkbox", text="✓")
            
            tree.column("Name", width=200)
            tree.column("Category", width=100)
            tree.column("Frequency", width=120)
            tree.column("Due Date", width=100)
            tree.column("Status", width=80)
            tree.column("Checkbox", width=50, anchor=tk.CENTER)
            
        elif list_type == "missed":
            tree.heading("Name", text="Chore Name")
            tree.heading("Category", text="Category")
            tree.heading("Frequency", text="Frequency")
            tree.heading("Due Date", text="Due Date")
            tree.heading("Miss Counter", text="Miss Counter")
            
            tree.column("Name", width=200)
            tree.column("Category", width=100)
            tree.column("Frequency", width=120)
            tree.column("Due Date", width=100)
            tree.column("Miss Counter", width=100)
            
        else:  # completed
            tree.heading("Name", text="Chore Name")
            tree.heading("Category", text="Category")
            tree.heading("Frequency", text="Frequency")
            tree.heading("Completion Time", text="Completion Time")
            tree.heading("Streak Counter", text="Streak Counter")
            
            tree.column("Name", width=200)
            tree.column("Category", width=100)
            tree.column("Frequency", width=120)
            tree.column("Completion Time", width=150)
            tree.column("Streak Counter", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store reference
        if list_type == "active":
            self.active_tree = tree
        elif list_type == "missed":
            self.missed_tree = tree
        elif list_type == "completed":
            self.completed_tree = tree
        
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_categories_tab(self):
        """Create the Categories tab."""
        # Header
        header_frame = ttk.Frame(self.categories_frame)
        ttk.Label(header_frame, text="Category Management", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Category controls
        controls_frame = ttk.Frame(header_frame)
        
        ttk.Button(controls_frame, text="Add Category", command=self._add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit Category", command=self._edit_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Category", command=self._delete_category).pack(side=tk.LEFT, padx=5)
        
        controls_frame.pack(pady=10)
        
        header_frame.pack(fill=tk.X)
        
        # Categories list
        list_frame = ttk.Frame(self.categories_frame)
        
        # Treeview for categories
        columns = ("Category", "Total Chores", "Completed Today", "Due Today", "Overdue")
        self.categories_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.categories_tree.heading("Category", text="Category Name")
        self.categories_tree.heading("Total Chores", text="Total Chores")
        self.categories_tree.heading("Completed Today", text="Completed Today")
        self.categories_tree.heading("Due Today", text="Due Today")
        self.categories_tree.heading("Overdue", text="Overdue")
        
        self.categories_tree.column("Category", width=200)
        self.categories_tree.column("Total Chores", width=100)
        self.categories_tree.column("Completed Today", width=120)
        self.categories_tree.column("Due Today", width=100)
        self.categories_tree.column("Overdue", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=scrollbar.set)
        
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _setup_layout(self):
        """Set up the main layout."""
        # Main container
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (left side)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Content area (right side)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Show initial section (chores)
        self._show_section_content("chores")
        
        # Add chore button (only visible in chores section)
        self.add_chore_btn.pack(pady=5)
        # FOR TESTING ONLY: Demo data button (remove before production)
        self.demo_data_btn.pack(pady=5)
        
        # Status bar
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _switch_section(self, section_id: str):
        """Switch to a different section."""
        self.current_section = section_id
        self._highlight_current_section()
        self._show_section_content(section_id)
        self.status_var.set(f"Switched to {section_id.title()} section")
    
    def _highlight_current_section(self):
        """Highlight the current section button."""
        for section_id, button in self.nav_buttons.items():
            if section_id == self.current_section:
                button.configure(style="Accent.TButton")  # Highlight current
            else:
                button.configure(style="TButton")  # Normal style
    
    def _show_section_content(self, section_id: str):
        """Show the content for the specified section."""
        # Hide all content frames
        self.notebook.pack_forget()
        self.habits_frame.pack_forget()
        self.goals_frame.pack_forget()
        self.social_frame.pack_forget()
        self.user_frame.pack_forget()
        self.achievements_frame.pack_forget()
        self.store_frame.pack_forget()
        self.settings_frame.pack_forget()
        
        # Show/hide add chore button
        if section_id == "chores":
            self.add_chore_btn.pack(pady=5)
        else:
            self.add_chore_btn.pack_forget()
        
        # Show the appropriate content
        if section_id == "chores":
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "habits":
            self.habits_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "goals":
            self.goals_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "social":
            self.social_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "user":
            self.user_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "achievements":
            self.achievements_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "store":
            self.store_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        elif section_id == "settings":
            self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _bind_events(self):
        """Bind event handlers."""
        # Treeview selection
        self.chores_tree.bind("<<TreeviewSelect>>", self._on_chore_select)
        self.chores_tree.bind("<Double-1>", self._on_chore_double_click)
        self.chores_tree.bind("<Button-3>", self._on_chore_right_click)
        
        # Calendar selection
        self.calendar.bind("<<CalendarSelected>>", self._on_date_select)
        
        # Categories tree selection
        self.categories_tree.bind("<<TreeviewSelect>>", self._on_category_select)
    
    def _on_chore_select(self, event):
        """Handle chore selection."""
        selection = self.chores_tree.selection()
        if selection:
            item = self.chores_tree.item(selection[0])
            # Find chore index by name (simplified)
            chore_name = item['values'][0]
            for i, chore in enumerate(self.chore_manager.chores):
                if chore.name == chore_name:
                    self.selected_chore_index = i
                    break
    
    def _on_chore_double_click(self, event):
        """Handle chore double-click."""
        if self.selected_chore_index is not None:
            self._edit_selected_chore()
    
    def _on_chore_right_click(self, event):
        """Handle right-click on chore."""
        # Select the item under cursor
        item = self.chores_tree.identify_row(event.y)
        if item:
            self.chores_tree.selection_set(item)
            self._on_chore_select(None)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _on_date_select(self, event):
        """Handle date selection in calendar."""
        selected_date_str = self.calendar.get_date()
        self.selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        self.selected_date_var.set(f"Selected Date: {selected_date_str}")
        self._refresh_calendar_chores()
    
    def _on_category_select(self, event):
        """Handle category selection."""
        pass  # Could be used for filtering
    
    def refresh_all(self):
        """Refresh all UI components."""
        self._refresh_today_chores()
        self._refresh_categories()
        self._refresh_calendar_chores()
        self._update_statistics()
    
    def _refresh_today_chores(self):
        """Refresh the today's chores list."""
        # Clear existing items
        for item in self.chores_tree.get_children():
            self.chores_tree.delete(item)
        
        # Get today's chores
        today_chores = self.chore_manager.get_chores_for_today()
        overdue_chores = self.chore_manager.get_overdue_chores()
        
        # Combine and sort
        all_chores = today_chores + overdue_chores
        
        for chore in all_chores:
            # Determine status
            if chore.completed_today:
                status = "✓ Completed"
                tags = ("completed",)
            elif chore.is_overdue():
                status = "⚠ Overdue"
                tags = ("overdue",)
            else:
                status = "□ Due"
                tags = ("due",)
            
            # Format due date
            due_date = chore.next_due_date.strftime("%Y-%m-%d") if chore.next_due_date else "N/A"
            
            values = (
                chore.name,
                chore.category,
                chore.get_frequency_description(),
                chore.streak_counter,
                chore.miss_counter,
                due_date,
                status
            )
            
            self.chores_tree.insert("", tk.END, values=values, tags=tags)
        
        # Configure tag colors
        self.chores_tree.tag_configure("completed", foreground="green")
        self.chores_tree.tag_configure("overdue", foreground="red")
        self.chores_tree.tag_configure("due", foreground="black")
    
    def _refresh_categories(self):
        """Refresh the categories list."""
        # Clear existing items
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Get category statistics
        stats = self.chore_manager.get_category_statistics()
        
        for category, stat in stats.items():
            values = (
                category,
                stat['total'],
                stat['completed_today'],
                stat['due_today'],
                stat['overdue']
            )
            self.categories_tree.insert("", tk.END, values=values)
    
    def _refresh_calendar_chores(self):
        """Refresh the calendar chores lists."""
        # Clear all trees
        for tree in [self.active_tree, self.missed_tree, self.completed_tree]:
            for item in tree.get_children():
                tree.delete(item)
        
        # Get chores for selected date
        date_chores = self.chore_manager.get_chores_for_date(self.selected_date)
        
        # Populate active chores (due today)
        active_chores = date_chores.get('due', [])
        for chore in active_chores:
            checkbox = "✓" if chore.completed_today else "☐"
            status = "Completed" if chore.completed_today else "Due"
            values = (
                chore.name,
                chore.category,
                chore.get_frequency_description(),
                chore.next_due_date.strftime("%Y-%m-%d") if chore.next_due_date else "N/A",
                status,
                checkbox
            )
            item = self.active_tree.insert("", tk.END, values=values)
            if chore.completed_today:
                self.active_tree.item(item, tags=("completed",))
        
        self.count_vars['active'].set(f"({len(active_chores)} items)")
        
        # Populate missed chores (overdue)
        missed_chores = date_chores.get('overdue', [])
        for chore in missed_chores:
            values = (
                chore.name,
                chore.category,
                chore.get_frequency_description(),
                chore.next_due_date.strftime("%Y-%m-%d") if chore.next_due_date else "N/A",
                chore.miss_counter
            )
            item = self.missed_tree.insert("", tk.END, values=values)
            self.missed_tree.item(item, tags=("overdue",))
        
        self.count_vars['missed'].set(f"({len(missed_chores)} items)")
        
        # Populate completed chores (completed today)
        completed_chores = date_chores.get('completed', [])
        for chore in completed_chores:
            completion_time = chore.last_completed_date.strftime("%H:%M") if chore.last_completed_date else "N/A"
            values = (
                chore.name,
                chore.category,
                chore.get_frequency_description(),
                completion_time,
                chore.streak_counter
            )
            item = self.completed_tree.insert("", tk.END, values=values)
            self.completed_tree.item(item, tags=("completed",))
        
        self.count_vars['completed'].set(f"({len(completed_chores)} items)")
        
        # Configure tag colors
        self.active_tree.tag_configure("completed", foreground="green")
        self.missed_tree.tag_configure("overdue", foreground="red")
        self.completed_tree.tag_configure("completed", foreground="green")
    
    def _update_statistics(self):
        """Update the statistics display."""
        stats = self.chore_manager.get_overall_statistics()
        
        self.stats_vars['total'].set(str(stats['total_chores']))
        self.stats_vars['completed'].set(str(stats['completed_today']))
        self.stats_vars['due'].set(str(stats['due_today']))
        self.stats_vars['overdue'].set(str(stats['overdue']))
        
        # Update status bar
        self.status_var.set(f"Total: {stats['total_chores']} | Completed Today: {stats['completed_today']} | Due: {stats['due_today']} | Overdue: {stats['overdue']}")
    
    def _show_add_chore_dialog(self):
        """Show dialog to add a new chore."""
        dialog = AddChoreDialog(self.root, self.chore_manager, self)
        self.root.wait_window(dialog.dialog)
        self.refresh_all()
    
    def _edit_selected_chore(self):
        """Edit the selected chore."""
        if self.selected_chore_index is not None:
            chore = self.chore_manager.get_chore_by_index(self.selected_chore_index)
            if chore:
                dialog = EditChoreDialog(self.root, self.chore_manager, chore, self.selected_chore_index, self)
                self.root.wait_window(dialog.dialog)
                self.refresh_all()
    
    def _delete_selected_chore(self):
        """Delete the selected chore."""
        if self.selected_chore_index is not None:
            chore = self.chore_manager.get_chore_by_index(self.selected_chore_index)
            if chore:
                result = messagebox.askyesno("Delete Chore", f"Are you sure you want to delete '{chore.name}'?")
                if result:
                    self.chore_manager.delete_chore(self.selected_chore_index)
                    self.selected_chore_index = None
                    self.refresh_all()
    
    def _mark_selected_complete(self):
        """Mark the selected chore as complete."""
        if self.selected_chore_index is not None:
            chore = self.chore_manager.get_chore_by_index(self.selected_chore_index)
            if chore and not chore.completed_today:
                chore.mark_completed()
                self.chore_manager.save_chores()
                self.refresh_all()
    
    def _mark_selected_incomplete(self):
        """Mark the selected chore as incomplete."""
        if self.selected_chore_index is not None:
            chore = self.chore_manager.get_chore_by_index(self.selected_chore_index)
            if chore and chore.completed_today:
                chore.unmark_completed()
                self.chore_manager.save_chores()
                self.refresh_all()
    
    def _add_category(self):
        """Add a new category."""
        category_name = simpledialog.askstring("Add Category", "Enter category name:")
        if category_name and category_name.strip():
            if self.chore_manager.add_category(category_name.strip()):
                self.refresh_all()
                messagebox.showinfo("Success", f"Category '{category_name}' added successfully!")
            else:
                messagebox.showerror("Error", f"Category '{category_name}' already exists!")
    
    def _edit_category(self):
        """Edit a category."""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to edit.")
            return
        
        item = self.categories_tree.item(selection[0])
        old_name = item['values'][0]
        
        new_name = simpledialog.askstring("Edit Category", f"Enter new name for '{old_name}':", initialvalue=old_name)
        if new_name and new_name.strip() and new_name != old_name:
            if self.chore_manager.edit_category(old_name, new_name.strip()):
                self.refresh_all()
                messagebox.showinfo("Success", f"Category renamed from '{old_name}' to '{new_name}'!")
            else:
                messagebox.showerror("Error", f"Could not rename category. '{new_name}' may already exist.")
    
    def _delete_category(self):
        """Delete a category."""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete.")
            return
        
        item = self.categories_tree.item(selection[0])
        category_name = item['values'][0]
        
        if category_name == "General":
            messagebox.showwarning("Warning", "Cannot delete the 'General' category.")
            return
        
        result = messagebox.askyesno("Delete Category", 
                                   f"Are you sure you want to delete '{category_name}'?\n\n"
                                   f"All chores in this category will be moved to 'General'.")
        if result:
            if self.chore_manager.delete_category(category_name):
                self.refresh_all()
                messagebox.showinfo("Success", f"Category '{category_name}' deleted successfully!")
            else:
                messagebox.showerror("Error", f"Could not delete category '{category_name}'.")

    # FOR TESTING ONLY: Demo data loader (remove before production)
    def _load_demo_data(self):
        self.chore_manager.create_sample_chores()
        self.refresh_all()
        self.status_var.set("Demo data loaded (FOR TESTING ONLY)")


class AddChoreDialog:
    """Dialog for adding a new chore."""
    
    def __init__(self, parent, chore_manager: ChoreManager, main_ui):
        self.chore_manager = chore_manager
        self.main_ui = main_ui
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Chore")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Name
        ttk.Label(self.dialog, text="Chore Name:").pack(anchor=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Category
        ttk.Label(self.dialog, text="Category:").pack(anchor=tk.W, padx=10, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.dialog, textvariable=self.category_var, 
                                          values=self.chore_manager.get_all_categories())
        self.category_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Description
        ttk.Label(self.dialog, text="Description:").pack(anchor=tk.W, padx=10, pady=5)
        self.description_text = tk.Text(self.dialog, height=3, width=50)
        self.description_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Frequency Type
        ttk.Label(self.dialog, text="Frequency Type:").pack(anchor=tk.W, padx=10, pady=5)
        self.frequency_type_var = tk.StringVar(value="daily")
        frequency_frame = ttk.Frame(self.dialog)
        
        frequency_types = [
            ("Daily", "daily"),
            ("Weekly", "weekly"),
            ("Monthly", "monthly"),
            ("Every X Days", "every_x_days"),
            ("Every X Weeks", "every_x_weeks"),
            ("Every X Months", "every_x_months"),
            ("Specific Days", "specific_days")
        ]
        
        for text, value in frequency_types:
            ttk.Radiobutton(frequency_frame, text=text, variable=self.frequency_type_var, 
                           value=value, command=self._on_frequency_change).pack(anchor=tk.W)
        
        frequency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frequency Value
        ttk.Label(self.dialog, text="Frequency Value:").pack(anchor=tk.W, padx=10, pady=5)
        self.frequency_value_var = tk.StringVar(value="1")
        self.frequency_value_entry = ttk.Entry(self.dialog, textvariable=self.frequency_value_var, width=10)
        self.frequency_value_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Specific Days Frame
        self.specific_days_frame = ttk.LabelFrame(self.dialog, text="Specific Days Selection")
        
        # Day checkboxes
        self.day_vars = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_frame = ttk.Frame(self.specific_days_frame)
        
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.day_vars[day.lower()] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).grid(row=i//3, column=i%3, sticky=tk.W, padx=5)
        
        days_frame.pack(padx=10, pady=5)
        
        # Repeat every X weeks for specific days
        self.repeat_weeks_frame = ttk.Frame(self.specific_days_frame)
        ttk.Label(self.repeat_weeks_frame, text="Repeat Every:").pack(side=tk.LEFT)
        self.repeat_weeks_var = tk.StringVar(value="1")
        self.repeat_weeks_entry = ttk.Entry(self.repeat_weeks_frame, textvariable=self.repeat_weeks_var, width=5)
        self.repeat_weeks_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.repeat_weeks_frame, text="Weeks").pack(side=tk.LEFT)
        self.repeat_weeks_frame.pack(pady=5)
        
        self.specific_days_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Monthly specific dates frame
        self.monthly_dates_frame = ttk.LabelFrame(self.dialog, text="Monthly Date Selection")
        
        # Date picker for monthly
        self.monthly_date_var = tk.StringVar()
        ttk.Label(self.monthly_dates_frame, text="Select dates for monthly repetition:").pack(pady=5)
        
        # Simple date entry (could be enhanced with calendar widget)
        self.monthly_date_entry = ttk.Entry(self.monthly_dates_frame, textvariable=self.monthly_date_var, width=20)
        self.monthly_date_entry.pack(pady=5)
        ttk.Label(self.monthly_dates_frame, text="Format: 1,15,30 (comma-separated dates)").pack()
        
        # Repeat every X months
        self.repeat_months_frame = ttk.Frame(self.monthly_dates_frame)
        ttk.Label(self.repeat_months_frame, text="Repeat Every:").pack(side=tk.LEFT)
        self.repeat_months_var = tk.StringVar(value="1")
        self.repeat_months_entry = ttk.Entry(self.repeat_months_frame, textvariable=self.repeat_months_var, width=5)
        self.repeat_months_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.repeat_months_frame, text="Months").pack(side=tk.LEFT)
        self.repeat_months_frame.pack(pady=5)
        
        self.monthly_dates_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start Date and Time
        ttk.Label(self.dialog, text="Start Date & Time:").pack(anchor=tk.W, padx=10, pady=5)
        
        datetime_frame = ttk.Frame(self.dialog)
        
        # Date picker
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(datetime_frame, text="Date:").pack(side=tk.LEFT)
        self.start_date_entry = ttk.Entry(datetime_frame, textvariable=self.start_date_var, width=15)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Time picker
        self.start_time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))
        ttk.Label(datetime_frame, text="Time:").pack(side=tk.LEFT, padx=(20, 0))
        self.start_time_entry = ttk.Entry(datetime_frame, textvariable=self.start_time_var, width=10)
        self.start_time_entry.pack(side=tk.LEFT, padx=5)
        
        datetime_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        ttk.Button(button_frame, text="Add Chore", command=self._add_chore).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        button_frame.pack(pady=20)
        
        # Initially hide specific frames
        self.specific_days_frame.pack_forget()
        self.monthly_dates_frame.pack_forget()
    
    def _setup_layout(self):
        """Set up the dialog layout."""
        pass  # Layout is handled in _create_widgets
    
    def _on_frequency_change(self):
        """Handle frequency type change."""
        freq_type = self.frequency_type_var.get()
        
        # Hide all specific frames
        self.specific_days_frame.pack_forget()
        self.monthly_dates_frame.pack_forget()
        
        # Show relevant frame
        if freq_type == "specific_days":
            self.specific_days_frame.pack(fill=tk.X, padx=10, pady=5, before=self.dialog.winfo_children()[-2])
        elif freq_type == "monthly":
            self.monthly_dates_frame.pack(fill=tk.X, padx=10, pady=5, before=self.dialog.winfo_children()[-2])
    
    def _add_chore(self):
        """Add the chore."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a chore name.")
            return
        
        category = self.category_var.get().strip() or "General"
        description = self.description_text.get("1.0", tk.END).strip()
        frequency_type = self.frequency_type_var.get()
        
        # Handle frequency value
        try:
            if frequency_type in ["every_x_days", "every_x_weeks", "every_x_months"]:
                frequency_value = int(self.frequency_value_var.get())
            elif frequency_type == "specific_days":
                frequency_value = int(self.repeat_weeks_var.get())
            elif frequency_type == "monthly":
                frequency_value = int(self.repeat_months_var.get())
            else:
                frequency_value = 1
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for frequency value.")
            return
        
        # Handle specific days
        specific_days = []
        if frequency_type == "specific_days":
            specific_days = [day for day, var in self.day_vars.items() if var.get()]
            if not specific_days:
                messagebox.showerror("Error", "Please select at least one day for specific days frequency.")
                return
        
        # Handle monthly dates
        if frequency_type == "monthly":
            monthly_dates = self.monthly_date_var.get().strip()
            if monthly_dates:
                try:
                    # Parse comma-separated dates
                    dates = [int(d.strip()) for d in monthly_dates.split(",")]
                    if not all(1 <= d <= 31 for d in dates):
                        raise ValueError("Dates must be between 1 and 31")
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid dates (1-31, comma-separated).")
                    return
        
        # Handle start date and time
        try:
            start_date_str = self.start_date_var.get()
            start_time_str = self.start_time_var.get()
            start_datetime = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date and time (YYYY-MM-DD HH:MM).")
            return
        
        # Create chore
        chore = Chore(
            name=name,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            description=description,
            category=category,
            specific_days=specific_days,
            created_date=start_datetime
        )
        
        # Add to manager
        self.chore_manager.add_chore(chore)
        self.dialog.destroy()


class EditChoreDialog:
    """Dialog for editing an existing chore."""
    
    def __init__(self, parent, chore_manager: ChoreManager, chore: Chore, chore_index: int, main_ui):
        self.chore_manager = chore_manager
        self.chore = chore
        self.chore_index = chore_index
        self.main_ui = main_ui
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Chore")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._setup_layout()
        self._load_chore_data()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Name
        ttk.Label(self.dialog, text="Chore Name:").pack(anchor=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Category
        ttk.Label(self.dialog, text="Category:").pack(anchor=tk.W, padx=10, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.dialog, textvariable=self.category_var, 
                                          values=self.chore_manager.get_all_categories())
        self.category_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Description
        ttk.Label(self.dialog, text="Description:").pack(anchor=tk.W, padx=10, pady=5)
        self.description_text = tk.Text(self.dialog, height=3, width=50)
        self.description_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Frequency Type
        ttk.Label(self.dialog, text="Frequency Type:").pack(anchor=tk.W, padx=10, pady=5)
        self.frequency_type_var = tk.StringVar()
        frequency_frame = ttk.Frame(self.dialog)
        
        frequency_types = [
            ("Daily", "daily"),
            ("Weekly", "weekly"),
            ("Monthly", "monthly"),
            ("Every X Days", "every_x_days"),
            ("Every X Weeks", "every_x_weeks"),
            ("Every X Months", "every_x_months"),
            ("Specific Days", "specific_days")
        ]
        
        for text, value in frequency_types:
            ttk.Radiobutton(frequency_frame, text=text, variable=self.frequency_type_var, 
                           value=value, command=self._on_frequency_change).pack(anchor=tk.W)
        
        frequency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frequency Value
        ttk.Label(self.dialog, text="Frequency Value:").pack(anchor=tk.W, padx=10, pady=5)
        self.frequency_value_var = tk.StringVar()
        self.frequency_value_entry = ttk.Entry(self.dialog, textvariable=self.frequency_value_var, width=10)
        self.frequency_value_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Specific Days Frame
        self.specific_days_frame = ttk.LabelFrame(self.dialog, text="Select Days")
        self.specific_days_vars = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            var = tk.BooleanVar()
            self.specific_days_vars[day.lower()] = var
            ttk.Checkbutton(self.specific_days_frame, text=day, variable=var).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        ttk.Button(button_frame, text="Save Changes", command=self._save_chore).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        button_frame.pack(pady=20)
    
    def _setup_layout(self):
        """Set up dialog layout."""
        self._on_frequency_change()
    
    def _load_chore_data(self):
        """Load existing chore data into the form."""
        self.name_var.set(self.chore.name)
        self.category_var.set(self.chore.category)
        self.description_text.insert("1.0", self.chore.description)
        self.frequency_type_var.set(self.chore.frequency_type)
        self.frequency_value_var.set(str(self.chore.frequency_value))
        
        # Set specific days
        for day, var in self.specific_days_vars.items():
            var.set(day in self.chore.specific_days)
    
    def _on_frequency_change(self):
        """Handle frequency type change."""
        freq_type = self.frequency_type_var.get()
        
        # Hide all specific frames
        self.specific_days_frame.pack_forget()
        
        # Show relevant frame
        if freq_type == "specific_days":
            self.specific_days_frame.pack(fill=tk.X, padx=10, pady=5, before=self.dialog.winfo_children()[-2])
    
    def _save_chore(self):
        """Save the chore changes."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a chore name.")
            return
        
        category = self.category_var.get().strip() or "General"
        description = self.description_text.get("1.0", tk.END).strip()
        frequency_type = self.frequency_type_var.get()
        frequency_value = int(self.frequency_value_var.get() or "1")
        
        # Get specific days if applicable
        specific_days = []
        if frequency_type == "specific_days":
            specific_days = [day for day, var in self.specific_days_vars.items() if var.get()]
            if not specific_days:
                messagebox.showerror("Error", "Please select at least one day for specific days frequency.")
                return
        
        # Create updated chore
        updated_chore = Chore(
            name=name,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            description=description,
            category=category,
            specific_days=specific_days,
            created_date=self.chore.created_date
        )
        
        # Copy existing data
        updated_chore.last_completed_date = self.chore.last_completed_date
        updated_chore.next_due_date = self.chore.next_due_date
        updated_chore.completed_today = self.chore.completed_today
        updated_chore.streak_counter = self.chore.streak_counter
        updated_chore.miss_counter = self.chore.miss_counter
        updated_chore.previous_status = self.chore.previous_status
        
        # Update in manager
        if self.chore_manager.edit_chore(self.chore_index, updated_chore):
            messagebox.showinfo("Success", f"Chore '{name}' updated successfully!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update chore.") 