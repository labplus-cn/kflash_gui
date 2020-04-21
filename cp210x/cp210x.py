# coding=utf-8

""" CP2104.GPIO2控制一个多路器切换串口连接目标:
GPIO2 = 0, target = K210
GPIO2 = 1, target = ESP32

Returns
-------
[type]
    [description]

Raises
------
OSError
    [description]
"""

import os
import usb.core
import usb.util
import serial.tools.list_ports

class cp2104:

    def _find_cp210x_by(self, name):
        # 根据串口名称查找序列号
        ports = serial.tools.list_ports.grep(name)
        serial_number = None
        for port in ports:
            serial_number = port.serial_number
            # print("{0}:vid = {1:04X}, pid = {2:04X}, serial = {3}".format(port.name, port.vid, port.pid, port.serial_number))
            break   # 只寻找一个设备
        
        # 根据设备序列号查找制定的usb device
        # serial_number = '01C96F79'
        device_finded = False
        if serial_number != None:
            for device in usb.core.find(idVendor=0x10c4, idProduct=0xea60, find_all=True):
                # print(device)
                if device.serial_number == serial_number:
                    device_finded = True
                    break
        if device_finded:
            return device
        else:
            return None
        # return usb.core.find(idVendor=0x10c4, idProduct=0xea60)

    def __init__(self, name):
        self.dev = self._find_cp210x_by(name)
        if self.dev == None:
            raise OSError("not found cp2104")

    def write_gpio(self, io_num, new_state):
        if self.dev != None:
            reqType = 0x41  
            bReq = 0xff     # VENDOR_SPECIFIC
            wVal = 0x37E1   # WRITE_LATCH(cp2103/4)
            # The write latch value that is supplied in wIndex is represented as follows:
            #   bits 0–7: Mask of the latch state (in bits 8-15) to write, where bit 0 is GPIO0, bit 1 is GPIO1, etc. up tp
            #   GPIOn where n is the total number of GPIO pins the interface supports.
            #   bits 8–15: Latch state to write, where bit 8 is GPIO0, bit 9 is GPIO1, etc. up to GPIOn where n is the total
            #   number of GPIO pins the interface supports.
            latch_mask = 0x0001 << io_num
            latch = 0x0000
            if new_state == 1:
                latch = 0x0100 << io_num
            wIndex = latch | latch_mask # the write
            self.dev.ctrl_transfer(reqType, bReq, wVal, wIndex)

    def read_gpio(self,io_num):
        if self.dev != None:
            reqType = 0x41  
            bReq = 0xff     # VENDOR_SPECIFIC
            wVal = 0x00C2   # READ_LATCH(cp2103/4)
            # The read latch value that is returned is represented as follows:
            #   bits 0–7: Current latch state, where bit 0 is GPIO0, bit 1 is GPIO1, etc. up to GPIOn where n is the total
            #   number of GPIO pins the interface supports.
            wIndex = 0
            result = self.dev.ctrl_transfer(reqType, bReq, wVal, wIndex)
            if resul & (0x0001 << io_num):
                return 1
            else:
                return 0         
                
# cp = cp2104('/dev/ttyUSB0')
# cp.write_gpio(0, 0)
# cp.close()