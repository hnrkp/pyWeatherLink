"""

    This file is part of the pyWeatherLink package,
    Copyright 2008 by Henrik Persson <root@fulhack.info>.

    pyWeatherLink is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    pyWeatherLink is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyWeatherLink.  If not, see <http://www.gnu.org/licenses/>.

"""

import serial
import struct
import time

from conversions import *

from datatypes import SensorImage, ArchiveImage

class Link:
    def __init__(self):
        self.__ser = serial.Serial('/dev/ttyS1', 2400, timeout=10)

    def __del__(self):
        self.__ser.close()

    def checkAck(self):
        resp = self.__ser.read()
        
        if resp == '':
            raise Exception("Timeout waiting for ack")
        
        ack = struct.unpack("<B", resp)

        if ack[0] == 0x21:
            raise Exception("Response NOK!")

        if ack[0] != 0x06:
            raise Exception("Response was not NOK, but not ACK either..")

    def getSensorImage(self):
        numLoops = struct.pack("<H", 0xFFFF)

        self.__ser.write("LOOP"+numLoops+"\r");

        self.checkAck()

        buf = self.__ser.read(18)
            
        response = struct.unpack("<BhhBHHBBHHH", buf)
        
        #TODO: Implement CRC-CCITT-check of the last Uint16! See Techref page 9.
        
        if response[0] != 0x01:
            raise Exception("Start of block-byte was not 0x01")
            
        img = SensorImage()
        img.WindSpeed = mph2kts(response[3])
        img.WindDirection = response[4]
        img.IndoorTemperature = f2c(float(response[1])/10)
        img.OutdoorTemperature = f2c(float(response[2])/10)
        
        return img
    
    def getArchiveImage(self):
        #buf = self.readLinkMem(4, 1, 0x3A)
        #periods = struct.unpack("<BB", buf)
        #print "SamplePeriod (s)" + str(256-periods[0]) + " archive period (m)" + str(periods[1])

        img = ArchiveImage()
        
        buf = self.readLinkMem(4, 1, 0x9C)
        
        wind = struct.unpack("<BB", buf)
        if wind[1] == 0xFF:
            img.AverageWindSpeed = 0
            img.DominantWindDirection = 0
        else:
            img.AverageWindSpeed = wind[0]
            img.DominantWindDirection = wind[1]*24
        
        buf = self.readLinkMem(2, 1, 0xA4) 
        
        img.Gust = struct.unpack("<B", buf)[0]
        
        return img
    
    def setArchiveTime(self, minutes):
        data = struct.pack("<B", minutes)
        
        self.__ser.write("SAP"+data+"\r")
        self.checkAck()
    
    def setSampleTime(self, seconds):
        data = struct.pack("<B", 256-seconds)
        
        self.__ser.write("SSP"+data+"\r")
        self.checkAck()
    
    def readLinkMem(self, nibbles, bank, addr):
        if nibbles > 8:
            raise Exception("nibbles > 8")
        
        data = struct.pack("<BBB", bank, addr, nibbles-1)
        
        self.__ser.write("RRD"+data+"\r")    
        
        self.checkAck()
        
        bufLen = int(float(nibbles)/2+0.5)
        
        buf = self.__ser.read(bufLen)
        
        return buf
    
    def readStationMem(self, nibbles, bank, addr):
        b = 2
        if bank == 0: b = 2
        if bank == 1: b = 4
        
        nib = (nibbles << 4) | b
        
        addr = struct.pack("<BB", nib, addr)
        
        self.__ser.write("WRD"+addr+"\r")    
        
        self.checkAck()
        
        bufLen = int(float(nibbles)/2+0.5)
        
        return self.__ser.read(bufLen)
    
    def writeStationMem(self, nibbles, bank, addr, data):
        b = 2
        if bank == 0: b = 1
        if bank == 1: b = 3
        
        nib = (nibbles << 4) | b
        addr = struct.pack("<BB", nib, addr)
        self.__ser.write("WWR"+addr+data+"\r")
        self.checkAck()
    
    def readStationTime(self):
        buf = self.readStationMem(2, 1, 0xBE)
        h = struct.unpack("<B", buf)
        
        buf = self.readStationMem(2, 1, 0xC0)
        m = struct.unpack("<B", buf)        

        buf = self.readStationMem(2, 1, 0xC2)
        s = struct.unpack("<B", buf)        

        print "H:M:S: "+str(h[0])+":"+str(m[0])+":"+str(s[0])

    # TODO: Verify somehow..?
    def readStationMake(self):
        buf = self.readStationMem(1, 0, 0x4d)
        
        print "Station reports model nibble: "+repr(buf)+" (0x00 is WWIII!)"