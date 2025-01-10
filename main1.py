import pywhatkit as pyw
import webbrowser
import time
import os
import re
import shutil
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkbootstrap import Style
import threading
import pyautogui
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Browser paths (update these if your browser is installed in a different location)
BROWSER_PATHS = {
    "chrome": [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ],
    "edge": [
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    ],
    "firefox": [
        "C:/Program Files/Mozilla Firefox/firefox.exe",
    ],
}

# Multi-language support
LANGUAGES = {
    "English": {
        "title": "WhatsApp Message Scheduler",
        "phone_label": "Recipient's Phone Number (with country code):",
        "message_label": "Message:",
        "template_label": "Select a Template:",
        "attachment_label": "Attachments (optional):",
        "time_label": "Scheduled Time (24-hour format):",
        "browser_label": "Select Browser/App:",
        "schedule_button": "Schedule Message",
        "view_scheduled_button": "View Scheduled Messages",
        "no_files_selected": "No files selected",
        "success": "Success",
        "error": "Error",
        "invalid_phone": "Invalid phone number. Please include the country code (e.g., +91).",
        "empty_message": "Message cannot be empty.",
        "invalid_time": "Invalid time. Please enter a future time.",
        "browser_not_found": "Browser '{browser}' is not installed. Please install it or use the default browser.",
        "scheduled_success": "Message scheduled successfully!",
        "sent_success": "Message sent successfully!",
        "send_failed": "Failed to send the message. Please try again.",
    },
    "Spanish": {
        "title": "Programador de Mensajes de WhatsApp",
        "phone_label": "Número de teléfono del destinatario (con código de país):",
        "message_label": "Mensaje:",
        "template_label": "Seleccione una plantilla:",
        "attachment_label": "Archivos adjuntos (opcional):",
        "time_label": "Hora programada (formato 24 horas):",
        "browser_label": "Seleccione Navegador/Aplicación:",
        "schedule_button": "Programar Mensaje",
        "view_scheduled_button": "Ver Mensajes Programados",
        "no_files_selected": "No se seleccionaron archivos",
        "success": "Éxito",
        "error": "Error",
        "invalid_phone": "Número de teléfono inválido. Por favor, incluya el código de país (ej. +91).",
        "empty_message": "El mensaje no puede estar vacío.",
        "invalid_time": "Hora inválida. Por favor, ingrese una hora futura.",
        "browser_not_found": "El navegador '{browser}' no está instalado. Por favor, instálelo o use el navegador predeterminado.",
        "scheduled_success": "¡Mensaje programado con éxito!",
        "sent_success": "¡Mensaje enviado con éxito!",
        "send_failed": "Error al enviar el mensaje. Por favor, intente nuevamente.",
    },
    "French": {
        "title": "Planificateur de Messages WhatsApp",
        "phone_label": "Numéro de téléphone du destinataire (avec l'indicatif du pays):",
        "message_label": "Message:",
        "template_label": "Sélectionnez un modèle:",
        "attachment_label": "Pièces jointes (optionnel):",
        "time_label": "Heure programmée (format 24 heures):",
        "browser_label": "Sélectionnez Navigateur/Application:",
        "schedule_button": "Planifier le Message",
        "view_scheduled_button": "Voir les Messages Planifiés",
        "no_files_selected": "Aucun fichier sélectionné",
        "success": "Succès",
        "error": "Erreur",
        "invalid_phone": "Numéro de téléphone invalide. Veuillez inclure l'indicatif du pays (ex. +91).",
        "empty_message": "Le message ne peut pas être vide.",
        "invalid_time": "Heure invalide. Veuillez entrer une heure future.",
        "browser_not_found": "Le navigateur '{browser}' n'est pas installé. Veuillez l'installer ou utiliser le navigateur par défaut.",
        "scheduled_success": "Message planifié avec succès!",
        "sent_success": "Message envoyé avec succès!",
        "send_failed": "Échec de l'envoi du message. Veuillez réessayer.",
    },
}

