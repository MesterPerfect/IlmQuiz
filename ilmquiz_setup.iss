#define MyAppName "IlmQuiz - تحدي المعرفة الإسلامية"
#define MyAppVersion "1.0.2"
#define AppVersion "1.0.2"
#define MyAppPublisher "MesterPerfect"
#define MyAppURL "https://github.com/MesterPerfect/IlmQuiz"
#define MyAppExeName "IlmQuiz.exe"
#define BuildDir "dist\IlmQuiz" 

[Setup]
AppName={#MyAppName}
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppVersion={#AppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
VersionInfoDescription=IlmQuiz - Islamic Knowledge Challenge
AppPublisher={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=copyright, ©2026; {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoOriginalFileName=IlmQuiz_Setup.exe
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
UninstallDisplayName=IlmQuiz - تحدي المعرفة الإسلامية
ArchitecturesAllowed=x64compatible arm64
ArchitecturesInstallIn64BitMode=x64compatible arm64
; Ensure you have an icon file in your project directory
SetupIconFile=assets\icons\app_icon.ico

; 🚨 الإصلاح الأهم: توجيه التثبيت للمسار الصحيح بناءً على الصلاحيات
DefaultDirName={autopf}\{#MyAppName}

DisableProgramGroupPage=yes
DisableDirPage=no

; 🚨 الصلاحيات المنخفضة لضمان التحديث الصامت
PrivilegesRequired=lowest

OutputDir=build_installer
OutputBaseFilename=IlmQuiz_Setup_v{#MyAppVersion}
Compression=lzma
CloseApplications=force
restartApplications=yes
SolidCompression=yes
WizardStyle=modern dark polar
DisableWelcomePage=no
MinVersion=0,6.2

Uninstallable=IsNormalInstall
UsedUserAreasWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
english.AppLNGfile=English
arabic.AppLNGfile=Arabic
english.DeleteSettingsPrompt=Do you want to delete the user data and settings folder?
arabic.DeleteSettingsPrompt=هل تريد حذف مجلد بيانات المستخدم والإعدادات وقاعدة البيانات؟

english.InstallModeTitle=Installation Mode
arabic.InstallModeTitle=نوع التثبيت
english.InstallModeDesc=Please select how you want to install {#MyAppName}.
arabic.InstallModeDesc=الرجاء تحديد كيف تريد تثبيت {#MyAppName}.
english.InstallModeText=Select Normal Installation for a standard setup with shortcuts, or Portable Version to extract files into a standalone folder without modifying your system registry.
arabic.InstallModeText=حدد "تثبيت عادي" لإعداد قياسي مع اختصارات، أو "نسخة محمولة" لاستخراج الملفات في مجلد مستقل دون تعديل سجل النظام الخاص بك.
english.InstallModeNormal=Normal Installation (Recommended)
arabic.InstallModeNormal=تثبيت عادي (مستحسن)
english.InstallModePortable=Portable Version
arabic.InstallModePortable=نسخة محمولة

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Check: IsNormalInstall

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "{#BuildDir}\assets\database\quiz.db"; DestDir: "{userappdata}\{#MyAppName}\database"; Flags: ignoreversion; Check: IsNormalInstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Check: IsNormalInstall
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Check: IsNormalInstall

[UninstallRun]
RunOnceId: "KillIlmQuiz"; Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden

[UninstallDelete]
; 🚨 الإصلاح الثاني: استخدام {app} لضمان حذف المسار الفعلي الذي اختاره المستخدم
Type: filesandordirs; Name: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
var
  InstallModePage: TInputOptionWizardPage;
  IsPortableMode: Boolean;
  UserProvidedDir: String;

function HasCmdLineParam(const ParamName: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
  begin
    if CompareText(ParamStr(I), ParamName) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  IsPortableMode := HasCmdLineParam('/PORTABLE');
  UserProvidedDir := ExpandConstant('{param:DIR}');
  Result := True;
end;

function GetDefaultDirName(Param: String): String;
begin
  if IsPortableMode then
    Result := ExpandConstant('{src}\{#MyAppName}_Portable')
  else
    // 🚨 توحيد المسار هنا ليتوافق مع autopf
    Result := ExpandConstant('{autopf}\{#MyAppName}');
end;

function IsNormalInstall: Boolean;
begin
  Result := not IsPortableMode;
end;

function IsPortableInstall: Boolean;
begin
  Result := IsPortableMode;
end;

procedure DeleteUserDataFolder();
begin
  DelTree(ExpandConstant('{userappdata}\{#MyAppName}'), True, True, True);
end;

procedure InitializeWizard;
begin
  InstallModePage := CreateInputOptionPage(wpWelcome,
    CustomMessage('InstallModeTitle'), 
    CustomMessage('InstallModeDesc'),
    CustomMessage('InstallModeText'),
    True, False);

  InstallModePage.Add(CustomMessage('InstallModeNormal'));
  InstallModePage.Add(CustomMessage('InstallModePortable'));

  if IsPortableMode then
  begin
    InstallModePage.Values[0] := False;
    InstallModePage.Values[1] := True;
  end
  else
  begin
    InstallModePage.Values[0] := True;
    InstallModePage.Values[1] := False;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ExpectedNormalDir, ExpectedPortableDir: String;
begin
  if CurPageID = InstallModePage.ID then
  begin
    // 🚨 توحيد المسار هنا أيضاً
    ExpectedNormalDir := ExpandConstant('{autopf}\{#MyAppName}');
    ExpectedPortableDir := ExpandConstant('{src}\{#MyAppName}_Portable');

    if (UserProvidedDir = '') and
       ((CompareText(WizardForm.DirEdit.Text, ExpectedNormalDir) = 0) or
        (CompareText(WizardForm.DirEdit.Text, ExpectedPortableDir) = 0)) then
    begin
      IsPortableMode := InstallModePage.Values[1];
      if IsPortableMode then
        WizardForm.DirEdit.Text := ExpectedPortableDir
      else
        WizardForm.DirEdit.Text := ExpectedNormalDir;
    end
    else
    begin
      IsPortableMode := InstallModePage.Values[1];
    end;
  end;
  Result := True;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if ((PageID = wpSelectProgramGroup) or (PageID = wpSelectTasks)) and IsPortableMode then
    Result := True
  else
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if IsPortableInstall then
    begin
      SaveStringToFile(ExpandConstant('{app}\.portable'), 'This file tells IlmQuiz to run in portable mode.', False);
    end;
  end;
end;

procedure DeinitializeUninstall();
begin
  if MsgBox(
      ExpandConstant('{cm:DeleteSettingsPrompt}') + #13#10 +
      ExpandConstant('{userappdata}\{#MyAppName}'),
      mbConfirmation, MB_YESNO) = IDYES then
  begin
    DeleteUserDataFolder();
  end;
end;
