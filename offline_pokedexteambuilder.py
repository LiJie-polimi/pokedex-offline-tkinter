import tkinter as tk
from tkinter import messagebox
import csv
import base64
from PIL import Image, ImageTk
import io

#############################################
# 1. GIF ANIMATION FUNCTIONS
#############################################

def load_gif_frames(gif_path):
    pil_image = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(pil_image.copy()))
            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        pass
    return frames

def animate_gif_once(label, frames, total_duration=7000):
    total_frames = len(frames)
    if total_frames == 0:
        return
    delay = total_duration // total_frames

    def update_frame(index=0):
        label.config(image=frames[index])
        label.image = frames[index]
        if index < total_frames - 1:
            label.after(delay, update_frame, index + 1)

    update_frame(0)

#############################################
# 2. DATA LOADING & SEARCH FUNCTIONS
#############################################

def load_pokemon_data(filename="all_pokemon_data.csv"):
    pokemon_data = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pokemon_data.append(row)
        print(f"Loaded {len(pokemon_data)} Pokémon from '{filename}'.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{filename}' not found.")
    return pokemon_data

def find_pokemon(pokemon_list, search_term):
    st_lower = search_term.lower()
    for p in pokemon_list:
        if p['name'].lower() == st_lower or p['id'] == search_term:
            return p
    return None

#############################################
# 3. MAIN APPLICATION CLASS
#############################################

class PokedexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex")
        self.mode = "opening"
        self.data = load_pokemon_data("all_pokemon_data.csv")
        self.team = []

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.opening_frames = load_gif_frames("pokedex_opening_gif.gif")
        self.bg_width = self.opening_frames[0].width()
        self.bg_height = self.opening_frames[0].height()
        self.canvas.config(width=self.bg_width, height=self.bg_height)

        self.animation_label = tk.Label(root, bd=0)
        self.canvas.create_window(self.bg_width // 2, self.bg_height // 2, window=self.animation_label)
        animate_gif_once(self.animation_label, self.opening_frames, total_duration=7000)

        self.root.after(7000, self.show_search_bar)

    def show_search_bar(self):
        self.mode = "search"
        self.canvas.delete("all")
        self.search_entry = tk.Entry(self.root, width=20, font=("Arial", 12))
        self.search_button = tk.Button(self.root, text="Search", font=("Arial", 12), command=self.perform_search)
        self.canvas.create_window(self.bg_width // 2, self.bg_height // 2, window=self.search_entry)
        self.canvas.create_window(self.bg_width // 2, (self.bg_height // 2) + 40, window=self.search_button)

    def perform_search(self):
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
        self.mode = "pokedex"
        self.canvas.delete("all")

        self.layout_image = Image.open("pokedex_layout.png")
        self.bg_width, self.bg_height = self.layout_image.size
        self.layout_photo = ImageTk.PhotoImage(self.layout_image)
        self.canvas.config(width=self.bg_width, height=self.bg_height)
        self.canvas.create_image(0, 0, image=self.layout_photo, anchor="nw")

        self.info_label = tk.Label(self.root, bg="#30fa04", fg="black", font=("Consolas", 8),
                                   justify="left", bd=3, relief="flat", highlightthickness=3, highlightbackground="#4a0707")
        self.info_label.config(wraplength=235)
        self.canvas.create_window(473, 180, anchor="center", window=self.info_label)

        self.display_pokemon(pokemon)

        self.add_team_button = tk.Button(self.root, text="Add to Team", font=("Arial", 10), command=self.add_to_team)
        self.canvas.create_window(self.bg_width // 2, self.bg_height - 100, window=self.add_team_button)

        self.go_back_button = tk.Button(self.root, text="Go Back to Search", font=("Arial", 10), command=self.show_search_bar)
        self.canvas.create_window(self.bg_width // 2, self.bg_height - 60, window=self.go_back_button)

        self.team_label = tk.Label(self.root, text="Team:", font=("Arial", 10), justify="left")
        self.canvas.create_window(self.bg_width // 2, self.bg_height - 30, window=self.team_label)

    def display_pokemon(self, pokemon):
        stats_str = pokemon['stats'].replace("special-attack", "SA").replace("special-defense", "SD")
        info_text = (
            f"Name: {pokemon['name']}  ID: {pokemon['id']}\n"
            f"Types: {pokemon['types']}\n"
            f"Stats: {stats_str}\n"
            f"Abilities: {pokemon['abilities']}"
        )
        self.info_label.config(text=info_text)
        self.current_pokemon = pokemon

    def add_to_team(self):
        if hasattr(self, 'current_pokemon') and self.current_pokemon:
            if len(self.team) < 6:
                self.team.append(self.current_pokemon)
                self.update_team_display()
            else:
                messagebox.showwarning("Team Full", "You can only have 6 Pokémon in a team!")

    def update_team_display(self):
        team_text = "Team:\n"
        for p in self.team:
            stats_str = p['stats'].replace("special-attack", "SA").replace("special-defense", "SD")
            team_text += f"{p['name']} (ID: {p['id']})\nTypes: {p['types']}\nStats: {stats_str}\n\n"
        self.team_label.config(text=team_text)

#############################################
# 4. RUN THE APPLICATION
#############################################

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.mainloop()
