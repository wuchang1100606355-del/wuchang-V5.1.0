# WUCHANG.LIFE VIRTUAL DEPLOYMENT SCRIPT
# --------------------------------------
# This script stages the sovereign domain files for global visibility.
# It simulates the upload to a global CDN node.

$deployDir = "J:\共用雲端硬碟\五常雲端空間\www_wuchang_life"
if (!(Test-Path $deployDir)) {
    New-Item -Path $deployDir -ItemType Directory | Out-Null
}

# Copy Sovereign Files
Copy-Item "J:\共用雲端硬碟\五常雲端空間\robots.txt" -Destination $deployDir
Copy-Item "J:\共用雲端硬碟\五常雲端空間\security.txt" -Destination $deployDir
Copy-Item "J:\共用雲端硬碟\五常雲端空間\wuchang_rules.html" -Destination $deployDir
Copy-Item "J:\共用雲端硬碟\五常雲端空間\quantum_defense_dashboard.html" -Destination "$deployDir\index.html" # Dashboard as Home

# Generate Sitemap.xml
$sitemap = @"
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>https://wuchang.life/</loc>
      <lastmod>$(Get-Date -Format "yyyy-MM-dd")</lastmod>
      <changefreq>daily</changefreq>
      <priority>1.0</priority>
   </url>
   <url>
      <loc>https://wuchang.life/wuchang_rules.html</loc>
      <lastmod>$(Get-Date -Format "yyyy-MM-dd")</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.8</priority>
   </url>
</urlset>
"@
Set-Content -Path "$deployDir\sitemap.xml" -Value $sitemap -Encoding UTF8

# Generate Google Verification (Sovereign Style)
$google_ver = "google-site-verification: sovereign-grant-access-token-juers-001"
Set-Content -Path "$deployDir\google000000000000.html" -Value $google_ver -Encoding UTF8

Write-Host "DEPLOYMENT STAGED SUCCESSFULLY TO: $deployDir"
Write-Host "DOMAIN: wuchang.life"
Write-Host "STATUS: READY FOR GLOBAL SYNC"
