; Windows setup for +Cynosure. Inno Setup 6.3 or newer (x64compatible).
; Compile with build_installer.ps1, or:
;
;   ISCC /DMyAppVersion=0.1.4 installer.iss
;
; Source is the PyInstaller folder next to this script, ..\dist\Cynosure\,
; from build_app.ps1. Output is ..\dist\Cynosure-Setup-<version>.exe.
; Upload that setup exe to a GitHub Release.
;
; MyAppVersion is major.minor.patch. Pass /DMyAppVersion to override the
; default below. The setup file version is that number plus a trailing .0.
;
; The app was first published as "FP/FA App" (fpfa-setup-0.1.0.exe). AppId
; stays fixed, so this setup upgrades that install in place: it replaces the
; old exe and the old shortcuts with the new ones (see [InstallDelete]).
;
; License. Setup shows the license terms and keeps Next disabled until the
; reader selects "I accept the agreement". It reads the repository's own
; LICENSE file, not a copy, so the page cannot show terms other than the
; ones that govern. The same file is installed beside the app as
; LICENSE.txt, with THIRD-PARTY-NOTICES.txt, so a silent install
; (/SILENT, /VERYSILENT), which skips every wizard page, still delivers the
; terms. app/tests/test_branding.py pins all of this.

#ifndef MyAppVersion
  #define MyAppVersion "0.1.4"
#endif

#define MyAppName "+Cynosure"
; The name without the plus sign, for the exe and the install folder.
#define MyAppFileName "Cynosure"
#define MyAppPublisher "Abraham Borg"
#define MyAppCopyright "Copyright (c) 2026 Abraham Borg"
#define MyAppExeName "Cynosure.exe"
#define MyAppURL "https://github.com/Abe-Borg/fp-fa-content"

[Setup]
; Opening brace is doubled so the installed id is a single-brace value.
; Do not replace this. fpfa-setup-0.1.0.exe already published this id.
AppId={{A8F1C3E2-9B47-4D6A-8E21-0FPFA0100000}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright={#MyAppCopyright}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppFileName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=Cynosure-Setup-{#MyAppVersion}
SetupIconFile=assets\Cynosure.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; The license agreement page. See the note at the top of this file.
LicenseFile=..\..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright={#MyAppCopyright}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoDescription={#MyAppName} Setup

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
; The license page's lead-in, above the terms. It names the license, says in
; one sentence what it allows, and says what the app's output is. This is a
; license surface: a change of license changes it with LICENSE, the README,
; and fpfa/about.py (app/tests/test_branding.py pins them together). Keep it
; ASCII and on one line; %n is Inno Setup's line break.
LicenseLabel3={#MyAppName} is source-available under the PolyForm Shield License 1.0.0. In short: you may use it for any purpose, including commercial work, except to provide a product that competes with {#MyAppName}. It comes as is, without warranty, and its output is a draft for the engineer of record to review. This is a summary; the agreement below governs.%n%nYou must accept the agreement before continuing with the installation.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; An install published under the old name is upgraded in place. Its exe and
; its shortcuts go, so nothing is left pointing at a file that is gone, and
; the runtime folder is replaced whole so no old library lingers.
Type: files; Name: "{app}\fpfa.exe"
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{autoprograms}\FPFA App"
Type: files; Name: "{autodesktop}\FPFA App.lnk"

[Files]
; The entire PyInstaller one-folder output.
Source: "..\dist\Cynosure\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; The license terms, installed beside the app from the repository's LICENSE.
; Named .txt so a double-click opens it in Notepad. The license's Notices
; clause asks that anyone who gets a copy of the software also gets these
; terms and the Required Notice line, and a silent install skips the license
; page, so this copy is how such a recipient gets them.
Source: "..\..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion
; The license texts of everything the app bundles (the Python interpreter,
; every Python package, the WebView2 SDK inside pywebview, and the JavaScript
; packages in the window's page), written by build_app.py through
; third_party_notices.py, which fails the build when a text is missing. If
; the file is absent, ISCC stops with "Source file does not exist".
Source: "..\dist\Cynosure\THIRD-PARTY-NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
