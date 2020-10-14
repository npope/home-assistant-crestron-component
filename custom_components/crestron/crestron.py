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
        self._serial = {}
        self._writer = None
        self._callbacks = set()
        self._server = None
        self._available = False
        self._sync_all_joins_callback = None

    async def start(self, port):
        ''' Start TCP XSIG server listening on configured port '''
        server = await asyncio.start_server( self.handle_connection, '0.0.0.0', port)
        self._server = server
        addr = server.sockets[0].getsockname()
        _LOGGER.info(f'Listening on {addr}:{port}')
        server.serve_forever()

    async def stop(self):
        ''' Stop TCP XSIG server '''
        self._available = False
        for callback in self._callbacks:
            await callback("available", "False")
        _LOGGER.info('Stop called. Closing connection')
        self._server.close()

    def register_sync_all_joins_callback(self, callback):
        ''' Allow callback to be registred for when control system requests an update to all joins '''
        self._sync_all_joins_callback = callback

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
            await callback("available", "True")

        connected = True
        while connected:
            data = await reader.read(1)
            if data:
                # Sync all joins request
                if data[0] == b'\xfb':
                    _LOGGER.debug("Got update all joins request")
                    if self._sync_all_joins_callback is not None:
                        self._sync_all_joins_callback()
                else:
                    data += await reader.read(1)
                    # Digital Join
                    if data[0] & 0b11000000 == 0b10000000 and data[1] & 0b10000000 == 0b00000000:
                        header = struct.unpack('BB',data)
                        join = ((header[0] & 0b00011111) << 7 | header[1]) + 1 
                        value = ~header[0] >> 5 & 0b1
                        self._digital[join] = True if value==1 else False
                        _LOGGER.debug(f'Got Digital: {join} = {value}')
                        for callback in self._callbacks:
                            await callback(f"d{join}", str(value))
                    # Analog Join
                    elif data[0] & 0b11001000 == 0b11000000 and data[1] & 0b10000000 == 0b00000000:
                        data += await reader.read(2)
                        header = struct.unpack('BBBB', data)
                        join = ((header[0] & 0b00000111) << 7 | header[1]) + 1
                        value = (header[0] & 0b00110000) << 10 | header[2] << 7 | header[3]
                        self._analog[join] = value
                        _LOGGER.debug(f'Got Analog: {join} = {value}')
                        for callback in self._callbacks:
                            await callback(f"a{join}", str(value))
                    # Serial Join
                    elif data[0] & 0b11111000 == 0b11001000 and data[1] & 0b10000000 == 0b00000000:
                        data += await reader.readuntil(b'\xff')
                        header = struct.unpack( 'BB', data[:2] )
                        join = (( header[0] & 0b00000111) << 7 | header[1]) + 1
                        string = data[2:-1].decode("utf-8")
                        self._serial[join] = string
                        _LOGGER.debug(f'Got String: {join} = {string}')
                        for callback in self._callbacks:
                            await callback(f"s{join}", string)
                    else:
                        _LOGGER.debug(f'Unknown Packet: {data.hex()}')
            else:
                _LOGGER.info('Control system disconnected')
                connected = False
                self._available = False
                for callback in self._callbacks:
                    await callback("available", "False")

    def is_available (self):
        '''Returns True if control system is connected'''
        return self._available

    def get_analog (self, join):
        ''' Return analog value for join'''
        return self._analog.get(join, 0)

    def get_digital (self, join):
        ''' Return digital value for join'''
        return self._digital.get(join, False)

    def get_serial (self, join):
        ''' Return serial value for join'''
        return self._serial.get(join, "")

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

    def set_serial (self, join, string):
        ''' Send String Join to Crestron XSIG symbol '''
        if len(string) > 252:
            _LOGGER.info(f'Could not send. String too long ({len(string)}>252)')
            return
        elif self._writer:
          data =  struct.pack('>BB', 0b11001000 | ( (join - 1) >> 7 ), (join - 1) & 0b01111111)
          data += string.encode()
          data += b'\xff'
          self._writer.write(data)
          _LOGGER.debug(f'Sending Serial: {join}, {string}')
        else:
          _LOGGER.info('Could not send.  No connection to hub')
