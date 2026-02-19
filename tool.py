import tkinter as tk
from tkinter import ttk
import threading
from main import checkCourtAvailability 

# ---------- Helper Functions ----------

def set_status(row, text="", color="white"):
    """Set the status box text and background color."""
    status = entries[row][5]
    status.config(state="normal")
    status.delete(0, "end")
    status.insert(0, text)
    status.config(bg=color)
    status.config(state="readonly")


def checkBookingStatus(row):
    """Check booking status for a row."""
    park = entries[row][2].get()
    date = entries[row][3].get()
    time = entries[row][4].get()
    
    valid = True
    if park == "" or date == "" or time == "":
        valid = False
    
    if not valid:
        print(f"Insufficient data to check booking status for row {row}")
        set_status(row, "Invalid", "red")
        return

    # Show "..." while checking
    set_status(row, "...", "yellow")
    
    park_slug = park.lower().replace(" ", "-")
    day, month, year = date.split("/")
    date_formatted = f"{year}-{month}-{day}"
    
    print(f"Checking booking status at {park_slug} on {date_formatted} at {time}")
    
    # Call your API (this can take time)
    available, court_name = checkCourtAvailability(park_slug, date_formatted, time)

    # Update status with color
    if available:
        print(f"Court available: {court_name}")
        set_status(row, "Available", "lightgreen")
    else:
        print("Court unavailable")
        set_status(row, "Unavailable", "red")


def paste_into_row(row):
    """Paste clipboard content into a row's first 4 columns."""
    try:
        data = root.clipboard_get()
    except tk.TclError:
        return 

    parts = data.split("\t")  # Google Sheets uses tabs

    for i in range(min(4, len(parts))):
        entries[row][1 + i].delete(0, tk.END)
        entries[row][1 + i].insert(0, parts[i])

    # Run booking check in a separate thread to prevent freeze
    threading.Thread(target=checkBookingStatus, args=(row,), daemon=True).start()


def delete_row():
    """Delete the last row (except row 0)."""
    global row_count
    if row_count == 0:
        return

    for widget in entries[row_count]:
        widget.destroy()

    del entries[row_count]
    row_count -= 1


def add_row():
    """Add a new row to the table."""
    global row_count
    row_count += 1
    entries[row_count] = []

    grid_row = row_count + 1  # +1 because headers are on row 0

    # Paste button
    paste_btn = ttk.Button(table_frame, text="P", width=3,
                           command=lambda r=row_count: paste_into_row(r))
    paste_btn.grid(row=grid_row, column=0, padx=5, pady=5)
    entries[row_count].append(paste_btn)

    # Main 4 input columns
    for col in range(4):
        entry = tk.Entry(table_frame)
        entry.grid(row=grid_row, column=col + 1, padx=5, pady=5)
        entries[row_count].append(entry)

    # Status box (tk.Entry to allow background color)
    status = tk.Entry(table_frame, width=10, state="readonly")
    status.grid(row=grid_row, column=5, padx=5, pady=5)
    status.insert(0, "")
    entries[row_count].append(status)

    # "B" button
    b_button = ttk.Button(table_frame, text="B", width=2)
    b_button.grid(row=grid_row, column=6, padx=5, pady=5)
    entries[row_count].append(b_button)


# ---------- GUI Setup ----------

root = tk.Tk()
root.title("Booking Table")

table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=10)

# Column headers
headers = ["", "Email", "Park", "Date", "Time", "Status", "Book"]
for col, text in enumerate(headers):
    label = ttk.Label(table_frame, text=text, font=("Arial", 10, "bold"))
    label.grid(row=0, column=col, padx=5, pady=5)

entries = {}
row_count = 0

# ---- Initial Row ----

entries[row_count] = []

# Paste button
paste_btn = ttk.Button(table_frame, text="P", width=3,
                       command=lambda r=row_count: paste_into_row(r))
paste_btn.grid(row=1, column=0, padx=5, pady=5)
entries[row_count].append(paste_btn)

# Editable input fields
for col in range(4):
    entry = tk.Entry(table_frame)
    entry.grid(row=1, column=col + 1, padx=5, pady=5)
    entries[row_count].append(entry)

# Status box
status = tk.Entry(table_frame, width=10, state="readonly")
status.grid(row=1, column=5, padx=5, pady=5)
status.insert(0, "")
entries[row_count].append(status)

# B button
b_button = ttk.Button(table_frame, text="B", width=2)
b_button.grid(row=1, column=6, padx=5, pady=5)
entries[row_count].append(b_button)

# Buttons to add & delete rows
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = ttk.Button(button_frame, text="Add Row", command=add_row)
add_button.pack(side=tk.LEFT, padx=5)

del_button = ttk.Button(button_frame, text="Delete Row", command=delete_row)
del_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
