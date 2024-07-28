import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import Button
from PIL import Image, ImageTk
import time
import ephem
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

# File paths
SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")

# Function to load settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"name": "User", "horoscope_sign": 1}  # Default settings

# Function to save settings
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# Global variable for settings
settings = load_settings()

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
    hours = int(hours_entry.get())
    minutes = int(minutes_entry.get())
    delay = hours * 3600 + minutes * 60
    if 0 <= delay <= 86340:  # Max 23h59m
        start_time = time.time()
        update_timer()
        with open(STORED_DATA_FILE, "w") as f:
            f.write(f"{hours},{minutes}")
        with Image.open("background2.png") as image:
            photo = ImageTk.PhotoImage(image)
            bg_label.config(image=photo)
            bg_label.image = photo
        cancel_button.place(relx=0.65, rely=0.85, anchor="e")
        timer_label.place(relx=0.5, rely=0.85, anchor="e")
        input_frame.place_forget()

def create_hibernate_input():
    global hours_entry, minutes_entry, input_frame
    
    input_frame = tk.Frame(window, bg="black")
    input_frame.place(relx=0.04, rely=0.85, anchor="w")

    delay_label = tk.Label(input_frame, text="Hibernate Delay:", font=("Courier", 11), bg="black", fg="white")
    delay_label.grid(row=0, column=0, padx=(0, 10))

    hours_entry = tk.Entry(input_frame, font=("Courier", 11), justify="center", width=4, bg="black", fg="white", insertbackground="white")
    hours_entry.grid(row=0, column=1, padx=(0, 5))
    hours_entry.insert(0, "0")

    hours_label = tk.Label(input_frame, text="h", font=("Courier", 11), bg="black", fg="white")
    hours_label.grid(row=0, column=2, padx=(0, 5))

    minutes_entry = tk.Entry(input_frame, font=("Courier", 11), justify="center", width=4, bg="black", fg="white", insertbackground="white")
    minutes_entry.grid(row=0, column=3, padx=(0, 5))
    minutes_entry.insert(0, "0")

    minutes_label = tk.Label(input_frame, text="m", font=("Courier", 11), bg="black", fg="white")
    minutes_label.grid(row=0, column=4)

    for entry in (hours_entry, minutes_entry):
        entry.bind("<Up>", lambda event, e=entry: adjust_value(e, 1))
        entry.bind("<Down>", lambda event, e=entry: adjust_value(e, -1))
        entry.bind("<Right>", lambda event, e=entry: adjust_value(e, 5))
        entry.bind("<Left>", lambda event, e=entry: adjust_value(e, -5))

def adjust_value(entry, delta):
    try:
        value = int(entry.get())
        new_value = max(0, value + delta)
        if entry == minutes_entry:
            new_value = min(59, new_value)
        entry.delete(0, tk.END)
        entry.insert(0, str(new_value))
    except ValueError:
        pass

def cancel_hibernate():
    if timer_id:
        window.after_cancel(timer_id)
        timer_label.config(text="Hibernation canceled")
        os.system("taskkill /f /im hibernate.exe")
    with open(STORED_DATA_FILE, "w") as f:
        f.write(f"{hours_entry.get()},{minutes_entry.get()}")
    window.destroy()

def get_current_moon_phase():
    url = "https://www.moongiant.com/phase/today/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    moon_details_div = soup.find("div", id="moonDetails")
    moon_phase_span = moon_details_div.find("span")
    moon_phase = moon_phase_span.get_text().strip()
    return moon_phase

def get_current_moon_age():
    url = "https://www.moongiant.com/phase/today/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    moon_details_div = soup.find("div", id="moonDetails")
    moon_age_spans = moon_details_div.find_all("span")
    moon_age = moon_age_spans[2].get_text().strip()
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
    with Image.open("moons.png") as moonsImage:
        photo = ImageTk.PhotoImage(moonsImage)
    moons_image_label = tk.Label(window, image=photo, bg="black")
    moons_image_label.image = photo
    moons_image_label.place(relx=0, rely=0.28, anchor="nw")

def get_days_until_full_moon():
    now = datetime.today()
    days_until_full_moon = ephem.next_full_moon(now)
    return days_until_full_moon

