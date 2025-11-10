import base64
from scapy.all import *
from bitstring import BitArray
import time
import sys


DST_IP = "10.255.255.255"  # ou broadcast "10.255.255.255"
DST_PORT = 30003
IFACE = sys.argv[1]          # interface de saída, ex: "wlan0" ou "eth0"

# -------------------------
# Envio via Scapy
# -------------------------
def send_adsb_from_file(filename):
    try:
        # Lê o conteúdo do arquivo (uma linha Base64)
        with open(filename, "r") as f:
            line = f.readline().strip()

        # Decodifica Base64 para bytes reais
        adsb_bytes = base64.b64decode(line)

        # Monta o pacote IP/UDP com payload ADS-B
        pkt = IP(dst=DST_IP) / UDP(dport=DST_PORT) / Raw(load=adsb_bytes)

        # Envia o pacote via Scapy
        send(pkt, iface=IFACE, verbose=0)

        print(f"Enviado {len(adsb_bytes)} bytes ADS-B via {IFACE} para {DST_IP}:{DST_PORT}")

    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
    except Exception as e:
        print(f"Erro ao enviar ADS-B: {e}")

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    while True:
        send_adsb_from_file('/tmp/mn-wifi-adsb-{}.log'.format('plane1'))
        time.sleep(0.5)
