import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import random



class FilipinoMealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The Filipino Meal Finder")
        self.root.geometry("1200x900")
        self.root.configure(bg="#F5E9DA")  # Light pastel background

        # Dictionaries to store meals and images
        self.meals = {}           # {meal_name: meal_id}
        self.meal_images = {}     # {meal_name: PhotoImage}
        self.meal_labels = {}     # Sidebar labels
        self.selected_photo = None
        self.current_highlight = None
        self.all_meal_photos = [] # Keep reference for grid gallery

        # Create GUI components
        self.create_widgets()
        # Load meals from TheMealDB API
        self.load_filipino_meals()

    # -------------------------------
    # Create all GUI components
    # -------------------------------
    def create_widgets(self):
        # Header with personal greeting
        header_frame = tk.Frame(self.root, bg="#EED6C4", bd=2, relief="raised")
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="Filipino Meal Finder 🇵🇭\nMade by: Lavhinia Joice Basilio",
            font=("Satoshi", 22, "bold"),
            bg="#EED6C4",
            fg="#6B4F3F",
            justify="center"
        ).pack(pady=10)

        # Main frame for sidebar + content
        main_frame = tk.Frame(self.root, bg="#F5E9DA")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar for meal thumbnails
        self.sidebar_frame = tk.Frame(main_frame, bg="#F5E0C3", bd=2, relief="sunken", width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas = tk.Canvas(self.sidebar_frame, bg="#F5E0C3", width=230)
        self.scrollbar = tk.Scrollbar(self.sidebar_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_sidebar = tk.Frame(self.canvas, bg="#F5E0C3")

        self.scrollable_sidebar.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_sidebar, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Content frame
        content_frame = tk.Frame(main_frame, bg="#F5E9DA")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Selection frame
        select_frame = tk.Frame(content_frame, bg="#F5E0C3", bd=2, relief="groove")
        select_frame.pack(pady=10, fill=tk.X)

        tk.Label(
            select_frame,
            text="Select a Filipino Meal:",
            font=("Arial", 14, "bold"),
            bg="#F5E0C3",
            fg="#5C4033"
        ).pack(pady=5)

        self.selected_meal = tk.StringVar()
        self.dropdown = tk.OptionMenu(select_frame, self.selected_meal, "")
        self.dropdown.config(width=40, font=("Arial", 12), bg="#FBE8D3", fg="#5C4033")
        self.dropdown.pack(pady=5)

        # Buttons: View, Random, Show All
        button_frame = tk.Frame(select_frame, bg="#F5E0C3")
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="View Meal", font=("Arial", 12, "bold"),
                  width=15, bg="#EED6C4", fg="#6B4F3F",
                  command=self.display_meal).grid(row=0, column=0, padx=5)

        tk.Button(button_frame, text="Random Meal", font=("Arial", 12, "bold"),
                  width=15, bg="#EED6C4", fg="#6B4F3F",
                  command=self.random_meal).grid(row=0, column=1, padx=5)

        tk.Button(button_frame, text="Show All Meals", font=("Arial", 12, "bold"),
                  width=15, bg="#EED6C4", fg="#6B4F3F",
                  command=self.show_all_meals).grid(row=0, column=2, padx=5)

        # Image frame for selected meal
        self.image_frame = tk.Frame(content_frame, bg="#F5E9DA", bd=2, relief="sunken")
        self.image_frame.pack(pady=10, fill=tk.BOTH, expand=False)
        self.image_label = tk.Label(self.image_frame, bg="#F5E9DA")
        self.image_label.pack(pady=10)

        # Result frame for ingredients and instructions
        self.result_frame = tk.Frame(content_frame, bg="#F5E9DA", bd=2, relief="sunken")
        self.result_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(
            self.result_frame,
            wrap=tk.WORD,
            font=("Arial", 14),
            bg="#FDF1E4",
            fg="#5C4033"
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # -------------------------------
    # Load meals from TheMealDB API
    # -------------------------------
    def load_filipino_meals(self):
        url = "https://www.themealdb.com/api/json/v1/1/filter.php?a=Filipino"
        response = requests.get(url)
        data = response.json()

        if data["meals"] is None:
            messagebox.showerror("Error", "No Filipino meals found.")
            return

        # Clear dropdown menu
        menu = self.dropdown["menu"]
        menu.delete(0, "end")

        for meal in data["meals"]:
            meal_name = meal["strMeal"]
            meal_id = meal["idMeal"]
            self.meals[meal_name] = meal_id

            # Add to dropdown
            menu.add_command(
                label=meal_name,
                command=lambda value=meal_name: self.selected_meal.set(value)
            )

            # Load thumbnail
            image_url = meal["strMealThumb"]
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))
            img = img.resize((80, 80))  # Slightly smaller for sidebar
            photo = ImageTk.PhotoImage(img)
            self.meal_images[meal_name] = photo

            # Sidebar label
            lbl = tk.Label(self.scrollable_sidebar, image=photo, text=meal_name,
                           compound="top", bg="#F5E0C3", fg="#5C4033", cursor="hand2")
            lbl.pack(pady=5)
            lbl.bind("<Button-1>", lambda e, name=meal_name: self.select_meal(name))
            self.meal_labels[meal_name] = lbl

        self.selected_meal.set("Select a Filipino meal")

    # -------------------------------
    # Select and display meal
    # -------------------------------
    def select_meal(self, meal_name):
        self.selected_meal.set(meal_name)
        self.display_meal()

    def display_meal(self):
        meal_name = self.selected_meal.get()
        if meal_name not in self.meals:
            messagebox.showwarning("Selection Error", "Please select a meal.")
            return

        meal_id = self.meals[meal_name]
        url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
        response = requests.get(url)
        meal = response.json()["meals"][0]

        self.show_meal_details(meal)
        self.highlight_sidebar(meal_name)

    # -------------------------------
    # Show meal details in text + image
    # -------------------------------
    def show_meal_details(self, meal):
        self.result_text.delete("1.0", tk.END)

        ingredients = ""
        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients += f"- {ingredient} ({measure})\n"

        details = (
            f"Meal Name: {meal['strMeal']}\n"
            f"Category: {meal['strCategory']}\n"
            f"Area: {meal['strArea']}\n\n"
            f"Ingredients:\n{ingredients}\n"
            f"Instructions:\n{meal['strInstructions']}"
        )
        self.result_text.insert(tk.END, details)

        # Main meal image
        image_url = meal["strMealThumb"]
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        img = img.resize((250, 250))  # Slightly smaller for student-friendly display
        photo = ImageTk.PhotoImage(img)
        self.selected_photo = photo
        self.image_label.config(image=photo)

    # -------------------------------
    # Highlight selected meal in sidebar
    # -------------------------------
    def highlight_sidebar(self, meal_name):
        if self.current_highlight:
            self.meal_labels[self.current_highlight].config(bg="#F5E0C3")
        self.meal_labels[meal_name].config(bg="#FFDAB9")  # Highlight color
        self.current_highlight = meal_name

        widget = self.meal_labels[meal_name]
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(widget.winfo_y() / self.scrollable_sidebar.winfo_height())

    # -------------------------------
    # Random meal
    # -------------------------------
    def random_meal(self):
        meal_name = random.choice(list(self.meals.keys()))
        self.selected_meal.set(meal_name)
        self.display_meal()

    # -------------------------------
    # Show all meals in grid gallery
    # -------------------------------
    def show_all_meals(self):
        # Clear previous content
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.result_frame, bg="#F5E9DA")
        scrollbar = tk.Scrollbar(self.result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5E9DA")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Grid layout: 3 columns
        cols = 3
        row = 0
        col = 0
        self.all_meal_photos = []

        for meal_name, photo in self.meal_images.items():
            self.all_meal_photos.append(photo)  # Keep reference

            frame = tk.Frame(scrollable_frame, bg="#F5E9DA", bd=1, relief="solid")
            frame.grid(row=row, column=col, padx=10, pady=10)

            lbl = tk.Label(frame, image=photo, text=meal_name, compound="top",
                           bg="#F5E9DA", fg="#5C4033", cursor="hand2")
            lbl.pack()
            lbl.bind("<Button-1>", lambda e, name=meal_name: self.select_meal(name))

            col += 1
            if col >= cols:
                col = 0
                row += 1


if __name__ == "__main__":
    root = tk.Tk()
    app = FilipinoMealApp(root)
    root.mainloop()
