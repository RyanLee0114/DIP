import tkinter as tk
from tkinter import messagebox

class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kiosk")
        self.root.attributes("-fullscreen", True)  # Fullscreen
        self.cart = []
        self.total_price = 0

        self.show_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_screen()

        main_frame = tk.Frame(self.root, bg='skyblue')
        main_frame.pack(expand=True, fill='both')

        items_frame = tk.Frame(main_frame, bg='skyblue')
        items_frame.pack(expand=True)

        food_items = [
            {"name": "Big Mac", "price": 6},
            {"name": "Fries", "price": 3},
            {"name": "Coke", "price": 2},
            {"name": "Chicken Nuggets", "price": 4},
            {"name": "Ice Cream", "price": 2},
            {"name": "Cheeseburger", "price": 5},
        ]

        row, col = 0, 0
        for item in food_items:
            frame = tk.Frame(items_frame, bg='hotpink', width=150, height=120)
            frame.grid(row=row, column=col, padx=15, pady=15)
            tk.Label(frame, text=item['name'], bg='hotpink', font=('Arial', 12)).pack(pady=10)
            tk.Label(frame, text=f"${item['price']}", bg='hotpink', font=('Arial', 10)).pack()
            tk.Button(frame, text="Add", command=lambda i=item: self.add_to_cart(i)).pack(pady=5)

            col += 1
            if col > 2:
                col = 0
                row += 1

        tk.Button(main_frame, text="Check Out", bg='orange', font=('Arial', 14), command=self.show_dine_option).pack(pady=20)

    def add_to_cart(self, item):
        self.cart.append(item)
        self.total_price += item['price']
        messagebox.showinfo("Item Added", f"{item['name']} added to cart.")

    def show_dine_option(self):
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_main_menu).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Dine In or Take Away?", font=('Arial', 24)).pack(pady=50)
        tk.Button(self.root, text="Dine In", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)
        tk.Button(self.root, text="Take Away", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)

    def show_cart(self):
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_dine_option).pack(anchor='nw', padx=10, pady=10)

        for item in self.cart:
            frame = tk.Frame(self.root, bg='lightcyan', padx=10, pady=5)
            frame.pack(pady=5, fill='x')
            tk.Label(frame, text=item['name'], font=('Arial', 14), width=20).pack(side='left')
            tk.Label(frame, text=f"${item['price']}", font=('Arial', 14)).pack(side='right')

        tk.Label(self.root, text=f"Total: ${self.total_price}", font=('Arial', 20)).pack(pady=20)
        tk.Button(self.root, text="Proceed to Payment", bg='orange', font=('Arial', 16), command=self.show_payment).pack(pady=20)

    def show_payment(self):
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_cart).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Choose Payment Method", font=('Arial', 24)).pack(pady=40)
        tk.Button(self.root, text="Cash", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)
        tk.Button(self.root, text="Card", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)

    def show_order_number(self):
        self.clear_screen()
        tk.Label(self.root, text="Your Order Number:", font=('Arial', 24)).pack(pady=50)
        tk.Label(self.root, text="#12345", font=('Arial', 40), bg='hotpink').pack(pady=30)
        tk.Button(self.root, text="Back to Home", font=('Arial', 16), bg='orange', command=self.reset).pack(pady=20)

    def reset(self):
        self.cart.clear()
        self.total_price = 0
        self.show_main_menu()


# Run it
root = tk.Tk()
app = KioskApp(root)
root.mainloop()
