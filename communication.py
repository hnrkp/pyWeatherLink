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

from conversions import dewpoint_approximation, f2c, inHg2hPa, mph2kts

from datatypes import SensorImage#, ArchiveImage
from crc import CRC_CCITT

class Link:
    def __init__(self, dev = '/dev/ttyUSB0', baud = 19200):
        self.__ser = serial.Serial(dev, baud, timeout = 2)
        self.__ser.open()
        self.wakeup()
        self.setTime()
        
        self.getModel()
        #self.getVersion()

    def __del__(self):
        self.__ser.close()
    
    def wakeup(self):
        while self.__ser.inWaiting():
            self.__ser.read()
        
        n = 0
        while True:
            self.__ser.write("\n")
            buf = self.__ser.read(1)
            
            if buf != '' and buf[0] == "\n":
                break
            
            n += 1
            
            if n >= 3:
                raise Exception("Failed to wake up console")
        

    def checkAck(self):
        resp = "\n"

        while resp == "\n" or resp == "\r":
            resp = self.__ser.read()

        if resp == '':
            raise Exception("Timeout waiting for ack")
        
        ack = struct.unpack("<B", resp)

        if ack[0] == 0x21:
            raise Exception("Response NOK!")
        
        if ack[0] == 0x18:
            raise Exception("CRC error!")

        if ack[0] != 0x06:
            print "ack: ", ack[0], "response: "
            for c in resp:
                print ord(c),
            while (self.__ser.inWaiting()):
                self.__ser.read()
            raise Exception("Response was not NOK, but not ACK either..")
        

    def getSensorImage(self):
        self.wakeup()
        self.__ser.write("LOOP 1\n");

        self.checkAck()

        buf = self.__ser.read(99)
        
        if buf[0:3] != "LOO":
            raise Exception("Start of block was not LOO")
            
        img = SensorImage()
        img.WindSpeed = mph2kts(struct.unpack("<B", buf[14])[0])
        img.AverageWindSpeed = mph2kts(struct.unpack("<B", buf[15])[0])
        img.WindDirection = struct.unpack("<H", buf[16:18])[0]
        img.IndoorTemperature = f2c(float(struct.unpack("<H", buf[9:11])[0])/10)
        img.IndoorRelativeHumidity = struct.unpack("<B", buf[11])[0]
        img.OutdoorTemperature = f2c(float(struct.unpack("<H", buf[12:14])[0])/10)
        img.OutdoorRelativeHumidity = struct.unpack("<B", buf[33])[0]
        img.QFE = inHg2hPa(float(struct.unpack("<H", buf[7:9])[0])/1000.0)
        img.QFETrend = struct.unpack("<b", buf[3])[0]
        
        img.RainRate = float(struct.unpack("<H", buf[41:43])[0]) * 0.2
        img.RainDay = float(struct.unpack("<H", buf[50:52])[0])* 0.2
        
        img.OutdoorDewpoint = dewpoint_approximation(img.OutdoorTemperature, img.OutdoorRelativeHumidity)
        
        stationcrc = struct.unpack(">H", buf[97:100])[0]
        
        crc = 0
        
        ccitt = CRC_CCITT()
        for c in buf[:97]:
            crc = ccitt.update_crc(crc, ord(c))

        if (stationcrc != crc):
            raise Exception("CRC error, image crc does not match our crc!")
                
        return img
    
    def getModel(self):
        self.wakeup()
        self.__ser.write("WRD" + chr(0x12) + chr(0x4d) + "\n")
        self.checkAck()
        
        make = ord(self.__ser.read())
        
        print "Talking to a",
        
        if make == 17:
            print "Vantage Vue"
    
    def getVersion(self):
        self.wakeup()
        self.__ser.write("NVER\n")
        
        print self.__ser.read(100)
        
        self.__ser.write("VER\n")
        
        print self.__ser.read(100)
    
    def setTime(self):
        self.wakeup()
        self.__ser.write("SETTIME\n")
        
        self.checkAck()
        
        t = time.localtime()
        
        timestr = struct.pack("<BBBBBB", t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon, t.tm_year - 1900)
        
        crc = CRC_CCITT()
        crc16 = 0
        for c in timestr:
            crc16 = crc.update_crc(crc16, ord(c))
        
        self.__ser.write(timestr + struct.pack(">H", crc16))
        self.checkAck()
        