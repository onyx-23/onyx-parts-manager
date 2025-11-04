# Onyx Parts Manager Installer Script with Update Support

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"

# Define constants
!define PRODUCT_NAME "Onyx Parts Manager"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Onyx Industries"
!define PRODUCT_WEB_SITE "https://github.com/onyx-23/onyx-parts-manager"
!define UPDATE_URL "https://api.github.com/repos/onyx-23/onyx-parts-manager/releases/latest"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\OnxPartsManager.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

# General settings
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "OnxPartsManager-Setup-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES64\Onyx Industries\Onyx Parts Manager"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
RequestExecutionLevel admin
SetCompressor /SOLID lzma

# Modern UI settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"  # Make sure to create a LICENSE file
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Languages
!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite on
    
    # Main executable and dependencies
    File /r "dist\Onyx Parts Manager\*.*"
    
    # Create AppData directories for user data
    CreateDirectory "$LOCALAPPDATA\OnyxIndustries\PartsManager\data"
    CreateDirectory "$LOCALAPPDATA\OnyxIndustries\PartsManager\data\datasheets"
    
    # Copy database file to AppData
    SetOutPath "$LOCALAPPDATA\OnyxIndustries\PartsManager\data"
    File "data\parts.db"
    
    # Create updates directory in install location
    SetOutPath "$INSTDIR"
    CreateDirectory "$INSTDIR\updates"
    
    # Environment file template
    File /oname=template.env "template.env"
    
    # Create version file for update checks
    FileOpen $0 "$INSTDIR\version.txt" w
    FileWrite $0 "${PRODUCT_VERSION}"
    FileClose $0
    
    # Create updater script
    FileOpen $0 "$INSTDIR\check_updates.ps1" w
    FileWrite $0 '$latestRelease = Invoke-RestMethod -Uri "${UPDATE_URL}"$\r$\n'
    FileWrite $0 '$currentVersion = Get-Content "$PSScriptRoot\version.txt"$\r$\n'
    FileWrite $0 'if ($latestRelease.tag_name -ne $currentVersion) {$\r$\n'
    FileWrite $0 '    $choice = [System.Windows.Forms.MessageBox]::Show("A new version is available. Would you like to download it?", "Update Available", "YesNo", "Question")$\r$\n'
    FileWrite $0 '    if ($choice -eq "Yes") {$\r$\n'
    FileWrite $0 '        Start-Process $latestRelease.assets[0].browser_download_url$\r$\n'
    FileWrite $0 '    }$\r$\n'
    FileWrite $0 '}$\r$\n'
    FileClose $0
    
    # Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\Onyx Parts Manager.exe"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Onyx Parts Manager.exe"
    
    # Registry entries
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Onyx Parts Manager.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Onyx Parts Manager.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    
    # Add update check to startup
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}UpdateCheck" "powershell.exe -ExecutionPolicy Bypass -File $\"$INSTDIR\check_updates.ps1$\""
SectionEnd

Section -Post
    WriteUninstaller "$INSTDIR\uninst.exe"
SectionEnd

# Uninstaller
Section Uninstall
    # Remove update check from startup
    DeleteRegValue HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}UpdateCheck"
    
    # Remove files and directories
    Delete "$INSTDIR\uninst.exe"
    Delete "$INSTDIR\Onyx Parts Manager.exe"
    Delete "$INSTDIR\template.env"
    Delete "$INSTDIR\version.txt"
    Delete "$INSTDIR\check_updates.ps1"
    
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
    RMDir /r "$INSTDIR\updates"
    RMDir /r "$INSTDIR\_internal"
    RMDir "$INSTDIR"
    
    # Ask user if they want to remove user data
    MessageBox MB_YESNO "Do you want to remove all user data (database and datasheets)?" IDNO skip_data_removal
    RMDir /r "$LOCALAPPDATA\OnyxIndustries\PartsManager"
    skip_data_removal:
    
    # Remove registry entries
    DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd

Function .onInit
    # Check if already installed
    ReadRegStr $R0 HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
    ${If} $R0 != ""
        MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "An installation of ${PRODUCT_NAME} is already present. $\n$\nClick OK to remove it first." IDOK uninst
        Abort
        
    uninst:
        ExecWait '$R0'
    ${EndIf}
FunctionEnd