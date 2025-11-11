import sys
import base64

from scapy.all import *
from bitstring import BitArray
from math import radians, sin, cos, sqrt, atan2

DST_PORT = 30003
IFACE = f'{sys.argv[1]}-mp0'
LOCAL_MAC = get_if_hwaddr(IFACE)
FILENAME = f"/tmp/mn-wifi-adsb-{sys.argv[1]}.log"
DIST = sys.argv[2]
V_SEP = sys.argv[3]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def decode_adsb(msg_bytes):
    bits = BitArray(msg_bytes)
    if len(bits) < 114:
        return
    bits = bits[:114]

    icao = bits[8:32].hex.upper()
    me = bits[32:90]

    type_code = me[0:5].uint
    alt_bits = me[11:23]
    f_bit = me[23]
    lat_bits = me[24:41]
    lon_bits = me[41:58]

    n = alt_bits[:11].uint
    q = alt_bits[11]
    altitude = n*25 - 1000 if q==1 else None

    lat_cpr = lat_bits.uint
    lon_cpr = lon_bits.uint
    latitude = (lat_cpr * 180 / 131072) - 90
    longitude = (lon_cpr * 360 / 131072) - 180

    return {
        "icao": icao,
        "altitude_ft": altitude,
        "latitude": latitude,
        "longitude": longitude,
    }


def packet_handler(pkt):
    src_mac = pkt[Ether].src.lower()
    if src_mac == LOCAL_MAC.lower():
        return
    if UDP in pkt and pkt[UDP].dport == DST_PORT and Raw in pkt:
        data = bytes(pkt[UDP].payload)
        decoded = decode_adsb(data)
        if decoded:
            print("\n=== Received TCAS Message ===")
            for k,v in decoded.items():
                print(f"{k:12}: {v}")

            line = None
            with open(FILENAME, "r") as f:
                line = f.readline().strip()

            if not line:
                return

            raw = base64.b64decode(line)
            bits = BitArray(raw)

            # campos fixos (DF, CA, ICAO, Type Code etc)
            df = bits[0:5].uint
            icao = bits[8:32].hex
            type_code = bits[32:37].uint

            # altitude (25 ft steps, -1000 offset como no encoder)
            alt_bits = bits[43:54]  # 11 bits
            n = alt_bits.uint
            altitude = (n * 25) - 1000

            # CPR latitude e longitude
            lat_bits = bits[56:73]
            lon_bits = bits[73:90]
            lat_cpr = lat_bits.uint
            lon_cpr = lon_bits.uint

            lat = (lat_cpr * 180 / 131072) - 90
            lon = (lon_cpr * 360 / 131072) - 180

            dist = haversine(lat, lon, decoded['latitude'], decoded['longitude'])
            v_sep = abs(altitude - decoded['altitude_ft']) # Vertical Separation
            if dist < int(DIST) and v_sep < int(V_SEP):
                print(f"Alert! Traffic Advisory with {decoded['icao']} - Dist: {dist:.0f}m, Alt: {v_sep}ft")

if __name__ == "__main__":
    print(f"Listening ADS-B packets interface {IFACE}, port {DST_PORT}...")
    sniff(iface=IFACE, filter=f"udp port {DST_PORT}", prn=packet_handler)
