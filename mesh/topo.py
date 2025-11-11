#!/usr/bin/env python

"""
This example is implemented using celestrak
"""

import os
from datetime import datetime, timezone

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
    # Lista dos CATNRs dos satélites Starlink
    catnrs = [
        44714, 44716, 44717, 44718, 44723, 44724, 44725, 44736, 44741, 44744,
        44747, 44748, 44751, 44752, 44753, 44758, 44759, 44765, 44768, 44771
    ]

    # Criação automática dos satélites
    sats = []
    for i, catnr in enumerate(catnrs, start=1):
        name = f"sat{i}"
        sat = net.addSatellite(name, catnr=catnr)
        sats.append(sat)

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=1.2)

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Creating links\n")
    mesh_params = {
        'cls': mesh,
        'ssid': 'meshNet',
        'channel': 5,
        'ht_cap': 'HT40+'
    }
    for i, sat in enumerate(sats, start=1):
        intf_name = f"sat{i}-wlan0"
        net.addLink(sat, intf=intf_name, **mesh_params)

    path = os.path.dirname(os.path.abspath(__file__))
    nodes = net.satellites
    net.telemetry(nodes=nodes, data_type='position', image='{}/map.jpg'.format(path),
                  min_x=-20_015_000, max_x=20_015_000, min_y=-10_007_000, max_y=10_007_000, icon_text_size=12,
                  icon='{}/plane.png'.format(path), icon_width=10.6, icon_height=10.6)

    info("*** Starting network\n")
    net.start()

    info("*** Configure Satellites\n")
    net.configureSatellites('{}/satellites.txt'.format(path), start_time=datetime(2025, 11, 11, 12, 0, 0, tzinfo=timezone.utc))

    makeTerm(sats[4], title='sat5', cmd="bash -c 'ping 10.0.0.18;'")
    makeTerm(sats[14], title='sat15', cmd="bash -c 'ping 10.0.0.6;'")

    info("*** Running CLI\n")
    CLI(net)

    info('*** Kill xterm terminals\n')
    os.system('pkill -9 -f \"xterm\"')

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
