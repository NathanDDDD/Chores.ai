from pywinauto.application import Application
from pywinauto import timings
import time
import os
import sys

# Path to your main.py
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')

# Helper to wait for a window
WAIT_TIME = 2

def test_ui():
    print("Launching Chores.ai Desktop POC UI...")
    quoted_path = f'"{APP_PATH}"'
    app = Application(backend="uia").start(f'python {quoted_path}')
    time.sleep(WAIT_TIME * 2)  # Wait for Tkinter to initialize

    # Get the main window
    win = app.window(title_re=".*Chores.ai.*")
    win.wait('visible', timeout=10)
    print("✓ Main window found")

    # Click the 'Categories' tab
    win.child_window(title="Categories", control_type="TabItem").select()
    time.sleep(WAIT_TIME)

    # Add a category
    win.child_window(title="Add Category", control_type="Button").click()
    time.sleep(WAIT_TIME)
    add_cat = app.window(title_re="Add Category")
    add_cat.child_window(control_type="Edit").type_keys("UIAutoCat{ENTER}")
    time.sleep(WAIT_TIME)
    print("✓ Category added via UI")

    # Edit the category
    win.child_window(title="Edit Category", control_type="Button").click()
    time.sleep(WAIT_TIME)
    edit_cat = app.window(title_re="Edit Category")
    edit_box = edit_cat.child_window(control_type="Edit")
    edit_box.select().type_keys("_Renamed{ENTER}")
    time.sleep(WAIT_TIME)
    print("✓ Category edited via UI")

    # Delete the category
    win.child_window(title="Delete Category", control_type="Button").click()
    time.sleep(WAIT_TIME)
    del_cat = app.window(title_re="Delete Category")
    del_cat.child_window(title="Yes", control_type="Button").click()
    time.sleep(WAIT_TIME)
    print("✓ Category deleted via UI")

    # Add a new chore
    win.child_window(title="Add New Chore", control_type="Button").click()
    time.sleep(WAIT_TIME)
    add_chore = app.window(title_re="Add New Chore")
    add_chore.child_window(control_type="Edit", found_index=0).type_keys("UIAutoChore")
    add_chore.child_window(control_type="Edit", found_index=1).type_keys("General")
    add_chore.child_window(control_type="Edit", found_index=2).type_keys("Automated chore for UI test")
    # Select frequency type: Every X Days
    add_chore.child_window(title="Every X Days", control_type="RadioButton").select()
    add_chore.child_window(control_type="Edit", found_index=3).type_keys("2")
    add_chore.child_window(title="Add Chore", control_type="Button").click()
    time.sleep(WAIT_TIME)
    print("✓ Chore added via UI")

    # Go to Today's Checklist
    win.child_window(title="Today's Checklist", control_type="TabItem").select()
    time.sleep(WAIT_TIME)
    # Mark the new chore as complete (right-click menu)
    tree = win.child_window(control_type="DataGrid")
    first_row = tree.children()[0]
    first_row.right_click_input()
    menu = app.window(control_type="Menu")
    menu.child_window(title="Mark Complete", control_type="MenuItem").click_input()
    time.sleep(WAIT_TIME)
    print("✓ Chore marked complete via UI")

    # Close the app
    win.close()
    print("UI automation test completed successfully!")

if __name__ == "__main__":
    test_ui() 