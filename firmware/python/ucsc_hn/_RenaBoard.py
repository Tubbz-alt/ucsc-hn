import pyrogue as pr
import ucsc_hn

class RenaBoard(pr.Device):
    def __init__(self, board, **kwargs):
        super().__init__(description="Rena Board Configuration", **kwargs)

        # Geographic Data
        self._board = board # Rena FPGA

        for i in range(2):
            self.add(ucsc_hn.RenaAsic(rena=i,name=f'Rena[{i}]'))

        self.add(pr.LocalVariable(name='ReadoutEnable',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Disable',1:'Enable'},
                                  description='Readout Enable'))

        self.add(pr.LocalVariable(name='ForceTrig',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Disable',1:'Enable'},
                                  description='Force Trigger Enable'))

        self.add(pr.LocalVariable(name='SerialNumber',
                                  value=0,
                                  mode='RW',
                                  description='Rena Board Serial Number'))

        self.add(pr.LocalVariable(name='OrMode',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Disable',1:'Enable'},
                                  description='Rena Board OR Mode'))

        self.add(pr.LocalVariable(name='SelectiveRead',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Disable',1:'Enable'},
                                  description='Channel Selective Read'))

        self.add(pr.LocalVariable(name='IntermediateBoard',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Even',1:'Odd',2:'Debug'},
                                  description='Intermediate Board'))

        self.add(pr.LocalVariable(name='FollowerEn',
                                  value=0,
                                  mode='RW',
                                  enum={0:'Disable',1:'Enable'},
                                  description='Follower Enable'))

        self.add(pr.LocalVariable(name='FollowerAsic',
                                  value=0,
                                  mode='RW',
                                  description='Follower ASIC'))

        self.add(pr.LocalVariable(name='FollowerChannel',
                                  value=0,
                                  mode='RW',
                                  description='Follower Channel'))


        @self.command()
        def ConfigBoard():
            for data in self.buildBoardConfigMessage(True):
                self.parent.sendData(data)


    @property
    def board(self):
        return self._board


    def buildBoardIdSub(self,bcast=False):
        data = bytearray(5)
        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer

        if bcast:
            data[2] = 0x3f # Broadcast
        else:
            data[2] = self.board & 0x3F # Rena Board address

        data[3] = 0x83 # Store address
        data[4] = 0xFF # End of packet

        return data


    def buildReadoutEnableSub(self,enable):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer

        if enable or self.ReadoutEnable.value():
            data[2] = 0x03

        data[3] = 0x49
        data[4] = 0xFF  # End of packaget

        return data


    def buildOrModeSub(self,enable):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer

        if enable or self.OrMode.value():
            data[2] = 0x03

        data[3] = 0x46
        data[4] = 0xFF  # End of packaget

        return data


    def buildForceTriggerSub(self,enable):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer

        if enable or self.ForceTrig.value():
            data[2] = 0x03

        data[3] = 0x47
        data[4] = 0xFF  # End of packaget


    def buildSelectiveReadSub(self):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer

        if self.SelectiveRead.value():
            data[2] = 0x01

        data[3] = 0x48
        data[4] = 0xFF  # End of packaget

        return data


    def buildIntermediateBoardSub(self):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer
        data[2] = self.IntermediateBoard.value() & 0x3f
        data[3] = 0x4a
        data[4] = 0xFF  # End of packaget

        return data


    def buildDiagnosticSub(self):
        data = bytearray(5)

        data[0] = 0xC0 # Packet start
        data[1] = 0x81 # Clear buffer
        data[2] = self.board & 0x3F # Rena Board address
        data[3] = 0x4E
        data[4] = 0xFF # End of packet

        return data


    def buildFollowerConfigSub(self):

        if self.FollowerEn.value():
            data = bytearray(7)

            data[0] = 0xC0 # Packet start
            data[1] = 0x81 # Clear buffer

            if self.FollowerAsic.value() == 0:
                data[2] = 0x01
            else:
                data[2] = 0x02

            data[3] = self.FollowerChannel.value() & 0x3F
            data[4] = 0x00 # Number of times to toggle TCLK 0 for PHA, 1 for U?, 2 for V?
            data[5] = 0x4D
            data[6] = 0xFF # End of packet

            return data

        else:
            data = bytearray(5)

            data[0] = 0xC0 # Packet start
            data[1] = 0x81 # Clear buffer
            data[2] = 0x3F # Turn off follower mode
            data[3] = 0x4D
            data[4] = 0xFF # End of packet

            return data



    def buildForceTriggerMessage(self,enable):
        yield self.buildBoardIdSub()
        yield self.buildForceTrigger(enable)
        yield self.buildReadoutEnable(enable)


    def buildReadoutModeMessage(self,enable):
        yield self.buildBoardIdSub()
        yield self.buildReadoutEnable(False)
        yield self.buildOrModeSub()
        yield self.buildForceTriggerSub(False)
        yield self.buildSelectiveReadSub()
        yield self.buildIntermediateBoardSub()


    def buildBoardConfigMessage(self,diagEnable):
        for rena in range(2):
            for channel in range(36):
                yield self.buildBoardIdSub()
                yield self.node(f'Rena[{rena}]').node(f'Channel[{channel}]').buildChannelConfigSub()
                if diagEnable:
                    yield self.buildDiagnosticSub()

        yield self.buildFollowerConfigSub()


    def buildBoardDiagMessage(self):
        yield self.buildBoardIdSub()
        yield self.buildDiagnosticSub()



    def _rxDiagnostic(self,ba):
        pass

