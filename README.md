
# Onyx Parts Manager

A desktop application for managing electronic components inventory with supplier integration.

## Release Information

Latest Release: November 3, 2025 (v1.0.0)

Features in this release:
- PyInstaller distribution with all dependencies
- NSIS installer with auto-update capability
- User-specific database storage (AppData)
- Database path resolution for frozen executables
- Full CRUD operations (Create, Read, Update, Delete)
- Search functionality with Enter key support
- Delete confirmation dialogs
- Improved UI styling and column layout
- Fixed column widths with horizontal scrolling
- Datasheet management with View, Change, and Add PDF buttons

Other features:
- Component search by part number, type, and value
- Add new components with datasheet upload
- Delete components with confirmation
- View and manage component datasheets
- Fixed-width columns with horizontal scroll
- Multi-user support (each Windows user gets their own database)
- Dark theme UI

## Installation

Download the installer from the [Releases](https://github.com/onyx-23/onyx-parts-manager/releases) page.

File: `OnxPartsManager-Setup-1.0.0.exe` (57 MB)

After downloading:
1. Run the installer
2. Follow the installation wizard
3. The application will be installed to `C:\Program Files\OnyxIndustries\PartsManager\`
4. Your database and datasheets will be stored in `%LOCALAPPDATA%\OnyxIndustries\PartsManager\`

System requirements:
- Windows 10 or later (64-bit)
- About 100 MB disk space
- No Python installation required (all dependencies are bundled)

## Development Setup

1. Install Python 3.11 or later
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Building the Installer

1. Install requirements:
   ```
   pip install pyinstaller
   ```
2. Install NSIS (Nullsoft Scriptable Install System)
3. Build the distribution:
   ```
   python -m PyInstaller "Onyx Parts Manager.spec"
   ```
4. Create the installer:
   ```
   "C:\Program Files (x86)\NSIS\makensis.exe" installer_with_updates.nsi
   ```

## Running the Application

To run from source:
```
python src/main.py
```

To use the executable:
1. Download the latest release from the releases page
2. Extract the zip file to your desired location
3. Copy `template.env` to `.env` and configure your API keys
4. Run `Onyx Parts Manager.exe`

## Project Structure

- `src/` - Source code
  - `gui/` - GUI components
  - `database/` - Database management
  - `suppliers/` - Supplier API integration
- `data/` - Data storage
  - `datasheets/` - PDF datasheets storage

## Managing Components

Importing from Master Parts File:
1. Ensure your Master Parts File is in Excel format
2. Use the File > Import menu to select your Master Parts File
3. The importer will map columns and import your components

Adding new components:
1. Use the application to add new components to your inventory
2. Store datasheets in the `data/datasheets` directory
3. Component information is stored in a SQLite database at `data/parts.db`

Company part numbers:
- Each component is assigned a unique Onyx Industries part number
- Parts can be searched by company part number or manufacturer part number
- The company part number is displayed in the interface

## Supplier Integration

The application integrates with major electronic component suppliers to fetch real-time pricing and stock information.

To use this feature:
1. Sign up for API access with the suppliers you want to use
2. Add your API keys to the `.env` file
3. The application will automatically fetch prices when viewing components

Note: Each supplier has their own API limits and terms of use. Please review their documentation for details.