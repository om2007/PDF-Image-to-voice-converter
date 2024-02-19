import tkinter as tk
from tkinter import messagebox
import easygui
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import pygame
from gtts import gTTS

pygame.mixer.init()

def get_string(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    result = pytesseract.image_to_string(Image.fromarray(img))
    return result

def get_text_from_pdf(pdf_path):
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.title("Image to Speech Converter")
        
        self.main_frame = MainFrame(self, self.show_privacy_policy, self.process_image)
        self.privacy_policy_frame = PrivacyPolicyFrame(self, self.back_to_main)

        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.privacy_policy_frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_main()

        self.bind_all("<Control-u>", self.upload_image)

    def upload_image(self, event=None):
        self.main_frame.on_circle_click()

    def show_privacy_policy(self):
        self.privacy_policy_frame.lift()

    def back_to_main(self):
        self.main_frame.lift()

    def show_main(self):
        self.main_frame.lift()

    def process_image(self, img_path):
        if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            text = get_string(img_path)
        elif img_path.lower().endswith('.pdf'):
            text = get_text_from_pdf(img_path)
        else:
            messagebox.showerror("Unsupported File", "The selected file type is not supported.")
            return
        
        if text.strip():
            speech = gTTS(text=text, lang='en', slow=False)
            audio_file_path = os.path.splitext(img_path)[0] + "_audio.mp3"
            speech.save(audio_file_path)
            messagebox.showinfo("Conversion Successful", f"Audio saved to: {audio_file_path}")
        else:
            messagebox.showinfo("No Text Found", "Could not find text in the document.")

class MainFrame(tk.Frame):
    def __init__(self, master, show_privacy_callback, process_image_callback):
        privacy_audio = 'Privacy Policy.mp3'
        privacy_file_path = os.path.join(os.path.dirname(__file__), privacy_audio)
        image_audio = 'Upload image.mp3'
        image_file_path = os.path.join(os.path.dirname(__file__), image_audio)
        click_audio = 'Click.mp3'
        click_file_path = os.path.join(os.path.dirname(__file__), click_audio)
        super().__init__(master, bg='SystemButtonFace')
        self.process_image_callback = process_image_callback
        
        title = tk.Label(self, text="Image to Speech Converter", font=("Arial", 36), bg='SystemButtonFace', fg='black')
        title.pack(pady=10)

        self.canvas = tk.Canvas(self, width=300, height=300, bg='SystemButtonFace', highlightthickness=0)
        self.canvas.create_oval(50, 50, 250, 250, fill="blue", outline="blue")
        self.canvas.pack(pady=20)
        self.canvas.bind("<Enter>", lambda event: self.play_audio(image_file_path))
        self.canvas.bind("<Button-1>", lambda event: [self.on_circle_click(event), self.play_audio(click_file_path)])

        privacy_button = tk.Label(self, text="Privacy Policy", bg='SystemButtonFace', fg='blue', cursor="hand2", font=("Arial", 24))
        privacy_button.pack(pady=20)
        privacy_button.bind("<Button-1>", lambda event: [show_privacy_callback(), self.play_audio(click_file_path)])
        privacy_button.bind("<Enter>", lambda event: self.play_audio(privacy_file_path))

    def on_circle_click(self, event=None):
        file_path = easygui.fileopenbox(title="Select Image or PDF", filetypes=[["*.*", "All files"]])
        if file_path:
            self.process_image_callback(file_path)

    def play_audio(self, audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

class PrivacyPolicyFrame(tk.Frame):
    def __init__(self, master, back_callback):
        back_audio = 'Back Button.mp3'
        back_file_path = os.path.join(os.path.dirname(__file__), back_audio)
        click_audio = 'Click.mp3'
        click_file_path = os.path.join(os.path.dirname(__file__), click_audio)
        super().__init__(master)
        
        title = tk.Label(self, text="Image to Speech Converter", font=("Arial", 36))
        title.pack(pady=10)

        policy_text = tk.Label(self, text="My desktop app prioritizes your privacy above all else. I don't collect, store, or share any personal data or images you upload for conversion. Everything is processed locally on your device, ensuring that your information stays private and secure. If you have any questions about my privacy practices, please feel free to reach out to me at omkakkad2007@gmail.com.", font=("Arial", 24), wraplength=self.winfo_screenwidth() - 100, justify="center")
        policy_text.pack(pady=20)

        self.back_button = tk.Button(self, text="Back", font=("Arial", 24), command=back_callback)
        self.back_button.pack(pady=20)
        self.back_button.bind("<Enter>", lambda event: self.play_audio(back_file_path))
        self.back_button.bind("<Button-1>", lambda event: self.play_audio(click_file_path))

    def play_audio(self, audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

if __name__ == "__main__":
    app = App()
    app.geometry("500x500")
    app.mainloop()