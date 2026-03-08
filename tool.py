import tkinter as tk
from tkinter import ttk, messagebox
import threading
from main import checkCourtAvailability, bookCourt, addDiscount, checkVoucher
from datetime import datetime, timedelta
from sendEmail import send_email_booked, send_email_denied, send_email_unavailable
import json
import os

# ---------- Helper Functions ----------

def get_week_monday(date):
    monday = date - timedelta(days=date.weekday())
    return monday.isoformat()  # "2026-03-02"

DB_FILE = "weekly_bookings.json"
weekly_db = {}
current_week_key = get_week_monday(datetime.now().date())

def init_week_database():
    global weekly_db

    print ("Initializing weekly database...")
    # Load existing database
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            weekly_db = json.load(f)
    else:
        weekly_db = {}

    # Ensure this week exists
    if current_week_key not in weekly_db:
        print (f"No entry for current week ({current_week_key}). Creating new entry.")
        weekly_db[current_week_key] = []
        save_database()
    else:
        print (f"Entry for current week ({current_week_key}) already exists.")

def save_database():
    with open(DB_FILE, "w") as f:
        json.dump(weekly_db, f, indent=4)

def manual_court_popup(row):
    popup = tk.Toplevel(root)
    popup.title("Gate Code Input")
    popup.grab_set()
    popup.resizable(False, False)

    width = 350
    height = 180

    # Get main window position & size
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)

    popup.geometry(f"{width}x{height}+{x}+{y}")

    # ---- UI ----
    ttk.Label(popup, text="Enter gate code:", font=("Arial", 11)).pack(pady=(20, 10))

    entry = tk.Entry(popup, justify="center", font=("Arial", 12))
    entry.pack(pady=5)
    entry.focus()

    def confirm():
        gate_code = entry.get()
        email = entries[row][1].get()
        park = entries[row][3].get()
        date = entries[row][4].get()
        time = entries[row][5].get()
        court = entries[row][6].get().split(" ")[1]

        send_email_booked(email, park, date, time, court, gate_code)

        entries[row][7].config(state="disabled")
        popup.destroy()

    ttk.Button(popup, text="Confirm", command=confirm).pack(pady=20)

    # Allow Enter key to submit
    popup.bind("<Return>", lambda event: confirm())

def set_status(row, text=""):
    """Set the status box text and background color."""
    status = entries[row][6]  # Index 6 corresponds to the Status column
    status.config(state="normal")
    status.delete(0, "end")
    status.insert(0, text)
    status.config(state="readonly")

