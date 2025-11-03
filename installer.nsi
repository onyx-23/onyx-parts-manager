# Onyx Parts Manager Installer Script

!define PRODUCT_NAME "Onyx Parts Manager"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "Onyx Industries"
!define PRODUCT_WEB_SITE "https://www.onyxindustries.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\OnxPartsManager.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

SetCompressor lzma
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "OnxPartsManager-Setup.exe"
InstallDir "$PROGRAMFILES\Onyx Industries\Onyx Parts Manager"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
    
    # Main executable and dependencies
    File "dist\Onyx Parts Manager\*.*"
    
    # Create data directories
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\datasheets"
    
    # Environment file template
    File /oname=template.env "template.env"
    
    # Start Menu
    CreateDirectory "$SMPROGRAMS\Onyx Parts Manager"
    CreateShortCut "$SMPROGRAMS\Onyx Parts Manager\Onyx Parts Manager.lnk" "$INSTDIR\Onyx Parts Manager.exe"
    CreateShortCut "$DESKTOP\Onyx Parts Manager.lnk" "$INSTDIR\Onyx Parts Manager.exe"
    
    # Registry entries
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Onyx Parts Manager.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Onyx Parts Manager.exe"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Section -Post
    WriteUninstaller "$INSTDIR\uninst.exe"
SectionEnd

# Uninstaller
Section Uninstall
    Delete "$INSTDIR\uninst.exe"
    Delete "$INSTDIR\Onyx Parts Manager.exe"
    Delete "$INSTDIR\template.env"
    
    Delete "$SMPROGRAMS\Onyx Parts Manager\Onyx Parts Manager.lnk"
    Delete "$DESKTOP\Onyx Parts Manager.lnk"
    
    RMDir "$SMPROGRAMS\Onyx Parts Manager"
    RMDir /r "$INSTDIR\data"
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd