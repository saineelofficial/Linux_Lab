#!/bin/bash

# network_diagnostics.sh
# Diagnostic script to run deeper network checks

TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: ./network_diagnostics.sh <hostname_or_ip>"
    exit 1
fi

echo "======================================"
echo "Diagnostics for: $TARGET"
echo "======================================"

echo -e "\n[1] PING Check"
# Send 4 ping requests
ping -c 4 $TARGET > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "SUCCESS: Host is reachable via ICMP (ping)."
else
    echo "FAILURE: Host is unreachable via ICMP (ping)."
fi

echo -e "\n[2] DNS Resolution Check (nslookup / dig)"
if command -v dig &> /dev/null; then
    dig +short $TARGET
else
    nslookup $TARGET
fi

echo -e "\n[3] Common Port Check (SSH: 22, HTTP: 80, HTTPS: 443) using netcat"
for port in 22 80 443; do
    nc -z -w 3 $TARGET $port > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "SUCCESS: Port $port is OPEN."
    else
        echo "FAILURE: Port $port is CLOSED or timed out."
    fi
done

echo -e "\n[4] HTTP Response Headers Check (if applicable)"
# Try connecting via http
HTTP_HEADER=$(curl -I -s --connect-timeout 3 http://$TARGET/ | head -n 1 | tr -d '\r')
if [ -n "$HTTP_HEADER" ]; then
    echo "HTTP: $HTTP_HEADER"
else
    echo "HTTP: No response or connection failed."
fi

# Try connecting via https
HTTPS_HEADER=$(curl -I -s --connect-timeout 3 https://$TARGET/ | head -n 1 | tr -d '\r')
if [ -n "$HTTPS_HEADER" ]; then
    echo "HTTPS: $HTTPS_HEADER"
else
    echo "HTTPS: No response or connection failed."
fi

echo -e "\n======================================"
echo "Diagnostics complete."
echo "======================================"