def update_time():
    current_time = time.strftime("%H:%M:%S, %b %d %Y")
    time_label.config(text=current_time)
    window.after(1000, update_time)

def save_text():
    text = text_entry.get("1.0", "end-1c")
    folder_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, datetime.now().strftime("%Y-%m-%d_%H-%M.txt"))
    with open(filename, "w") as file:
        file.write(text)
    status_label.config(text=f"File saved as {filename}")
    status_label.place(relx=0.5, rely=0.98, anchor="center")

def horoscope(zodiac_sign: int, day: str) -> str:
    url = (
        "https://www.horoscope.com/us/horoscopes/general/"
        f"horoscope-general-daily-{day}.aspx?sign={zodiac_sign}"
    )
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    horoscope_text = soup.find("div", class_="main-horoscope").p
    for strong_tag in horoscope_text.find_all("strong"):
        strong_tag.extract()
    horoscope_text = horoscope_text.get_text().strip()
    horoscope_text = horoscope_text.lstrip(" - ")
    return horoscope_text

def animate_gif(frame=0):
    animation_label.config(image=animation_frames[frame])
    frame = (frame + 1) % len(animation_frames)
    window.after(100, animate_gif, frame)

def create_settings_overlay():
    global settings_frame
    settings_frame = tk.Frame(window, bg="black", width=window.winfo_width(), height=window.winfo_height())
    settings_frame.place(x=0, y=0)

    settings_content = tk.Frame(settings_frame, bg="black")
    settings_content.place(relx=0.5, rely=0.5, anchor="center")

    name_label = tk.Label(settings_content, text="Your Name:", font=("Courier", 10), bg="black", fg="white")
    name_label.pack(pady=10)
    name_entry = tk.Entry(settings_content, font=("Courier", 10))
    name_entry.insert(0, settings['name'])
    name_entry.pack()

    sign_label = tk.Label(settings_content, text="Your Horoscope Sign:", font=("Courier", 10), bg="black", fg="white")
    sign_label.pack(pady=10)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sign_var = tk.StringVar(settings_content)
    sign_var.set(signs[settings['horoscope_sign'] - 1])
    sign_menu = tk.OptionMenu(settings_content, sign_var, *signs)
    sign_menu.pack()

    def check_changes():
        return (name_entry.get() != settings['name'] or
                signs.index(sign_var.get()) + 1 != settings['horoscope_sign'])

    apply_button = ttk.Button(settings_content, text="Apply", style="Black.TButton")
    apply_button.pack(pady=10)

    close_button = ttk.Button(settings_content, text="Close", command=close_settings, style="Black.TButton")
    close_button.pack(pady=5)

    def apply_settings():
        if check_changes():
            apply_button.config(text="Saving...")
            settings['name'] = name_entry.get()
            settings['horoscope_sign'] = signs.index(sign_var.get()) + 1
            save_settings(settings)
            update_welcome_label()
            update_horoscope()
            window.after(1000, close_settings)

    apply_button.config(command=apply_settings)

    def update_apply_button(*args):
        apply_button.config(state="normal" if check_changes() else "disabled")

    name_entry.bind("<KeyRelease>", update_apply_button)
    sign_var.trace("w", update_apply_button)

    update_apply_button()

def close_settings():
    settings_frame.destroy()

def open_settings():
    create_settings_overlay()

def update_welcome_label():
    welcome_label.config(text=f"Hello {settings['name']}")

def update_horoscope():
    horoscope_text = horoscope(settings['horoscope_sign'], "today")
    horoscope_label.config(text=f"{horoscope_text}")

# Create the main window
window = tk.Tk()
window.title("Nighty Night")
window.configure(bg="black")
window.resizable(False, False)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = 700
window_height = 640
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

with Image.open("background.png") as image:
    photo = ImageTk.PhotoImage(image)

bg_label = tk.Label(window, image=photo, bg="black")
bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

show_moons_image()

icon_path = "icon.ico"
window.iconbitmap(icon_path)

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

create_hibernate_input()

button = Button(input_frame, text="Activate", command=schedule_hibernate, bg='black', fg='white', font=("Courier", 10))
button.grid(row=0, column=5, padx=(10, 0))

