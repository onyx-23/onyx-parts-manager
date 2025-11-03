from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
import fitz  # PyMuPDF for PDF preview
import os
from pathlib import Path
import shutil
from datetime import datetime

class DatasheetViewer(QDialog):
    def __init__(self, datasheet_path, parent=None):
        super().__init__(parent)
        self.datasheet_path = Path(datasheet_path)
        self.component_id = self.datasheet_path.parent.name  # Assuming parent dir is component_id
        self.setAcceptDrops(True)  # Enable drag and drop
        self.init_ui()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for files being dragged into the viewer"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                event.acceptProposedAction()
                
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for files being dropped into the viewer"""
        urls = event.mimeData().urls()
        pdf_files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith('.pdf')]
        
        if not pdf_files:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please drop a PDF file only."
            )
            return
            
        pdf_path = pdf_files[0]  # Take only the first PDF if multiple files are dropped
        
        if not os.path.exists(pdf_path):
            QMessageBox.critical(
                self,
                "Error",
                f"File not found: {pdf_path}"
            )
            return
            
        reply = QMessageBox.question(
            self,
            "Replace Datasheet",
            "Do you want to replace the current datasheet with the new one?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Create backup of current file
                backup_dir = self.datasheet_path.parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"{timestamp}_{self.datasheet_path.name}"
                
                # Backup current file if it exists
                if self.datasheet_path.exists():
                    shutil.copy2(self.datasheet_path, backup_path)
                
                # Copy new file
                shutil.copy2(pdf_path, self.datasheet_path)
                
                # Reload the preview
                self.load_preview()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Datasheet replaced successfully.\nBackup saved in: {backup_dir.name}"
                )
                
            except OSError as e:
                QMessageBox.critical(
                    self,
                    "File Error",
                    f"Failed to replace datasheet: {str(e)}\n\n"
                    "Please check that you have permissions to modify the file "
                    "and that it is not open in another program."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An unexpected error occurred: {str(e)}"
                )
        
    def init_ui(self):
        self.setWindowTitle("Datasheet Viewer")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.open_btn = QPushButton("Open in Default App")
        self.open_btn.clicked.connect(self.open_in_default_app)
        toolbar.addWidget(self.open_btn)
        
        self.save_btn = QPushButton("Save Copy")
        self.save_btn.clicked.connect(self.save_copy)
        toolbar.addWidget(self.save_btn)
        
        layout.addLayout(toolbar)
        
        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)
        
        self.load_preview()
    
    def load_preview(self):
        """Load first page of PDF as preview"""
        try:
            doc = fitz.open(self.datasheet_path)
            first_page = doc[0]
            
            # Render to PNG
            pix = first_page.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Display in label
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            
            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.preview_label.setText(f"Preview not available\n{str(e)}")
    
    def open_in_default_app(self):
        """Open the PDF in the system's default PDF viewer"""
        import subprocess
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(self.datasheet_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', self.datasheet_path])
        else:  # Linux
            subprocess.run(['xdg-open', self.datasheet_path])
    
    def save_copy(self):
        """Save a copy of the datasheet to a user-selected location"""
        file_name = os.path.basename(self.datasheet_path)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Datasheet Copy",
            file_name,
            "PDF Files (*.pdf)"
        )
        
        if save_path:
            import shutil
            try:
                shutil.copy2(self.datasheet_path, save_path)
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save copy: {str(e)}"
                )