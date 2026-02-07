Param(
  [Parameter(Mandatory=$false)][string]$DbTar,
  [Parameter(Mandatory=$false)][string]$WebTar
)
if ($DbTar) {
  $dir = Split-Path -Parent $DbTar
  $file = Split-Path -Leaf $DbTar
  docker run --rm -v odoo-db-data:/data -v "$dir":/backup busybox sh -c "rm -rf /data/* && tar xzf /backup/$file -C /data"
}
if ($WebTar) {
  $dir = Split-Path -Parent $WebTar
  $file = Split-Path -Leaf $WebTar
  docker run --rm -v odoo-web-data:/data -v "$dir":/backup busybox sh -c "rm -rf /data/* && tar xzf /backup/$file -C /data"
}
