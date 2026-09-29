import http.server
import socketserver
import threading
import webbrowser
import json
import time
import platform
import psutil
import socket
from urllib.parse import urlparse

PORT = 8765

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Ultimate PC Dashboard</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #080b10;
    color: white;
    font-family: Arial, sans-serif;
}

.header {
    height: 80px;
    background: #10151d;
    border-bottom: 1px solid #29313d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
}

.logo {
    font-size: 25px;
    font-weight: bold;
    color: #00e5ff;
}

.clock {
    color: #ddd;
}

.container {
    padding: 25px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
}

.card {
    background: #151a22;
    border: 1px solid #29313d;
    border-radius: 15px;
    padding: 20px;
}

.card h2 {
    margin-top: 0;
    font-size: 17px;
    color: #aeb7c5;
}

.value {
    font-size: 38px;
    font-weight: bold;
    margin: 12px 0;
}

.cpu {
    color: #00e5ff;
}

.ram {
    color: #00ff88;
}

.disk {
    color: #ffaa00;
}

.net {
    color: #c77dff;
}

.bar {
    height: 12px;
    width: 100%;
    background: #272e38;
    border-radius: 10px;
    overflow: hidden;
}

.fill {
    height: 100%;
    width: 0%;
    transition: width .4s;
}

.cpu-fill {
    background: #00e5ff;
}

.ram-fill {
    background: #00ff88;
}

.disk-fill {
    background: #ffaa00;
}

.wide {
    grid-column: span 2;
}

.full {
    grid-column: span 4;
}

canvas {
    width: 100%;
    height: 250px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 10px;
    border-bottom: 1px solid #29313d;
    text-align: left;
}

th {
    color: #00e5ff;
}

button {
    background: #00e5ff;
    border: none;
    padding: 12px 18px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    margin: 5px;
}

button:hover {
    transform: scale(1.04);
}

.online {
    color: #00ff88;
}

@media(max-width: 900px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .wide,
    .full {
        grid-column: span 2;
    }
}

@media(max-width: 600px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .wide,
    .full {
        grid-column: span 1;
    }
}
</style>
</head>

<body>

<div class="header">

    <div class="logo">
        ⚡ ULTIMATE PC DASHBOARD
    </div>

    <div class="clock" id="clock">
        Loading...
    </div>

</div>

<div class="container">

<div class="grid">

<!-- CPU -->

<div class="card">

<h2>⚙ CPU</h2>

<div class="value cpu" id="cpu">
0%
</div>

<div class="bar">
<div class="fill cpu-fill" id="cpuBar"></div>
</div>

<p id="cpuInfo">Loading...</p>

</div>


<!-- RAM -->

<div class="card">

<h2>🧠 RAM</h2>

<div class="value ram" id="ram">
0%
</div>

<div class="bar">
<div class="fill ram-fill" id="ramBar"></div>
</div>

<p id="ramInfo">Loading...</p>

</div>


<!-- DISK -->

<div class="card">

<h2>💾 DISK</h2>

<div class="value disk" id="disk">
0%
</div>

<div class="bar">
<div class="fill disk-fill" id="diskBar"></div>
</div>

<p id="diskInfo">Loading...</p>

</div>


<!-- NETWORK -->

<div class="card">

<h2>🌐 NETWORK</h2>

<div class="value net" id="download">
0 MB/s
</div>

<p id="upload">Upload: 0 MB/s</p>

<p class="online">
● ONLINE
</p>

</div>


<!-- SYSTEM -->

<div class="card wide">

<h2>🖥 SYSTEM INFORMATION</h2>

<p id="systemInfo">
Loading...
</p>

</div>


<!-- POWER -->

<div class="card wide">

<h2>🔋 POWER</h2>

<p id="battery">
Checking battery...
</p>

</div>


<!-- GRAPH -->

<div class="card wide">

<h2>📊 LIVE PERFORMANCE</h2>

<canvas id="graph"></canvas>

</div>


<!-- TOP PROCESSES -->

<div class="card wide">

<h2>🔥 TOP PROCESSES</h2>

<table>

<thead>

<tr>
<th>Process</th>
<th>PID</th>
<th>CPU</th>
<th>RAM</th>
</tr>

