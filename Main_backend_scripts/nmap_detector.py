# nmap_detector.py

from scapy.all import sniff, IP, TCP
from alert import send_email
from collections import defaultdict
import time

scan_tracker = defaultdict(list)
SCAN_THRESHOLD = 10  # Number of ports accessed within TIME_WINDOW to consider a scan
TIME_WINDOW = 10     # Time in seconds

def detect_nmap(pkt):
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        src_ip = pkt[IP].src
        dst_port = pkt[TCP].dport
        timestamp = time.time()

        # Track ports accessed by each source IP
        scan_tracker[src_ip].append((dst_port, timestamp))

        # Filter old entries
        scan_tracker[src_ip] = [(p, t) for p, t in scan_tracker[src_ip] if timestamp - t <= TIME_WINDOW]

        # Check for port scan pattern
        if len(set(p for p, _ in scan_tracker[src_ip])) > SCAN_THRESHOLD:
            msg = f"⚠️ Potential port scan detected from {src_ip}"
            print(msg)
            send_email("Nmap/Port Scan Detected", msg)
            scan_tracker[src_ip] = []  # Reset after detection

def start_sniffing():
    print("[INFO] Starting network monitor for port scans...")
    sniff(filter="tcp", prn=detect_nmap, store=0)
