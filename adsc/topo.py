#!/usr/bin/env python

"""
This example is implemented using celestrak
"""

import os

from mininet.term import makeTerm
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, mesh
from mn_wifi.wmediumdConnector import interference


def topology():
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    sat1 = net.addSatellite('sat1', catnr=26900) # Intelsat 901

    num_aircrafts = 1
    planes = {}
    for i in range(1, num_aircrafts + 1):
        name = f'plane{i}'
        planes[name] = net.addAircraft(name)

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=2)

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Creating links\n")
    net.addLink(planes['plane1'], cls=mesh, ssid='meshNet', ip6="2001:db8:10::1/64",
                intf='plane1-wlan0', channel=5, ht_cap='HT40+')

    sats = [sat1]
    mesh_params = {
        'cls': mesh,
        'ssid': 'meshNet',
        'channel': 5,
        'ht_cap': 'HT40+'
    }
    for i, sat in enumerate(sats, start=1):
        intf_name = f'sat{i}-wlan0'
        net.addLink(sat, intf=intf_name, ip6=f'2001:db8:10::2/64' , **mesh_params)

    path = os.path.dirname(os.path.abspath(__file__))
    nodes = net.aircrafts + net.satellites
    net.telemetry(nodes=nodes, data_type='position', image='{}/map.jpg'.format(path),
                  min_x=-180, max_x=180, min_y=-90, max_y=90, icon_text_size=12,
                  icon='{}/plane.png'.format(path), icon_width=10.6, icon_height=10.6)

    info("*** Starting network\n")
    net.start()

    sat1.cmd('ip -6 route add default dev sat1-mp0')
    planes['plane1'].cmd('ip -6 route add default dev plane1-mp0')

    info("*** Configure Satellites\n")
    net.configureSatellites('{}/satellites.txt'.format(path))

    info("*** Configure Aircrafts\n")
    net.configureAircrafts(21, -32, 2000000, protocol='adsc') # lat, long, range

    makeTerm(planes["plane1"], title='plane1', cmd="bash -c 'python sender.py {};'".format("plane1"))
    makeTerm(sat1, title='sat1', cmd="bash -c 'python decoder.py {};'".format("sat1"))

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
