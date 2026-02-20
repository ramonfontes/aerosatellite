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
    num_aircrafts = 2
    aircrafts = []
    for i in range(1, num_aircrafts + 1):
        name = f'plane{i}'
        aircraft = net.addAircraft(name)
        aircrafts.append(aircraft)

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=1)

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Creating links\n")
    mesh_params = {
        'cls': mesh,
        'ssid': 'meshNet',
        'channel': 5,
        'ht_cap': 'HT40+'
    }
    for i, plane in enumerate(aircrafts, start=1):
        intf_name = f"plane{i}-wlan0"
        net.addLink(plane, intf=intf_name, **mesh_params)

    path = os.path.dirname(os.path.abspath(__file__))
    nodes = net.aircrafts
    net.telemetry(nodes=nodes, data_type='position', image='{}/map.jpg'.format(path),
                  min_x=-20_015_000, max_x=20_015_000, min_y=-10_007_000, max_y=10_007_000, icon_text_size=12,
                  icon='{}/plane.png'.format(path), icon_width=150000, icon_height=150000)

    info("*** Starting network\n")
    net.start()

    info("*** Configure Aircrafts\n")
    net.configureAircrafts(38.73, -9.13, 150000, protocol='adsb')  # lat, long, range

    for node in aircrafts:
        makeTerm(node, title=node.name+"-sender", cmd="bash -c 'python sender.py {};'".format(node.name))
        makeTerm(node, title=node.name+"-decoder", cmd="bash -c 'python decoder.py {} {} {};'".format(node.name, 740000, 85000))

    info("*** Running CLI\n")
    CLI(net)

    info('*** Kill xterm terminals\n')
    os.system('pkill -9 -f \"xterm\"')

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
