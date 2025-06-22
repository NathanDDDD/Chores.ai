# Chores.ai Desktop POC

A desktop application for managing daily chores and tasks, built with Python and Tkinter.

## Overview

Chores.ai is a simple yet powerful chore management application that helps you:
- Track chores with different frequencies (daily, weekly, monthly, custom)
- Mark chores as complete and track streaks
- View overdue and completed chores
- Maintain persistent data storage

## Features

### Core Features
- **Today's Checklist**: View and complete chores due today
- **Chore Management**: Add, edit, and remove chores
- **Frequency Tracking**: Support for daily, weekly, monthly, and custom frequencies
- **Progress Tracking**: Track completion streaks and missed days
- **Persistent Storage**: Data is automatically saved to a JSON file

### UI Components
- **Main Window**: Clean, intuitive interface with tabbed views
- **Add Chore Dialog**: Easy-to-use form for creating new chores
- **Chore Lists**: Organized views for different chore statuses
- **Statistics**: Real-time progress tracking and statistics

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- No external dependencies required (uses built-in tkinter)

### Quick Start
1. Clone or download the project files
2. Ensure all files are in the same directory:
   - `main.py`
   - `chore_model.py`
   - `chore_manager.py`
   - `chore_ui.py`
   - `requirements.txt`
   - `README.md`

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Getting Started
1. **Launch the Application**: Run `python main.py`
2. **Load Sample Data**: Click "Load Sample Data" to see example chores
3. **Add Your Own Chores**: Use "Add New Chore" to create your first chore

### Managing Chores

#### Adding a New Chore
1. Click "Add New Chore" button
2. Fill in the chore details:
   - **Name**: Required - the name of your chore
   - **Description**: Optional - additional details
   - **Frequency Type**: Choose from daily, weekly, monthly, or custom
   - **Frequency Value**: How often (e.g., every 2 days, every 3 weeks)
3. Click "Add Chore"

#### Completing Chores
- **Today's Chores Tab**: Check the checkbox next to a chore to mark it complete
- **All Chores Tab**: Click on any chore to view details
- **Overdue Tab**: View chores that are past their due date

#### Viewing Statistics
The application shows real-time statistics at the top:
- Total number of chores
- Chores due today
- Completed today
- Overdue chores
- Completion rate percentage

### Data Persistence
- All chore data is automatically saved to `chores.json`
- Data persists between application sessions
- No manual save required

## File Structure

```
Chores.ai/
├── main.py              # Main entry point
├── chore_model.py       # Chore data model and logic
├── chore_manager.py     # Chore collection management and persistence
├── chore_ui.py          # Tkinter UI components and main application
├── requirements.txt     # Python dependencies (none for basic POC)
├── README.md           # This documentation
├── chores.json         # Data file (created automatically)
└── Chore.ai.drawio     # Architecture diagram
```

## Architecture

The application follows a simple MVC-like pattern:

### Model (`chore_model.py`)
- `Chore` class: Represents a single chore with all its properties
- Handles frequency calculations, due dates, and completion tracking
- Provides serialization/deserialization for data persistence

### Controller (`chore_manager.py`)
- `ChoreManager` class: Manages the collection of chores
- Handles business logic (filtering, statistics, persistence)
- Coordinates between the UI and data layer

### View (`chore_ui.py`)
- `ChoresAIApp` class: Main application window
- `AddChoreDialog` class: Dialog for adding new chores
- `ChoreListFrame` class: Reusable component for displaying chore lists
- Built with Tkinter for cross-platform compatibility

## Development

### Adding New Features
The modular design makes it easy to extend:

1. **New Chore Properties**: Add fields to the `Chore` class in `chore_model.py`
2. **New UI Views**: Create new frames and add them to the notebook in `chore_ui.py`
3. **New Business Logic**: Add methods to `ChoreManager` class

### Testing
- The application includes sample data for testing
- Use "Load Sample Data" to populate with example chores
- All data is saved locally, so you can experiment safely

## Future Enhancements

This POC provides a solid foundation for future development:

### Planned Features
- **Calendar View**: Visual calendar showing chore completion status
- **Habits Module**: Track daily habits with streak counters
- **Goals Module**: Set and track long-term goals
- **Social Network**: Share progress with friends and family
- **Achievements**: Gamification with badges and rewards
- **Settings**: User preferences and customization options

### Technical Improvements
- **Database Integration**: Replace JSON with SQLite or PostgreSQL
- **Modern UI**: Migrate to PyQt or Kivy for more modern appearance
- **Notifications**: Desktop notifications for due chores
- **Data Export**: Export chore data to CSV or other formats
- **Backup/Restore**: Cloud backup and sync capabilities

## Troubleshooting

### Common Issues

**Import Error**: Make sure all Python files are in the same directory
```
Error importing required modules: No module named 'chore_model'
```

**Permission Error**: Ensure you have write permissions in the directory
```
Error saving chores: [Errno 13] Permission denied
```

**Tkinter Not Available**: Install tkinter (usually included with Python)
```
ModuleNotFoundError: No module named 'tkinter'
```

### Getting Help
1. Check that all required files are present
2. Ensure Python 3.6+ is installed
3. Try running with sample data first
4. Check the console output for error messages

## License

This is a proof-of-concept application. Feel free to use and modify for educational purposes.

## Contributing

This is a POC project, but suggestions and improvements are welcome!

---

**Chores.ai Desktop POC** - Making daily tasks manageable, one chore at a time! 🧹✨