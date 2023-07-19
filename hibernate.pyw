import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import ephem
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# File path to store the last activated number
STORED_DATA_FILE = os.path.join(os.getcwd(), "last_activated_number.txt")


def hibernate():
    os.system("shutdown /h")


def update_timer():
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = delay - elapsed_time
    if remaining_time <= 0:
        hibernate()
    else:
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_label.config(text=f"Time until hibernation: {minutes:02d}:{seconds:02d}")
        timer_id = window.after(1000, update_timer)


def schedule_hibernate():
    global delay, start_time, timer_id
    delay = entry.get()  # Get the delay value from the text box
    try:
        delay = float(delay)
        if 0 <= delay <= 999:  # Check if delay is within range
            delay *= 60  # Convert minutes to seconds
            start_time = time.time()
            update_timer()
            # Store the last activated number in the file
            with open(STORED_DATA_FILE, "w") as f:
                f.write(entry.get())
            # Change the background image
            with Image.open("background2.png") as image:
                photo = ImageTk.PhotoImage(image)
                bg_label.config(image=photo)
                bg_label.image = photo  # Store reference to avoid garbage collection
            # Show the cancel button
            cancel_button.place(relx=0.5, rely=0.86, anchor="center")
            # Show Timer
            timer_label.place(relx=0.5, rely=0.8, anchor="center")
            # Hide the activate button
            button.place_forget()
            # Hide Hibernate Delay Label
            delay_label.place_forget()
            # Hide Hibernate Time Entry
            entry.place_forget()
    except ValueError:
        pass


def cancel_hibernate():
    if timer_id:
        window.after_cancel(timer_id)
        timer_label.config(text="Hibernation canceled")
        os.system("taskkill /f /im hibernate.exe")
    # Store the last activated number in the file
    with open(STORED_DATA_FILE, "w") as f:
        f.write(entry.get())
    # Close the application window
    window.destroy()


def get_moon_phase(date):
    # Define the observer's location (Quito, Ecuador)
    observer = ephem.Observer()
    observer.lat = '-0.2295'
    observer.long = '-78.5249'

    # Define the date
    observer.date = date

    # Define the moon
    moon = ephem.Moon()

    # Calculate the phase of the moon
    moon.compute(observer)

    # Determine the moon phase name based on the moon's phase
    phase = moon.phase / 100  # Get the moon's phase as a fraction of the cycle

    if 0 <= phase < 0.03 or 0.97 <= phase <= 1:
        return "New Moon"
    elif 0.03 <= phase < 0.125:
        return "Waxing Crescent"
    elif 0.125 <= phase < 0.25:
        return "First Quarter Waxing Crescent"
    elif 0.25 <= phase < 0.375:
        return "First Quarter Waxing Gibbous"
    elif 0.375 <= phase < 0.625:
        return "Waxing Gibbous"
    elif 0.625 <= phase < 0.75:
        return "Full Moon"
    elif 0.75 <= phase < 0.875:
        return "LastQuarter Waning Gibbous"
    elif 0.875 <= phase < 0.97:
        return "Waning Gibbous"

    return "Unknown Phase"  # If the moon phase cannot be determined


def get_days_until_full_moon():
    now = datetime.today()
    days_until_full_moon = ephem.next_full_moon(now)
    return days_until_full_moon


def update_time():
    current_time = time.strftime("%H:%M:%S, %b %d %Y")  # Format the current time and date
    time_label.config(text=current_time)  # Update the time label

    # Schedule the next update in 1 second
    window.after(1000, update_time)


def save_text():
    text = text_entry.get("1.0", "end-1c")  # Get the text from the text entry field
    folder_path = os.path.join(os.getcwd(), "logs")  # Path to the "logs" folder in the app directory
    os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist
    filename = os.path.join(folder_path, datetime.now().strftime("%Y-%m-%d_%H-%M.txt"))  # Generate the filename using current date and time within the "logs" folder
    with open(filename, "w") as file:
        file.write(text)
    status_label.config(text=f"File saved as {filename}")

    # Show the status
    status_label.place(relx=0.5, rely=0.98, anchor="center")


# Create the main window
window = tk.Tk()
window.title("Hibernate App")

# Set the window background to black
window.configure(bg="black")

# Prevent the window from being resizable
window.resizable(False, False)

# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the window position
window_width = 700  # Set the desired window width
window_height = 700  # Set the desired window height
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set the window size and position
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Load the background image
with Image.open("background.png") as image:
    photo = ImageTk.PhotoImage(image)

# Create a label to hold the background image
bg_label = tk.Label(window, image=photo, bg="black")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Set the custom icon for the window
icon_path = "icon.ico"
window.iconbitmap(icon_path)

