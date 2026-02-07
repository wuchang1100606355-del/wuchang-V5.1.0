$ErrorActionPreference='Continue'
$t = Get-Date
$log = 'C:\wuchang V5.1.0\wuchang_os\_action_log.txt'
Add-Content -Path $log -Value "[$t] 授權: 管理員通道啟動"
$names= @('OpenVPNService','OpenVPNServiceInteractive','agent_ovpnconnect','ovpnhelper_service')
foreach($n in $names){
  try{
    Set-Service -Name $n -StartupType Automatic
    Start-Service -Name $n -ErrorAction Continue
    $s=Get-Service -Name $n
    Add-Content -Path $log -Value "[$t] 服務 $($s.Name): $($s.Status) ($($s.StartType))"
  } catch {
    Add-Content -Path $log -Value "[$t] 服務 $n 操作失敗: $($_.Exception.Message)"
  }
}
ipconfig /flushdns | Out-Null
try{
  $dns=(Resolve-DnsName openvpn.net -ErrorAction Continue)
  $ips = ($dns | Select-Object -ExpandProperty IPAddress -ErrorAction SilentlyContinue | Sort-Object | Select-Object -Unique) -join ', '
  Add-Content -Path $log -Value "[$t] DNS openvpn.net: $ips"
} catch {
  Add-Content -Path $log -Value "[$t] DNS 解析失敗"
}
try{
  $hdr=(curl.exe -I https://openvpn.net 2>&1 | Select-Object -First 5)
  Add-Content -Path $log -Value "[$t] HTTPS openvpn.net 首部: $($hdr -join ' | ')"
} catch {
  Add-Content -Path $log -Value "[$t] HTTPS 測試失敗"
}
Add-Content -Path $log -Value "[$t] 管理員通道作業完成"
