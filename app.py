
from flask import Flask, render_template, Response
from datetime import datetime
import csv
import io

from scanner import (
    scan_network,
    get_local_ip,
    get_interface,
    get_gateway,
    get_network_range
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template(
        "index.html",
        scanned=False
    )


@app.route("/scan", methods=["POST"])
def scan():

    local_ip = get_local_ip()
    interface = get_interface()
    gateway = get_gateway()
    network_range = get_network_range()

    devices = scan_network()
    total_devices = len(devices)

    reachable_count = sum(
        1 for device in devices
        if device["status"] == "Reachable"
    )

    cached_count = sum(
        1 for device in devices
        if device["status"] == "Cached - not confirmed online"
    )

    other_count = total_devices - reachable_count - cached_count

    scan_time = datetime.now().strftime(
        "%d %B %Y, %I:%M:%S %p"
    )

    return render_template(
        "index.html",
        devices=devices,
        local_ip=local_ip,
        interface=interface,
        gateway=gateway,
        network_range=network_range,
        total_devices=total_devices,
        reachable_count=reachable_count,
        cached_count=cached_count,
        other_count=other_count,
        scan_time=scan_time,
        scanned=True
    )


@app.route("/export")
def export_csv():

    devices = scan_network()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "IP Address",
        "MAC Address",
        "Hostname",
        "Status"
    ])

    for device in devices:
        writer.writerow([
            device["ip"],
            device["mac"],
            device["hostname"],
            device["status"]
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=network_devices.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
