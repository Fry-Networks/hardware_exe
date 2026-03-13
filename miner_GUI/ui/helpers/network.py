from typing import Optional

from miner_GUI.utils.data import log_step

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore


def populate_network_interfaces(self) -> None:
    """Populate network interface name on the MainWindow instance.

    MAC address is now read from the weekly status JSON (mac_address field)
    in update_rewards_hint(), so only the active interface name is detected here.
    """
    try:
        chosen_iface: Optional[str] = None

        if psutil:
            addrs = psutil.net_if_addrs()

            # Identify the internet-facing interface via active local IP
            primary_ip = None
            try:
                import socket as _sock
                s = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    primary_ip = s.getsockname()[0]
                finally:
                    try:
                        s.close()
                    except Exception:
                        pass
            except Exception:
                primary_ip = None

            if primary_ip:
                for name, lst in addrs.items():
                    has_primary_ip = any(getattr(a, 'family', None) == 2 and getattr(a, 'address', '') == primary_ip for a in lst)
                    if has_primary_ip:
                        chosen_iface = name
                        break

        if chosen_iface:
            self.activeNetworkName = chosen_iface
        else:
            self.activeNetworkName = None

        if hasattr(self, 'networkValueLabel'):
            self.networkValueLabel.setText(self.activeNetworkName if self.activeNetworkName else "-")

        log_step("network_detection", {
            "iface": getattr(self, 'activeNetworkName', None),
        })
    except Exception as e:
        log_step("Error populating network interfaces", {"error": str(e)})