def checkBookingStatus(row):
    """Check booking status for a row."""

    blocked_hours = {
        "monday": ["12:00", "13:00", "14:00", "15:00"],
        "wednesday": ["12:00", "13:00", "14:00", "15:00", "16:00"],
        "friday": ["14:00", "15:00"]
    }

    days_buffer = 3

    request_time = entries[row][0].get().split(" ")[0] 
    park = entries[row][3].get()
    date = entries[row][4].get()
    time = entries[row][5].get()
    email = entries[row][1].get()
    
    request_date = datetime.strptime(request_time, '%d/%m/%Y').date()
    booking_date = datetime.strptime(date, '%d/%m/%Y').date()
    days_difference = (booking_date - request_date).days

    booking_monday = get_week_monday(booking_date) 
    if booking_monday not in weekly_db:
        weekly_db[booking_monday] = []
        save_database()

    valid = True
    if park == "" or date == "" or time == "":
        valid = False
    
    if not valid:
        print(f"Insufficient data to check booking status for row {row}")
        set_status(row, "Invalid")
        entries[row][7].config(state="disabled")
        return

    if days_difference < days_buffer:
        print(f"Booking date must be at least {days_buffer} days in the future. Date requested: {request_date}, Booking date: {booking_date}")
        set_status(row, "Not 3 Days")
        entries[row][7].config(text="D")
        entries[row][7].config(command=lambda: denyBooking(row, f"booking must be made at least {days_buffer} days in advance"))
        return

    day_of_week = booking_date.strftime("%A").lower() 
    dt = datetime.strptime(time, "%I%p")
    formatted = dt.strftime("%H:%M") #13:00

    if day_of_week in blocked_hours and formatted in blocked_hours[day_of_week]:
        print(f"Time slot {time} on {day_of_week.capitalize()}s is blocked for booking.")
        set_status(row, "Blocked Hour")
        entries[row][7].config(text="D")
        entries[row][7].config(command=lambda: denyBooking(row, f"{time} on {day_of_week.capitalize()}s is unavailable for booking due to social sessions."))
        return
    
    if email in weekly_db[booking_monday]:
        print(f"User {email} has already booked courts this week.")
        set_status(row, "Hit Limit")
        entries[row][7].config(text="D")
        entries[row][7].config(command=lambda: denyBooking(row, f"you have already booked your 1 hour for this week"))
        return

    set_status(row, "...")
    
    park_slug = park.lower().replace(" ", "-")
    day, month, year = date.split("/")
    date_formatted = f"{year}-{month}-{day}"    
    
    print(f"Checking booking status at {park_slug} on {date_formatted} at {time}")
    
    available, court_name = checkCourtAvailability(park_slug, date_formatted, time)

    if available:
        print(f"Court available: {court_name}")
        set_status(row, court_name)
    else:
        print("Court unavailable")
        set_status(row, "Unavailable")
        entries[row][7].config(text="U")
        entries[row][7].config(command=lambda: denyBooking(row, f"court unavailable"))


def denyBooking(row, reason):
    email = entries[row][1].get()
    name = entries[row][2].get().split(" ")[0]

    if reason == "you have already booked your 1 hour for this week":
        send_email_denied(email, name, reason) 
    elif reason != "court unavailable":
        send_email_denied(email, name, reason) 
    else: 
        send_email_unavailable(email, name)

    entries[row][7].config(state="disabled")

def bookAndDiscountCourt(row):
    global uses_left

    """Book the court for the given row."""

    email = entries[row][1].get()
    firstName = entries[row][2].get().split(" ")[0]
    park = entries[row][3].get().lower().replace(" ", "_")
    date = entries[row][4].get()

    day, month, year = date.split("/")
    date_formatted = f"{year}-{month}-{day}"

    time = entries[row][5].get()

    time_Formatted = datetime.strptime(time, "%I%p").strftime("%H:%M")

    booking_date = datetime.strptime(date, '%d/%m/%Y').date()
    booking_monday = get_week_monday(booking_date) 

    court = entries[row][6].get().split(" ")
    if len(court) > 1:
        court = court[1]
    else:
        court = court[0]

    print(f"Attempting to book court for {firstName} at {park} on {date_formatted} at {time_Formatted} with email {email}, court: {court}")

    if court in ["Unavailable", "Invalid", ""]:
        messagebox.showerror("Error", "Court Unavailable for Booking.")
        return
    response1 = bookCourt(park, court, date_formatted, time_Formatted)
    response2 = addDiscount(voucher_code)

    if response1 == 200 and response2 == 200:
        manual_court_popup(row)
        uses_left -= 1 
        uses_label.config(text=f"Uses left: {uses_left}")
        weekly_db[booking_monday].append(email)
        save_database()

        print (f"Booking successful for {email}, court {court} on {date_formatted} at {time_Formatted}. Discount applied. Emailed added to database. Uses left: {uses_left}")
    else:
        messagebox.showerror("Error", "Booking or Discount Failed. Check console for details.")

def paste_into_table():
    try:
        data = root.clipboard_get()
    except tk.TclError:
        return 

    lines = data.split("\n")

    for row in range(len(lines)):
        
        if row != 0:
            add_row() 

        parts = lines[row].split("\t")  # Google Sheets uses tabs

        for i in range(min(6, len(parts))):
            entries[row][i].delete(0, tk.END)
            entries[row][i].insert(0, parts[i])

        # Run booking check in a separate thread to prevent freeze
        threading.Thread(target=checkBookingStatus, args=(row,), daemon=True).start()

