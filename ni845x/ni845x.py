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

    def configure_i2c(self, size=dll.kNi845xI2cAddress7Bit, address=0, clock_rate=100):
        """
        Set the ni845x I2C configuration.
        
        Parameters
        ----------
            size : Configuration address size (default 7Bit).
            address : Configuration address (default 0).
            clock_rate : Configuration clock rate in kilohertz (default 100).

        Returns
        -------
            None
        """
        
        #
        # create configuration reference
        #
        errChk(ni845xI2cConfigurationOpen(&self._I2CHandle))
        
        #
        # configure configuration properties
        #
        errChk(ni845xI2cConfigurationSetAddressSize(self._I2CHandle, size))
        errChk(ni845xI2cConfigurationSetAddress(self._I2CHandle, address))
        errChk(ni845xI2cConfigurationSetClockRate(self._I2CHandle, clock_rate))
        
    def I2cClose(self):
        """
        Release the handles to the ni845x I2C interface.

        Parameters
        ----------
            None

        Returns
        -------
            None
        """

        if self._I2CHandle:
            ni845xI2cConfigurationClose(self._I2CHandle)
            
        if self._DeviceHandle:
            ni845xClose(self._DeviceHandle)
