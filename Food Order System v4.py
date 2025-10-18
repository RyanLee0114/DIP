import math
import os
import random
import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Tuple, Optional

# UI constants
UI_RADIUS = 20


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    # Sequence of points that the canvas turns into a smooth rounded rectangle.
    points = [x1 + radius, y1,x2 - radius, y1,x2, y1,x2, y1 + radius,x2, y2 - radius,x2, y2,x2 - radius, y2,x1 + radius, y2,x1, y2,x1, y2 - radius,x1, y1 + radius,x1, y1,]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)


def _normalize_key(value: str) -> str:
    if not value:
        return ''
    return ''.join(ch.lower() for ch in value if ch.isalnum())


class FoodItem:
    """Represents a single menu item."""

    def __init__(self, name: str, price: float, category: str) -> None:
        self.name = name
        self.price = float(price)
        self.category = category

    def __hash__(self) -> int:
        return hash((self.name.lower(), round(self.price, 2), self.category.lower()))

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FoodItem)
            and self.name.lower() == other.name.lower()
            and round(self.price, 2) == round(other.price, 2)
            and self.category.lower() == other.category.lower()
        )


class Menu:
    """Stores menu items grouped by category."""

    def __init__(self, items_by_category: Optional[Dict[str, List[FoodItem]]] = None) -> None:
        self._items_by_category: Dict[str, List[FoodItem]] = items_by_category or {}

    @classmethod
    def from_mapping(cls, mapping: Dict[str, List[Dict[str, float]]]) -> "Menu":
        # Convert the simple dict structure into strongly typed FoodItem rows.
        items: Dict[str, List[FoodItem]] = {}
        for category, raw_items in mapping.items():
            items[category] = [
                FoodItem(entry.get("name", ""), entry.get("price", 0), category)
                for entry in raw_items
                if entry.get("name")
            ]
        return cls(items)

    def categories(self) -> List[str]:
        return list(self._items_by_category.keys())

    def items_for(self, category: str) -> List[FoodItem]:
        return list(self._items_by_category.get(category, []))

    def add_item(self, item: FoodItem) -> None:
        self._items_by_category.setdefault(item.category, []).append(item)

    def all_items(self) -> List[FoodItem]:
        items: List[FoodItem] = []
        for category_items in self._items_by_category.values():
            items.extend(category_items)
        return items


class Cart:
    """Tracks cart quantities and totals."""

    def __init__(self) -> None:
        self._lines: Dict[FoodItem, int] = {}

    def add(self, item: FoodItem, quantity: int = 1) -> None:
        # Defensive guard keeps bogus values from skewing totals.
        if quantity <= 0:
            return
        self._lines[item] = self._lines.get(item, 0) + quantity

    def set_quantity(self, item: FoodItem, quantity: int) -> None:
        if quantity <= 0:
            self._lines.pop(item, None)
        else:
            self._lines[item] = quantity

    def remove_item(self, item: FoodItem) -> None:
        self._lines.pop(item, None)

    def clear(self) -> None:
        self._lines.clear()

    def lines(self) -> List[Tuple[FoodItem, int]]:
        return [(item, qty) for item, qty in self._lines.items()]

    @property
    def total(self) -> float:
        return sum(item.price * qty for item, qty in self._lines.items())

    def is_empty(self) -> bool:
        return not self._lines
