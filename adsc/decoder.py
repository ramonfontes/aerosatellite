#!/usr/bin/env python3
from scapy.all import *
import json
import sys

# Porta usada no tráfego ATN/IPS (deve coincidir com o sender)
UDP_PORT = 4001

def handle_packet(pkt):
    """Callback para cada pacote capturado"""
    if IPv6 in pkt and UDP in pkt and pkt[UDP].dport == UDP_PORT:
        try:
            data = pkt[Raw].load.decode()
            msg = json.loads(data)
            print("\n=== Received ATN/IPS Message ===")
            for k, v in msg.items():
                print(f"{k:15s}: {v}")
        except Exception as e:
            print(f"[!] Erro ao decodificar payload: {e}")

def main():
    print(f"[*] Satellite receiver listening on UDP port {UDP_PORT} (IPv6)...")
    sniff(iface=sys.argv[1]+"-mp0", filter=f"ip6 and udp port {UDP_PORT}", prn=handle_packet, store=0)

if __name__ == "__main__":
    main()
