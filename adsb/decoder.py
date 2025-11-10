from scapy.all import *
from bitstring import BitArray

DST_PORT = 30003
IFACE = "decoder1-eth0"


def decode_adsb(msg_bytes):
    print(msg_bytes)
    bits = BitArray(msg_bytes)
    if len(bits) < 114:
        return
    bits = bits[:114]

    df = bits[0:5].uint
    ca = bits[5:8].uint
    icao = bits[8:32].hex.upper()
    me = bits[32:90]
    crc = bits[90:114].hex.upper()

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
        "df": df,
        "ca": ca,
        "icao": icao,
        "type_code": type_code,
        "altitude_ft": altitude,
        "odd_flag": bool(f_bit),
        "lat_cpr": lat_cpr,
        "lon_cpr": lon_cpr,
        "latitude": latitude,
        "longitude": longitude,
        "crc": crc
    }

def packet_handler(pkt):
    if UDP in pkt and pkt[UDP].dport == DST_PORT and Raw in pkt:
        data = bytes(pkt[UDP].payload)
        decoded = decode_adsb(data)
        if decoded:
            print("\n=== Received ADS-B ===")
            for k,v in decoded.items():
                print(f"{k:12}: {v}")

if __name__ == "__main__":
    print(f"Listening ADS-B packets interface {IFACE}, port {DST_PORT}...")
    sniff(iface=IFACE, filter=f"udp port {DST_PORT}", prn=packet_handler)
