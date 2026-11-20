"""tailnet_ip() with each command's output faked. Run: python3 -m unittest discover tests"""
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

_path = str(Path(__file__).resolve().parent.parent / "redpen")
_loader = importlib.machinery.SourceFileLoader("redpen_mod", _path)
_spec = importlib.util.spec_from_loader("redpen_mod", _loader)
redpen = importlib.util.module_from_spec(_spec)
_loader.exec_module(redpen)

IP_ADDR = "4: tailscale0    inet 100.84.119.113/32 scope global tailscale0\\       valid_lft forever preferred_lft forever\n"
TAILSCALE = "100.84.119.113\n"
TAILSCALE_GUI_FAIL = "The Tailscale GUI failed to start\n"
IFCONFIG_MAC = """lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
\tinet 127.0.0.1 netmask 0xff000000
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
\tinet 192.168.1.20 netmask 0xffffff00 broadcast 192.168.1.255
utun4: flags=8051<UP,POINTOPOINT,RUNNING,MULTICAST> mtu 1280
\tinet 100.84.119.113 --> 100.84.119.113 netmask 0xffffffff
\tinet6 fd7a:115c:a1e0::1 prefixlen 48
"""


def fake(outputs, present):
    calls = []

    def run(argv):
        calls.append(argv)
        return outputs.get(Path(argv[0]).name, "")

    def which(name):
        return f"/usr/bin/{name}" if name in present else None

    return run, which, calls


class TailnetIp(unittest.TestCase):
    def test_linux_ip_addr(self):
        run, which, calls = fake({"ip": IP_ADDR}, {"ip", "tailscale"})
        self.assertEqual(redpen.tailnet_ip(run, which, "linux"), "100.84.119.113")
        self.assertEqual(calls[0][1:], ["-4", "-o", "addr", "show", "tailscale0"])

    def test_linux_tailscale_cli_when_no_ip(self):
        run, which, _ = fake({"tailscale": TAILSCALE}, {"tailscale"})
        self.assertEqual(redpen.tailnet_ip(run, which, "linux"), "100.84.119.113")

    def test_linux_tailscale_cli_when_ip_finds_nothing(self):
        run, which, _ = fake({"ip": "", "tailscale": TAILSCALE}, {"ip", "tailscale"})
        self.assertEqual(redpen.tailnet_ip(run, which, "linux"), "100.84.119.113")

    def test_mac_ifconfig(self):
        run, which, calls = fake({"ifconfig": IFCONFIG_MAC}, {"ifconfig", "tailscale"})
        self.assertEqual(redpen.tailnet_ip(run, which, "darwin"), "100.84.119.113")
        self.assertNotIn("tailscale", [Path(c[0]).name for c in calls])

    def test_gui_failure_text_is_not_an_answer(self):
        run, which, _ = fake({"tailscale": TAILSCALE_GUI_FAIL, "ifconfig": IFCONFIG_MAC},
                             {"tailscale", "ifconfig"})
        self.assertEqual(redpen.tailnet_ip(run, which, "linux"), "100.84.119.113")

    def test_nothing_found(self):
        run, which, _ = fake({}, set())
        # /sbin/ifconfig may exist on the test machine; fake run returns "" for it.
        self.assertIsNone(redpen.tailnet_ip(run, which, "linux"))

    def test_non_tailscale_100_address_ignored(self):
        self.assertEqual(redpen._cgnat_ips("inet 100.12.1.1 inet 100.100.1.2"), ["100.100.1.2"])


if __name__ == "__main__":
    unittest.main()
