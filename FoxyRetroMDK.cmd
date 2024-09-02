@ECHO OFF
REM ## Get MC Version ##
if "%mc_ver%" EQU "" (
	set /p mc_ver="Enter Minecraft Version [1.1 - 1.6.4]: "
)
REM ## Remove Quotes & Spaces ##
set mc_ver=%mc_ver:"=%
set mc_ver=%mc_ver: =%
REM ## Run Main Script ##
powershell -ExecutionPolicy Bypass -File "%~dp0\FoxyRetroMDK.ps1" -mc_ver "%mc_ver%"
