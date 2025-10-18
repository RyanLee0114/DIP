import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List, Tuple, Optional


class FoodItem:
    """Represents a single menu item grouped by category."""

    def __init__(self, name: str, price: float, category: str) -> None:
        self.name = name
        self.price = float(price)
        self.category = category


class Menu:
    """Provides categorized menu data for the kiosk."""

    def __init__(self, menu_filename: str = "menu.txt") -> None:
        data = self._load_menu_file(menu_filename)
        if not data:
            data = self._default_menu()
        self._items_by_category = data

    def _load_menu_file(self, filename: str) -> Dict[str, List[FoodItem]]:
        menu_path = Path(__file__).resolve().parent / filename
        items: Dict[str, List[FoodItem]] = {}
        current_category: Optional[str] = None

        try:
            with menu_path.open("r", encoding="utf-8") as menu_file:
                for raw_line in menu_file:
                    line = raw_line.strip()
                    if not line or line.lower() == "menu":
                        continue
                    if not line.startswith("-"):
                        current_category = line
                        items.setdefault(current_category, [])
                        continue
                    if current_category is None:
                        continue
                    entry = line[1:].strip()
                    if ":" not in entry:
                        continue
                    name_part, price_part = entry.split(":", 1)
                    name = name_part.strip()
                    price_text = price_part.strip().lstrip("$")
                    if not name or not price_text:
                        continue
                    try:
                        price_value = float(price_text)
                    except ValueError:
                        continue
                    if price_value.is_integer():
                        price_value = int(price_value)
                    items[current_category].append(FoodItem(name, price_value, current_category))
        except FileNotFoundError:
            messagebox.showwarning("Menu", f"Could not find {filename}. Loading default menu.")
        except OSError:
            messagebox.showwarning("Menu", f"Could not read {filename}. Loading default menu.")

        return {category: menu_items for category, menu_items in items.items() if menu_items}

    def _default_menu(self) -> Dict[str, List[FoodItem]]:
        return {
            "Burgers": [
                FoodItem("Big Mac", 6.00, "Burgers"),
                FoodItem("Cheeseburger", 5.00, "Burgers"),
                FoodItem("McChicken Burger", 6.50, "Burgers"),
                FoodItem("McCrispy", 7.00, "Burgers"),
                FoodItem("McCrispy Bacon Deluxe", 7.50, "Burgers"),
                FoodItem("McCrispy Double", 9.00, "Burgers"),
                FoodItem("Quarter Pounder", 7.00, "Burgers"),
                FoodItem("Quarter Pounder Double", 8.00, "Burgers"),
            ],
            "Sides": [
                FoodItem("Fries", 3.00, "Sides"),
                FoodItem("Chicken Nuggets", 4.00, "Sides"),
                FoodItem("Ice Cream", 2.50, "Sides"),
            ],
            "Drinks": [
                FoodItem("Coke", 2.00, "Drinks"),
                FoodItem("Coke Zero Sugar", 2.00, "Drinks"),
                FoodItem("Fanta Orange", 2.50, "Drinks"),
                FoodItem("Sprite Zero", 2.50, "Drinks"),
            ],
        }

    def categories(self) -> List[str]:
        return list(self._items_by_category.keys())

    def items_for(self, category: str) -> List[FoodItem]:
        return list(self._items_by_category.get(category, []))


class Cart:
    """Stores the cart as item → quantity to keep totals accurate."""

    def __init__(self) -> None:
        self._lines: Dict[FoodItem, int] = {}

    def add(self, item: FoodItem, quantity: int = 1) -> None:
        if quantity <= 0:
            return
        self._lines[item] = self._lines.get(item, 0) + quantity

    def set_quantity(self, item: FoodItem, quantity: int) -> None:
        if quantity <= 0:
            self._lines.pop(item, None)
        else:
            self._lines[item] = quantity

    def lines(self) -> List[Tuple[FoodItem, int]]:
        return [(item, qty) for item, qty in self._lines.items()]

    def clear(self) -> None:
        self._lines.clear()

    @property
    def total(self) -> float:
        return sum(item.price * qty for item, qty in self._lines.items())

    def is_empty(self) -> bool:
        return not self._lines


