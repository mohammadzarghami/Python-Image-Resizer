import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QLineEdit, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QIcon, QFont
from PIL import Image

# Increase maximum image pixel limit
Image.MAX_IMAGE_PIXELS = None

class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()

        # Load translations
        self.load_translations()

        self.setWindowTitle(self.translations["title"])
        self.setGeometry(100, 100, 500, 600)

        # Set modern appearance
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: white;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #88C0D0;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QComboBox {
                background-color: #3B4252;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #4C566A;
                padding: 5px;
                font-size: 14px;
                color: white;
            }
        """)

        # Main vertical layout
        self.layout = QVBoxLayout()

        # Create a translucent window frame
        self.setWindowOpacity(0.95)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(1000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(0.95)
        self.fade_in_animation.start()

        # Label to display file size
        self.file_size_label = QLabel(self.translations["file_size"], self)
        self.layout.addWidget(self.file_size_label)

        # Create ScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_content)

        self.scroll_area.setWidget(self.scroll_area_content)
        self.layout.addWidget(self.scroll_area)

        # Select image button
        self.select_button = QPushButton(self.translations["select_image"], self)
        self.select_button.clicked.connect(self.select_image)
        self.layout.addWidget(self.select_button)

        # Standard dimensions
        self.standard_dimensions = {
            "640x480": (640, 480),
            "800x600": (800, 600),
            "1024x768": (1024, 768),
            "1280x720": (1280, 720),
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3840x2160": (3840, 2160)
        }

        # Standard dimension selection
        self.standard_combo = QComboBox(self)
        self.standard_combo.addItem(self.translations["select_standard_dimension"])
        for key in self.standard_dimensions.keys():
            self.standard_combo.addItem(key)
        self.standard_combo.currentIndexChanged.connect(self.update_image_info)
        self.scroll_area_layout.addWidget(QLabel(self.translations["standard_dimension"], self))
        self.scroll_area_layout.addWidget(self.standard_combo)

        # Custom dimensions
        self.custom_width = QLineEdit(self)
        self.custom_height = QLineEdit(self)
        self.scroll_area_layout.addWidget(QLabel(self.translations["width"], self))
        self.scroll_area_layout.addWidget(self.custom_width)
        self.scroll_area_layout.addWidget(QLabel(self.translations["height"], self))
        self.scroll_area_layout.addWidget(self.custom_height)

        # Suggested dimensions
        self.suggested_combo = QComboBox(self)
        self.suggested_combo.addItem(self.translations["select_suggested_dimension"])
        self.scroll_area_layout.addWidget(QLabel(self.translations["suggested_dimension"], self))
        self.scroll_area_layout.addWidget(self.suggested_combo)
        self.suggested_combo.currentIndexChanged.connect(self.update_image_info)

        # Resize button
        self.resize_button = QPushButton(self.translations["resize"], self)
        self.resize_button.clicked.connect(self.resize_image)
        self.layout.addWidget(self.resize_button)

        # Label to display new size and reduction percentage
        self.size_info_label = QLabel("", self)
        self.layout.addWidget(self.size_info_label)

        # Language selection menu
        self.language_combo = QComboBox(self)
        self.language_combo.addItem("English")
        self.language_combo.addItem("فارسی")
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.layout.addWidget(self.language_combo)

        # Add layout to the main window
        self.setLayout(self.layout)

        self.image_path = None
        self.original_file_size = 0

    def select_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, self.translations["select_image"], "", "Image files (*.jpg *.jpeg *.png *.gif)")
        if self.image_path:
            self.original_file_size = os.path.getsize(self.image_path)
            self.file_size_label.setText(f"{self.translations['file_size']}: {self.format_size(self.original_file_size)}")
            self.update_suggested_dimensions()

    def format_size(self, size):
        """Format size to KB, MB, GB."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def update_suggested_dimensions(self):
        """Update suggested dimensions based on original dimensions."""
        img = Image.open(self.image_path)
        original_width, original_height = img.size
        self.suggested_combo.clear()
        self.suggested_combo.addItem(self.translations["select_suggested_dimension"])
        for i in range(1, 9):
            width = original_width // i
            height = original_height // i
            self.suggested_combo.addItem(f"{width}x{height}")

    def update_image_info(self):
        """Update image information based on selected dimensions."""
        if self.image_path:
            img = Image.open(self.image_path)
            original_width, original_height = img.size

            # Determine dimensions based on user selection
            if self.standard_combo.currentText() != self.translations["select_standard_dimension"]:
                width, height = self.standard_dimensions[self.standard_combo.currentText()]
            else:
                suggestion = self.suggested_combo.currentText()
                if suggestion != self.translations["select_suggested_dimension"]:
                    if 'x' not in suggestion:
                        return
                    width, height = map(int, suggestion.split('x'))
                else:
                    try:
                        width = int(self.custom_width.text())
                        height = int(self.custom_height.text())
                    except ValueError:
                        return

            new_file_size = (self.original_file_size * (width * height)) / (original_width * original_height)

            reduction_percentage = ((self.original_file_size - new_file_size) / self.original_file_size) * 100 if self.original_file_size > 0 else 0

            jpg_estimated_size = new_file_size * 0.75
            png_estimated_size = new_file_size * 1.5

            self.size_info_label.setText(
                f"{self.translations['new_size']}: {self.format_size(new_file_size)}\n"
                f"{self.translations['size_reduction']}: {reduction_percentage:.2f}%\n"
                f"{self.translations['size_jpg']}: {self.format_size(jpg_estimated_size)}\n"
                f"{self.translations['size_png']}: {self.format_size(png_estimated_size)}"
            )

    def resize_image(self):
        img = Image.open(self.image_path)
        original_width, original_height = img.size

        if self.standard_combo.currentText() != self.translations["select_standard_dimension"]:
            width, height = self.standard_dimensions[self.standard_combo.currentText()]
        else:
            suggestion = self.suggested_combo.currentText()
            if suggestion != self.translations["select_suggested_dimension"]:
                if 'x' not in suggestion:
                    return
                width, height = map(int, suggestion.split('x'))
            else:
                try:
                    width = int(self.custom_width.text())
                    height = int(self.custom_height.text())
                except ValueError:
                    return

        resized_image = img.resize((width, height), Image.ANTIALIAS)
        resized_image.save(self.image_path)

        QMessageBox.information(self, self.translations["success"], self.translations["image_resized"])

    def change_language(self):
        selected_language = self.language_combo.currentText()
        if selected_language == "English":
            self.load_translations("english.json")
        elif selected_language == "فارسی":
            self.load_translations("persian.json")

    def load_translations(self, language_file="english.json"):
        """Load translations from a JSON file."""
        try:
            with open(language_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            self.translations = {
                "title": "Image Resizer",
                "select_image": "Select Image",
                "file_size": "File Size",
                "select_standard_dimension": "Select Standard Dimension",
                "standard_dimension": "Standard Dimension:",
                "width": "Width:",
                "height": "Height:",
                "suggested_dimension": "Suggested Dimension:",
                "select_suggested_dimension": "Select Suggested Dimension",
                "new_size": "New Size",
                "size_reduction": "Size Reduction Percentage",
                "size_jpg": "Estimated Size for JPG",
                "size_png": "Estimated Size for PNG",
                "resize": "Resize Image",
                "success": "Success",
                "image_resized": "Image resized successfully!"
            }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizer()
    window.show()
    sys.exit(app.exec_())
