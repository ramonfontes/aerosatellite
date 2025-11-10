from scapy.all import *
from bitstring import BitArray
import time

DST_IP = "10.255.255.255"  # ou broadcast "10.255.255.255"
DST_PORT = 30003
IFACE = "plane1-wlan0"          # interface de saída, ex: "wlan0" ou "eth0"

# -------------------------
# Helpers do build_adsb
# -------------------------
def crc24(msg_bits):
    poly = 0xFFF409
    reg = 0
    for i in range(len(msg_bits)):
        reg <<= 1
        bit = int(msg_bits[i])
        if ((reg >> 24) ^ bit) & 1:
            reg ^= poly
    return reg & 0xFFFFFF

def encode_fake(lat, lon):
    lat_cpr = int((lat + 90) * 131072 / 180)
    lon_cpr = int((lon + 180) * 131072 / 360)
    return lat_cpr, lon_cpr

def build_adsb(icao_hex="AABBCC", lat=-23.5505, lon=-46.6333, altitude=12000, odd_flag=0):
    df = BitArray(uint=17, length=5)
    ca = BitArray(uint=0, length=3)
    icao = BitArray(hex=icao_hex)
    type_code = BitArray(uint=11, length=5)
    n = int((altitude + 1000) / 25)
    alt_bits = BitArray(uint=n, length=11) + BitArray(uint=1, length=1)
    f_bit = BitArray(uint=odd_flag, length=1)
    lat_cpr, lon_cpr = encode_fake(lat, lon)
    lat_bits = BitArray(uint=lat_cpr, length=17)
    lon_bits = BitArray(uint=lon_cpr, length=17)
    me = type_code + BitArray(uint=0, length=6) + alt_bits + f_bit + lat_bits + lon_bits
    msg = df + ca + icao + me
    crc = BitArray(uint=crc24(msg.bin), length=24)
    return (msg + crc).tobytes()  # retorna bytes

# -------------------------
# Envio via Scapy
# -------------------------
def send_adsb_scapy(adsb_bytes):
    pkt = IP(dst=DST_IP)/UDP(dport=DST_PORT)/Raw(load=adsb_bytes)
    print(adsb_bytes)
    send(pkt, iface=IFACE, verbose=0)
    print(f"Enviado {len(adsb_bytes)} bytes ADS-B via {IFACE} para {DST_IP}:{DST_PORT}")

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    while True:
        msg = build_adsb("AABBCC", -22.5505, -46.6333, 12000, odd_flag=0)
        send_adsb_scapy(msg)
        time.sleep(0.5)