</thead>

<tbody id="processes">

</tbody>

</table>

</div>


<!-- CONTROLS -->

<div class="card full">

<h2>🚀 DASHBOARD CONTROLS</h2>

<button onclick="location.reload()">
🔄 Refresh
</button>

<button onclick="document.documentElement.requestFullscreen()">
⛶ Fullscreen
</button>

<button onclick="gamingMode()">
🎮 Gaming Mode
</button>

<button onclick="darkMode()">
🌑 Dark Mode
</button>

</div>


<div class="card full">

<h2>📡 STATUS</h2>

<p id="status">
Connecting to Python...
</p>

</div>

</div>

</div>


<script>

let cpuHistory = [];
let ramHistory = [];


async function getStats() {

    try {

        const response =
            await fetch("/stats");

        const data =
            await response.json();


        // CPU

        document.getElementById("cpu").innerText =
            data.cpu + "%";

        document.getElementById("cpuBar").style.width =
            data.cpu + "%";

        document.getElementById("cpuInfo").innerText =
            "Cores: " + data.cpu_cores +
            " | Frequency: " +
            data.cpu_freq + " MHz";


        // RAM

        document.getElementById("ram").innerText =
            data.ram + "%";

        document.getElementById("ramBar").style.width =
            data.ram + "%";

        document.getElementById("ramInfo").innerText =
            data.ram_used + " GB / " +
            data.ram_total + " GB";


        // DISK

        document.getElementById("disk").innerText =
            data.disk + "%";

        document.getElementById("diskBar").style.width =
            data.disk + "%";

        document.getElementById("diskInfo").innerText =
            data.disk_used + " GB / " +
            data.disk_total + " GB";


        // NETWORK

        document.getElementById("download").innerText =
            "↓ " + data.download + " MB/s";

        document.getElementById("upload").innerText =
            "↑ Upload: " +
            data.upload +
            " MB/s";


        // SYSTEM

        document.getElementById("systemInfo").innerHTML =
            "<b>OS:</b> " + data.os +
            "<br><b>Computer:</b> " +
            data.hostname +
            "<br><b>Processor:</b> " +
            data.processor;


        // BATTERY

        document.getElementById("battery").innerHTML =
            data.battery;


        // PROCESSES

        let processHTML = "";

        data.processes.forEach(p => {

            processHTML += `
            <tr>
                <td>${p.name}</td>
                <td>${p.pid}</td>
                <td>${p.cpu}%</td>
                <td>${p.ram} MB</td>
            </tr>
            `;

        });

        document.getElementById("processes").innerHTML =
            processHTML;


        // GRAPH

        cpuHistory.push(data.cpu);
        ramHistory.push(data.ram);

        if(cpuHistory.length > 60) {
            cpuHistory.shift();
            ramHistory.shift();
        }

        drawGraph();


        document.getElementById("status").innerHTML =
            '<span class="online">● PYTHON CONNECTED</span>';

    }

    catch(error) {

        document.getElementById("status").innerHTML =
            "❌ Python server disconnected";

    }

}


function drawGraph() {

    const canvas =
        document.getElementById("graph");

    const ctx =
        canvas.getContext("2d");

    canvas.width =
        canvas.clientWidth;

    canvas.height = 250;

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    drawLine(
        ctx,
        cpuHistory,
        canvas.width,
        canvas.height
    );

    drawLine(
        ctx,
        ramHistory,
        canvas.width,
        canvas.height
    );

}


function drawLine(ctx, values, width, height) {

    if(values.length < 2)
        return;


    ctx.beginPath();

    values.forEach((value, index) => {

        const x =
            index * width /
            (values.length - 1);

        const y =
            height -
            (value / 100) *
            height;

        if(index === 0)
            ctx.moveTo(x, y);
        else
            ctx.lineTo(x, y);

    });


    ctx.strokeStyle = "#00e5ff";
    ctx.lineWidth = 3;

    ctx.stroke();

}


function updateClock() {

    const now =
        new Date();

    document.getElementById("clock").innerText =
        now.toLocaleDateString() +
        " | " +
        now.toLocaleTimeString();

}


function gamingMode() {

    document.body.style.background =
        "#020305";

    document.getElementById("status").innerHTML =
        "🎮 GAMING MODE ENABLED";

}


