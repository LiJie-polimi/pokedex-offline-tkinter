import tkinter as tk
from tkinter import messagebox
import csv
import base64
from PIL import Image, ImageTk
import io

#############################################
# 1. GIF ANIMATION FUNCTIONS
#############################################

# This function loads all frames from an animated GIF.
# I loop through the frames until an EOFError occurs (which means there are no more frames).
def load_gif_frames(gif_path):
    # Open the GIF file using PIL (Python Imaging Library)
    pil_image = Image.open(gif_path)
    frames = []  # This list will store all our frames as PhotoImage objects
    try:
        while True:
            # Append a copy of the current frame converted to a PhotoImage (for Tkinter)
            frames.append(ImageTk.PhotoImage(pil_image.copy()))
            # Move to the next frame
            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        # We hit the end of the GIF
        pass
    return frames

# This function animates the GIF frames once over a total duration.
# It will leave the last frame on the screen.
def animate_gif_once(label, frames, total_duration=7000):
    total_frames = len(frames)
    if total_frames == 0:
        return  # Nothing to animate if there are no frames
    # Calculate how long each frame should show
    delay = total_duration // total_frames
    # Define a nested function to update frames one by one
    def update_frame(index=0):
        label.config(image=frames[index])
        label.image = frames[index]  # Keep a reference so it doesn't get garbage-collected
        if index < total_frames - 1:
            # Schedule the next frame update
            label.after(delay, update_frame, index + 1)
    update_frame(0)  # Start with the first frame

#############################################
# 2. DATA LOADING & SEARCH FUNCTIONS
#############################################

# This function loads Pokémon data from a CSV file.
# The CSV file is expected to have columns: name, id, types, stats, abilities, image_base64.
def load_pokemon_data(filename="all_pokemon_data.csv"):
    pokemon_data = []  # This list will hold all the dictionaries of Pokémon data
    try:
        # Open the CSV file for reading
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)  # Use DictReader so each row is a dictionary
            for row in reader:
                pokemon_data.append(row)
        print(f"Loaded {len(pokemon_data)} Pokémon from '{filename}'.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{filename}' not found.")
    return pokemon_data

# This function searches through the list of Pokémon dictionaries for a given search term.
def find_pokemon(pokemon_list, search_term):
    st_lower = search_term.lower()  # Convert search term to lower case for case-insensitive matching
    for p in pokemon_list:
        # Check if the name or id matches the search term
        if p['name'].lower() == st_lower or p['id'] == search_term:
            return p
    return None

#############################################
# 3. MAIN APPLICATION CLASS
#############################################