def clear_table():
    """Delete all rows except row 0 and clear row 0 contents."""
    global row_count

    # Delete all rows except row 0
    for row in range(1, row_count + 1):
        for widget in entries[row]:
            widget.destroy()

    # Clear row 0 contents
    for col in range(6):
        entries[0][col].delete(0, tk.END)

    # Clear status column separately (readonly field)
    entries[0][6].config(state="normal")
    entries[0][6].delete(0, tk.END)
    entries[0][6].config(state="readonly")

    # Reset row_count
    row_count = 0

def add_row():
    """Add a new row to the table."""
    global row_count
    row_count += 1
    entries[row_count] = []

    grid_row = row_count + 1  # +1 because headers are on row 0

    # Main 6 input columns
    for col in range(6):
        entry = tk.Entry(table_frame)
        entry.grid(row=grid_row, column=col, padx=5, pady=5)
        entries[row_count].append(entry)

    # Status box
    status = tk.Entry(table_frame, width=10, state="readonly")
    status.grid(row=grid_row, column=6, padx=5, pady=5)
    status.insert(0, "")
    entries[row_count].append(status)

    # "B" Book button
    b_button = ttk.Button(table_frame, text="B", width=2, command=lambda r=row_count: bookAndDiscountCourt(r))
    b_button.grid(row=grid_row, column=7, padx=5, pady=5)
    entries[row_count].append(b_button)

uses_left = 0 
voucher_code = "NA"

def populate_voucher_info():
    global voucher_code, uses_left
    voucher_code, uses_left = checkVoucher()#

    uses_left = int(uses_left) 
    
    voucher_label.config(text=f"Voucher: {voucher_code}")
    uses_label.config(text=f"Uses left: {uses_left}")

# ---------- GUI Setup ----------

root = tk.Tk()
root.title("Booking Table")

table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=10)

# Column headers
headers = ["Date Requested", "Email", "Name", "Park", "Date", "Time", "Status", "Book"]
for col, text in enumerate(headers):
    label = ttk.Label(table_frame, text=text, font=("Arial", 10, "bold"))
    label.grid(row=0, column=col, padx=5, pady=5)

entries = {}
row_count = 0

voucher = "Loading..."
uses_left = "Loading..."

# ---- Initial Row ----

entries[row_count] = []

# Editable input fields
for col in range(6):
    entry = tk.Entry(table_frame)
    entry.grid(row=1, column=col, padx=5, pady=5)
    entries[row_count].append(entry)

# Status box
status = tk.Entry(table_frame, width=10, state="readonly")
status.grid(row=1, column=6, padx=5, pady=5)
status.insert(0, "")
entries[row_count].append(status)

# B button
b_button = ttk.Button(table_frame, text="B", width=2, command=lambda r=row_count: bookAndDiscountCourt(r))
b_button.grid(row=1, column=7, padx=5, pady=5)
entries[row_count].append(b_button)

# Voucher display (between table and buttons)
voucher_frame = tk.Frame(root)
voucher_frame.pack(pady=5, anchor="w")

voucher_label = tk.Label(voucher_frame, text=f"Voucher: {voucher}", font=("Arial", 10), padx=15)
voucher_label.pack(anchor="w")

uses_label = tk.Label(voucher_frame, text=f"Uses left: {uses_left}", font=("Arial", 10), padx=15)
uses_label.pack(anchor="w")
root.after(100, populate_voucher_info)

# Buttons to add & delete rows
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

paste_btn = ttk.Button(button_frame, text="Paste", command=paste_into_table)
paste_btn.pack(side=tk.LEFT, padx=5)

clear_btn = ttk.Button(button_frame, text="Clear Table", command=clear_table)
clear_btn.pack(side=tk.LEFT, padx=5)

init_week_database()
root.mainloop()