class KioskApp:
    """Tkinter front end that orchestrates menu display and cart interactions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Kiosk")
        self.root.attributes("-fullscreen", True)  # Fullscreen
        self.menu = Menu()
        self.cart = Cart()
        self.selected_category: Optional[tk.StringVar] = None
        self.total_label: Optional[tk.Label] = None

        # Draw the default menu view immediately after startup.
        self.show_main_menu()

    def clear_screen(self) -> None:
        # Wipe the window before rendering the next flow step.
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self) -> None:
        self.clear_screen()

        left_frame = tk.Frame(self.root, bg='lightgrey', width=200)
        left_frame.pack(side='left', fill='y')

        categories = self.menu.categories()
        default_category = categories[0] if categories else ""
        self.selected_category = tk.StringVar(value=default_category)

        right_frame = tk.Frame(self.root, bg='skyblue')
        right_frame.pack(side='right', expand=True, fill='both')

        # Items grid lives on the right; category rail stays pinned left.
        items_frame = tk.Frame(right_frame, bg='skyblue')
        items_frame.pack(expand=True)

        def render_items(category: str) -> None:
            # Rebuild the tile grid whenever a new category is selected.
            for widget in items_frame.winfo_children():
                widget.destroy()
            row, col = 0, 0
            for menu_item in self.menu.items_for(category):
                frame = tk.Frame(items_frame, bg='hotpink', width=150, height=120)
                frame.grid(row=row, column=col, padx=15, pady=15)
                btn = tk.Button(
                    frame,
                    text=f"{menu_item.name}\n${menu_item.price:.2f}",
                    bg='hotpink',
                    font=('Arial', 12),
                    width=15,
                    height=4,
                    command=lambda i=menu_item: self.show_quantity_popup(i),
                )
                btn.pack(expand=True, fill='both')
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        for cat in categories:
            tk.Radiobutton(
                left_frame,
                text=cat,
                variable=self.selected_category,
                value=cat,
                indicatoron=0,
                width=15,
                font=('Arial', 14),
                bg='black',
                selectcolor='hotpink',
                command=lambda: render_items(self.selected_category.get()),
            ).pack(pady=10, padx=10, fill='x')

        if default_category:
            render_items(default_category)

        tk.Button(
            right_frame,
            text="Check Out",
            bg='orange',
            font=('Arial', 14),
            command=self.show_dine_option,
        ).pack(pady=20)  # Checkout CTA stays visible as guests browse.

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

        tk.Label(popup, text=f"{item.name} (${item.price:.2f})", font=('Arial', 14)).pack(pady=(10, 0))
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
            # Modal acknowledgement mimics the kiosk confirmation chime.
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
        # Consistent back button placement reinforces kiosk navigation muscle memory.
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

        # Inline quantity controls keep adjustments quick without extra popups.
        for item, quantity in cart_lines:
            frame = tk.Frame(self.root, bg='black', padx=10, pady=5)
            frame.pack(pady=5, fill='x')
            tk.Label(frame, text=item.name, font=('Arial', 14), width=20).pack(side='left')
            tk.Label(frame, text=f"${item.price:.2f}", font=('Arial', 14)).pack(side='left', padx=10)

            var = tk.IntVar(value=quantity)
            item_total_label = tk.Label(frame, text=f"= ${item.price * quantity:.2f}", font=('Arial', 14), fg='green')
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
                total_lbl.config(text=f"= ${menu_item.price * new_qty:.2f}")
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

        self.total_label = tk.Label(self.root, text=f"Total: ${self.cart.total:.2f}", font=('Arial', 20))
        self.total_label.pack(pady=20)
        tk.Button(self.root, text="Proceed to Payment", bg='orange', font=('Arial', 16), command=self.show_payment).pack(pady=20)

    def update_total_label(self) -> None:
        if self.total_label is not None:
            self.total_label.config(text=f"Total: ${self.cart.total:.2f}")

    def show_payment(self) -> None:
        self.clear_screen()
        tk.Button(self.root, text="< Back", font=('Arial', 12), command=self.show_cart).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Choose Payment Method", font=('Arial', 24)).pack(pady=40)
        # Payment buttons funnel into the same pickup number for now.
        tk.Button(self.root, text="Cash", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)
        tk.Button(self.root, text="Card", bg='hotpink', font=('Arial', 20), width=15, command=self.show_order_number).pack(pady=20)

    def show_order_number(self) -> None:
        self.clear_screen()
        # Final screen mirrors QSR kiosks with a simple collection number.
        tk.Label(self.root, text="Your Order Number:", font=('Arial', 24)).pack(pady=50)
        tk.Label(self.root, text="#12345", font=('Arial', 40), bg='hotpink').pack(pady=30)
        tk.Button(self.root, text="Back to Home", font=('Arial', 16), bg='orange', command=self.reset).pack(pady=20)

    def reset(self) -> None:
        # Tear down the window entirely so a new session can relaunch cleanly.
        self.cart.clear()
        self.root.destroy()


# Run it
# Entry point: create the Tk root and drive the kiosk UI event loop.
# Makes it easy to run the kiosk standalone for exploratory testing.
root = tk.Tk()
app = KioskApp(root)
root.mainloop()
