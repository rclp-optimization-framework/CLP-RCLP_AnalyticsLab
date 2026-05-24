param(
  [string]$BackendUrl = 'http://localhost:8000'
)

$exampleFiles = @(
  Join-Path $PSScriptRoot '..\docs\examples\battery\battery-example-01.json',
  Join-Path $PSScriptRoot '..\docs\examples\battery\battery-example-02.json'
)

foreach ($file in $exampleFiles) {
  $payload = Get-Content -Raw -Path $file | ConvertFrom-Json
  try {
    $battery = Invoke-RestMethod -Uri "$BackendUrl/bateria/" -Method Post -Body ($payload | ConvertTo-Json -Depth 20) -ContentType 'application/json'
    Write-Host "Created battery $($battery.id) from $(Split-Path $file -Leaf)"

    $result = Invoke-RestMethod -Uri "$BackendUrl/cache/bateria/$($battery.id)" -Method Post -ContentType 'application/json'
    Write-Host "Stored $($result.Count) cache records for battery $($battery.id)"
  }
  catch {
    Write-Error "Failed with $(Split-Path $file -Leaf): $($_.Exception.Message)"
    exit 1
  }
}

Write-Host 'Battery example tests passed.'
