import ctypes
import numpy as np

MAX_SIZE = 1024
DEV_SIZE = 256

class Ni845xError(Exception):
    def __init__(self, status_code):

        cdef bytes message
        cdef char status_string[MAX_SIZE]
        
        ni845xStatusToString(status_code, MAX_SIZE, status_string)
        message = status_string
        
        Exception.__init__(self, message)
        
def errChk(err):
    if err:
        raise Ni845xError(err)

class NI845x():
    def __init__(self):

        self.dll = ctypes.windll.LoadLibrary('Ni845x.dll')
       
        # Determine available devices
        NextDevice = ctypes.create_string_buffer(DEV_SIZE)
        FindDeviceHandle = ctypes.c_int32()
        NumberFound = ctypes.c_int32()
        
        self._DeviceHandle = 0
        self._I2CHandle = 0
        
        errChk(self.dll.ni845xFindDevice(NextDevice, &FindDeviceHandle, &NumberFound))
            
        self.devices_list = [NextDevice]
        
        for i in range(NumberFound-1):
            errChk(ni845xFindDeviceNext(FindDeviceHandle, NextDevice))
            self.devices_list.append(NextDevice)
        
        self._name = self.devices_list[0]

