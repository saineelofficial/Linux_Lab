#!/usr/bin/env python3
import json
import socket
import urllib.request
import urllib.error
import time
import os
import sys
import subprocess
from urllib.parse import urlparse
from datetime import datetime

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'monitoring.log')

def log_event(level, component, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [{component}] {message}\n"
    print(log_entry.strip())
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        log_event("ERROR", "CONFIG", f"Configuration file {CONFIG_FILE} not found.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def run_diagnostics(target):
    log_event("INFO", "DIAGNOSTICS", f"Triggering network_diagnostics.sh for {target}")
    script_path = os.path.join(os.path.dirname(__file__), 'network_diagnostics.sh')
    try:
        result = subprocess.run([script_path, target], capture_output=True, text=True, timeout=15)
        for line in result.stdout.split('\n'):
            if line.strip():
                log_event("DIAG", target, line.strip())
    except Exception as e:
        log_event("ERROR", "DIAGNOSTICS", f"Failed to run diagnostic script: {e}")


def check_dns(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        log_event("INFO", "DNS", f"Resolved {hostname} to {ip}")
        return True
    except socket.gaierror as e:
        log_event("ERROR", "DNS", f"Failed to resolve {hostname}: {e}")
        return False

def check_tcp(host, port):
    try:
        # 3 seconds timeout
        sock = socket.create_connection((host, int(port)), timeout=3)
        sock.close()
        log_event("INFO", "TCP", f"Successfully connected to {host}:{port}")
        return True
    except socket.timeout:
        log_event("ERROR", "TCP", f"Connection to {host}:{port} timed out.")
        return False
    except ConnectionRefusedError:
        log_event("ERROR", "TCP", f"Connection to {host}:{port} was refused.")
        return False
    except Exception as e:
        log_event("ERROR", "TCP", f"Failed to connect to {host}:{port}: {e}")
        return False

def check_http(url, max_latency_ms):
    start_time = time.time()
    try:
        # Add a basic User-Agent to avoid simple blocks
        req = urllib.request.Request(url, headers={'User-Agent': 'MonitoringLab/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            latency_ms = int((time.time() - start_time) * 1000)
            
            if status_code == 200:
                if latency_ms > max_latency_ms:
                    log_event("WARNING", "HTTP_LATENCY", f"High latency for {url}: {latency_ms}ms (Threshold: {max_latency_ms}ms)")
                else:
                    log_event("INFO", "HTTP", f"Service OK: {url} reached in {latency_ms}ms")
                return True
            else:
                log_event("ERROR", "HTTP", f"Received unexpected status code {status_code} from {url}")
                return False
    except urllib.error.HTTPError as e:
        log_event("ERROR", "HTTP", f"HTTP Error from {url}: Code {e.code}")
        return False
    except urllib.error.URLError as e:
        log_event("ERROR", "HTTP", f"URL Error for {url}: {e.reason}")
        return False
    except socket.timeout:
        log_event("ERROR", "HTTP", f"Timeout connecting to {url}")
        return False
    except Exception as e:
        log_event("ERROR", "HTTP", f"Error connecting to {url}: {e}")
        return False

def main():
    log_event("INFO", "SYSTEM", "Starting monitoring cycle")
    config = load_config()

    # Process DNS targets
    for target in config.get("dns_targets", []):
        if not check_dns(target):
            run_diagnostics(target)

    # Process TCP targets
    for target in config.get("tcp_targets", []):
        host = target.get("host")
        if not check_tcp(host, target.get("port")):
            run_diagnostics(host)
        
    # Process HTTP targets
    for target in config.get("http_targets", []):
        url = target.get("url")
        if not check_http(url, target.get("max_latency_ms", 500)):
            domain = urlparse(url).netloc.split(':')[0]
            if domain:
                run_diagnostics(domain)

    log_event("INFO", "SYSTEM", "Completed monitoring cycle")

if __name__ == "__main__":
    main()
