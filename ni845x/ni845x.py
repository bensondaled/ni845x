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
    def __init__(self):
       
        # Determine available devices
        NextDevice = ctypes.create_string_buffer(DEV_SIZE)
        FindDeviceHandle = ctypes.c_int32()
        NumberFound = ctypes.c_int32()
        
        self._DeviceHandle = 0
        
        errChk(dll.ni845xFindDevice(ctypes.byref(NextDevice), ctypes.byref(FindDeviceHandle), ctypes.byref(NumberFound)))

        if NumberFound.value != 1:
            raise Exception('Only implemented support for exactly 1 USB card. {} found.'.format(NumberFound.value))
        self._name = NextDevice
        
        self._open()

    def _open(self):
        self.dev_handle = ctypes.c_int32()
        errChk(dll.ni845xOpen(ctypes.byref(self._name), ctypes.byref(self.dev_handle)))
        
    def end(self):
        errChk(dll.ni845xClose(self.dev_handle))
