import sys
import json
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt


# Load all config values from configs.json
def load_config():
    with open("./data/configs.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_product_config_path():
    return load_config()["product_config_path"]


# Load full product objects
def load_products():
    product_config_path = get_product_config_path()
    with open(product_config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def DCA_deactivate_all_product():
    config = load_config()
    url = f"http://{config['product_service_ip']}:{config['product_service_port']}/product/deactivate"
    try:
        response = requests.post(url)
        return True, f"All products deactivated successfully! {response.text}"
    except Exception as e:
        return False, f"Failed to deactivate products: {e}"

# Send selected product to API endpoint

def DCA_activate_product(product):
    config = load_config()
    url = f"http://{config['product_service_ip']}:{config['product_service_port']}/product/{product}/activate"
    try:
        response = requests.post(url)
        response.raise_for_status()
        return True, f"Product '{product}' activated successfully!"
    except Exception as e:
        return False, f"Failed to send product: {e}"


def notify_capture_service(product, view_id):
    config = load_config()
    url = f"http://{config['capture_service_ip']}:{config['capture_service_port']}/api/capture/set-product-id/{product}/{view_id}"
    try:
        response = requests.post(url)
        response.raise_for_status()
        return True, "Capture service notified successfully!"
    except Exception as e:
        return False, f"Failed to notify capture service: {e}"

class ProductApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Selector")
        self.setGeometry(100, 100, 300, 150)
        self.setWindowIcon(QIcon("imgs/logo.png"))
        self.products = load_products()  # List of dicts
        self.product_name_id_map = [(p["product_name"], p["product_id"]) for p in self.products]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add deephawk-logo.png at the top
        top_logo_label = QLabel()
        top_logo_pixmap = QPixmap("imgs/deephawk-logo.png")
        if not top_logo_pixmap.isNull():
            top_logo_label.setPixmap(top_logo_pixmap.scaledToHeight(60))
        layout.addWidget(top_logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        label = QLabel("Select a product:")
        layout.addWidget(label)

        self.combobox = QComboBox()
        for name, _id in self.product_name_id_map:
            self.combobox.addItem(name, _id)
        self.combobox.currentIndexChanged.connect(self.on_product_changed)
        layout.addWidget(self.combobox)

        # View dropdown
        self.view_combobox = QComboBox()
        layout.addWidget(self.view_combobox)
        self.update_views_dropdown()  # Initialize views for first product

        # Add refresh button
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.reload_products)
        layout.addWidget(self.refresh_button)

        self.button = QPushButton("Change Product")
        self.button.clicked.connect(self.on_send)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def reload_products(self):
        self.products = load_products()
        self.product_name_id_map = [(p["product_name"], p["product_id"]) for p in self.products]
        self.combobox.clear()
        for name, _id in self.product_name_id_map:
            self.combobox.addItem(name, _id)
        self.update_views_dropdown()

    def on_product_changed(self, idx):
        self.update_views_dropdown()

    def update_views_dropdown(self):
        idx = self.combobox.currentIndex()
        self.view_combobox.clear()
        if idx < 0 or idx >= len(self.products):
            return
        product = self.products[idx]
        views = product.get("views", [])
        for view in views:
            view_name = view.get("view_name", view.get("view_id", ""))
            view_id = view.get("view_id", "")
            self.view_combobox.addItem(view_name, view_id)

    def on_send(self):
        idx = self.combobox.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "No selection", "Please select a product.")
            return
        product_id = self.combobox.itemData(idx)
        if not product_id:
            QMessageBox.warning(self, "No selection", "Please select a product.")
            return
        view_idx = self.view_combobox.currentIndex()
        if view_idx < 0:
            QMessageBox.warning(self, "No view", "Please select a view.")
            return
        view_id = self.view_combobox.itemData(view_idx)
        if not view_id:
            QMessageBox.warning(self, "No view", "Please select a view.")
            return
        success_dca_deactivate, message_dca_deactivate = DCA_deactivate_all_product()
        success_dca_activate, message_dca_activate = DCA_activate_product(product_id)
        # Send both product_id and view_id to notify_capture_service
        success_capture, message_capture = notify_capture_service(product_id, view_id)
        if success_dca_deactivate and success_dca_activate and success_capture:
            QMessageBox.information(self, "Success", "All operations completed successfully: \n " +
                                    message_dca_deactivate + "\n" + message_dca_activate + "\n" + message_capture)
        else:
            QMessageBox.critical(self, "Error", message_dca_deactivate + "\n" + message_dca_activate + "\n" + message_capture)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductApp()
    window.show()
    sys.exit(app.exec())
