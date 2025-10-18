import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Tuple, Optional


class FoodItem:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price

class Menu:
    def __init__(self) -> None:
        self._items: List[FoodItem] = [
            FoodItem("Big Mac", 6.00),
            FoodItem("Cheeseburger", 5.00),
            FoodItem("McChicken Burger", 6.50),
            FoodItem("McCrispy", 7.00),
            FoodItem("McCrispy Bacon Deluxe", 7.50),
            FoodItem("McCrispy Double", 9.00),
            FoodItem("Quarter Pounder", 7.00),
            FoodItem("Quarter Pounder Double", 8.00),
            FoodItem("Fries", 3.00),
            FoodItem("Chicken Nuggets", 4.00),
            FoodItem("Ice Cream", 2.50),
            FoodItem("Coke", 2.00),
            FoodItem("Coke Zero Sugar", 2.00),
            FoodItem("Fanta Orange", 2.50),
            FoodItem("Sprite Zero", 2.50),
        ]


    def items(self) -> List[FoodItem]:
        return list(self._items)

class Cart:
    def __init__(self) -> None:
        self._lines: Dict[FoodItem, int] = {}

    def add(self, item: FoodItem, quantity: int = 1) -> None:
        if quantity > 0:
            self._lines[item] = self._lines.get(item, 0) + quantity

    def set_quantity(self, item: FoodItem, quantity: int) -> None:
        if quantity <= 0:
            self._lines.pop(item, None)
        else:
            self._lines[item] = quantity

    def lines(self) -> List[Tuple[FoodItem, int]]:
        return [(item, qty) for item, qty in self._lines.items()]

    @property
    def total(self) -> int:
        return sum(item.price * qty for item, qty in self._lines.items())


