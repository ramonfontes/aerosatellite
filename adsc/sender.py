from scapy.all import *
import sys
import json
import time
import os

# IPv6 ATN/IPS addresses
src_ip = "2001:db8:10::1"   # aicraft
dst_ip = "2001:db8:10::2"   # satatellite

def send_adsc_from_log(aircraft_name):
    log_file = f"/tmp/mn-wifi-adsc-{aircraft_name}.log"

    if not os.path.exists(log_file):
        print(f"[ERRO] File {log_file} not found.")
        return

    with open(log_file, "r") as f:
        try:
            adsc_msg = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON invalid {log_file}: {e}")
            return

    pkt = (
        IPv6(src=src_ip, dst=dst_ip, hlim=64) /
        UDP(sport=4000, dport=4001) /
        Raw(load=json.dumps(adsc_msg))
    )

    send(pkt, iface=aircraft_name+"-mp0")


if __name__ == "__main__":
    aircraft_name = sys.argv[1]
    while True:
        send_adsc_from_log(aircraft_name)
        time.sleep(5)
