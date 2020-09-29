import asyncio
import struct
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

class CrestronHub():

    def __init__(self):
        ''' Initialize CrestronHub object '''
        self._digital = {}
        self._analog = {}
        self._writer = None
        self._callbacks = set()
        self._server = None
        self._available = False
        for callback in self._callbacks:
            callback()

    async def start(self, port):
        ''' Start TCP XSIG server listening on configured port '''
        server = await asyncio.start_server( self.handle_connection, '0.0.0.0', port)
        self._server = server
        addr = server.sockets[0].getsockname()
        _LOGGER.info(f'Listening on {addr}:{port}')
        server.serve_forever()

    def stop(self):
        ''' Stop TCP XSIG server '''
        self._available = False
        for callback in self._callbacks:
            callback()
        self._server.close()

    def register_callback(self, callback):
        ''' Allow callbacks to be registered for when dict entries change '''
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        ''' Allow callbacks to be de-registered '''
        self._callbacks.discard(callback)


    async def handle_connection (self, reader, writer):
        ''' Parse packets from Crestron XSIG symbol '''
        self._writer = writer
        peer = writer.get_extra_info('peername')
        _LOGGER.info(f'Control system connection from {peer}')
        _LOGGER.debug('Sending update request')
        writer.write(b'\xfd')
        self._available = True
        for callback in self._callbacks:
            callback()

        connected = True
        while connected:
            data = await reader.read(1)
            if data:
                if data[0] & 0b11000000 == 0b10000000:
                    data += await reader.read(1)
                    unpack = struct.unpack('BB',data)
                    join = (unpack[1] | (unpack[0] & 0b00011111) << 7) + 1 
                    value = ~unpack[0] >> 5 & 0b1
                    self._digital[join] = True if value==1 else False
                    _LOGGER.debug(f'Got Digital: {join} = {value}')
                    for callback in self._callbacks:
                        callback()
                elif data[0] & 0b11001000 == 0b11000000:
                    data += await reader.read(3)
                    unpack = struct.unpack('BBBB', data)
                    join = (unpack[1] | (unpack[0] & 0b00000111) << 7) + 1
                    value = unpack[3] | unpack[2] << 7 | (unpack[0] & 0b00110000) << 10
                    self._analog[join] = value
                    _LOGGER.debug(f'Got Analog: {join} = {value}')
                    for callback in self._callbacks:
                        callback()
                else:
                    _LOGGER.debug(f'Unknown Packet: {data.hex()}')
            else:
                _LOGGER.info('Control system disconnected')
                connected = False
                self._available = False
                for callback in self._callbacks:
                    callback()

    def is_available (self):
        '''Returns True if control system is connected'''
        return self._available

    def get_analog (self, join):
        ''' Return analog value for join'''
        return self._analog.get(join, 0)

    def get_digital (self, join):
        ''' Return digital value for join'''
        return self._digital.get(join, False)

    def set_analog (self, join, value):
        ''' Send Analog Join to Crestron XSIG symbol '''
        if self._writer:
          data =  struct.pack('>BBBB', 0b11000000 | ( value >> 10 & 0b00110000 ) | (join - 1) >> 7,
            (join - 1) & 0b01111111, value >> 7 & 0b01111111, value & 0b01111111 )
          self._writer.write(data)
          _LOGGER.debug(f'Sending Analog: {join}, {value}')
        else:
          _LOGGER.info('Could not send.  No connection to hub')

    def set_digital (self, join, value):
        ''' Send Digital Join to Crestron XSIG symbol '''
        if self._writer:
          data = struct.pack('>BB', 0b10000000 | ( ~value << 5 & 0b00100000 ) | (join - 1) >> 7,
            (join - 1) & 0b01111111)
          self._writer.write(data)
          _LOGGER.debug(f'Sending Digital: {join}, {value}')
        else:
          _LOGGER.info('Could not send.  No connection to hub')