def validate_phone_number(phone):
    """Validate the phone number."""
    if not re.match(r"^\+[1-9]\d{1,14}$", phone):
        return False
    return True

def validate_time(hour, minute):
    """Validate the time input."""
    now = datetime.now()
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled_time < now:
        return False
    return True

def check_browser_installed(browser):
    """Check if the selected browser is installed."""
    if browser == "default":
        return True
    for path in BROWSER_PATHS.get(browser, []):
        if os.path.exists(path):
            return True
    return False

def register_browser(browser):
    """Register the browser with webbrowser."""
    for path in BROWSER_PATHS.get(browser, []):
        if os.path.exists(path):
            webbrowser.register(browser, None, webbrowser.BackgroundBrowser(path))
            return True
    return False

def send_whatsapp_message(phone, message, hour, minute, attachments=None, browser=None):
    """Send a WhatsApp message with optional attachments."""
    try:
        if browser and browser != "default":
            if not check_browser_installed(browser):
                raise Exception(f"Browser '{browser}' is not installed.")

            if not register_browser(browser):
                raise Exception(f"Failed to register browser '{browser}'.")

            # Open WhatsApp Web in the specified browser
            url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
            webbrowser.get(browser).open(url)
            time.sleep(20)  # Wait for WhatsApp Web to load

            # Send the message
            pyautogui.press("enter")

            # Attach files (if any)
            if attachments:
                for file in attachments:
                    # Locate the attachment button using image recognition
                    try:
                        attachment_button = pyautogui.locateOnScreen("attachment_button.png", confidence=0.8)
                        if attachment_button:
                            pyautogui.click(attachment_button)
                            time.sleep(1)
                            pyautogui.write(file)
                            pyautogui.press("enter")
                            time.sleep(2)  # Wait for the file to upload
                        else:
                            logging.error("Attachment button not found.")
                    except Exception as e:
                        logging.error(f"Error locating attachment button: {e}")
        else:
            # Use pywhatkit to send the message
            pyw.sendwhatmsg(phone, message, hour, minute)

        logging.info(f"Message sent to {phone} at {hour}:{minute}.")
        return True
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

