cd C:\jenkins\workspace\resolvusclient\JD\jenkins-windows

RMDIR /S /Q .
DEL /S /Q *.*

if exist .git RMDIR /S /Q .git
git clone git@github.com:champax/resolvusclient.git .

jenkins\windows_build.bat resolvusclient 888 jenkins-windows