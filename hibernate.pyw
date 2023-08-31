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

# Create the main window
window1 = tk.Tk()
window1.overrideredirect(True)  # Remove window border and title bar

# Set the window background to black
window1.configure(bg="black")

# Prevent the window from being resizable
window1.resizable(False, False)

# Get the screen width and height
screen_width = window1.winfo_screenwidth()
screen_height = window1.winfo_screenheight()

# Calculate the window position
window1_width = 500  # Set the desired window width
window1_height = 500  # Set the desired window height
x = (screen_width - window1_width) // 2
y = (screen_height - window1_height) // 2

# Set the window size and position
window1.geometry(f"{window1_width}x{window1_height}+{x}+{y}")

# Load the image
image_path = "opening-screen.png"  # Replace with the actual image path
with Image.open(image_path) as image1:
    photo = ImageTk.PhotoImage(image1)

# Create a label to hold the image
image1_label = tk.Label(window1, image=photo)
image1_label.pack()

# Display the image
window1.update()

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
            cancel_button.place(relx=0.5, rely=0.96, anchor="center")
            # Show Timer
            timer_label.place(relx=0.5, rely=0.91, anchor="center")
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

# Add the get_current_moon_phase() function
def get_current_moon_phase():
    url = "https://www.moongiant.com/phase/today/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    moon_details_div = soup.find("div", id="moonDetails")
    moon_phase_span = moon_details_div.find("span")
    moon_phase = moon_phase_span.get_text().strip()
    return moon_phase

# Add the get_current_moon_age() function
def get_current_moon_age():
    url = "https://www.moongiant.com/phase/today/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    moon_details_div = soup.find("div", id="moonDetails")
    moon_age_spans = moon_details_div.find_all("span")  # Find all span elements inside the moonDetails div
    moon_age = moon_age_spans[2].get_text().strip()  # Get the text from the third span element (index 2)
    return moon_age

def get_quote_of_the_day():
    url = "https://www.philosophybits.com"
    try:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        quote_element = soup.find("blockquote", class_="medium")
        quote_text = quote_element.get_text().strip()
        return quote_text
    except Exception as e:
        print("Error occurred while fetching the quote:", e)
        return "Quote not available"

def get_quote_of_the_day_author():
    url = "https://www.philosophybits.com"
    try:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        quote_element = soup.find("blockquote", class_="medium")
        author_element = quote_element.find_next_sibling("div", class_="source")
        author_text = author_element.get_text().strip()
        return author_text
    except Exception as e:
        print("Error occurred while fetching the author:", e)
        return "Author not available"

def show_moons_image():
    # Load the new image
    with Image.open("moon_phases_image.jpg") as moonsImage:
        photo = ImageTk.PhotoImage(moonsImage)

    # Create a label to display the new image
    moons_image_label = tk.Label(window, image=photo, bg="black")
    moons_image_label.image = photo  # Store reference to avoid garbage collection
    moons_image_label.place(relx=0, rely=0, anchor="nw")

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

time.sleep(4)  # Display the image for 3 seconds

# Close the image window
window1.destroy()

# Create the main window
window = tk.Tk()
window.title("Nighty Night")

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

# Call the function to show the new image and "Image" label when the application starts
show_moons_image()

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
    relief="flat",
    foreground="black",
    background="black",
    highlightbackground="white",
)

# Create a custom style for the button
style2 = ttk.Style()
style2.configure(
    "main.TButton",
    font=("Courier", 8),
    padding=2,
    borderwidth=0,
    relief="flat",
    overrelief="raised",
    foreground="black",
    background="black",
    highlightbackground="black",
)

# Create a label and entry for the delay time
delay_label = tk.Label(window, text="Hibernate Delay (minutes):", font=("Courier", 11), bg="black", fg="white")
delay_label.place(relx=0.04, rely=0.921, anchor="w")

entry = tk.Entry(window, font=("Courier", 10), justify="center", width=8)
entry.place(relx=0.395, rely=0.92, anchor="w")

# Create a button with the custom style
button = ttk.Button(window, text="Activate", command=schedule_hibernate, style="main.TButton")
button.place(relx=0.51, rely=0.92, anchor="w")

