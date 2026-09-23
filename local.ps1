[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [ValidateSet("doctor", "dev", "parity", "test", "seed", "reset", "smoke", "logs", "status", "down")]
  [string]$Command = "status",
  [ValidateSet("demo")]
  [string]$Profile = "demo"
)

$ErrorActionPreference = "Stop"
$projectId = "ai-website-cloner"
$root = $PSScriptRoot
$devUrl = "http://ai-website-cloner.localhost:3101"
$parityUrl = "http://ai-website-cloner.localhost:3100"

function Invoke-Compose {
  param([string[]]$Arguments, [ValidateSet("dev", "parity")][string]$Mode = "parity")
  $overlay = if ($Mode -eq "dev") { "compose.dev.yaml" } else { "compose.parity.yaml" }
  & docker compose --project-name "$projectId-$Mode" -f "$root\compose.yaml" -f "$root\$overlay" @Arguments
  if ($LASTEXITCODE -ne 0) { throw "docker compose failed with exit code $LASTEXITCODE" }
}

function Wait-Healthy {
  param([string]$Mode, [string]$Url)
  $deadline = (Get-Date).AddMinutes(3)
  do {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 4
      if ($response.StatusCode -eq 200) { return }
    } catch {}
    Start-Sleep -Seconds 2
  } while ((Get-Date) -lt $deadline)
  Invoke-Compose -Mode $Mode -Arguments @("ps")
  throw "Readiness timeout for $Url"
}

Write-Host "PROJECT_ID=$projectId TARGET_ENV=local MODE=$Command PROFILE=$Profile"

switch ($Command) {
  "doctor" {
    & docker version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not ready. Start it and retry ./local.ps1 doctor." }
    & docker compose version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose v2 is unavailable." }
    $nodeMajor = [int]((node --version).TrimStart("v").Split(".")[0])
    if ($nodeMajor -ne 24) { throw "Node.js 24 is required; found $(node --version)." }
    if (-not (Test-Path -LiteralPath "$root\package-lock.json")) { throw "package-lock.json is required." }
    & docker compose --project-name "$projectId-parity" -f "$root\compose.yaml" -f "$root\compose.parity.yaml" config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Parity Compose configuration is invalid." }
    Write-Host "PASS: Docker, Compose, Node, lockfile and parity configuration are ready."
  }
  "dev" {
    Invoke-Compose -Mode dev -Arguments @("up", "--build", "--detach", "--wait")
    Wait-Healthy -Mode dev -Url $devUrl
    Write-Host "READY MODE=dev BASE_URL=$devUrl"
  }
  "parity" {
    Invoke-Compose -Mode parity -Arguments @("up", "--build", "--detach", "--wait")
    Wait-Healthy -Mode parity -Url $parityUrl
    Write-Host "READY MODE=parity BASE_URL=$parityUrl"
  }
  "test" { & npm run check; if ($LASTEXITCODE -ne 0) { throw "npm run check failed." } }
  "seed" { Write-Host "NOT_APPLICABLE: this static frontend has no mutable local data." }
  "reset" {
    Invoke-Compose -Mode dev -Arguments @("down", "--volumes", "--remove-orphans")
    Invoke-Compose -Mode parity -Arguments @("down", "--volumes", "--remove-orphans")
    Write-Host "RESET: only $projectId local resources were removed."
  }
  "smoke" {
    Wait-Healthy -Mode parity -Url $parityUrl
    $body = (Invoke-WebRequest -Uri $parityUrl -UseBasicParsing -TimeoutSec 10).Content
    if ($body -notmatch "<!DOCTYPE html|<html") { throw "Smoke failed: HTML document not returned." }
    Write-Host "PASS MODE=parity BASE_URL=$parityUrl"
  }
  "logs" { Invoke-Compose -Mode parity -Arguments @("logs", "--tail", "200", "app") }
  "status" {
    Invoke-Compose -Mode dev -Arguments @("ps")
    Invoke-Compose -Mode parity -Arguments @("ps")
  }
  "down" {
    Invoke-Compose -Mode dev -Arguments @("down", "--remove-orphans")
    Invoke-Compose -Mode parity -Arguments @("down", "--remove-orphans")
  }
}
