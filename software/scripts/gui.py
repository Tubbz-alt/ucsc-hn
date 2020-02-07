#!/usr/bin/env python3

import pyrogue

pyrogue.addLibraryPath('../../firmware/submodules/rce-gen3-fw-lib/python')
pyrogue.addLibraryPath('../../firmware/submodules/surf/python')
pyrogue.addLibraryPath('../../firmware/python')
pyrogue.addLibraryPath('../python')

import pyrogue.pydm
import pyrogue.gui
import rogue
import logging

from ucsc_hn_app.MultiRenaRoot import MultiRenaRoot

#rogue.Logging.setFilter('pyrogue.memory.block.InterCardRoot.PcieControl[0].Fpga.PrbsTx',rogue.Logging.Debug)
#rogue.Logging.setFilter('pyrogue.memory.block',rogue.Logging.Debug)

#rogue.Logging.setLevel(rogue.Logging.Debug)

#logger = logging.getLogger('pyrogue.PollQueue')
#logger.setLevel(logging.DEBUG)

with MultiRenaRoot(host="192.168.2.50",pollEn=True) as root:

    pyrogue.pydm.runPyDM(root=root)
    #pyrogue.gui.runGui(root=root)
    #pyrogue.waitCntrlC()


