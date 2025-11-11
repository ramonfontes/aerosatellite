#!/usr/bin/env python

"""
This example is implemented using celestrak
"""

import os

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def topology():
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    net.addSatellite('sat1', catnr=25544) # ISS
    net.addSatellite('sat2', catnr=48274) # Starlink
    net.addSatellite('sat3', catnr=56393) # Starlink
    net.addSatellite('sat4', catnr=27426) # INTELSAT
    net.addSatellite('sat5', catnr=44874) # CHEOPS
    net.addSatellite('sat6', catnr=41860) # GALILEO
    net.addSatellite('sat7', catnr=42063) # SENTINEL-2B
    net.addSatellite('sat8', catnr=43013) # NOAA-20
    net.addSatellite('sat9', catnr=25994) # TERRA
    net.addSatellite('sat10', catnr=27424) # AQUA

    num_aircrafts = 20
    for i in range(1, num_aircrafts + 1):
        name = f'plane{i}'
        ip = f'10.0.0.{i}/8'
        net.addAircraft(name, ip=ip)
    decoder1 = net.addHost('decoder1', ip='10.0.0.5/8')
    ap1 = net.addAccessPoint('LIS1', ssid="ads-b", mode="g", channel="1",
                             position='-9.13, 38.73, 0', failMode='standalone')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=1)

    info("*** Configuring nodes\n")
    net.configureNodes()

    path = os.path.dirname(os.path.abspath(__file__))
    nodes = net.aircrafts + net.aps + net.satellites
    net.telemetry(nodes=nodes, data_type='position', image='{}/image10.jpg'.format(path),
                  min_x=-180, max_x=180, min_y=-90, max_y=90, icon_text_size=12,
                  icon='plane.png', icon_width=1.6, icon_height=1.6)

    info("*** Starting network\n")
    net.start()

    info("*** Configure Satellites\n")
    net.configureSatellites('{}/satellites.txt'.format(path))

    info("*** Configure Aircrafts\n")
    net.configureAircrafts(38.73, -9.13, 2000000) # lat, long, range

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
