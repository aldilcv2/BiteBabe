import sys
import json
import os
import shutil
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, 
                             QFormLayout, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QListWidget, QCheckBox, QGroupBox, QScrollArea)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
from PIL import Image

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # Parent of 'editor' folder
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
PRODUCTS_DIR = os.path.join(ASSETS_DIR, "products")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
TOPPINGS_FILE = os.path.join(DATA_DIR, "toppings.json")
STORE_FILE = os.path.join(DATA_DIR, "store.json")
LOGO_TARGET = os.path.join(ASSETS_DIR, "logo.png")
FAVICON_TARGET = os.path.join(ASSETS_DIR, "favicon.png")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(PRODUCTS_DIR, exist_ok=True)

class BiteBabeAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BiteBabe Editor PRO")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #FFE8F1; }
            QTabWidget::pane { border: 1px solid #FFD6E8; background: white; border-radius: 10px; }
            QTabBar::tab { background: #FFD6E8; color: #3B3B3B; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
            QTabBar::tab:selected { background: #FF5C9E; color: white; }
            QPushButton { background-color: #FF5C9E; color: white; border-radius: 5px; padding: 8px 15px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #ff3385; }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox { padding: 8px; border: 1px solid #FFD6E8; border-radius: 5px; }
            QLabel { color: #3B3B3B; font-weight: 500; }
            QTableWidget { border: 1px solid #FFD6E8; gridline-color: #FFD6E8; }
            QHeaderView::section { background-color: #FFD6E8; padding: 5px; border: none; font-weight: bold; color: #3B3B3B; }
        """)

        self.load_data()
        self.init_ui()

    def load_data(self):
        self.products = self.load_json(PRODUCTS_FILE, [])
        self.toppings = self.load_json(TOPPINGS_FILE, [])
        self.store_config = self.load_json(STORE_FILE, {})

    def load_json(self, filepath, default):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default

    def save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Header
        header = QLabel("BiteBabe Admin Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF5C9E; margin-bottom: 10px;")
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self.create_dashboard_tab(), "Dashboard & Branding")
        self.tabs.addTab(self.create_products_tab(), "Products Manager")
        self.tabs.addTab(self.create_toppings_tab(), "Toppings")

        # Footer removed - save buttons now in each form

    # --- Dashboard Tab ---
    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Store Config
        group = QGroupBox("Store Configuration")
        form = QFormLayout()
        
        self.store_name_edit = QLineEdit(self.store_config.get("name", ""))
        self.store_slogan_edit = QLineEdit(self.store_config.get("slogan", ""))
        self.store_wa_edit = QLineEdit(self.store_config.get("whatsapp", ""))
        
        form.addRow("Store Name:", self.store_name_edit)
        form.addRow("Slogan:", self.store_slogan_edit)
        form.addRow("WhatsApp (62...):", self.store_wa_edit)
        
        btn_layout = QHBoxLayout()
        save_local_btn = QPushButton("💾 Save Local")
        save_local_btn.clicked.connect(self.save_store_config)
        save_push_btn = QPushButton("☁️ Save & Push")
        save_push_btn.clicked.connect(self.save_store_config_and_push)
        save_push_btn.setStyleSheet("background-color: #3B3B3B;")
        btn_layout.addWidget(save_local_btn)
        btn_layout.addWidget(save_push_btn)
        form.addRow("", btn_layout)
        
        group.setLayout(form)
        layout.addWidget(group)

        # Logo Upload
        logo_group = QGroupBox("Branding Assets")
        logo_layout = QVBoxLayout()
        
        self.logo_preview = QLabel("No Logo")
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setStyleSheet("border: 2px dashed #FFD6E8; border-radius: 10px;")
        self.update_logo_preview()
        
        upload_btn = QPushButton("Upload Logo (Auto Resize)")
        upload_btn.clicked.connect(self.upload_logo)
        
        logo_layout.addWidget(self.logo_preview, alignment=Qt.AlignCenter)
        logo_layout.addWidget(upload_btn, alignment=Qt.AlignCenter)
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)
        
        layout.addStretch()
        return tab

    def update_logo_preview(self):
        if os.path.exists(LOGO_TARGET):
            pixmap = QPixmap(LOGO_TARGET)
            self.logo_preview.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_preview.setText("")

    def save_store_config(self):
        self.store_config["name"] = self.store_name_edit.text()
        self.store_config["slogan"] = self.store_slogan_edit.text()
        self.store_config["whatsapp"] = self.store_wa_edit.text()
        self.save_json(STORE_FILE, self.store_config)
        QMessageBox.information(self, "Success", "Store configuration saved locally!")
    
    def save_store_config_and_push(self):
        self.save_store_config()
        self.save_and_push_to_github("Store configuration")

    def upload_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Upload Logo", "", "Images (*.png *.jpg *.jpeg)")
        if not path: return

        try:
            img = Image.open(path).convert("RGBA")
            
            # Create square canvas
            size = 512
            canvas = Image.new("RGBA", (size, size), (255, 232, 241, 255)) # Soft pink bg
            
            # Resize and center
            img.thumbnail((size*0.8, size*0.8), Image.Resampling.LANCZOS)
            x = (size - img.width) // 2
            y = (size - img.height) // 2
            canvas.paste(img, (x, y), img)
            
            canvas.save(LOGO_TARGET, "PNG", optimize=True)
            
            # Favicon
            fav = canvas.copy()
            fav.thumbnail((64, 64), Image.Resampling.LANCZOS)
            fav.save(FAVICON_TARGET, "PNG", optimize=True)
            
            self.update_logo_preview()
            QMessageBox.information(self, "Success", "Logo updated and favicon generated!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # --- Products Tab ---
    def create_products_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left: List
        left_layout = QVBoxLayout()
        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(3)
        self.prod_table.setHorizontalHeaderLabels(["Name", "Price", "Stock"])
        self.prod_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.prod_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.prod_table.itemClicked.connect(self.load_product_details)
        left_layout.addWidget(self.prod_table)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add New")
        add_btn.clicked.connect(self.clear_product_form)
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background-color: #ff4444;")
        del_btn.clicked.connect(self.delete_product)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, stretch=1)

        # Right: Form
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        form = QFormLayout()

        self.p_id = QLineEdit()
        self.p_id.setReadOnly(True)
        self.p_id.setPlaceholderText("Auto-generated")
        
        self.p_name = QLineEdit()
        self.p_price = QDoubleSpinBox()
        self.p_price.setRange(0, 1000000)
        self.p_price.setSingleStep(1000)
        
        self.p_desc = QTextEdit()
        self.p_desc.setMaximumHeight(80)
        
        self.p_stock = QSpinBox()
        self.p_stock.setRange(0, 1000)
        
        self.p_max = QSpinBox()
        self.p_max.setRange(1, 100)
        
        self.p_cat = QLineEdit()
        
        self.p_img_btn = QPushButton("Choose Image")
        self.p_img_btn.clicked.connect(self.upload_product_image)
        self.p_img_label = QLabel("No Image")
        self.p_img_path = ""

        # Toppings Checkboxes
        self.topping_checks = []
        toppings_group = QGroupBox("Available Toppings")
        toppings_layout = QVBoxLayout()
        self.toppings_container = QWidget()
        self.toppings_vbox = QVBoxLayout(self.toppings_container)
        toppings_layout.addWidget(self.toppings_container)
        toppings_group.setLayout(toppings_layout)

        form.addRow("ID:", self.p_id)
        form.addRow("Name:", self.p_name)
        form.addRow("Price:", self.p_price)
        form.addRow("Category:", self.p_cat)
        form.addRow("Stock:", self.p_stock)
        form.addRow("Max Order:", self.p_max)
        form.addRow("Description:", self.p_desc)
        form.addRow("Image:", self.p_img_btn)
        form.addRow("", self.p_img_label)
        
        right_layout.addLayout(form)
        right_layout.addWidget(toppings_group)
        
        btn_layout = QHBoxLayout()
        save_local_btn = QPushButton("💾 Save Local")
        save_local_btn.clicked.connect(self.save_product)
        save_push_btn = QPushButton("☁️ Save & Push")
        save_push_btn.clicked.connect(self.save_product_and_push)
        save_push_btn.setStyleSheet("background-color: #3B3B3B;")
        btn_layout.addWidget(save_local_btn)
        btn_layout.addWidget(save_push_btn)
        right_layout.addLayout(btn_layout)
        right_layout.addStretch()

        layout.addWidget(right_widget, stretch=1)
        
        self.refresh_product_table()
        self.refresh_topping_checks()
        return tab

    def refresh_product_table(self):
        self.prod_table.setRowCount(0)
        for p in self.products:
            row = self.prod_table.rowCount()
            self.prod_table.insertRow(row)
            self.prod_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.prod_table.setItem(row, 1, QTableWidgetItem(str(p['price'])))
            self.prod_table.setItem(row, 2, QTableWidgetItem(str(p['stock'])))
            self.prod_table.item(row, 0).setData(Qt.UserRole, p['id'])

    def refresh_topping_checks(self):
        # Clear existing
        for i in reversed(range(self.toppings_vbox.count())): 
            self.toppings_vbox.itemAt(i).widget().setParent(None)
        
        self.topping_checks = []
        for t in self.toppings:
            cb = QCheckBox(f"{t['name']} (+{t['price']})")
            cb.setProperty("t_id", t['id'])
            self.toppings_vbox.addWidget(cb)
            self.topping_checks.append(cb)

    def load_product_details(self, item):
        row = item.row()
        p_id = self.prod_table.item(row, 0).data(Qt.UserRole)
        product = next((p for p in self.products if p['id'] == p_id), None)
        
        if product:
            self.p_id.setText(product['id'])
            self.p_name.setText(product['name'])
            self.p_price.setValue(product['price'])
            self.p_desc.setText(product.get('description', ''))
            self.p_stock.setValue(product.get('stock', 0))
            self.p_max.setValue(product.get('max_order', 5))
            self.p_cat.setText(product.get('category', ''))
            self.p_img_path = product.get('image', '')
            self.p_img_label.setText(os.path.basename(self.p_img_path) if self.p_img_path else "No Image")
            
            # Set toppings
            p_toppings = product.get('toppings', [])
            for cb in self.topping_checks:
                cb.setChecked(cb.property("t_id") in p_toppings)

    def clear_product_form(self):
        self.p_id.clear()
        self.p_name.clear()
        self.p_price.setValue(0)
        self.p_desc.clear()
        self.p_stock.setValue(10)
        self.p_max.setValue(5)
        self.p_cat.clear()
        self.p_img_path = ""
        self.p_img_label.setText("No Image")
        for cb in self.topping_checks:
            cb.setChecked(False)
        self.prod_table.clearSelection()

    def upload_product_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            filename = f"prod_{int(QApplication.instance().applicationPid())}_{os.path.basename(path)}"
            target = os.path.join(PRODUCTS_DIR, filename)
            
            # Resize and save
            img = Image.open(path)
            img.thumbnail((500, 500))
            img.save(target)
            
            self.p_img_path = f"assets/products/{filename}"
            self.p_img_label.setText(filename)

    def save_product(self):
        p_id = self.p_id.text()
        is_new = not p_id
        
        if is_new:
            import uuid
            p_id = str(uuid.uuid4())
        
        selected_toppings = [cb.property("t_id") for cb in self.topping_checks if cb.isChecked()]
        
        product_data = {
            "id": p_id,
            "name": self.p_name.text(),
            "price": self.p_price.value(),
            "description": self.p_desc.toPlainText(),
            "stock": self.p_stock.value(),
            "max_order": self.p_max.value(),
            "category": self.p_cat.text(),
            "image": self.p_img_path,
            "toppings": selected_toppings
        }
        
        if is_new:
            self.products.append(product_data)
        else:
            for i, p in enumerate(self.products):
                if p['id'] == p_id:
                    self.products[i] = product_data
                    break
        
        self.save_json(PRODUCTS_FILE, self.products)
        self.refresh_product_table()
        self.clear_product_form()
        QMessageBox.information(self, "Success", "Product saved locally!")
    
    def save_product_and_push(self):
        self.save_product()
        self.save_and_push_to_github("Product")

    def delete_product(self):
        row = self.prod_table.currentRow()
        if row < 0: return
        
        p_id = self.prod_table.item(row, 0).data(Qt.UserRole)
        confirm = QMessageBox.question(self, "Confirm", "Delete this product?", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.products = [p for p in self.products if p['id'] != p_id]
            self.save_json(PRODUCTS_FILE, self.products)
            self.refresh_product_table()
            self.clear_product_form()

    # --- Toppings Tab ---
    def create_toppings_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # List
        self.top_list = QListWidget()
        self.top_list.itemClicked.connect(self.load_topping_details)
        layout.addWidget(self.top_list)
        
        # Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form = QFormLayout()
        
        self.t_id = QLineEdit()
        self.t_id.setReadOnly(True)
        self.t_name = QLineEdit()
        self.t_price = QDoubleSpinBox()
        self.t_price.setRange(0, 100000)
        
        form.addRow("ID:", self.t_id)
        form.addRow("Name:", self.t_name)
        form.addRow("Price:", self.t_price)
        
        form_layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("New")
        add_btn.clicked.connect(self.clear_topping_form)
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background-color: #ff4444;")
        del_btn.clicked.connect(self.delete_topping)
        save_local_btn = QPushButton("💾 Save")
        save_local_btn.clicked.connect(self.save_topping)
        save_push_btn = QPushButton("☁️ Save & Push")
        save_push_btn.clicked.connect(self.save_topping_and_push)
        save_push_btn.setStyleSheet("background-color: #3B3B3B;")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(save_local_btn)
        btn_layout.addWidget(save_push_btn)
        
        form_layout.addLayout(btn_layout)
        form_layout.addStretch()
        
        layout.addWidget(form_widget)
        
        self.refresh_topping_list()
        return tab

    def refresh_topping_list(self):
        self.top_list.clear()
        for t in self.toppings:
            self.top_list.addItem(f"{t['name']} - {t['price']}")
            list_item = self.top_list.item(self.top_list.count() - 1)
            list_item.setData(Qt.UserRole, t['id'])
        
        self.refresh_topping_checks() # Update product tab checks too

    def load_topping_details(self, item):
        t_id = item.data(Qt.UserRole)
        topping = next((t for t in self.toppings if t['id'] == t_id), None)
        if topping:
            self.t_id.setText(topping['id'])
            self.t_name.setText(topping['name'])
            self.t_price.setValue(topping['price'])

    def clear_topping_form(self):
        self.t_id.clear()
        self.t_name.clear()
        self.t_price.setValue(0)
        self.top_list.clearSelection()

    def save_topping(self):
        t_id = self.t_id.text()
        is_new = not t_id
        
        if is_new:
            import uuid
            t_id = str(uuid.uuid4())
            
        topping_data = {
            "id": t_id,
            "name": self.t_name.text(),
            "price": self.t_price.value()
        }
        
        if is_new:
            self.toppings.append(topping_data)
        else:
            for i, t in enumerate(self.toppings):
                if t['id'] == t_id:
                    self.toppings[i] = topping_data
                    break
        
        self.save_json(TOPPINGS_FILE, self.toppings)
        self.refresh_topping_list()
        self.clear_topping_form()
        QMessageBox.information(self, "Success", "Topping saved locally!")
    
    def save_topping_and_push(self):
        self.save_topping()
        self.save_and_push_to_github("Topping")

    def delete_topping(self):
        row = self.top_list.currentRow()
        if row < 0: return
        
        t_id = self.top_list.item(row).data(Qt.UserRole)
        self.toppings = [t for t in self.toppings if t['id'] != t_id]
        self.save_json(TOPPINGS_FILE, self.toppings)
        self.refresh_topping_list()
        self.clear_topping_form()

    # --- Git Sync ---
    def save_and_push_to_github(self, item_name):
        """Save changes and push to GitHub"""
        try:
            git_dir = os.path.join(PROJECT_DIR, ".git")
            if not os.path.exists(git_dir):
                QMessageBox.warning(self, "Git Error", "This folder is not a Git repository.\n\nPlease initialize git first with:\ngit init\ngit remote add origin <your-repo-url>")
                return False

            subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"Update {item_name} from BiteBabe Admin"], cwd=PROJECT_DIR, check=True)
            subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True)
            
            QMessageBox.information(self, "Success", f"{item_name} saved locally!\n\n✅ Changes pushed to GitHub successfully!")
            return True
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Sync Error", f"{item_name} saved locally!\n\n❌ Failed to push to GitHub: {str(e)}")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = BiteBabeAdmin()
    window.show()
    sys.exit(app.exec_())
