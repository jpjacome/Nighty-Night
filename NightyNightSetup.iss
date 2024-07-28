#define MyAppName "Nighty Night"
#define MyAppVersion "1.0"
#define MyAppPublisher "Babaloniq"
#define MyAppExeName "nighty-night.exe"

[Setup]
AppId={{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userpf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=NightyNightSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\background.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\background2.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\moons.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\animation.gif"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\settings-icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\settings.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Set full control permissions for the current user on the installation directory
    Exec(ExpandConstant('{sys}\icacls.exe'), ExpandConstant('"{app}" /grant:r "{username}:(OI)(CI)F" /T'), '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;