import socket
import psutil

def get_active_interfaces():
    """Returns a dict of {interface_name: ip_address} for active physical NICs."""
    interfaces = {}
    for interface, addrs in psutil.net_if_addrs().items():
        # Filter for physical-ish names (customized for this machine)
        if "Wi-Fi" in interface or "乙太網路" in interface:
             for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces[interface] = addr.address
    return interfaces

print(get_active_interfaces())
