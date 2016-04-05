import ctypes
import numpy as np

MAX_SIZE = 1024
DEV_SIZE = 256

dll = ctypes.windll.LoadLibrary('Ni845x.dll')

class Ni845xError(Exception):
    def __init__(self, status_code):

        message = ctypes.create_string_buffer(MAX_SIZE)
        
        dll.ni845xStatusToString(status_code, MAX_SIZE, message)
        
        Exception.__init__(self, message.value)
        
def errChk(err):
    if err:
        raise Ni845xError(err)


class NI845x():
    VOLTS33 = 33
    VOLTS25 = 25
    VOLTS18 = 18
    VOLTS15 = 15
    VOLTS12 = 12
    INPUT,OUTPUT = 0,1
    def __init__(self):
       
        # Determine available devices
        NextDevice = ctypes.create_string_buffer(DEV_SIZE)
        FindDeviceHandle = ctypes.c_int32()
        NumberFound = ctypes.c_int32()
                
        errChk(dll.ni845xFindDevice(ctypes.byref(NextDevice), ctypes.byref(FindDeviceHandle), ctypes.byref(NumberFound)))

        if NumberFound.value != 1:
            raise Exception('Only implemented support for exactly 1 USB card. {} found.'.format(NumberFound.value))
        self._name = NextDevice
        
        self._open()
        self.set_io_voltage_level(self.VOLTS33)
        self.set_port_line_direction_map(self.OUTPUT*np.ones(8))

    def _open(self):
        self.dev_handle = ctypes.c_int32()
        errChk(dll.ni845xOpen(ctypes.byref(self._name), ctypes.byref(self.dev_handle)))
    
    def set_port_line_direction_map(self, mapp, port=0):
        # mapp: np array or list with 8 0's or 1's
        # 0 = input, 1 = output
        port = ctypes.c_uint8(port)
        mapp = np.asarray(mapp)
        assert len(mapp)==8
        r = np.arange(7,-1,-1)
        _map = np.sum(2**r * mapp).astype(int)
        bitmap = ctypes.c_uint8(_map)
        errChk(dll.ni845xDioSetPortLineDirectionMap(self.dev_handle, port, bitmap))
        
    def set_io_voltage_level(self, lev):
        lev = ctypes.c_uint8(lev)
        errChk(dll.ni845xSetIoVoltageLevel(self.dev_handle, lev))
    
    def end(self):
        errChk(dll.ni845xClose(self.dev_handle))

    def write_dio(self, line, val, port=0):
        line = ctypes.c_uint8(line)
        port = ctypes.c_uint8(port)
        val = ctypes.c_int32(val)
        errChk(dll.ni845xDioWriteLine( self.dev_handle, port, line, val ))
        