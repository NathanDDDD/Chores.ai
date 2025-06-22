"""
Chores.ai Desktop UI Module

This module contains the Tkinter-based user interface for the Chores.ai desktop application.
It includes the main window, dialogs, and all UI components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import List, Optional, Callable
from chore_model import Chore
from chore_manager import ChoreManager


class AddChoreDialog:
    """
    Dialog for adding a new chore.
    
    This dialog collects all necessary information to create a new chore:
    - Name (required)
    - Description (optional)
    - Frequency type and value
    """
    
    def __init__(self, parent):
        """
        Initialize the Add Chore Dialog.
        
        Args:
            parent: The parent window (main application window)
        """
        self.parent = parent
        self.result = None
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Chore")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal (user must interact with it before returning to main window)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent window
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create all the widgets for the dialog."""
        # Title label
        self.title_label = tk.Label(self.dialog, text="Add New Chore", font=("Arial", 14, "bold"))
        
        # Name field
        self.name_label = tk.Label(self.dialog, text="Chore Name *:")
        self.name_entry = tk.Entry(self.dialog, width=40)
        
        # Description field
        self.desc_label = tk.Label(self.dialog, text="Description:")
        self.desc_text = tk.Text(self.dialog, height=3, width=40)
        
        # Frequency frame
        self.freq_frame = tk.LabelFrame(self.dialog, text="Frequency", padx=10, pady=5)
        
        # Frequency type
        self.freq_type_label = tk.Label(self.freq_frame, text="Type:")
        self.freq_type_var = tk.StringVar(value="daily")
        self.freq_type_combo = ttk.Combobox(
            self.freq_frame, 
            textvariable=self.freq_type_var,
            values=["daily", "weekly", "monthly", "custom"],
            state="readonly",
            width=15
        )
        
        # Frequency value
        self.freq_value_label = tk.Label(self.freq_frame, text="Every:")
        self.freq_value_var = tk.StringVar(value="1")
        self.freq_value_spinbox = tk.Spinbox(
            self.freq_frame,
            from_=1,
            to=365,
            textvariable=self.freq_value_var,
            width=10
        )
        
        # Buttons
        self.button_frame = tk.Frame(self.dialog)
        self.ok_button = tk.Button(self.button_frame, text="Add Chore", command=self._on_ok)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self._on_cancel)
        
        # Bind Enter key to OK button
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _setup_layout(self):
        """Set up the layout of all widgets."""
        # Main layout using grid
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))
        
        # Name field
        self.name_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # Description field
        self.desc_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.desc_text.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # Frequency frame
        self.freq_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Frequency widgets
        self.freq_type_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.freq_type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.freq_value_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.freq_value_spinbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        self.ok_button.pack(side="left", padx=10)
        self.cancel_button.pack(side="left", padx=10)
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(1, weight=1)
        self.freq_frame.grid_columnconfigure(1, weight=1)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def _on_ok(self):
        """Handle OK button click - validate and create chore."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Chore name is required!")
            self.name_entry.focus()
            return
        
        # Get description
        description = self.desc_text.get("1.0", tk.END).strip()
        
        # Get frequency
        frequency_type = self.freq_type_var.get()
        try:
            frequency_value = int(self.freq_value_var.get())
            if frequency_value < 1:
                raise ValueError("Frequency value must be at least 1")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid frequency value: {e}")
            self.freq_value_spinbox.focus()
            return
        
        # Create the chore
        chore = Chore(
            name=name,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            description=description
        )
        
        self.result = chore
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.dialog.destroy()
    
    def show(self) -> Optional[Chore]:
        """
        Show the dialog and wait for user input.
        
        Returns:
            The created Chore instance if OK was clicked, None if cancelled
        """
        self.dialog.wait_window()
        return self.result


class ChoreListFrame(ttk.Frame):
    """
    A frame that displays a list of chores with checkboxes.
    
    This component can be used to display different types of chore lists:
    - Chores due today
    - Overdue chores
    - Completed chores
    """
    
    def __init__(self, parent, title: str, chores: List[Chore], 
                 on_chore_click: Optional[Callable[[Chore], None]] = None,
                 show_checkboxes: bool = True):
        """
        Initialize the ChoreListFrame.
        
        Args:
            parent: Parent widget
            title: Title for the list
            chores: List of chores to display
            on_chore_click: Callback function when a chore is clicked
            show_checkboxes: Whether to show checkboxes for completion
        """
        super().__init__(parent)
        self.title = title
        self.chores = chores
        self.on_chore_click = on_chore_click
        self.show_checkboxes = show_checkboxes
        
        self._create_widgets()
        self._setup_layout()
        self._update_display()
    
    def _create_widgets(self):
        """Create the widgets for the chore list."""
        # Title label
        self.title_label = tk.Label(self, text=self.title, font=("Arial", 12, "bold"))
        
        # Create a frame for the list with scrollbar
        self.list_frame = tk.Frame(self)
        
        # Create a canvas and scrollbar for the list
        self.canvas = tk.Canvas(self.list_frame, height=200)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empty label for when no chores
        self.empty_label = tk.Label(self.scrollable_frame, text="No chores to display", 
                                   fg="gray", font=("Arial", 10, "italic"))
    
    def _setup_layout(self):
        """Set up the layout of the widgets."""
        # Title
        self.title_label.pack(fill="x", padx=5, pady=5)
        
        # List frame
        self.list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _update_display(self):
        """Update the display with the current list of chores."""
        # Clear existing widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.chores:
            # Show empty message
            self.empty_label = tk.Label(self.scrollable_frame, text="No chores to display", 
                                       fg="gray", font=("Arial", 10, "italic"))
            self.empty_label.pack(pady=20)
            return
        
        # Create widgets for each chore
        for i, chore in enumerate(self.chores):
            self._create_chore_widget(chore, i)
    
    def _create_chore_widget(self, chore: Chore, index: int):
        """
        Create a widget for a single chore.
        
        Args:
            chore: The chore to display
            index: The index of the chore in the list
        """
        # Create frame for this chore
        chore_frame = tk.Frame(self.scrollable_frame, relief="solid", borderwidth=1)
        chore_frame.pack(fill="x", padx=5, pady=2)
        
        # Checkbox for completion (if enabled)
        if self.show_checkboxes:
            checkbox_var = tk.BooleanVar(value=chore.completed_today)
            checkbox = tk.Checkbutton(
                chore_frame,
                variable=checkbox_var,
                command=lambda: self._on_checkbox_click(chore, checkbox_var)
            )
            checkbox.pack(side="left", padx=5, pady=5)
        
        # Chore information
        info_frame = tk.Frame(chore_frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Chore name
        name_label = tk.Label(
            info_frame,
            text=chore.name,
            font=("Arial", 10, "bold" if not chore.completed_today else "normal"),
            fg="green" if chore.completed_today else "black"
        )
        name_label.pack(anchor="w")
        
        # Chore details
        details_text = f"Frequency: {chore.frequency_type} (every {chore.frequency_value})"
        if chore.next_due_date:
            details_text += f" | Due: {chore.next_due_date.strftime('%Y-%m-%d')}"
        if chore.streak_counter > 0:
            details_text += f" | Streak: {chore.streak_counter}"
        
        details_label = tk.Label(info_frame, text=details_text, font=("Arial", 8), fg="gray")
        details_label.pack(anchor="w")
        
        # Description (if any)
        if chore.description:
            desc_label = tk.Label(info_frame, text=chore.description, font=("Arial", 8), fg="blue")
            desc_label.pack(anchor="w")
        
        # Make the entire frame clickable
        if self.on_chore_click:
            for widget in [chore_frame, info_frame, name_label, details_label]:
                widget.bind("<Button-1>", lambda e, c=chore: self.on_chore_click(c))
                widget.bind("<Enter>", lambda e, w=chore_frame: w.config(bg="lightblue"))
                widget.bind("<Leave>", lambda e, w=chore_frame: w.config(bg="white"))
    
    def _on_checkbox_click(self, chore: Chore, checkbox_var: tk.BooleanVar):
        """
        Handle checkbox click for chore completion.
        
        Args:
            chore: The chore being marked as complete/incomplete
            checkbox_var: The checkbox variable
        """
        if checkbox_var.get():
            # Mark as completed
            chore.mark_completed()
        else:
            # Mark as incomplete (reset today's completion)
            chore.completed_today = False
        
        # Update the display
        self._update_display()
    
    def update_chores(self, new_chores: List[Chore]):
        """
        Update the list of chores and refresh the display.
        
        Args:
            new_chores: New list of chores to display
        """
        self.chores = new_chores
        self._update_display()


class ChoresAIApp:
    """
    Main application class for Chores.ai Desktop POC.
    
    This class manages the main window and coordinates between the UI,
    chore manager, and data persistence.
    """
    
    def __init__(self):
        """Initialize the Chores.ai application."""
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Chores.ai - Desktop POC")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize the chore manager
        self.chore_manager = ChoreManager()
        
        # Create the UI
        self._create_widgets()
        self._setup_layout()
        self._setup_menu()
        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initial refresh
        self._refresh_all()
    
    def _create_widgets(self):
        """Create all the widgets for the main window."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        
        # Header
        self.header_frame = tk.Frame(self.main_frame)
        self.title_label = tk.Label(
            self.header_frame,
            text="Chores.ai - Today's Checklist",
            font=("Arial", 16, "bold")
        )
        self.date_label = tk.Label(
            self.header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("Arial", 10),
            fg="gray"
        )
        
        # Statistics frame
        self.stats_frame = tk.LabelFrame(self.main_frame, text="Today's Progress", padx=10, pady=5)
        self.stats_label = tk.Label(self.stats_frame, text="Loading statistics...", font=("Arial", 10))
        
        # Notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Today's chores tab
        self.today_frame = ttk.Frame(self.notebook)
        self.today_chores_list = ChoreListFrame(
            self.today_frame,
            "Chores Due Today",
            [],
            on_chore_click=self._on_chore_click,
            show_checkboxes=True
        )
        
        # All chores tab
        self.all_frame = ttk.Frame(self.notebook)
        self.all_chores_list = ChoreListFrame(
            self.all_frame,
            "All Chores",
            [],
            on_chore_click=self._on_chore_click,
            show_checkboxes=False
        )
        
        # Overdue chores tab
        self.overdue_frame = ttk.Frame(self.notebook)
        self.overdue_chores_list = ChoreListFrame(
            self.overdue_frame,
            "Overdue Chores",
            [],
            on_chore_click=self._on_chore_click,
            show_checkboxes=False
        )
        
        # Buttons frame
        self.button_frame = tk.Frame(self.main_frame)
        self.add_chore_button = tk.Button(
            self.button_frame,
            text="Add New Chore",
            command=self._add_chore,
            bg="lightgreen",
            font=("Arial", 10, "bold")
        )
        self.refresh_button = tk.Button(
            self.button_frame,
            text="Refresh",
            command=self._refresh_all
        )
        self.sample_data_button = tk.Button(
            self.button_frame,
            text="Load Sample Data",
            command=self._load_sample_data
        )
    
    def _setup_layout(self):
        """Set up the layout of all widgets."""
        # Main frame
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.title_label.pack()
        self.date_label.pack()
        
        # Statistics
        self.stats_frame.pack(fill="x", pady=(0, 10))
        self.stats_label.pack()
        
        # Notebook
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Add tabs to notebook
        self.notebook.add(self.today_frame, text="Today's Chores")
        self.notebook.add(self.all_frame, text="All Chores")
        self.notebook.add(self.overdue_frame, text="Overdue")
        
        # Today's chores
        self.today_chores_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # All chores
        self.all_chores_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Overdue chores
        self.overdue_chores_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons
        self.button_frame.pack(fill="x", pady=(10, 0))
        self.add_chore_button.pack(side="left", padx=(0, 10))
        self.refresh_button.pack(side="left", padx=(0, 10))
        self.sample_data_button.pack(side="left")
    
    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self._refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Chores menu
        chores_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chores", menu=chores_menu)
        chores_menu.add_command(label="Add New Chore", command=self._add_chore)
        chores_menu.add_command(label="Load Sample Data", command=self._load_sample_data)
        chores_menu.add_separator()
        chores_menu.add_command(label="Clear All Chores", command=self._clear_all_chores)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _refresh_all(self):
        """Refresh all displays with current data."""
        # Update statistics
        stats = self.chore_manager.get_statistics()
        stats_text = (
            f"Total Chores: {stats['total_chores']} | "
            f"Due Today: {stats['due_today']} | "
            f"Completed Today: {stats['completed_today']} | "
            f"Overdue: {stats['overdue']} | "
            f"Completion Rate: {stats['completion_rate_today']:.1f}%"
        )
        self.stats_label.config(text=stats_text)
        
        # Update chore lists
        self.today_chores_list.update_chores(self.chore_manager.get_chores_due_today())
        self.all_chores_list.update_chores(self.chore_manager.get_all_chores())
        self.overdue_chores_list.update_chores(self.chore_manager.get_overdue_chores())
    
    def _add_chore(self):
        """Open the add chore dialog."""
        dialog = AddChoreDialog(self.root)
        new_chore = dialog.show()
        
        if new_chore:
            # Check if chore with same name already exists
            existing = self.chore_manager.get_chore_by_name(new_chore.name)
            if existing:
                messagebox.showerror("Error", f"A chore named '{new_chore.name}' already exists!")
                return
            
            # Add the new chore
            self.chore_manager.add_chore(new_chore)
            self._refresh_all()
            messagebox.showinfo("Success", f"Chore '{new_chore.name}' added successfully!")
    
    def _on_chore_click(self, chore: Chore):
        """
        Handle clicking on a chore in the list.
        
        Args:
            chore: The chore that was clicked
        """
        # Show chore details in a message box
        details = f"Chore: {chore.name}\n"
        if chore.description:
            details += f"Description: {chore.description}\n"
        details += f"Frequency: {chore.frequency_type} (every {chore.frequency_value})\n"
        if chore.next_due_date:
            details += f"Next Due: {chore.next_due_date.strftime('%Y-%m-%d')}\n"
        if chore.last_completed_date:
            details += f"Last Completed: {chore.last_completed_date.strftime('%Y-%m-%d %H:%M')}\n"
        details += f"Streak: {chore.streak_counter}\n"
        details += f"Missed: {chore.miss_counter}"
        
        messagebox.showinfo("Chore Details", details)
    
    def _load_sample_data(self):
        """Load sample chore data for testing."""
        if self.chore_manager.chores:
            result = messagebox.askyesno(
                "Load Sample Data",
                "This will add sample chores to your existing list. Continue?"
            )
            if not result:
                return
        
        self.chore_manager.create_sample_chores()
        self._refresh_all()
        messagebox.showinfo("Sample Data", "Sample chores have been loaded!")
    
    def _clear_all_chores(self):
        """Clear all chores after confirmation."""
        result = messagebox.askyesno(
            "Clear All Chores",
            "This will permanently delete all chores. Are you sure?"
        )
        if result:
            self.chore_manager.clear_all_chores()
            self._refresh_all()
            messagebox.showinfo("Cleared", "All chores have been cleared.")
    
    def _show_about(self):
        """Show the about dialog."""
        about_text = """Chores.ai Desktop POC

A simple desktop application for managing daily chores and tasks.

Features:
• Track chores with different frequencies
• Mark chores as complete
• View overdue and completed chores
• Persistent data storage

Version: 1.0
Built with Python and Tkinter"""
        
        messagebox.showinfo("About Chores.ai", about_text)
    
    def _on_closing(self):
        """Handle application closing."""
        # Save any pending changes
        self.chore_manager.save_chores()
        
        # Close the application
        self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the Chores.ai application."""
    app = ChoresAIApp()
    app.run()


if __name__ == "__main__":
    main() 