function darkMode() {

    document.body.style.background =
        "#000000";

}


setInterval(getStats, 1000);
setInterval(updateClock, 1000);

getStats();
updateClock();

</script>

</body>
</html>
"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/":

            content = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                len(content)
            )
            self.end_headers()

            self.wfile.write(content)

        elif path == "/stats":

            data = get_stats()

            content = json.dumps(data).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.send_header(
                "Content-Length",
                len(content)
            )
            self.end_headers()

            self.wfile.write(content)

        else:

            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


last_net = psutil.net_io_counters()
last_time = time.time()


def get_stats():

    global last_net
    global last_time

    # CPU
    cpu = psutil.cpu_percent(interval=None)

    cpu_freq = psutil.cpu_freq()

    if cpu_freq:
        frequency = round(cpu_freq.current)
    else:
        frequency = 0


    # RAM
    memory = psutil.virtual_memory()

    ram_percent = memory.percent
    ram_used = round(
        memory.used / (1024 ** 3),
        2
    )
    ram_total = round(
        memory.total / (1024 ** 3),
        2
    )


    # DISK
    disk_path = "C:\\" if platform.system() == "Windows" else "/"

    disk = psutil.disk_usage(disk_path)

    disk_percent = disk.percent

    disk_used = round(
        disk.used / (1024 ** 3),
        2
    )

    disk_total = round(
        disk.total / (1024 ** 3),
        2
    )


    # NETWORK
    current_net = psutil.net_io_counters()

    current_time = time.time()

    elapsed = current_time - last_time

    if elapsed <= 0:
        elapsed = 1

    download = (
        current_net.bytes_recv -
        last_net.bytes_recv
    ) / elapsed

    upload = (
        current_net.bytes_sent -
        last_net.bytes_sent
    ) / elapsed

    last_net = current_net
    last_time = current_time


    # BATTERY
    battery = psutil.sensors_battery()

    if battery:

        if battery.power_plugged:
            battery_text = (
                f"🔋 {battery.percent}% "
                f"⚡ Charging"
            )
        else:
            battery_text = (
                f"🔋 {battery.percent}% "
                f"On Battery"
            )

    else:

        battery_text = "🔌 Desktop PC / No Battery"


    # PROCESSES
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_info"]
    ):

        try:

            info = proc.info

            ram_mb = round(
                info["memory_info"].rss /
                (1024 ** 2),
                1
            )

            processes.append({
                "name": info["name"] or "Unknown",
                "pid": info["pid"],
                "cpu": round(
                    info["cpu_percent"],
                    1
                ),
                "ram": ram_mb
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            pass


    processes.sort(
        key=lambda x: x["cpu"],
        reverse=True
    )

    processes = processes[:10]


    return {

        "cpu": round(cpu, 1),

        "cpu_freq": frequency,

        "cpu_cores":
            psutil.cpu_count(logical=True),

        "ram":
            round(ram_percent, 1),

        "ram_used":
            ram_used,

        "ram_total":
            ram_total,

        "disk":
            round(disk_percent, 1),

        "disk_used":
            disk_used,

        "disk_total":
            disk_total,

        "download":
            round(
                download / (1024 ** 2),
                2
            ),

        "upload":
            round(
                upload / (1024 ** 2),
                2
            ),

        "battery":
            battery_text,

        "os":
            platform.platform(),

        "hostname":
            socket.gethostname(),

        "processor":
            platform.processor(),

        "processes":
            processes
    }


def main():

    server = socketserver.ThreadingTCPServer(
        ("127.0.0.1", PORT),
        DashboardHandler
    )

    server.allow_reuse_address = True

    url = f"http://127.0.0.1:{PORT}"

    print()
    print("=" * 55)
    print("⚡ ULTIMATE PC DASHBOARD")
    print("=" * 55)
    print()
    print(f"Dashboard: {url}")
    print()
    print("Open Chrome and visit the address above.")
    print("Press CTRL+C in this terminal to stop.")
    print()

    threading.Timer(
        1.0,
        lambda: webbrowser.open(url)
    ).start()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\nDashboard stopped.")

        server.shutdown()


if __name__ == "__main__":
    main()