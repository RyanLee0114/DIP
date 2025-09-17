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

        # Left frame for categories
        left_frame = tk.Frame(self.root, bg='lightgrey', width=200)
        left_frame.pack(side='left', fill='y')

        categories = ["Burgers", "Sides", "Drinks"]
        self.selected_category = tk.StringVar(value=categories[0])

        def update_items():
            show_items(self.selected_category.get())

        for cat in categories:
            btn = tk.Radiobutton(
                left_frame, text=cat, variable=self.selected_category, value=cat,
                indicatoron=0, width=15, font=('Arial', 14), bg='black', selectcolor='hotpink',
                command=update_items
            )
            btn.pack(pady=10, padx=10, fill='x')

        # Right frame for items
        right_frame = tk.Frame(self.root, bg='skyblue')
        right_frame.pack(side='right', expand=True, fill='both')

        items_frame = tk.Frame(right_frame, bg='skyblue')
        items_frame.pack(expand=True)

        # Define items by category
        food_items_by_cat = {
            "Burgers": [
                {"name": "Big Mac", "price": 6},
                {"name": "Cheeseburger", "price": 5},
            ],
            "Sides": [
                {"name": "Fries", "price": 3},
                {"name": "Chicken Nuggets", "price": 4},
                {"name": "Ice Cream", "price": 2},
            ],
            "Drinks": [
                {"name": "Coke", "price": 2},
            ]
        }

        def show_items(category):
            # Clear previous items
            for widget in items_frame.winfo_children():
                widget.destroy()
            row, col = 0, 0
            for item in food_items_by_cat.get(category, []):
                frame = tk.Frame(items_frame, bg='hotpink', width=150, height=120)
                frame.grid(row=row, column=col, padx=15, pady=15)
                btn = tk.Button(
                    frame,
                    text=f"{item['name']}\n${item['price']}",
                    bg='hotpink',
                    font=('Arial', 12),
                    width=15,
                    height=4,
                    command=lambda i=item: self.show_quantity_popup(i)
                )
                btn.pack(expand=True, fill='both')
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        show_items(self.selected_category.get())

        tk.Button(right_frame, text="Check Out", bg='orange', font=('Arial', 14), command=self.show_dine_option).pack(pady=20)

    def show_quantity_popup(self, item):
        popup = tk.Toplevel(self.root)
        popup.title(f"Select Quantity for {item['name']}")
        popup.geometry("300x150")

        # Back button at top left
        tk.Button(popup, text="Go Back", bg='lightgrey', font=('Arial', 12), command=popup.destroy).pack(anchor='nw', padx=10, pady=10)

        tk.Label(popup, text=f"{item['name']} (${item['price']})", font=('Arial', 14)).pack(pady=(10,0))
        tk.Label(popup, text="Quantity:", font=('Arial', 12)).pack()
        qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(popup, from_=1, to=50, textvariable=qty_var, font=('Arial', 12), width=5)
        qty_spin.pack(pady=5)

        def add_with_qty():
            qty = qty_var.get()
            for _ in range(qty):
                self.cart.append(item)
                self.total_price += item['price']
            messagebox.showinfo("Item Added", f"{qty} x {item['name']} added to cart.")
            popup.destroy()

        tk.Button(popup, text="Add to Cart", bg='orange', font=('Arial', 12), command=add_with_qty).pack(pady=10)

    def show_dine_option(self):
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_main_menu).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Dine In or Take Away?", font=('Arial', 24)).pack(pady=50)
        tk.Button(self.root, text="Dine In", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)
        tk.Button(self.root, text="Take Away", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)

    def show_cart(self):
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_dine_option).pack(anchor='nw', padx=10, pady=10)
 
        # Aggregate cart items by name
        item_counts = {}
        for item in self.cart:
            key = item['name']
            if key not in item_counts:
                item_counts[key] = {'item': item, 'qty': 0}
            item_counts[key]['qty'] += 1
 
        self.cart_spin_vars = {} # Store IntVars for each item
 
        def on_spin_change(item_name):
            var = self.cart_spin_vars[item_name]
            new_qty = int(var.get())
            old_qty = item_counts[item_name]['qty']
            item = item_counts[item_name]['item']
            diff = new_qty - old_qty
            if diff > 0:
                for _ in range(diff):
                    self.cart.append(item)
                    self.total_price += item['price']
            elif diff < 0:
                count = 0
                new_cart = []
                for cart_item in self.cart:
                    if cart_item['name'] == item_name and count < abs(diff):
                        self.total_price -= cart_item['price']
                        count += 1
                    else:
                        new_cart.append(cart_item)
                self.cart = new_cart
            item_counts[item_name]['qty'] = new_qty
            # Update total label
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text").startswith("Total:"):
                    widget.config(text=f"Total: ${self.total_price}")
 
        for item_name, data in item_counts.items():
            frame = tk.Frame(self.root, bg='BLACK', padx=10, pady=5)
            frame.pack(pady=5, fill='x')
            tk.Label(frame, text=data['item']['name'], font=('Arial', 14), width=20).pack(side='left')
            tk.Label(frame, text=f"${data['item']['price']}", font=('Arial', 14)).pack(side='left', padx=10)
            # Spinbox for quantity
            var = tk.IntVar(value=data['qty'])
            self.cart_spin_vars[item_name] = var

            # Create the item total label so we can update it
            item_total_label = tk.Label(frame, text=f"= ${data['item']['price'] * data['qty']}", font=('Arial', 14), fg='green')
            item_total_label.pack(side='right', padx=10)

            def update_qty(name=item_name, v=var, lbl=item_total_label):
                new_qty = v.get()
                old_qty = item_counts[name]['qty']
                item = item_counts[name]['item']
                diff = new_qty - old_qty
                if diff > 0:
                    for _ in range(diff):
                        self.cart.append(item)
                        self.total_price += item['price']
                elif diff < 0:
                    count = 0
                    new_cart = []
                    for cart_item in self.cart:
                        if cart_item['name'] == name and count < abs(diff):
                            self.total_price -= cart_item['price']
                            count += 1
                        else:
                            new_cart.append(cart_item)
                    self.cart = new_cart
                item_counts[name]['qty'] = new_qty
                # Update total label
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Label) and widget.cget("text").startswith("Total:"):
                        widget.config(text=f"Total: ${self.total_price}")
                # Update this item's total label
                lbl.config(text=f"= ${item['price'] * new_qty}")

            spin = tk.Spinbox(
                frame, from_=1, to=50, textvariable=var, font=('Arial', 14), width=5,
                command=update_qty
            )
            spin.pack(side='right', padx=10)
            spin.update_idletasks()

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
        self.root.destroy()

# Run it
root = tk.Tk()
app = KioskApp(root)
root.mainloop()
