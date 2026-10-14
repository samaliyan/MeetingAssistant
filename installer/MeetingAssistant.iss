; The Windows installer (Inno Setup 6). Built by the GitHub workflows after tools/build.py:
;   iscc /DAppVersion=6.33 installer\MeetingAssistant.iss   ->  dist\MeetingAssistant-Setup.exe
;
; - Installs for the current user only (no administrator rights, no security prompt), in
;   %LOCALAPPDATA%\Programs\Meeting Assistant, like most programs that update often.
; - Start menu and desktop shortcuts; an uninstaller in Settings > Apps.
; - An update simply installs over it: the program is closed first, the settings, meetings and models (the Data
;   folder) stay.
; - The first install finds the earlier single-file copy from its desktop shortcut and leaves a note, so the program
;   brings its settings and meetings over on its first start.

#ifndef AppVersion
  #define AppVersion "0.0"
#endif

[Setup]
AppId={{6C1F2B7E-3D4A-4E5B-9F60-7A8B9C0D1E2F}
AppName=Meeting Assistant
AppVersion={#AppVersion}
AppVerName=Meeting Assistant {#AppVersion}
AppPublisher=Meeting Assistant
AppPublisherURL=https://github.com/samaliyan/MeetingAssistant
AppSupportURL=https://github.com/samaliyan/MeetingAssistant/issues
DefaultDirName={localappdata}\Programs\Meeting Assistant
DefaultGroupName=Meeting Assistant
DisableProgramGroupPage=yes
DisableDirPage=auto
DisableReadyPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=MeetingAssistant-Setup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\MeetingAssistant.exe
UninstallDisplayName=Meeting Assistant
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=force
RestartApplications=no
UsedUserAreasWarning=no
VersionInfoVersion={#AppVersion}

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[InstallDelete]
; the program files of the version before (never the Data folder)
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\MeetingAssistant\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Meeting Assistant"; Filename: "{app}\MeetingAssistant.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Meeting Assistant"; Filename: "{app}\MeetingAssistant.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\MeetingAssistant.exe"; Description: "Start Meeting Assistant now"; Flags: nowait postinstall skipifsilent

[Code]
var
  OldCopy: String;

{ the folder the old desktop shortcut "Meeting Assistant" pointed to, when it was another copy of the program }
function OldCopyFromShortcut(): String;
var
  Shell, Link: Variant;
  Target, Dir: String;
begin
  Result := '';
  if not FileExists(ExpandConstant('{userdesktop}\Meeting Assistant.lnk')) then
    exit;
  try
    Shell := CreateOleObject('WScript.Shell');
    Link := Shell.CreateShortcut(ExpandConstant('{userdesktop}\Meeting Assistant.lnk'));
    Target := Link.TargetPath;
  except
    Target := '';
  end;
  if (Target = '') or (CompareText(ExtractFileName(Target), 'MeetingAssistant.exe') <> 0) then
    exit;
  Dir := ExtractFileDir(Target);
  if (CompareText(Dir, ExpandConstant('{app}')) <> 0) and FileExists(Dir + '\Data\config.json') then
    Result := Dir;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Lines: TArrayOfString;
begin
  if CurStep = ssInstall then
    OldCopy := OldCopyFromShortcut();
  if (CurStep = ssPostInstall) and (OldCopy <> '') and not FileExists(ExpandConstant('{app}\Data\config.json')) then
  begin
    ForceDirectories(ExpandConstant('{app}\Data'));
    SetArrayLength(Lines, 1);
    Lines[0] := OldCopy;
    SaveStringsToUTF8File(ExpandConstant('{app}\Data\.old_portable'), Lines, False);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if (CurUninstallStep = usPostUninstall) and DirExists(ExpandConstant('{app}\Data')) then
    if SuppressibleMsgBox('Also delete your settings, saved meetings and downloaded models?' + #13#10#13#10 +
                          ExpandConstant('{app}\Data') + #13#10#13#10 +
                          'Choose No to keep them (they are used again if you install the program later).',
                          mbConfirmation, MB_YESNO or MB_DEFBUTTON2, IDNO) = IDYES then
      DelTree(ExpandConstant('{app}'), True, True, True);
end;
