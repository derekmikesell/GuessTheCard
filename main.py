import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import random

class GuessTheCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guess That Card!")

        self.card_image_label = tk.Label(self.root)
        self.card_image_label.pack(pady=10)

        

        

        

        self.next_card_button = tk.Button(self.root, text="Next Card", command=self.reset_game)
        self.card_name_label = tk.Label(self.root, text="")
        self.card_name_label.pack(pady=5)

        self.next_card_button = tk.Button(self.root, text="Next Card", command=self.reset_game)
        self.next_card_button.pack(pady=5)

        self.card_name_label = tk.Label(self.root, text="")
        self.card_name_label.pack(pady=5)

        self.image_type_var = tk.StringVar(self.root)
        self.image_type_var.set("Full") # default value
        image_type_options = ["Cropped", "Full"]
        self.image_type_menu = tk.OptionMenu(self.root, self.image_type_var, *image_type_options, command=self.change_image_type)
        self.image_type_menu.pack(pady=5)

        self.revealed_squares = set()
        self.reveal_job = None

        
        self.fetch_random_card()

    def fetch_random_card(self):
        try:
            api_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
            response = requests.get(api_url)
            response.raise_for_status()
            card_data = response.json()["data"]
            random_card = random.choice(card_data)
            self.card_name = random_card['name']
            
            if self.image_type_var.get() == "Cropped":
                image_url = random_card['card_images'][0]['image_url_cropped']
            else:
                image_url = random_card['card_images'][0]['image_url'] # Full image URL

            image_response = requests.get(image_url)
            image_response.raise_for_status()
            self.original_card_image = Image.open(io.BytesIO(image_response.content))
            self.blacked_out_image = Image.new("RGB", self.original_card_image.size)
            self.display_image(self.blacked_out_image)
            self.start_reveal()

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch card data: {e}")
            self.root.quit()

    def display_image(self, image):
        photo = ImageTk.PhotoImage(image)
        self.card_image_label.config(image=photo)
        self.card_image_label.image = photo

    def start_reveal(self):
        self.reveal_image()

    def reveal_image(self):
        square_size = 60 # Increased square size
        width, height = self.original_card_image.size
        
        cols = width // square_size
        rows = height // square_size
        
        all_squares = [(r, c) for r in range(rows) for c in range(cols)]
        unrevealed_squares = [s for s in all_squares if s not in self.revealed_squares]

        if not unrevealed_squares:
            self.stop_reveal()
            return

        row, col = random.choice(unrevealed_squares)
        self.revealed_squares.add((row, col))

        x1 = col * square_size
        y1 = row * square_size
        x2 = x1 + square_size
        y2 = y1 + square_size

        region = self.original_card_image.crop((x1, y1, x2, y2))
        self.blacked_out_image.paste(region, (x1, y1))
        self.display_image(self.blacked_out_image)

        self.reveal_job = self.root.after(100, self.reveal_image)

    def stop_reveal(self):
        if self.reveal_job:
            self.root.after_cancel(self.reveal_job)
            self.reveal_job = None
        self.card_name_label.config(text=self.card_name)
        self.card_name_label.config(text=self.card_name)

    

    

    def reset_game(self):
        self.stop_reveal()
        self.revealed_squares.clear()
        self.card_name_label.config(text="") # Clear the card name
        self.fetch_random_card()

    def change_image_type(self, selected_type):
        self.reset_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuessTheCardApp(root)
    root.mainloop()