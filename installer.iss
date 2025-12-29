[Setup]
AppName=EIMS
AppVersion=1.0
DefaultDirName={pf}\EIMS
DefaultGroupName=EIMS
OutputDir=.
OutputBaseFilename=EIMS-Setup
Compression=lzma
SolidCompression=yes

[Files]
// Copy all project files to the installation directory
Source: "c:\Users\snara\OneDrive\Desktop\EMS\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\EIMS"; Filename: "{app}\App.py"
Name: "{userdesktop}\EIMS"; Filename: "{app}\App.py"

[Run]
// Run the program after installation (optional)
Filename: "{app}\App.py"; Description: "Run EIMS"; Flags: postinstall skipifsilent
