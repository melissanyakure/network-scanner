
import socket
import subprocess
import ipaddress


def get_local_ip():
    """Get the local IP address."""

    try:
        result = subprocess.run(
            ["ip", "route", "get", "1.1.1.1"],
            capture_output=True,
            text=True,
            check=True
        )

        parts = result.stdout.split()

        if "src" in parts:
            return parts[parts.index("src") + 1]

        return "Unknown"

    except (subprocess.CalledProcessError, ValueError):
        return "Unknown"


def get_interface():
    """Get the active network interface."""

    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=True
        )

        parts = result.stdout.split()

        if "dev" in parts:
            return parts[parts.index("dev") + 1]

        return "Unknown"

    except (subprocess.CalledProcessError, ValueError):
        return "Unknown"


def get_gateway():
    """Get the default network gateway."""

    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=True
        )

        parts = result.stdout.split()

        if "via" in parts:
            return parts[parts.index("via") + 1]

        return "Unknown"

    except subprocess.CalledProcessError:
        return "Unknown"


def get_network_range():
    """Get the local network range."""

    interface = get_interface()

    if interface == "Unknown":
        return "Unknown"

    try:
        result = subprocess.run(
            ["ip", "-o", "-4", "addr", "show", "dev", interface],
            capture_output=True,
            text=True,
            check=True
        )

        for part in result.stdout.split():

            if "/" in part:
                try:
                    network = ipaddress.ip_interface(part)
                    return str(network.network)

                except ValueError:
                    continue

        return "Unknown"

    except subprocess.CalledProcessError:
        return "Unknown"


def scan_network():
    """
    Read the local Linux neighbor table.
    This does not actively probe other devices.
    """

    interface = get_interface()
    devices = []

    if interface == "Unknown":
        return devices

    result = subprocess.run(
        ["ip", "-4", "neigh", "show", "dev", interface],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():

        parts = line.split()

        if len(parts) < 2:
            continue

        ip_address = parts[0]

        if "lladdr" not in parts:
            continue

        mac_index = parts.index("lladdr") + 1

        if mac_index >= len(parts):
            continue

        mac_address = parts[mac_index]
        status = parts[-1]

        try:
            hostname = socket.gethostbyaddr(ip_address)[0]

        except (socket.herror, OSError):
            hostname = "Unknown"

        if status == "REACHABLE":
            device_status = "Reachable"

        elif status == "STALE":
            device_status = "Cached - not confirmed online"

        elif status in ["DELAY", "PROBE"]:
            device_status = "Checking"

        elif status == "FAILED":
            device_status = "Unreachable"

        else:
            device_status = status

        devices.append({
            "ip": ip_address,
            "hostname": hostname,
            "mac": mac_address,
            "status": device_status
        })

    return devices


if __name__ == "__main__":

    print("\n========== NETWORK SCANNER ==========\n")

    print("Local IP:", get_local_ip())
    print("Interface:", get_interface())
    print("Gateway:", get_gateway())
    print("Network Range:", get_network_range())

    found_devices = scan_network()

    print("\n========== DISCOVERED ENTRIES ==========")
    print("Total entries:", len(found_devices))

    for device in found_devices:
        print(device)

    print("\nScan completed!")
