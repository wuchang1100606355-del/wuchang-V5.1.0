# 雙螢幕模式打開 UI
# 在兩個瀏覽器視窗中打開，可以分別放在兩個螢幕上

$url = "http://127.0.0.1:8788/"

Write-Host "正在以雙螢幕模式打開 UI..."
Write-Host "URL: $url"

# 打開第一個視窗
Start-Process $url
Start-Sleep -Seconds 1

# 打開第二個視窗
Start-Process $url

Write-Host "已打開兩個瀏覽器視窗"
Write-Host "提示：可以將兩個視窗分別拖到兩個螢幕上"
