@echo off
REM Script to untrack server configuration files from git
REM This keeps the files locally but removes them from git tracking

echo ================================================
echo Untracking Server Configuration Files from Git
echo ================================================
echo.
echo This will:
echo   1. Keep the files on your local system
echo   2. Remove them from git tracking
echo   3. Prevent them from being pushed to GitHub
echo.
echo Files to untrack:
echo   - .htaccess
echo   - passenger_wsgi.py
echo.

set /p confirm="Do you want to continue? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo Untracking .htaccess...
    git rm --cached .htaccess 2>nul || echo   .htaccess not tracked or already removed
    
    echo Untracking passenger_wsgi.py...
    git rm --cached passenger_wsgi.py 2>nul || echo   passenger_wsgi.py not tracked or already removed
    
    echo.
    echo [SUCCESS] Files untracked successfully!
    echo.
    echo Next steps:
    echo   1. Commit the changes: git commit -m "Untrack server config files"
    echo   2. Push to GitHub: git push
    echo.
    echo Note: The files will remain on your local system and server,
    echo       but won't be tracked or pushed to GitHub anymore.
) else (
    echo.
    echo Operation cancelled.
)

pause
