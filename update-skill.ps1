# update-skill.ps1
# Syncs the skill to the Claude Code skills folder after git pull.
# Usage: .\update-skill.ps1

$dest = Join-Path $env:USERPROFILE ".claude\skills\obsidian-second-brain"

# Create destination folders
New-Item -ItemType Directory -Path (Join-Path $dest "assets\templates") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $dest "references")        -Force | Out-Null

# Copy skill definition
Copy-Item (Join-Path $PSScriptRoot "SKILL.md") $dest -Force

# Copy templates
Copy-Item (Join-Path $PSScriptRoot "assets\templates\*.md") (Join-Path $dest "assets\templates") -Force

# Copy settings example
Copy-Item (Join-Path $PSScriptRoot "assets\settings.json.example") (Join-Path $dest "assets") -Force

# Copy references
Copy-Item (Join-Path $PSScriptRoot "references\*.md") (Join-Path $dest "references") -Force

Write-Host "Skill updated: $dest"
Write-Host ""
Write-Host "Hooks (optional):"
Write-Host "  Global:  Copy-Item '$dest\assets\settings.json.example' '$env:USERPROFILE\.claude\settings.json'"
Write-Host "  Project: Copy-Item '$dest\assets\settings.json.example' '.claude\settings.json'"
Write-Host ""
Write-Host "New session required for changes to take effect."