# Create a button to cancel hibernation
cancel_button = ttk.Button(window, text="Cancel", command=cancel_hibernate, style="Black.TButton")

# Create a label for the timer
timer_label = tk.Label(window, text="", font=("Courier", 14), bg="black", fg="white")

# Create a label for the welcome message
welcome_label = tk.Label(window, text="Hello JP", font=("Courier", 14), bg="black", fg="white")
welcome_label.place(relx=0.04, rely=0.22, anchor="nw")

# Create a label for the Daily Horoscope Title
horoscope_title = tk.Label(
    window, text="Daily Horoscope:", font=("Courier", 10), bg="black", fg="white"
)
horoscope_title.place(relx=0.96, rely=0.23, anchor="ne")

# Create a label for the daily horoscope
horoscope_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=350, anchor="e", justify="left")
horoscope_label.place(relx=0.96, rely=0.27, anchor="ne")

# Create a label for the daily quote Title
quote_title = tk.Label(
    window, text="Latest Quote:", font=("Courier", 10), bg="black", fg="white"
)
quote_title.place(relx=0.96, rely=0.5, anchor="ne")

# Create a label for the daily quote
quote_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=350, anchor="e", justify="left")
quote_label.place(relx=0.96, rely=0.54, anchor="ne")

# Create a label for the daily quote author
quote_author_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=300, anchor="e", justify="left")
quote_author_label.place(relx=0.96, rely=0.54 + (quote_label.winfo_reqheight() / window.winfo_reqheight()) + 0.01, anchor="ne")

# Create a label for the current time and date
time_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
time_label.place(relx=0.04, rely=0.28, anchor="w")

# Create a label for the moon phase
moon_phase_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
moon_phase_label.place(relx=0.04, rely=0.34, anchor="nw")

# Create a label for the moon age
moon_age_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
moon_age_label.place(relx=0.04, rely=0.38, anchor="nw")

# Create a label for the days until full moon
full_moon_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
full_moon_label.place(relx=0.04, rely=0.42, anchor="nw")

# Load the animated GIF image
animation_frames = []

# Open the animated GIF and extract each frame
with Image.open("animation.gif") as image:
    for frame in range(image.n_frames):
        image.seek(frame)
        frame_image = ImageTk.PhotoImage(image.copy())
        animation_frames.append(frame_image)

# Function to animate the GIF frames
def animate_gif(frame=0):
    animation_label.config(image=animation_frames[frame])
    frame = (frame + 1) % len(animation_frames)
    window.after(100, animate_gif, frame)

# Create a label to display the animated GIF
animation_label = tk.Label(window, bg="black")
animation_label.place(relx=0.1, rely=0.51, anchor="nw")

# Start animating the GIF
animate_gif()

# Create a label and entry for the thought of the day
thought_label = tk.Label(
    window, text="Thought of the day:", font=("Courier", 11), bg="black", fg="white")
thought_label.place(relx=0.04, rely=0.87, anchor="sw")

# Create a text entry field
text_entry = tk.Text(window, height=2, width=40)
text_entry.place(relx=0.31, rely=0.85, anchor="w")

# Create a button to save the text
save_button = ttk.Button(window, text="Save", command=save_text, style="Black.TButton")
save_button.place(relx=0.785, rely=0.85, anchor="w")

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

# Get the horoscope for Sagittarius
horoscope_text = horoscope(9, "today")  # Set Sagittarius as the default sign and "today" as the day
# Update the horoscope label
horoscope_label.config(text=f"{horoscope_text}")
# Get the quote of the day and update label
quote_of_the_day = get_quote_of_the_day()
quote_label.config(text=f"{quote_of_the_day}")
# Get the quote of the day author and update label
quote_author = get_quote_of_the_day_author()
quote_author_label.config(text=f"{quote_author}")
# Get the current moon phase and update the moon phase label
moon_phase = get_current_moon_phase()
moon_phase_label.config(text=f"Moon Phase: {moon_phase}")
# Get the current moon age and update the moon age label
moon_age = get_current_moon_age()
moon_age_label.config(text=f"Moon Age: {moon_age}")
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
