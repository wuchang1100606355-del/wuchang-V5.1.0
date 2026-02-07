Param(
  [string]$OutDir = (Join-Path (Get-Location).Path "backups")
)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ts = Get-Date -Format "yyyyMMddHHmmss"
$dbTar = Join-Path $OutDir ("odoo-db-data_" + $ts + ".tgz")
$webTar = Join-Path $OutDir ("odoo-web-data_" + $ts + ".tgz")
$memDir = Join-Path $OutDir ("memory_store_" + $ts)
$volNames = docker volume ls --format '{{.Name}}'
$dbVolume = ($volNames | Where-Object { $_ -match '_odoo-db-data$' } | Select-Object -First 1)
$webVolume = ($volNames | Where-Object { $_ -match '_odoo-web-data$' } | Select-Object -First 1)
if (-not $dbVolume) { $dbVolume = 'odoo-db-data' }
if (-not $webVolume) { $webVolume = 'odoo-web-data' }
$dbFile = Split-Path -Leaf $dbTar
$webFile = Split-Path -Leaf $webTar
$bindBackup = "${OutDir}:/backup"
docker run --rm -v ${dbVolume}:/data -v $bindBackup busybox sh -c "cd /data && tar czf /backup/$dbFile ."
docker run --rm -v ${webVolume}:/data -v $bindBackup busybox sh -c "cd /data && tar czf /backup/$webFile ."
New-Item -ItemType Directory -Force -Path $memDir | Out-Null
try {
  $srcMem = Join-Path (Get-Location).Path "memory_store"
  if (Test-Path $srcMem) {
    robocopy $srcMem $memDir /E /NFL /NDL /NJH /NJS /NP | Out-Null
    $hashPath = Join-Path $memDir "hashes.sha256"
    $files = Get-ChildItem -Path $memDir -Recurse -File -ErrorAction SilentlyContinue
    foreach ($f in $files) {
      try {
        $h = Get-FileHash -Algorithm SHA256 -LiteralPath $f.FullName
        Add-Content -Path $hashPath -Value ($h.Hash.ToLower() + "  " + ($f.FullName.Substring($memDir.Length).TrimStart('\')))
      } catch {}
    }
  }
} catch {}
Write-Output $dbTar
Write-Output $webTar
Write-Output $memDir