cancel_button = Button(window, text="Cancel", command=cancel_hibernate, bg='black', fg='white', font=("Courier", 12))

timer_label = tk.Label(window, text="", font=("Courier", 14), bg="black", fg="white")

welcome_label = tk.Label(window, text="", font=("Courier", 14), bg="black", fg="white")
welcome_label.place(relx=0.04, rely=0.04, anchor="nw")

horoscope_title = tk.Label(
    window, text="Daily Horoscope:", font=("Courier", 10), bg="black", fg="white"
)
horoscope_title.place(relx=0.04, rely=0.51, anchor="nw")

horoscope_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=350, anchor="e", justify="left")
horoscope_label.place(relx=0.04, rely=0.55, anchor="nw")
horoscope_label.config(wraplength=300) 

quote_title = tk.Label(
    window, text="Latest Quote:", font=("Courier", 10), bg="black", fg="white"
)
quote_title.place(relx=0.52, rely=0.51, anchor="nw")

quote_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=350, anchor="e", justify="left")
quote_label.place(relx=0.52, rely=0.55, anchor="nw")
quote_label.config(wraplength=300)

quote_author_label = tk.Label(window, text="", font=("Courier", 9), bg="black", fg="white", wraplength=300, anchor="e", justify="left")
quote_author_label.place(relx=0.52, rely=0.59 + (quote_label.winfo_reqheight() / window.winfo_reqheight()) + 0.01, anchor="nw")

time_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
time_label.place(relx=0.04, rely=0.10, anchor="nw")

moon_phase_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
moon_phase_label.place(relx=0.04, rely=0.15, anchor="nw")

moon_age_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
moon_age_label.place(relx=0.04, rely=0.18, anchor="nw")

full_moon_label = tk.Label(window, text="", font=("Courier", 10), bg="black", fg="white")
full_moon_label.place(relx=0.04, rely=0.21, anchor="nw")

animation_frames = []
with Image.open("animation.gif") as image:
    for frame in range(image.n_frames):
        image.seek(frame)
        frame_image = ImageTk.PhotoImage(image.copy())
        animation_frames.append(frame_image)

animation_label = tk.Label(window, bg="black")
animation_label.place(relx=0.6, rely=0.02, anchor="nw")

animate_gif()

thought_label = tk.Label(
    window, text="Thought of the day:", font=("Courier", 11), bg="black", fg="white")
thought_label.place(relx=0.04, rely=0.95, anchor="sw")

text_entry = tk.Text(window, height=2, width=40, bg="black", fg="white", insertbackground="white")
text_entry.place(relx=0.31, rely=0.94, anchor="w")

save_button = Button(window, text="Save", command=save_text, bg='black', fg='white', font=("Courier", 10))
save_button.place(relx=0.785, rely=0.94, anchor="w")

status_label = tk.Label(window, text="")

button.configure(cursor="hand2")
cancel_button.configure(cursor="hand2")
save_button.configure(cursor="hand2")

delay = 0
start_time = 0
timer_id = None

update_horoscope()

quote_of_the_day = get_quote_of_the_day()
quote_label.config(text=f"{quote_of_the_day}")

quote_author = get_quote_of_the_day_author()
quote_author_label.config(text=f"{quote_author}")

moon_phase = get_current_moon_phase()
moon_phase_label.config(text=f"Moon Phase: {moon_phase}")

moon_age = get_current_moon_age()
moon_age_label.config(text=f"Moon Age: {moon_age}")

days_until_full_moon = get_days_until_full_moon()
full_moon_label.config(text=f"Next Full Moon: {days_until_full_moon}")

update_time()

# Load the settings icon
settings_icon = Image.open("settings-icon.png")  # Make sure you have this icon file
settings_icon = settings_icon.resize((20, 20), Image.LANCZOS)  # Resize the icon as needed
settings_icon = ImageTk.PhotoImage(settings_icon)

# Create the settings button with an icon
settings_button = ttk.Button(window, image=settings_icon, command=open_settings, style="Icon.TButton")
settings_button.place(relx=0.999, rely=0.001, anchor="ne")

# Create a new style for the icon button
style.configure(
    "Icon.TButton",
    padding=0,
    relief="flat",
    background="black"
)

update_welcome_label()

window.mainloop()

sys.exit()