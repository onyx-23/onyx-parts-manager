import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Union
import logging

class DatasheetManager:
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the DatasheetManager.
        
        Args:
            base_path: Optional base path for datasheets. If None, will use data/datasheets in the project directory
        """
        if base_path is None:
            # Get the application's data directory
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - use AppData for writable storage
                appdata = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
                application_path = appdata / 'OnyxIndustries' / 'PartsManager'
            else:
                # Running as script
                current_file = Path(__file__)
                application_path = current_file.parent.parent.parent
            
            self.base_path = application_path / "data" / "datasheets"
        else:
            self.base_path = Path(base_path)
            
        # Ensure the datasheets directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for datasheet operations."""
        self.logger = logging.getLogger("DatasheetManager")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.base_path / "datasheet_operations.log")
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def get_datasheet_path(self, component_id: str, filename: str) -> Path:
        """
        Get the full path for a datasheet.
        
        Args:
            component_id: The component ID (used for organizing files)
            filename: The original filename of the datasheet
        
        Returns:
            Path object for the datasheet location
        """
        # Create component-specific directory
        component_dir = self.base_path / component_id
        component_dir.mkdir(exist_ok=True)
        return component_dir / filename
    
    def store_datasheet(self, component_id: str, file_path: Union[str, Path]) -> Optional[Path]:
        """
        Store a datasheet file in the managed location.
        
        Args:
            component_id: The component ID for organization
            file_path: Path to the datasheet file to store
        
        Returns:
            Path where the datasheet was stored, or None if failed
            
        Raises:
            ValueError: If the file is not a PDF or component_id is invalid
            FileNotFoundError: If the source file doesn't exist
            OSError: If there's an error copying the file
        """
        try:
            file_path = Path(file_path)
            
            # Validate component_id
            if not component_id or not isinstance(component_id, str):
                raise ValueError(f"Invalid component ID: {component_id}")
            
            # Check file exists
            if not file_path.exists():
                raise FileNotFoundError(f"Source file does not exist: {file_path}")
            
            # Validate file type
            if file_path.suffix.lower() != '.pdf':
                raise ValueError(f"Only PDF files are supported: {file_path}")
            
            # Get destination path and ensure parent directory exists
            dest_path = self.get_datasheet_path(component_id, file_path.name)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file with error handling
            try:
                shutil.copy2(file_path, dest_path)
            except (OSError, shutil.Error) as e:
                raise OSError(f"Failed to copy datasheet: {e}") from e
            
            self.logger.info(f"Stored datasheet for component {component_id}: {dest_path}")
            return dest_path
        
        except (ValueError, FileNotFoundError, OSError) as e:
            self.logger.error(f"Error storing datasheet: {str(e)}")
            raise  # Re-raise the caught exceptions
        except Exception as e:
            self.logger.error(f"Unexpected error storing datasheet: {str(e)}")
            return None
    
    def get_preview_path(self, datasheet_path: Union[str, Path]) -> Optional[Path]:
        """
        Get path for datasheet preview (e.g., first page as PNG).
        Could be extended to generate previews for faster loading.
        
        Args:
            datasheet_path: Path to the datasheet
            
        Returns:
            Path to preview file or None
        """
        try:
            pdf_path = Path(datasheet_path)
            if not pdf_path.exists():
                return None
            
            # For now, just return the PDF path
            # Could be extended to generate and cache PNG previews
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Error getting preview: {str(e)}")
            return None
    
    def sync_with_cloud(self):
        """
        Synchronize local datasheets with cloud storage.
        This is a placeholder for OneDrive integration.
        """
        # OneDrive sync will be implemented here
        pass