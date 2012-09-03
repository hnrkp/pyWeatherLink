"""
    WxDaemon - A sample SocketServer, serving weather data as an example on how to use pyWeatherLink.

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

import SocketServer
import time

import random

import threading
from communication import Link
from datatypes import ArchiveImage, SensorImage

class DummyLink:
    def getArchiveImage(self):
        a = ArchiveImage()
        a.AverageWindSpeed = random.randint(1,100)
        a.Gust = random.randint(1,100)
        return a
    def getSensorImage(self):
        s = SensorImage()
        s.IndoorTemperature = random.randint(1,100)
        s.OutdoorTemperature = random.randint(1,100)
        s.WindDirection = random.randint(1,100)
        s.WindSpeed = random.randint(1,100)
        return s

class Poller(threading.Thread):
    def __init__(self):
        #self.link = DummyLink()
        self.link = Link()
        #self.link.setArchiveTime(1)
        #self.link.setSampleTime(5)

        #self.aimg = self.link.getArchiveImage()
        self.simg = self.link.getSensorImage()
        threading.Thread.__init__ ( self )
    
    def run(self):
        gust = 0
        #counter = 0
        while 1:
            time.sleep(2)
            try:
                self.simg = self.link.getSensorImage()
            except Exception as e:
                self.simg = None
                print "Exception while getting sensor image!", e
                import traceback
                traceback.print_exc()
                continue
            
            if self.simg.WindSpeed > gust:
                gust = self.simg.WindSpeed
            
            #counter += 1
            #if counter >= 3:
            #    counter = 0
            #    try:
            #        self.aimg = self.link.getArchiveImage()
            #    except:
            #        print "Exception while getting archive image!"
            #        self.aimg = None
            #        continue
            #    
            #    # Ugly hack to protect ourselves from strange readings when gust
            #    # in the beginning of the archive image is lower than average and 
            #    # current wind speeds
            #    if self.aimg.AverageWindSpeed > self.aimg.Gust:
            #        self.aimg.Gust = self.aimg.AverageWindSpeed
            #    
            #    if self.aimg.Gust < gust:
            #        self.aimg.Gust = gust
            #gust = 0
    
poller = Poller()
poller.daemon = True
poller.start()

class WxRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        #print self.client_address, 'connected!'
        #a = poller.aimg
        s = poller.simg
        if s is None is None:
            self.request.send("ERROR"+"\n")
            return
        self.request.send("WS " + str(s.WindSpeed) + "\n")
        self.request.send("WSAVG "+str(s.AverageWindSpeed)+"\n")
        self.request.send("WDIR " + str(s.WindDirection) + "\n")
        #self.request.send("WDIRAVG "+str(a.DominantWindDirection)+"\n")
        #self.request.send("GUST "+str(a.Gust)+"\n")
        self.request.send("ITEMP " + str(s.IndoorTemperature) + "\n")
        self.request.send("OTEMP " + str(s.OutdoorTemperature) + "\n")
        self.request.send("ODEW " + str(round(s.OutdoorDewpoint, 1)) + "\n")
        self.request.send("IRELH " + str(s.IndoorRelativeHumidity) + "\n")
        self.request.send("ORELH " + str(s.OutdoorRelativeHumidity) + "\n")
        self.request.send("QFE " + str(round(s.QFE, 1)) + "\n")
        self.request.send("QFETREND " + str(s.QFETrend) + "\n")
        self.request.send("RRATE " + str(round(s.RainRate, 2)) + "\n")
        self.request.send("RDAY "+ str(round(s.RainDay, 2)) + "\n")
        self.request.send("FORECAST " + str(s.Forecast) + "\n")
        self.request.send("TIMESTAMP " + str(s.Timestamp) + "\n")

    def handle(self):
        return

    def finish(self):
        #print self.client_address, 'disconnected!'
        return

SocketServer.ThreadingTCPServer.allow_reuse_address = True
server = SocketServer.ThreadingTCPServer(('127.0.0.1', 6666), WxRequestHandler)
server.serve_forever()