class Button(tk.Canvas):
    def __init__(
        self,
        master,
        text,
        command=None,
        width=220,
        height=70,
        font=('Arial', 24),
        radius=UI_RADIUS,
        fill='white',
        outline='black',
        active_fill='#f2f2f2',
        selected_fill=None,
        text_color='black',
        image=None,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=master.cget('bg'),
        )
        self._fill = fill
        self._outline = outline
        self._active_fill = active_fill
        self._selected_fill = selected_fill if selected_fill is not None else fill
        self._text_color = text_color
        self._command = command
        self._is_selected = False
        self._image = image
        self._image_ref = image

        self._shape = draw_rounded_rectangle(
            self,
            2,
            2,
            width - 2,
            height - 2,
            radius,
            fill=self._fill,
            outline=self._outline,
            width=2,
        )

        text_anchor = 'center'
        text_x = width / 2
        text_width = int(width * 0.85)
        text_justify = 'center'
        if self._image is not None:
            icon_center = width * 0.22
            try:
                icon_half_width = self._image.width() / 2
            except tk.TclError:
                icon_half_width = 0
            text_left = icon_center + icon_half_width + 12
            text_right = width - 20
            if text_right <= text_left:
                text_left = width * 0.55
                text_right = width - 20
            text_x = (text_left + text_right) / 2
            text_anchor = 'center'
            text_width = max(50, int(text_right - text_left))
            text_justify = 'center'
            self.create_image(
                width * 0.22,
                height / 2,
                image=self._image,
                anchor='center',
            )

        self._text = self.create_text(
            text_x,
            height / 2,
            text=text,
            font=font,
            fill=self._text_color,
            justify=text_justify,
            anchor=text_anchor,
            width=text_width,
        )

        self.configure(cursor='hand2', takefocus=1)
        self.bind('<Button-1>', self._on_click)
        self.bind('<Return>', self._on_click)
        self.bind('<space>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _apply_state(self):
        fill = self._selected_fill if self._is_selected else self._fill
        self.itemconfigure(self._shape, fill=fill)

    def _on_click(self, _event=None):
        if callable(self._command):
            self._command()
        self._apply_state()

    def _on_enter(self, _event=None):
        if not self._is_selected:
            self.itemconfigure(self._shape, fill=self._active_fill)

    def _on_leave(self, _event=None):
        self._apply_state()

    def set_selected(self, selected: bool):
        self._is_selected = bool(selected)
        self._apply_state()


class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kiosk")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg='white')

        self.cart = Cart()
        self.order_number_counter = random.randint(10000, 90000)

        # Resolve asset folders up-front so every screen can pull icons/images.
        self.assets_root = os.path.dirname(__file__)
        self.icons_dir = os.path.join(self.assets_root, "icons image")
        self.items_dir = os.path.join(self.assets_root, "items image")

        raw_menu_data = self.load_menu_data()

        self.items_per_row = 4  # Default grid density; tuned for 1080p kiosks.

        # Resize bookkeeping so the menu grid can stay square when window resizes.
        self._tile_canvases = []
        self._square_canvas_bind_id = None
        self._square_frame_bind_id = None
        self.category_buttons = []

        self.item_images = {}
        self.item_display_names = {}
        self.load_item_images()

        self.category_images = {}
        self.load_category_images()
        self.category_button_images = {}

        self.action_images = {}
        self.action_image_cache = {}
        self.load_action_images()

        self.menu = Menu.from_mapping(raw_menu_data)
        self.merge_image_items_into_menu(self.menu)

        self.show_main_menu()

    def load_menu_data(self, filename: str = "menu.txt"):
        # Parse the plaintext menu file into a category → items structure.
        menu_path = os.path.join(os.path.dirname(__file__), filename)
        menu = {}
        current_category = None

        # Expected layout: category on its own line, followed by "- Name: $Price".
        try:
            with open(menu_path, "r", encoding="utf-8") as menu_file:
                for raw_line in menu_file:
                    line = raw_line.strip()
                    if not line:
                        continue
                    if line.lower() == "menu":
                        continue
                    if line.startswith('-'):
                        if current_category is None:
                            continue
                        item_line = line[1:].strip()
                        if ':' not in item_line:
                            continue
                        name_part, price_part = item_line.split(':', 1)
                        name = name_part.strip()
                        price_text = price_part.strip().lstrip('$')
                        if not name or not price_text:
                            continue
                        try:
                            price_value = float(price_text)
                        except ValueError:
                            continue
                        price_value = int(price_value) if price_value.is_integer() else round(price_value, 2)
                        menu.setdefault(current_category, []).append({"name": name, "price": price_value})
                    else:
                        current_category = line
                        menu.setdefault(current_category, [])
        except FileNotFoundError:
            messagebox.showwarning("Menu", f"Could not find {filename}. Loading default menu.")
            return {}
        except OSError:
            messagebox.showwarning("Menu", f"Could not read {filename}. Loading default menu.")
            return {}

        return {category: items for category, items in menu.items() if items}

    def load_item_images(self):
        # Map normalized item names to Tk PhotoImages for later lookup.
        self.item_images.clear()
        self.item_display_names.clear()
        if not os.path.isdir(self.items_dir):
            return

        for filename in sorted(os.listdir(self.items_dir)):
            lower = filename.lower()
            if not lower.endswith(('.png')):
                continue
            path = os.path.join(self.items_dir, filename)
            if not os.path.exists(path):
                continue
            try:
                image = tk.PhotoImage(file=path)
            except tk.TclError:
                continue

            name_root, _ = os.path.splitext(filename)
            clean_name = name_root.replace('_', ' ').replace('-', ' ')
            clean_name = clean_name.replace('Thumbnail', '').replace('thumbnail', '').strip()
            clean_name = ' '.join(clean_name.split())
            if not clean_name:
                clean_name = name_root

            key = _normalize_key(clean_name)
            if not key:
                continue
            self.item_images[key] = image
            self.item_display_names[key] = clean_name



    def load_category_images(self):
        image_map = {
            "Burgers": "Fast Food Burger Icon.png",
            "Sides": "French Fries Icon.png",
            "Drinks": "Coke Coloring Icon.png",
        }

        for name, filename in image_map.items():
            paths_to_try = [
                os.path.join(self.icons_dir, filename),
                os.path.join(self.assets_root, filename),
            ]
            path = next((p for p in paths_to_try if os.path.exists(p)), None)
            if path is None:
                continue
            try:
                self.category_images[name] = tk.PhotoImage(file=path)
            except tk.TclError:
                continue

    def get_category_button_image(self, category, target_dim=60):
        if category in self.category_button_images:
            return self.category_button_images[category]
        source = self.category_images.get(category)
        if source is None:
            return None
        display_image = self._fit_photoimage(source, target_dim)
        self.category_button_images[category] = display_image
        return display_image

    def load_action_images(self):
        image_map = {
            "Check Out": "Pos Coloring Icon.png",
            "Cart": "Cart Coloring Icon.png",
            "Dine In": "dine in.png",
            "Take Away": "take away.png",
            "Cash": "Color Style Icon Wallet.png",
            "Card": "Coloring Style Icon.png",
            "Brand": "Fast Food Coloring Icon.png",
        }

        for name, filename in image_map.items():
            paths_to_try = [
                os.path.join(self.icons_dir, filename),
                os.path.join(self.assets_root, filename),
            ]
            path = next((p for p in paths_to_try if os.path.exists(p)), None)
            if path is None:
                continue
            try:
                self.action_images[name] = tk.PhotoImage(file=path)
            except tk.TclError:
                continue

    def get_action_image(self, name, target_dim=70):
        cache_key = (name, target_dim)
        if cache_key in self.action_image_cache:
            return self.action_image_cache[cache_key]
        source = self.action_images.get(name)
        if source is None:
            return None
        display_image = self._fit_photoimage(source, target_dim)
        self.action_image_cache[cache_key] = display_image
        return display_image

    def _fit_photoimage(self, image, target_dim):
        if image is None or target_dim is None:
            return image
        try:
            max_dim = max(image.width(), image.height())
        except tk.TclError:
            return image
        if max_dim <= 0 or target_dim <= 0 or max_dim <= target_dim:
            return image
        factor = max(1, int(math.ceil(max_dim / float(target_dim))))
        try:
            return image.subsample(factor, factor)
        except tk.TclError:
            return image

    def get_item_image(self, name):
        key = _normalize_key(name)
        if not key:
            return None
        return self.item_images.get(key)

    def infer_category_from_name(self, name: str) -> str:
        text = (name or "").lower()
        if any(keyword in text for keyword in ("drink", "coke", "sprite", "fanta", "juice", "tea", "water")):
            return "Drinks"
        if any(keyword in text for keyword in ("fries", "nugget", "ice cream", "snack", "side", "salad", "dessert")):
            return "Sides"
        return "Burgers"

    def merge_image_items_into_menu(self, menu: Menu) -> None:
        if menu is None:
            return

        existing_keys = {
            key
            for item in menu.all_items()
            if (key := _normalize_key(item.name))
        }

        for key, display_name in self.item_display_names.items():
            if not display_name or key in existing_keys:
                continue
            category = self.infer_category_from_name(display_name)
            # Skip auto-adding if no menu price has been specified for this item.
            if category not in menu._items_by_category:
                continue
            # Without a configured price, leave the item out of the menu.
            continue

    def format_price(self, price):
        try:
            value = float(price)
        except (TypeError, ValueError):
            return f"${price}"
        if value.is_integer():
            return f"${int(value)}"
        return f"${value:.2f}"

    def _render_tile(self, tile, cell_size):
        canvas = tile['canvas']
        if not canvas.winfo_exists():
            return
        canvas.config(width=cell_size, height=cell_size)
        canvas.delete('tile_shape')
        canvas.delete('tile_text')
        canvas.delete('tile_image')
        if cell_size <= 0:
            return
        draw_rounded_rectangle(
            canvas,
            3,
            3,
            cell_size - 3,
            cell_size - 3,
            UI_RADIUS,
            fill='white',
            outline='black',
            width=2,
            tags=('tile_shape',),
        )
        image = tile.get('image')
        text_y = cell_size / 2
        if image is not None:
            display_image = self._fit_photoimage(image, cell_size * 0.6)
            tile['image_display'] = display_image
            canvas.create_image(
                cell_size / 2,
                cell_size * 0.42,
                image=display_image,
                anchor='center',
                tags=('tile_image',),
            )
            text_y = cell_size * 0.78

        canvas.create_text(
            cell_size / 2,
            text_y,
            text=tile['text'],
            font=('Arial', 24),
            fill='black',
            width=cell_size * 0.85,
            justify='center',
            tags=('tile_text',),
        )

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_screen()

        left_frame = tk.Frame(self.root, width=240, bg='white')
        left_frame.pack(side='left', fill='y', padx=10, pady=10)

        brand_icon = self.get_action_image("Brand", target_dim=140)
        if brand_icon is not None:
            brand_label = tk.Label(left_frame, image=brand_icon, bg='white')
            brand_label.image = brand_icon
            brand_label.pack(pady=(0, 20))

        right_frame = tk.Frame(self.root, bg='white')
        right_frame.pack(side='right', expand=True, fill='both', padx=10, pady=10)

        # Right-hand pane hosts the scrollable menu grid.
        items_container = tk.Frame(right_frame, bg='white')
        items_container.pack(side='top', expand=True, fill='both')

        # Canvas + scrollbar combo gives us a smooth, scrollable tile grid.
        items_canvas = tk.Canvas(items_container, highlightthickness=0, bg='white')
        items_canvas.pack(side='left', expand=True, fill='both')

        items_scrollbar = tk.Scrollbar(
            items_container,
            orient=tk.VERTICAL,
            command=items_canvas.yview,
            bg='white',
            activebackground='white',
            troughcolor='white',
            highlightthickness=0,
            relief='flat',
            borderwidth=0,
        )
        try:
            items_scrollbar.config(troughcolor='white', activebackground='white')
        except tk.TclError:
            pass
        items_scrollbar.pack(side='right', fill='y')
        items_canvas.configure(yscrollcommand=items_scrollbar.set)

        items_frame = tk.Frame(items_canvas, bg='white')
        items_window = items_canvas.create_window((0, 0), window=items_frame, anchor='nw')
        self._square_canvas_bind_id = None
        self._square_frame_bind_id = None

        def _update_scrollregion(_event):
            items_canvas.configure(scrollregion=items_canvas.bbox('all'))

        items_frame.bind('<Configure>', _update_scrollregion)

        def _resize_items_frame(event):
            items_canvas.itemconfigure(items_window, width=event.width)

        items_canvas.bind('<Configure>', _resize_items_frame)

        def _on_mousewheel(event):
            # Normalise scrolling so Tk works the same on Windows/Mac/Linux wheels.
            first, last = items_canvas.yview()
            span = last - first
            if event.delta:
                scale = 1200 if abs(event.delta) >= 120 else 600
                delta_fraction = -event.delta / scale
            else:
                wheel = getattr(event, 'num', None)
                if wheel == 4:
                    delta_fraction = -0.1
                elif wheel == 5:
                    delta_fraction = 0.1
                else:
                    delta_fraction = 0
            if delta_fraction:
                upper_bound = max(0, 1 - span)
                new_first = min(max(first + delta_fraction, 0), upper_bound)
                items_canvas.yview_moveto(new_first)

        def _bind_mousewheel(_event):
            items_canvas.bind_all('<MouseWheel>', _on_mousewheel)
            items_canvas.bind_all('<Button-4>', _on_mousewheel)
            items_canvas.bind_all('<Button-5>', _on_mousewheel)

        def _unbind_mousewheel(_event):
            items_canvas.unbind_all('<MouseWheel>')
            items_canvas.unbind_all('<Button-4>')
            items_canvas.unbind_all('<Button-5>')

        items_canvas.bind('<Enter>', _bind_mousewheel)
        items_canvas.bind('<Leave>', _unbind_mousewheel)
        items_frame.bind('<Enter>', _bind_mousewheel)
        items_frame.bind('<Leave>', _unbind_mousewheel)

        bottom_frame = tk.Frame(right_frame, bg='white')
        bottom_frame.pack(side='bottom', fill='x', pady=10)

        categories = self.menu.categories()
        if not categories:
            tk.Label(self.root, text="No menu items available.", font=('Arial', 36), fg='black', bg='white').pack(pady=40)
            return

        self.selected_category = tk.StringVar(value=categories[0])
        self.category_buttons = []

        def update_category_buttons():
            current = self.selected_category.get()
            for name, button in self.category_buttons:
                button.set_selected(name == current)

        def show_items(category):
            # Repaint the grid each time the user picks a new category.
            for widget in items_frame.winfo_children():
                widget.destroy()

            items = self.menu.items_for(category)
            self._tile_canvases = []
            if not items:
                items_frame.grid_columnconfigure(0, weight=1)
                tk.Label(items_frame, text="No items in this category.", font=('Arial', 28), fg='black', bg='white').grid(row=0, column=0, padx=10, pady=10)
                return

            columns = max(1, self.items_per_row)
            total_items = len(items)
            rows = max(1, math.ceil(total_items / columns))

            for col_index in range(columns):
                items_frame.grid_columnconfigure(col_index, weight=1, uniform="menu_cols")

            items_frame.grid_rowconfigure(0, weight=1)
            items_frame.grid_rowconfigure(rows + 1, weight=1)
            spacer_top = tk.Frame(items_frame, bg='white')
            spacer_top.grid(row=0, column=0, columnspan=columns, sticky='nsew')
            spacer_bottom = tk.Frame(items_frame, bg='white')
            spacer_bottom.grid(row=rows + 1, column=0, columnspan=columns, sticky='nsew')

            cell_frames = []

            for row_index in range(rows):
                items_frame.grid_rowconfigure(row_index + 1, weight=1, uniform="menu_rows")
                row_items = items[row_index * columns:(row_index + 1) * columns]
                slots = [None] * columns
                for idx, item in enumerate(row_items):
                    if idx < columns:
                        slots[idx] = item

                for col_index, item in enumerate(slots):
                    grid_row = row_index + 1
                    grid_col = col_index
                    pad_x = (10, 5) if col_index == 0 else (5, 10) if col_index == columns - 1 else (5, 5)
                    pad_y = (10, 5) if row_index == 0 else (5, 10) if row_index == rows - 1 else (5, 5)
                    frame = tk.Frame(items_frame, bg='white')
                    frame.grid(row=grid_row, column=grid_col, padx=pad_x, pady=pad_y, sticky='nsew')
                    frame.grid_propagate(False)
                    cell_frames.append(frame)

                    canvas = tk.Canvas(frame, bg='white', highlightthickness=0, bd=0, takefocus=1)
                    canvas.pack(fill='both', expand=True)

                    if item is None:
                        continue

                    tile = {
                        'canvas': canvas,
                        'item': item,
                        'text': f"{item.name}\n{self.format_price(item.price)}",
                        'image': self.get_item_image(item.name)
                    }
                    self._tile_canvases.append(tile)

                    def _make_click_handler(target_item, widget=canvas):
                        def handler(_event=None):
                            if widget.winfo_exists():
                                widget.focus_set()
                            self.show_quantity_popup(target_item)
                        return handler

                    click_handler = _make_click_handler(item)
                    canvas.bind('<Button-1>', click_handler)
                    canvas.bind('<Return>', click_handler)
                    canvas.bind('<space>', click_handler)
                    canvas.bind('<Enter>', lambda _e, c=canvas: c.itemconfig('tile_shape', fill='#f5f5f5'))
                    canvas.bind('<Leave>', lambda _e, c=canvas: c.itemconfig('tile_shape', fill='white'))
                    canvas.config(cursor='hand2')

            def _resize_cells(_event=None):
                if not items_canvas.winfo_exists() or not items_frame.winfo_exists():
                    return
                available_width = items_canvas.winfo_width()
                if available_width <= 1:
                    self.root.after(50, _resize_cells)
                    return
                horizontal_padding = 20 + (columns - 1) * 10
                cell_size = max(60, int((available_width - horizontal_padding) / max(1, columns)))
                for col_index in range(columns):
                    items_frame.grid_columnconfigure(col_index, minsize=cell_size)
                for row_index in range(rows):
                    items_frame.grid_rowconfigure(row_index + 1, minsize=cell_size)
                for frame in cell_frames:
                    if frame.winfo_exists():
                        frame.configure(width=cell_size, height=cell_size)
                for tile in self._tile_canvases:
                    self._render_tile(tile, cell_size)

                available_height = items_canvas.winfo_height()
                if available_height > 1:
                    vertical_padding = 20 + (rows - 1) * 10
                    content_height = rows * cell_size + vertical_padding
                    spacer = max(0, (available_height - content_height) // 2)
                    items_frame.grid_rowconfigure(0, minsize=spacer)
                    items_frame.grid_rowconfigure(rows + 1, minsize=spacer)

            if self._square_canvas_bind_id is not None:
                items_canvas.unbind('<Configure>', self._square_canvas_bind_id)
            self._square_canvas_bind_id = items_canvas.bind('<Configure>', _resize_cells, add='+')

            if self._square_frame_bind_id is not None:
                items_frame.unbind('<Configure>', self._square_frame_bind_id)
            self._square_frame_bind_id = items_frame.bind('<Configure>', _resize_cells, add='+')

            _resize_cells()
            items_canvas.yview_moveto(0)

        def handle_category_click(category):
            self.selected_category.set(category)
            show_items(category)
            update_category_buttons()

        for cat in categories:
            category_image = self.get_category_button_image(cat)
            button = Button(
                left_frame,
                text=cat,
                command=lambda c=cat: handle_category_click(c),
                width=220,
                height=80,
                font=('Arial', 28),
                radius=25,
                selected_fill='#d9d9d9',
                image=category_image,
            )
            button.pack(pady=10, padx=5)
            self.category_buttons.append((cat, button))

        handle_category_click(self.selected_category.get())

        checkout_icon = self.get_action_image("Check Out", target_dim=70)
        Button(
            bottom_frame,
            text="Check Out",
            command=self.show_dine_option,
            width=280,
            height=80,
            font=('Arial', 28),
            radius=25,
            image=checkout_icon,
        ).pack(pady=10)

    def show_quantity_popup(self, item: FoodItem) -> None:
        popup = tk.Toplevel(self.root)
        popup.title(f"Select Quantity for {item.name}")
        popup.configure(bg='white')

        image = self.get_item_image(item.name)
        popup_width = 360
        popup_height = 260
        if image is not None:
            # Expand popup if a product photo is available.
            popup_height = 420
        popup.geometry(f"{popup_width}x{popup_height}")

        Button(
            popup,
            text="Go Back",
            command=popup.destroy,
            width=160,
            height=60,
            font=('Arial', 24),
            radius=20,
        ).pack(anchor='nw', padx=10, pady=10)

        if image is not None:
            display_image = self._fit_photoimage(image, 200)
            popup._item_image_ref = display_image
            tk.Label(popup, image=display_image, bg='white').pack(pady=(5, 10))

        tk.Label(popup, text=f"{item.name} ({self.format_price(item.price)})", font=('Arial', 28), fg='black', bg='white').pack(pady=(10, 0))
        tk.Label(popup, text="Quantity:", font=('Arial', 24), fg='black', bg='white').pack()

        qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(popup, from_=1, to=50, textvariable=qty_var, font=('Arial', 24), width=5, fg='black', bg='white')
        qty_spin.pack(pady=5)

        def add_with_qty():
            try:
                qty = int(qty_var.get())
            except (tk.TclError, ValueError):
                qty = 1
            qty = max(1, qty)
            self.cart.add(item, qty)
            # Quick toast-style dialog reassures the guest their tap registered.
            messagebox.showinfo("Item Added", f"{qty} x {item.name} added to cart.")
            popup.destroy()

        Button(
            popup,
            text="Add to Cart",
            command=add_with_qty,
            width=200,
            height=70,
            font=('Arial', 24),
            radius=20,
        ).pack(pady=10)

    def show_dine_option(self):
        self.clear_screen()

        Button(
            self.root,
            text="< Back",
            command=self.show_main_menu,
            width=160,
            height=60,
            font=('Arial', 24),
            radius=20,
        ).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Dine In or Take Away?", font=('Arial', 48), fg='black', bg='white').pack(pady=50)

        dine_in_icon = self.get_action_image("Dine In", target_dim=90)
        Button(
            self.root,
            text="Dine In",
            command=self.show_cart,
            width=320,
            height=90,
            font=('Arial', 40),
            radius=30,
            image=dine_in_icon,
        ).pack(pady=20)

        take_away_icon = self.get_action_image("Take Away", target_dim=90)
        Button(
            self.root,
            text="Take Away",
            command=self.show_cart,
            width=320,
            height=90,
            font=('Arial', 40),
            radius=30,
            image=take_away_icon,
        ).pack(pady=20)

    def show_cart(self):
        self.clear_screen()

        Button(
            self.root,
            text="< Back",
            command=self.show_dine_option,
            width=160,
            height=60,
            font=('Arial', 24),
            radius=20,
        ).pack(anchor='nw', padx=10, pady=10)

        cart_icon = self.get_action_image("Cart", target_dim=100)
        if cart_icon is not None:
            header_frame = tk.Frame(self.root, bg='white')
            header_frame.pack(pady=(10, 20))
            header_frame._icon = cart_icon
            tk.Label(header_frame, image=cart_icon, bg='white').pack(side='left', padx=(0, 15))
            tk.Label(header_frame, text="Cart", font=('Arial', 48), fg='black', bg='white').pack(side='left')
        else:
            tk.Label(self.root, text="Cart", font=('Arial', 48), fg='black', bg='white').pack(pady=20)

        cart_lines = self.cart.lines()
        if not cart_lines:
            tk.Label(self.root, text="Your cart is empty.", font=('Arial', 28), fg='black', bg='white').pack(pady=20)

        total_label = tk.Label(self.root, text=f"Total: {self.format_price(self.cart.total)}", font=('Arial', 40), fg='black', bg='white')

        def delete_item(menu_item: FoodItem):
            self.cart.remove_item(menu_item)
            self.show_cart()

        def update_total_label():
            total_label.configure(text=f"Total: {self.format_price(self.cart.total)}")

        # Render each unique cart line with its image, price, and quantity controls.
        for item, quantity in cart_lines:
            frame = tk.Frame(self.root, padx=10, pady=5, bg='white')
            frame.pack(pady=5, fill='x')

            image = self.get_item_image(item.name)
            if image is not None:
                display_image = self._fit_photoimage(image, 90)
                frame._item_image_ref = display_image
                tk.Label(frame, image=display_image, bg='white').pack(side='left', padx=(0, 10))

            tk.Label(frame, text=item.name, font=('Arial', 28), width=20, fg='black', bg='white').pack(side='left')
            tk.Label(frame, text=self.format_price(item.price), font=('Arial', 28), fg='black', bg='white').pack(side='left', padx=10)

            var = tk.IntVar(value=quantity)

            item_total_label = tk.Label(frame, text=f"= {self.format_price(item.price * quantity)}", font=('Arial', 28), fg='black', bg='white')
            item_total_label.pack(side='right', padx=10)

            def update_qty(menu_item=item, quantity_var=var, total_lbl=item_total_label):
                try:
                    new_qty = int(quantity_var.get())
                except (tk.TclError, ValueError):
                    return
                if new_qty < 1:
                    new_qty = 1
                    quantity_var.set(new_qty)
                self.cart.set_quantity(menu_item, new_qty)
                total_lbl.configure(text=f"= {self.format_price(menu_item.price * new_qty)}")
                update_total_label()

            spin = tk.Spinbox(
                frame,
                from_=1,
                to=50,
                textvariable=var,
                font=('Arial', 28),
                width=5,
                command=update_qty,
                fg='black',
                bg='white',
            )
            spin.pack(side='right', padx=10)

            # Dedicated delete button keeps the flow familiar to fast-food kiosks.
            delete_button = Button(
                frame,
                text="Delete",
                command=lambda menu_item=item: delete_item(menu_item),
                width=160,
                height=60,
                font=('Arial', 24),
                radius=18,
            )
            delete_button.pack(side='right', padx=10)

        total_label.pack(pady=20)

        Button(
            self.root,
            text="Proceed to Payment",
            command=self.show_payment,
            width=320,
            height=80,
            font=('Arial', 32),
            radius=25,
        ).pack(pady=20)

    def show_payment(self):
        self.clear_screen()

        Button(
            self.root,
            text="< Back",
            command=self.show_cart,
            width=160,
            height=60,
            font=('Arial', 24),
            radius=20,
        ).pack(anchor='nw', padx=10, pady=10)

        tk.Label(self.root, text="Choose Payment Method", font=('Arial', 48), fg='black', bg='white').pack(pady=40)

        cash_icon = self.get_action_image("Cash", target_dim=90)
        Button(
            self.root,
            text="Cash",
            command=self.show_order_number,
            width=320,
            height=90,
            font=('Arial', 40),
            radius=30,
            image=cash_icon,
        ).pack(pady=20)

        card_icon = self.get_action_image("Card", target_dim=90)
        Button(
            self.root,
            text="Card",
            command=self.show_order_number,
            width=320,
            height=90,
            font=('Arial', 40),
            radius=30,
            image=card_icon,
        ).pack(pady=20)

    def show_order_number(self):
        self.clear_screen()
        order_number = self._generate_order_number()

        tk.Label(self.root, text="Your Order Number:", font=('Arial', 48), fg='black', bg='white').pack(pady=50)
        tk.Label(self.root, text=f"#{order_number}", font=('Arial', 80), fg='black', bg='white').pack(pady=30)

        Button(
            self.root,
            text="Back to Home",
            command=self.reset,
            width=260,
            height=80,
            font=('Arial', 32),
            radius=25,
        ).pack(pady=20)

    def reset(self):
        # Tear down the window so an external launcher can reopen a fresh session.
        self.root.destroy()

    def _generate_order_number(self) -> int:
        # Increment a simple counter to keep pickup numbers unique per run.
        value = self.order_number_counter
        self.order_number_counter += 1
        return value


# Entry point: instantiate Tk and launch the high-fidelity kiosk UI.
# Running the module standalone is perfect for visual regressions.
if __name__ == '__main__':
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()
