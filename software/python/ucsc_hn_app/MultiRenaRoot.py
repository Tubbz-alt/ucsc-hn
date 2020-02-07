import pyrogue
import pyrogue.protocols
import rogue
import surf.protocols.pgp as pgp
import surf.protocols.batcher
import surf.protocols.ssi
import surf.ethernet.udp
import RceG3
import ucsc_hn

class MultiRenaRoot(pyrogue.Root):
    def __init__(self,host="",pollEn=True):
        pyrogue.Root.__init__(self,name='MultiRenaRoot',description='tester', pollEn=pollEn)

        self._remMem = rogue.interfaces.memory.TcpClient(host, 9000)

        self.add(ucsc_hn.MultiRena(memBase=self._remMem))

        self._remRssi = pyrogue.protocols.UdpRssiPack(port=8192,host=host,packVer=2)

        self._prbsRx = pyrogue.utilities.prbs.PrbsRx(width=32)

        self._remRssi.application(0) >> self._prbsRx

