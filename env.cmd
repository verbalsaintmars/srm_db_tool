rem
rem build environment
rem
rem TCROOT needs to be forward slashed
set TCROOT=C:/toolchain
set TC_ROOT=%TCROOT:\=/%
rem commented to eliminate win32\bin causing issue on 64-bit Win7
rem set PATH=%TC_ROOT%\win32\make-3.81;%TC_ROOT%\win32\bin;%PATH%;%TC_ROOT%\win32\visualstudio-2003
set PATH=%TC_ROOT%\win32\make-3.81;%PATH%;%TC_ROOT%\win32\visualstudio-2003
set SRC=%cd%
net use \\build-apps.eng.vmware.com\apps /persistent:yes
net use \\build-current.eng.vmware.com\current /persistent:yes
net use \\build-public.eng.vmware.com /persistent:yes
cd /d %SRC%


rem
rem unit test local env
rem
set SRCROOT=%SRC%

rem
rem this command should be the last one, because the bat file doesn't behave good and all comands after it are not executed.
rem You can disable it if you don't want to build SRM installer.
rem
rem "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat"
"c:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\vcvarsall.bat"

set PATHONPATH=C:\Python27\Lib;C:\Python27\DLLs;C:\Source\db-tool
set PATH=%PATH%;%TCROOT%\win32\bin
