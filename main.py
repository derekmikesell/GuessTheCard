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

        

        

        self.image_type_var = tk.StringVar(self.root)
        self.image_type_var.set("Full") # default value
        image_type_options = ["Cropped", "Full"]
        self.image_type_menu = tk.OptionMenu(self.root, self.image_type_var, *image_type_options, command=self.change_image_type)
        self.image_type_menu.pack(pady=5)

        self.next_card_button = tk.Button(self.root, text="Next Card", command=self.reset_game)
        self.next_card_button.pack(pady=5)

        
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
            self.display_image(self.original_card_image)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch card data: {e}")
            self.root.quit()

    def display_image(self, image):
        photo = ImageTk.PhotoImage(image)
        self.card_image_label.config(image=photo)
        self.card_image_label.image = photo

    

    

    def reset_game(self):
        self.fetch_random_card()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuessTheCardApp(root)
    root.mainloop()