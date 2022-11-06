"""
FP run.py
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.term import makeTerm
from minicps.mcps import MiniCPS
from topo import FPTopo

import sys, time


class FPCPS(MiniCPS):

    """Main container used to run the simulation."""

    def __init__(self, name, net, sleep=0.5):

        self.name = name
        self.net = net
        debug = True
        net.start()
        net.pingAll()

        plc1, plc2, plc3, s1, hmi, attacker, server = self.net.get(
            "plc1",
            "plc2",
            "plc3",
            "s1",
            "hmi",
            "attacker",
            "server",
        )

        if not debug:

            s1.cmd(
                sys.executable + " -u " + " physical_process.py  &> logs/process.log &"
            )
            time.sleep(sleep)
            s1.cmd(
                sys.executable
                + " -u "
                + " physical_process_bottle.py  &> logs/process_bottle.log &"
            )
            time.sleep(sleep)
            server.cmd(sys.executable + " -u " + " server.py &> logs/server.log &")
            time.sleep(sleep)
            plc3.cmd(sys.executable + " -u " + " plc3.py  &> logs/plc3.log &")
            time.sleep(sleep)
            plc2.cmd(sys.executable + " -u " + " plc2.py &> logs/plc2.log &")
            time.sleep(sleep * 3)  # sleeping a bit more to make sure the PLCs are up

            plc1.cmd(sys.executable + " -u " + " plc1.py  &> logs/plc1.log &")
            time.sleep(sleep)
            net.terms += makeTerm(plc1, title="plc1", display=None)
            time.sleep(sleep)
            net.terms += makeTerm(hmi, title="hmi", display=None)
            time.sleep(sleep)
            server.cmd(sys.executable + " -u " + " server.py &> logs/server.log &")
            time.sleep(sleep)
            net.terms += makeTerm(attacker, title="attacker", display=None)
            time.sleep(sleep)

        else:
            # Th first 4 mostly wont change
            net.terms += makeTerm(
                s1,
                title="physical_process_bottle",
                display=None,
                cmd="python3 physical_process_bottle.py",
            )
            time.sleep(sleep)
            net.terms += makeTerm(
                s1,
                title="physical_process",
                display=None,
                cmd="python3 physical_process.py",
            )
            time.sleep(sleep)
            net.terms += makeTerm(
                server,
                title="server",
                display=None,
                cmd="python3 server.py",
            )
            time.sleep(sleep)
            net.terms += makeTerm(
                plc3,
                title="plc3",
                display=None,
                cmd="python3 plc3.py",
            )
            time.sleep(sleep)
            net.terms += makeTerm(
                plc2,
                title="plc2",
                display=None,
                cmd="python3 plc2.py",
            )
            time.sleep(sleep)
            net.terms += makeTerm(
                plc1,
                title="plc1",
                display=None,
                cmd="python3 plc1.py",
            )
            time.sleep(
                sleep * 2
            )  # make sure everything is up and running before starting the HMI and attacker

            # timer = 10  # number in minutes
            # net.terms += makeTerm(
            #     hmi,
            #     title="hmi",
            #     display=None,
            #     cmd=f"python3 attack_fdi.py {timer}",
            # )
            time.sleep(sleep)
            net.terms += makeTerm(attacker, title="attacker", display=None)

        CLI(self.net)
        self.net.stop()


if __name__ == "__main__":

    topo = FPTopo()
    net = Mininet(topo=topo)
    fpcps = FPCPS(name="FPCPS", net=net)