class WhatsAppApp:
    def __init__(self, root):
        self.root = root
        self.language = "English"  # Default language
        self.root.title(LANGUAGES[self.language]["title"])
        self.root.geometry("600x700")
        self.style = Style(theme="superhero")

        # Variables
        self.phone_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.hour_var = tk.IntVar()
        self.minute_var = tk.IntVar()
        self.browser_var = tk.StringVar(value="default")
        self.template_var = tk.StringVar(value="Custom")
        self.attachments = []
        self.scheduled_messages = []
        self.active_threads = {}  # Track active threads using a dictionary

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create all UI components."""
        # Language Selection
        language_frame = ttk.Frame(self.root)
        language_frame.pack(pady=10)
        ttk.Label(language_frame, text="Select Language:").grid(row=0, column=0, padx=5)
        self.language_var = tk.StringVar(value=self.language)
        language_options = list(LANGUAGES.keys())
        ttk.Combobox(language_frame, textvariable=self.language_var, values=language_options, state="readonly", width=15).grid(row=0, column=1, padx=5)
        ttk.Button(language_frame, text="Apply", command=self.change_language).grid(row=0, column=2, padx=5)

        # Phone Number
        ttk.Label(self.root, text=LANGUAGES[self.language]["phone_label"]).pack(pady=5)
        ttk.Entry(self.root, textvariable=self.phone_var, width=30).pack(pady=5)

        # Message
        ttk.Label(self.root, text=LANGUAGES[self.language]["message_label"]).pack(pady=5)
        self.message_entry = ttk.Entry(self.root, textvariable=self.message_var, width=30)
        self.message_entry.pack(pady=5)

        # Message Templates
        ttk.Label(self.root, text=LANGUAGES[self.language]["template_label"]).pack(pady=5)
        templates = ["Custom", "Happy Birthday!", "Reminder: Meeting at 3 PM", "Good Morning!"]
        ttk.Combobox(self.root, textvariable=self.template_var, values=templates, state="readonly").pack(pady=5)
        self.template_var.trace("w", self.update_message)

        # Attachments
        ttk.Label(self.root, text=LANGUAGES[self.language]["attachment_label"]).pack(pady=5)
        ttk.Button(self.root, text="Add Files", command=self.add_files).pack(pady=5)
        self.attachment_label = ttk.Label(self.root, text=LANGUAGES[self.language]["no_files_selected"], foreground="gray")
        self.attachment_label.pack(pady=5)

        # Time
        ttk.Label(self.root, text=LANGUAGES[self.language]["time_label"]).pack(pady=5)
        time_frame = ttk.Frame(self.root)
        time_frame.pack(pady=5)
        ttk.Entry(time_frame, textvariable=self.hour_var, width=5).grid(row=0, column=0, padx=5)
        ttk.Label(time_frame, text=":").grid(row=0, column=1)
        ttk.Entry(time_frame, textvariable=self.minute_var, width=5).grid(row=0, column=2, padx=5)

        # Browser Selection
        ttk.Label(self.root, text=LANGUAGES[self.language]["browser_label"]).pack(pady=5)
        browsers = ["default", "chrome", "edge", "firefox"]
        ttk.Combobox(self.root, textvariable=self.browser_var, values=browsers, state="readonly").pack(pady=5)

        # Send Button
        ttk.Button(self.root, text=LANGUAGES[self.language]["schedule_button"], command=self.schedule_message).pack(pady=20)

        # Scheduled Messages Button
        ttk.Button(self.root, text=LANGUAGES[self.language]["view_scheduled_button"], command=self.view_scheduled_messages).pack(pady=10)

    def change_language(self):
        """Change the language of the GUI."""
        self.language = self.language_var.get()
        self.root.title(LANGUAGES[self.language]["title"])
        self.create_widgets()

    def update_message(self, *args):
        """Update the message based on the selected template."""
        template = self.template_var.get()
        if template != "Custom":
            self.message_var.set(template)

    def add_files(self):
        """Add multiple files as attachments."""
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("All Files", "*.*"), ("Images", "*.jpg;*.png"), ("Videos", "*.mp4"), ("Documents", "*.pdf")]
        )
        if files:
            self.attachments = list(files)
            self.attachment_label.config(text=f"{len(files)} file(s) selected", foreground="black")

    def schedule_message(self):
        """Schedule the WhatsApp message."""
        phone = self.phone_var.get()
        message = self.message_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        browser = self.browser_var.get()

        # Validate inputs
        if not validate_phone_number(phone):
            messagebox.showerror(LANGUAGES[self.language]["error"], LANGUAGES[self.language]["invalid_phone"])
            return
        if not message:
            messagebox.showerror(LANGUAGES[self.language]["error"], LANGUAGES[self.language]["empty_message"])
            return
        if not validate_time(hour, minute):
            messagebox.showerror(LANGUAGES[self.language]["error"], LANGUAGES[self.language]["invalid_time"])
            return

        # Check if the selected browser is available
        if browser != "default" and not check_browser_installed(browser):
            messagebox.showerror(LANGUAGES[self.language]["error"], LANGUAGES[self.language]["browser_not_found"].format(browser=browser))
            return

        # Add the message to the scheduled messages list
        message_id = f"{phone}_{hour}:{minute}"
        self.scheduled_messages.append({
            "id": message_id,
            "phone": phone,
            "message": message,
            "time": f"{hour}:{minute}",
            "attachments": self.attachments,
        })

        # Clear input fields
        self.phone_var.set("")
        self.message_var.set("")
        self.hour_var.set(0)
        self.minute_var.set(0)
        self.attachments = []
        self.attachment_label.config(text=LANGUAGES[self.language]["no_files_selected"], foreground="gray")

        # Schedule the message
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.send_message_later,
            args=(message_id, phone, message, hour, minute, self.attachments, browser, stop_event),
            daemon=True
        )
        self.active_threads[message_id] = (thread, stop_event)
        thread.start()

        messagebox.showinfo(LANGUAGES[self.language]["success"], LANGUAGES[self.language]["scheduled_success"])

    def send_message_later(self, message_id, phone, message, hour, minute, attachments, browser, stop_event):
        """Send the message at the scheduled time."""
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        delay = (scheduled_time - now).total_seconds()

        if delay > 0:
            time.sleep(delay)  # Wait until the scheduled time

        if not stop_event.is_set():
            success = send_whatsapp_message(phone, message, hour, minute, attachments, browser)
            if success:
                messagebox.showinfo(LANGUAGES[self.language]["success"], LANGUAGES[self.language]["sent_success"])
            else:
                messagebox.showerror(LANGUAGES[self.language]["error"], LANGUAGES[self.language]["send_failed"])

        # Remove the thread from active threads
        if message_id in self.active_threads:
            del self.active_threads[message_id]

    def view_scheduled_messages(self):
        """Display all scheduled messages in a new window."""
        scheduled_window = tk.Toplevel(self.root)
        scheduled_window.title("Scheduled Messages")
        scheduled_window.geometry("600x400")

        # Display scheduled messages
        for i, msg in enumerate(self.scheduled_messages):
            msg_frame = ttk.Frame(scheduled_window)
            msg_frame.pack(pady=5, fill=tk.X, padx=10)

            ttk.Label(msg_frame, text=f"To: {msg['phone']}, Time: {msg['time']}, Message: {msg['message']}").pack(side=tk.LEFT)
            ttk.Button(msg_frame, text="Edit", command=lambda i=i: self.edit_scheduled_message(i)).pack(side=tk.RIGHT, padx=5)
            ttk.Button(msg_frame, text="Delete", command=lambda i=i: self.delete_scheduled_message(i)).pack(side=tk.RIGHT)

    def edit_scheduled_message(self, index):
        """Edit a scheduled message."""
        if not self.scheduled_messages:
            messagebox.showerror(LANGUAGES[self.language]["error"], "No scheduled messages to edit.")
            return

        # Access the message before removing it
        msg = self.scheduled_messages[index]

        # Stop the thread for the old message
        if msg["id"] in self.active_threads:
            thread, stop_event = self.active_threads[msg["id"]]
            stop_event.set()
            del self.active_threads[msg["id"]]

        # Remove the old scheduled message
        self.scheduled_messages.pop(index)

        # Populate the input fields with the selected message
        self.phone_var.set(msg["phone"])
        self.message_var.set(msg["message"])
        self.hour_var.set(int(msg["time"].split(":")[0]))
        self.minute_var.set(int(msg["time"].split(":")[1]))
        self.attachments = msg["attachments"]
        self.attachment_label.config(text=f"{len(msg['attachments'])} file(s) selected", foreground="black")

    def delete_scheduled_message(self, index):
        """Delete a scheduled message."""
        if not self.scheduled_messages:
            messagebox.showerror(LANGUAGES[self.language]["error"], "No scheduled messages to delete.")
            return

        # Stop the thread for the deleted message
        msg = self.scheduled_messages[index]
        if msg["id"] in self.active_threads:
            thread, stop_event = self.active_threads[msg["id"]]
            stop_event.set()
            del self.active_threads[msg["id"]]

        # Remove the message from the list
        self.scheduled_messages.pop(index)
        messagebox.showinfo(LANGUAGES[self.language]["success"], "Scheduled message deleted.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppApp(root)
    root.mainloop()