# Create a custom style for the button
style = ttk.Style()
style.configure(
    "Black.TButton",
    font=("Courier", 10),
    padding=2,
    borderwidth=0,
    relief="solid",
    foreground="black",
    background="white",
)  # Change text color to black

# Create a button with the custom style
button = ttk.Button(window, text="Activate", command=schedule_hibernate, style="Black.TButton")
button.place(relx=0.5, rely=0.9, anchor="center")

# Create a button to cancel hibernation
cancel_button = ttk.Button(window, text="Cancel", command=cancel_hibernate, style="Black.TButton")

# Create a label and entry for the delay time
delay_label = tk.Label(window, text="Hibernate Delay (minutes):", font=("Courier", 13), bg="black", fg="white")
delay_label.place(relx=0.5, rely=0.78, anchor="center")

entry = tk.Entry(window, font=("Courier", 12), justify="center")
entry.place(relx=0.5, rely=0.83, anchor="center")

# Create a label for the timer
timer_label = tk.Label(window, text="", font=("Courier", 14), bg="black", fg="white")

# Create a label for the welcome message
welcome_label = tk.Label(window, text="Hello JP", font=("Courier", 14), bg="black", fg="white")
welcome_label.place(relx=0.04, rely=0.02, anchor="nw")

# Create a label for the daily horoscope
horoscope_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=350, anchor="e", justify="left")
horoscope_label.place(relx=0.96, rely=0.02, anchor="ne")


# Create a label for the current time and date
time_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
time_label.place(relx=0.04, rely=0.1, anchor="w")

# Create a label for the moon phase
moon_phase_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
moon_phase_label.place(relx=0.04, rely=0.14, anchor="w")

# Create a label for the days until full moon
full_moon_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
full_moon_label.place(relx=0.04, rely=0.18, anchor="w")

# Load the animated GIF image
animation_frames = []

# Open the animated GIF and extract each frame
with Image.open("animation.gif") as image:
    for frame in range(image.n_frames):
        image.seek(frame)
        frame_image = ImageTk.PhotoImage(image.copy())
        animation_frames.append(frame_image)

# Create a label to display the animated GIF
animation_label = tk.Label(window, bg="black")
animation_label.place(relx=0.5, rely=0.4, anchor="center")

# Function to animate the GIF frames
def animate_gif(frame=0):
    animation_label.config(image=animation_frames[frame])
    frame = (frame + 1) % len(animation_frames)
    window.after(100, animate_gif, frame)

# Start animating the GIF
animate_gif()

# Create a label and entry for the thought of the day
thought_label = tk.Label(
    window, text="Thought of the day:", font=("Courier", 13), bg="black", fg="white"
)
thought_label.place(relx=0.5, rely=0.57, anchor="center")

# Create a text entry field
text_entry = tk.Text(window, height=3, width=40)
text_entry.place(relx=0.5, rely=0.64, anchor="center")

# Create a button to save the text
save_button = ttk.Button(window, text="Save", command=save_text, style="Black.TButton")
save_button.place(relx=0.5, rely=0.72, anchor="center")

# Create a label to show the status
status_label = tk.Label(window, text="")

# Configure the cursor style for the buttons
button.configure(cursor="hand2")
cancel_button.configure(cursor="hand2")
save_button.configure(cursor="hand2")

# Initialize variables
delay = 0
start_time = 0
timer_id = None

def horoscope(zodiac_sign: int, day: str) -> str:
    url = (
        "https://www.horoscope.com/us/horoscopes/general/"
        f"horoscope-general-daily-{day}.aspx?sign={zodiac_sign}"
    )
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    horoscope_text = soup.find("div", class_="main-horoscope").p
    # Remove the date portion from the horoscope text
    for strong_tag in horoscope_text.find_all("strong"):
        strong_tag.extract()
    horoscope_text = horoscope_text.get_text().strip()
    # Remove the leading " - " prefix
    horoscope_text = horoscope_text.lstrip(" - ")
    return horoscope_text

# Get the horoscope for Sagittarius
horoscope_text = horoscope(9, "today")  # Set Sagittarius as the default sign and "today" as the day
# Update the horoscope label
horoscope_label.config(text=f"{horoscope_text}")
# Calculate the moon phase
moon_phase = get_moon_phase(ephem.now())
# Update the moon phase label
moon_phase_label.config(text=f"Moon Phase: {moon_phase}")
# Calculate the days until the next full moon
days_until_full_moon = get_days_until_full_moon()
# Update the days until full moon label
full_moon_label.config(text=f"Next Full Moon: {days_until_full_moon}")

# Update the current time, date, moon phase, and days until full moon
update_time()

# Run the main event loop
window.mainloop()

# Close the window gracefully
sys.exit()