class KioskApp:
    """Tkinter front end that orchestrates menu display and cart interactions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Kiosk")
        self.root.attributes("-fullscreen", True)
        self.menu = Menu()
        self.cart = Cart()
        self.total_label: Optional[tk.Label] = None
        # Landing screen draws immediately so the kiosk feels responsive at boot.
        self.show_main_menu()

    def clear_screen(self) -> None:
        # Remove all widgets before painting the next screen.
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self) -> None:
        self.clear_screen()

        right_frame = tk.Frame(self.root, bg='skyblue')
        right_frame.pack(side='right', expand=True, fill='both')

        items_frame = tk.Frame(right_frame, bg='skyblue')
        items_frame.pack(expand=True)

        row, col = 0, 0
        # Build a 3-column grid of menu tiles with quantity prompts attached.
        for item in self.menu.items():
            frame = tk.Frame(items_frame, bg='hotpink', width=150, height=120)
            frame.grid(row=row, column=col, padx=15, pady=15)
            btn = tk.Button(
                frame,
                text=f"{item.name}\n${item.price}",
                bg='hotpink',
                font=('Arial', 12),
                width=15,
                height=4,
                command=lambda i=item: self.show_quantity_popup(i),
            )
            btn.pack(expand=True, fill='both')

            col += 1
            if col > 2:
                col = 0
                row += 1

        tk.Button(
            right_frame,
            text="Check Out",
            bg='orange',
            font=('Arial', 14),
            command=self.show_dine_option,
        ).pack(pady=20)  # Persistent checkout button nudges users to proceed.

    def show_quantity_popup(self, item: FoodItem) -> None:
        popup = tk.Toplevel(self.root)
        popup.title(f"Select Quantity for {item.name}")
        popup.geometry("300x150")

        tk.Button(
            popup,
            text="Go Back",
            bg='lightgrey',
            font=('Arial', 12),
            command=popup.destroy,
        ).pack(anchor='nw', padx=10, pady=10)

        tk.Label(popup, text=f"{item.name} (${item.price})", font=('Arial', 14)).pack(pady=(10, 0))
        tk.Label(popup, text="Quantity:", font=('Arial', 12)).pack()
        qty_var = tk.IntVar(value=1)
        tk.Spinbox(popup, from_=1, to=50, textvariable=qty_var, font=('Arial', 12), width=5).pack(pady=5)

        def add_with_qty() -> None:
            try:
                qty = int(qty_var.get())
            except (tk.TclError, ValueError):
                qty = 1
            qty = max(1, qty)
            self.cart.add(item, qty)
            # Feedback dialog mirrors the tactile kiosk confirmation tone.
            messagebox.showinfo("Item Added", f"{qty} x {item.name} added to cart.")
            popup.destroy()

        tk.Button(
            popup,
            text="Add to Cart",
            bg='orange',
            font=('Arial', 12),
            command=add_with_qty,
        ).pack(pady=10)

    def show_dine_option(self) -> None:
        self.clear_screen()
        # Keep the back affordance anchored in the same spot for every screen.
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_main_menu).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Dine In or Take Away?", font=('Arial', 24)).pack(pady=50)
        tk.Button(self.root, text="Dine In", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)
        tk.Button(self.root, text="Take Away", bg='hotpink', font=('Arial', 20), width=15, command=self.show_cart).pack(pady=20)

    def show_cart(self) -> None:
        self.clear_screen()
        self.total_label = None
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_dine_option).pack(anchor='nw', padx=10, pady=10)

        cart_lines = self.cart.lines()
        if not cart_lines:
            tk.Label(self.root, text="Your cart is empty.", font=('Arial', 14)).pack(pady=20)

        # Each row lets guests update quantities without leaving the summary.
        for item, quantity in cart_lines:
            frame = tk.Frame(self.root, bg='black', padx=10, pady=5)
            frame.pack(pady=5, fill='x')
            tk.Label(frame, text=item.name, font=('Arial', 14), width=20).pack(side='left')
            tk.Label(frame, text=f"${item.price}", font=('Arial', 14)).pack(side='left', padx=10)

            var = tk.IntVar(value=quantity)
            item_total_label = tk.Label(frame, text=f"= ${item.price * quantity}", font=('Arial', 14), fg='green')
            item_total_label.pack(side='right', padx=10)

            def apply_new_qty(menu_item=item, quantity_var=var, total_lbl=item_total_label) -> None:
                try:
                    new_qty = int(quantity_var.get())
                except (tk.TclError, ValueError):
                    return
                if new_qty < 1:
                    new_qty = 1
                    quantity_var.set(new_qty)
                self.cart.set_quantity(menu_item, new_qty)
                total_lbl.config(text=f"= ${menu_item.price * new_qty}")
                self.update_total_label()

            spin = tk.Spinbox(
                frame,
                from_=1,
                to=50,
                textvariable=var,
                font=('Arial', 14),
                width=5,
                command=apply_new_qty,
            )
            spin.pack(side='right', padx=10)
            spin.bind("<FocusOut>", lambda _event, cb=apply_new_qty: cb())
            spin.bind("<Return>", lambda _event, cb=apply_new_qty: cb())

        self.total_label = tk.Label(self.root, text=f"Total: ${self.cart.total}", font=('Arial', 20))
        self.total_label.pack(pady=20)
        tk.Button(self.root, text="Proceed to Payment", bg='orange', font=('Arial', 16), command=self.show_payment).pack(pady=20)

    def update_total_label(self) -> None:
        if self.total_label is not None:
            self.total_label.config(text=f"Total: ${self.cart.total}")

    def show_payment(self) -> None:
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_cart).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Choose Payment Method", font=('Arial', 24)).pack(pady=40)
        # Payment paths converge—the kiosk simply hands out an order ticket.
        tk.Button(self.root, text="Cash", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)
        tk.Button(self.root, text="Card", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)

    def show_order_number(self) -> None:
        self.clear_screen()
        # Mimic the real-world experience with a pseudo order number.
        tk.Label(self.root, text="Your Order Number:", font=('Arial', 24)).pack(pady=50)
        tk.Label(self.root, text="#12345", font=('Arial', 40), bg='hotpink').pack(pady=30)
        tk.Button(self.root, text="Back to Home", font=('Arial', 16), bg='orange', command=self.reset).pack(pady=20)

    def reset(self) -> None:
        # Reset the cart and return to the menu so the next guest can start.
        self.cart.clear()
        self.show_main_menu()


# Run it
# Entry point: construct the Tk root window and hand control to the kiosk.
# Useful for quick manual smoke checks outside of the full suite.
root = tk.Tk()
app = KioskApp(root)
root.mainloop()
