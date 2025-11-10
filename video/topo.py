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
    sta1 = net.addStation('sta1', position='-49,-5,0')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=1.5)

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Creating links\n")
    net.addLink(sat1, cls=mesh, ssid='meshNet',
                intf='sat1-wlan0', channel=5, ht_cap='HT40+')
    net.addLink(sta1, cls=mesh, ssid='meshNet',
                intf='sta1-wlan0', channel=5, ht_cap='HT40+')

    path = os.path.dirname(os.path.abspath(__file__))
    nodes = net.satellites + net.stations
    net.telemetry(nodes=nodes, data_type='position', image='{}/map.jpg'.format(path),
                  min_x=-180, max_x=180, min_y=-90, max_y=90, icon_text_size=12,
                  icon='{}/plane.png'.format(path), icon_width=10.6, icon_height=10.6)

    info("*** Starting network\n")
    net.start()

    info("*** Configure Satellites\n")
    net.configureSatellites('{}/satellites.txt'.format(path))

    makeTerm(sat1, title='sat1', cmd="bash -c 'cvlc --loop video.mp4 --sout \"#transcode{vcodec=h264,vb=500,scale=0.5,acodec=mp3,ab=64,channels=2,samplerate=44100}:rtp{dst=10.0.0.2,port=5004,mux=ts}\" :no-sout-all :sout-keep;'")
    makeTerm(sta1, title='sta1', cmd="bash -c 'cvlc rtp://@:5004;'")

    info("*** Running CLI\n")
    CLI(net)

    info('*** Kill xterm terminals\n')
    os.system('pkill -9 -f \"xterm\"')

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
