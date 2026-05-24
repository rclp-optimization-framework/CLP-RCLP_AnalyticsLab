param(
  [string]$BackendUrl = 'http://localhost:8000',
  [string]$FrontendUrl = 'http://localhost:3000'
)

$errors = @()

try {
  $backendPing = Invoke-RestMethod -Uri "$BackendUrl/ping" -Method Get -TimeoutSec 10
  if ($backendPing.message -ne 'Conectado correctamente') {
    $errors += 'Backend ping returned an unexpected payload.'
  }
}
catch {
  $errors += "Backend ping failed: $($_.Exception.Message)"
}

try {
  $frontendPage = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 10
  if ($frontendPage.StatusCode -ne 200) {
    $errors += 'Frontend returned a non-200 status code.'
  }
}
catch {
  $errors += "Frontend check failed: $($_.Exception.Message)"
}

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  exit 1
}

Write-Host 'Smoke test passed.'
