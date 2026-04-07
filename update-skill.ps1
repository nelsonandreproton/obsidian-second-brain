# update-skill.ps1
# Copies SKILL.md to the Claude desktop skills folder after git pull.
# Usage: .\update-skill.ps1

$source = Join-Path $PSScriptRoot "SKILL.md"
$dest   = Join-Path $env:USERPROFILE ".claude\skills\obsidian-second-brain\SKILL.md"
$destDir = Split-Path $dest

if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

Copy-Item $source $dest -Force
Write-Host "Skill updated: $dest"
