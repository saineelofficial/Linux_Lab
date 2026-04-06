# Linux Network and Service Monitoring Lab

A lightweight, automated early-warning system and diagnostic toolkit built primarily with Python and Bash. This project continuously monitors mission-critical infrastructure such as DNS resolution, TCP port connectivity, and HTTP endpoint latency, alerting you to outages or performance degradation. When an anomaly is detected, it automatically executes a suite of deep-dive diagnostic tools to help pinpoint the root cause.

---

## 🏗️ System Architecture

The project relies on a **cron-driven architecture** consisting of three main layers:

1. **Configuration Layer (`config.json`)**: Dictates exactly what infrastructure is tested (IPs, Ports, Hostnames, Latency Thresholds).
2. **Monitoring Engine (`monitor.py`)**: A dependency-free Python script executed every 5 minutes by the system's `cron` daemon. It handles socket connections, logs results, and identifies degraded network states.
3. **Diagnostic Engine (`network_diagnostics.sh`)**: A Bash toolkit leveraging standard Linux networking tools (`ping`, `dig`, `nc`, `curl`). It is automatically triggered by the Python engine upon detecting a failure to gather detailed forensic data.

---

## 📂 File Structure

```text
Linux_Lab/
├── README.md                 # System documentation
├── config.json               # JSON configuration map of your targets
├── monitor.py                # Core Python monitoring engine 
├── network_diagnostics.sh    # Bash script for deep-dive network checks
├── setup_cron.sh             # Installation script to schedule the monitor
└── logs/                     # Directory generated to store output
    ├── monitoring.log        # Primary log for health checks and anomalies
    └── cron.log              # Debug log for cron execution errors
```

---

## ⚙️ Component Breakdown

### `config.json`
A human-readable JSON file that allows you to easily scale up the lab. You define your targets here:
- `dns_targets`: Domains that must successfully resolve to an IP address.
- `tcp_targets`: Servers and their explicit ports (e.g., checking if SSH on port `22` or a webserver on port `8080` is open).
- `http_targets`: Application endpoints with a strict `max_latency_ms`. If a response takes longer than the threshold, an anomaly is logged.

### `monitor.py`
The brain of the system. Written using Python's standard library (`urllib` and `socket`) to ensure it runs universally without needing `pip install`. If `monitor.py` detects an unreachable target, it automatically triggers `network_diagnostics.sh`. 

### `network_diagnostics.sh`
Your automated forensic toolkit. When triggered, it runs a chain of Linux tools:
1. **ICMP (`ping`)**: Verifies raw network reachability.
2. **DNS (`dig` / `nslookup`)**: Tests the name server resolution directly.
3. **TCP (`nc`)**: Probes specific ports directly.
4. **HTTP Head (`curl`)**: Attempts to grab raw server responses using forced timeouts.

### `setup_cron.sh`
A convenience script that binds `monitor.py` to your terminal's `crontab`, ensuring the engine executes silently in the background at a 5-minute interval without keeping a terminal window open.

---

## 🚀 Getting Started

1. **Clone/Navigate** into the directory. Ensure the `logs` folder exists (run `mkdir -p logs` if it doesn't).
2. **Make Scripts Executable**:
   ```bash
   chmod +x monitor.py network_diagnostics.sh setup_cron.sh
   ```
3. **Update Configuration**: Open `config.json` and insert your actual IPs and domains.
4. **Install the Automator**:
   ```bash
   ./setup_cron.sh
   ```
5. **View the Logs**:
   You can view the active output of the system at any time by reading the log file:
   ```bash
   tail -f logs/monitoring.log
   ```

---

## 🛠️ Troubleshooting 

**Issue: Cron job isn't writing to the logs (macOS)**
If you are running this lab on macOS and the `monitor.py` script throws `[Errno 1] Operation not permitted` inside `cron.log`, macOS's privacy settings are blocking `cron` from reading your Desktop.
* *Fix*: Either move the project folder out of your `Desktop` / `Documents` into your root user folder (e.g., `~/Linux_Lab`), or grant `/usr/sbin/cron` "Full Disk Access" in macOS Settings -> Privacy & Security.

---

## 🔭 Future Scope

This monitoring lab is highly extensible. Future functionality could include:
- **Alert Notifications**: Integrate Webhooks (like Discord or Slack API) into `monitor.py` to ping you on your phone the minute a server drops.
- **Database Backend**: Migrate from flat-file logging (`monitoring.log`) to an SQLite database to allow for historic uptime queries.
- **SSL Certificate Monitoring**: Add a Python check to explicitly monitor how many days are left until an HTTPS certificate expires.
- **Data Visualization**: A simple frontend dashboard (using Flask or HTML/JS) to parse the JSON logs and show green/red indicators visually.
