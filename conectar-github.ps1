$repoUrl = "https://github.com/miyerpriasb-svg/erp-oxylive.git"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Git no esta instalado o no esta disponible en PATH."
  Write-Host "Instala Git para Windows y vuelve a ejecutar este archivo."
  Write-Host "Descarga: https://git-scm.com/download/win"
  exit 1
}

if (-not (Test-Path ".git")) {
  git init
}

git branch -M main
git add .
git commit -m "Initial Oxylive ERP web app"

$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
  git remote set-url origin $repoUrl
} else {
  git remote add origin $repoUrl
}

git push -u origin main