# This is the main class for our Pokédex application.
# It handles the opening animation, search bar, and final UI.
class PokedexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex")
        self.mode = "opening"  # We start in opening mode

        # Load all Pokémon data from the CSV file
        self.data = load_pokemon_data("all_pokemon_data.csv")
        
        # Create a canvas for our GUI. This canvas will hold everything.
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # --- Opening Animation ---
        # Load our GIF frames from the file
        self.opening_frames = load_gif_frames("pokedex_opening_gif.gif")
        # Use the dimensions of the first frame as our canvas size
        self.bg_width = self.opening_frames[0].width()
        self.bg_height = self.opening_frames[0].height()
        self.canvas.config(width=self.bg_width, height=self.bg_height)
        
        # Create a label that will show our animated GIF
        self.animation_label = tk.Label(root, bd=0)
        # Place it in the center of the canvas
        self.canvas.create_window(self.bg_width // 2, self.bg_height // 2, window=self.animation_label)
        # Animate the GIF (playing only once)
        animate_gif_once(self.animation_label, self.opening_frames, total_duration=7000)
        
        # After 7 seconds (when the GIF is done), show the search bar
        self.root.after(7000, self.show_search_bar)
        
    def show_search_bar(self):
        """
        This method overlays a centered search bar (Entry widget and Button)
        on top of the final frame of the opening GIF.
        """
        self.mode = "search"
        # Create the search entry widget
        self.search_entry = tk.Entry(self.root, width=20, font=("Arial", 12))
        # Create the search button
        self.search_button = tk.Button(self.root, text="Search", font=("Arial", 12), command=self.perform_search)
        # Place them in the center of the canvas
        self.canvas.create_window(self.bg_width // 2, self.bg_height // 2, window=self.search_entry)
        self.canvas.create_window(self.bg_width // 2, (self.bg_height // 2) + 40, window=self.search_button)
        
    def perform_search(self):
        """
        This method is called when the search button is pressed.
        It gets the text from the search entry, finds the Pokémon, and moves to the full UI.
        """
        term = self.search_entry.get().strip()
        if not term:
            messagebox.showinfo("Input Needed", "Please enter a Pokémon name or ID.")
            return
        pokemon = find_pokemon(self.data, term)
        if not pokemon:
            messagebox.showerror("Not Found", "No Pokémon found with that name or ID.")
            return
        self.show_pokedex_ui(pokemon)
        
    def show_pokedex_ui(self, pokemon):
        """
        This method transitions the application to the full Pokédex UI.
        It loads the background layout image, positions the Pokémon sprite and info text.
        """
        self.mode = "pokedex"
        self.canvas.delete("all")  # Remove all previous items from the canvas
        
        # Load the layout background image (we expect it to be 620x449)
        self.layout_image = Image.open("pokedex_layout.png")
        self.bg_width, self.bg_height = self.layout_image.size
        self.layout_photo = ImageTk.PhotoImage(self.layout_image)
        self.canvas.config(width=self.bg_width, height=self.bg_height)
        # Draw the background image on the canvas
        self.canvas.create_image(0, 0, image=self.layout_photo, anchor="nw")
        
        # ---- Sprite Placement (Left Half) ----
        # We want the sprite to appear in the left half of the image.
        # The left half center horizontally is at 620/4 = 155, and vertically centered at 449/2 ≈ 224.
        # Then we move it up by 30 pixels.
        sprite_center_x = 155
        sprite_center_y = (449 // 2) - 30
        self.sprite_size = 125  # Increase the sprite size by 5 pixels (from 120 to 125)
        # Create a label for the sprite, with a background color of #fbfbfb
        self.pokemon_image_label = tk.Label(self.root, bd=0, bg="#fbfbfb")
        self.canvas.create_window(int(sprite_center_x), int(sprite_center_y), anchor="center", window=self.pokemon_image_label)
        
        # ---- Text Placement (Right Half) ----
        # We want the info text to be inside a box defined by these coordinates:
        # Left boundary: 376 pixels, Right boundary: 570 (which is 620 - 50),
        # Top boundary: 136 pixels, Bottom boundary: 224 pixels.
        # The center of this box is at ((376+570)/2, (136+224)/2) = (473, 180).
        # Then we want to move the text box down by 2 pixels, so the new center is (473, 182).
        # The text box width (wraplength) is 570 - 376 + 20 = 214 + 10 = 235 pixels.
        text_center_x = (376 + 570) // 2  # 473
        text_center_y = (136 + 224) // 2 + 2   # 180 + 2 = 182
        text_wrap = 570 - 376 + 20  # 570 - 376 = 194, plus 20 = 214; however, the requirement said 235 before, so we use 235
        text_wrap = 235  # final wraplength: 235 pixels wide
        # Create the info label. We change the background to #30fa04, text color to black,
        # use Consolas font at size 8, and add a border of color #4a0707. To simulate borders, we can
        # use the "highlightbackground" property.
        self.info_label = tk.Label(
            self.root,
            bg="#30fa04",
            fg="black",
            font=("Consolas", 8),
            justify="left",
            bd=3,
            relief="flat",
            highlightthickness=3,
            highlightbackground="#4a0707"
        )
        self.info_label.config(wraplength=text_wrap)
        self.canvas.create_window(int(text_center_x), int(text_center_y), anchor="center", window=self.info_label)
        
        # Now display the Pokémon data in the text box.
        self.display_pokemon(pokemon)
        
    def display_pokemon(self, pokemon):
        """
        Loads and displays the Pokémon sprite and information.
        """
        # 1) Display the sprite image
        image_b64 = pokemon.get('image_base64', '')
        if image_b64:
            try:
                image_data = base64.b64decode(image_b64)
                pil_img = Image.open(io.BytesIO(image_data))
                # Resize the sprite to our specified size (125x125)
                pil_img = pil_img.resize((self.sprite_size, self.sprite_size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_img)
                self.pokemon_image_label.config(image=photo)
                self.pokemon_image_label.image = photo  # keep a reference
            except Exception as e:
                messagebox.showerror("Image Error", f"Could not load image: {e}")
        else:
            self.pokemon_image_label.config(image='')
            self.pokemon_image_label.image = None

        # 2) Prepare and display the Pokémon info text.
        # Write the ID next to the name, and replace "special-attack" with "SA" and "special-defense" with "SD".
        stats_str = pokemon['stats'].replace("special-attack", "SA").replace("special-defense", "SD")
        # Now, write the name and ID on the same line.
        info_text = (
            f"Name: {pokemon['name']}  ID: {pokemon['id']}\n"
            f"Types: {pokemon['types']}\n"
            f"Stats: {stats_str}\n"
            f"Abilities: {pokemon['abilities']}"
        )
        self.info_label.config(text=info_text)

#############################################
# 4. RUN THE APPLICATION
#############################################
if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.bind('<Return>', lambda event: app.perform_search() if hasattr(app, 'perform_search') else None)
    root.mainloop()
