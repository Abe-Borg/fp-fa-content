; Windows setup for the FP/FA desktop app. Inno Setup 6.3 or newer
; (x64compatible). Compile with build_installer.ps1, or:
;
;   ISCC /DMyAppVersion=0.1.1 installer.iss
;
; Source is the PyInstaller folder next to this script, ..\dist\fpfa\,
; from build_app.ps1. Output is ..\dist\fpfa-setup-<version>.exe.
; Upload that setup exe to a GitHub Release.
;
; MyAppVersion is major.minor.patch. Pass /DMyAppVersion to override the
; default below. The setup file version is that number plus a trailing .0.
; AppId stays fixed so a later setup upgrades the published 0.1.0 install.

#ifndef MyAppVersion
  #define MyAppVersion "0.1.1"
#endif

#define MyAppName "FP/FA App"
; Shortcut and Start Menu folder names are path segments. A slash in
; "FP/FA App" would create an FP folder and nest the shortcut under it.
#define MyAppShortcut "FPFA App"
#define MyAppPublisher "Ehvert"
#define MyAppExeName "fpfa.exe"

[Setup]
; Opening brace is doubled so the installed id is a single-brace value.
; Do not replace this. fpfa-setup-0.1.0.exe already published this id.
AppId={{A8F1C3E2-9B47-4D6A-8E21-0FPFA0100000}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\FPFA
DefaultGroupName={#MyAppShortcut}
OutputDir=..\dist
OutputBaseFilename=fpfa-setup-{#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoDescription={#MyAppName} Setup

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\fpfa\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppShortcut}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppShortcut}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
