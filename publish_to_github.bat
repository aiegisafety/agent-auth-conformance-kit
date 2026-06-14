@echo off
setlocal
cd /d "%~dp0"
echo ================================================================
echo  Publishing AACP kit to:
echo    https://github.com/aiegisafety/agent-auth-conformance-kit  (PUBLIC)
echo ================================================================
echo.

where gh >nul 2>nul
if %errorlevel%==0 goto use_gh

echo GitHub CLI (gh) not found - using git + Git Credential Manager.
echo.
echo STEP 1: Create an EMPTY public repo first (do NOT add README/license):
echo    https://github.com/new
echo    Owner: aiegisafety   Name: agent-auth-conformance-kit   Visibility: Public
echo.
echo When the empty repo exists, press any key to push...
pause >nul
git init -b main 2>nul || (git init && git branch -M main)
git add .
git commit -m "AACP v0.1: agent authorization conformance kit (L2 reference)"
git remote remove origin 2>nul
git remote add origin https://github.com/aiegisafety/agent-auth-conformance-kit.git
git push -u origin main
goto done

:use_gh
echo Using GitHub CLI...
git init -b main 2>nul || (git init && git branch -M main)
git add .
git commit -m "AACP v0.1: agent authorization conformance kit (L2 reference)"
gh repo create aiegisafety/agent-auth-conformance-kit --public --source . --remote origin --push

:done
echo.
echo Done. First-time push opens a browser - click "Authorize git-credential-manager".
pause
