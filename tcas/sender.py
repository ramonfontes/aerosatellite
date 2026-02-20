import base64
from scapy.all import *
from bitstring import BitArray
import time
import sys


DST_IP = "10.255.255.255"  # ou broadcast "10.255.255.255"
DST_PORT = 30003
IFACE = sys.argv[1] + "-mp0"

# -------------------------
# Envio via Scapy
# -------------------------
def send_adsb_from_file(filename):
    try:
        with open(filename, "r") as f:
            line = f.readline().strip()

        adsb_bytes = base64.b64decode(line)
        pkt = IP(dst=DST_IP) / UDP(dport=DST_PORT) / Raw(load=adsb_bytes)
        send(pkt, iface=IFACE, verbose=0)
        print(f"{len(adsb_bytes)} ADS-B bytes sent via {IFACE} to {DST_IP}:{DST_PORT}")

    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error: {e}")

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    while True:
        send_adsb_from_file('/tmp/mn-wifi-adsb-{}.log'.format(sys.argv[1]))
        time.sleep(5)
