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

class ArchiveImage:
    def __init__(self):
        self.__avgwnd = 0
        self.__domwnddir = 0
        self.__gust = 0
        
    def __getavgwnd(self):
        return self.__avgwnd
    def __setavgwnd(self, avgwnd):
        self.__avgwnd = avgwnd
    AverageWindSpeed = property(__getavgwnd, __setavgwnd)
    
    def __getdomwnddir(self):
        return self.__domwnddir
    def __setdomwnddir(self, domwnddir):
        self.__domwnddir = domwnddir
    DominantWindDirection = property(__getdomwnddir, __setdomwnddir)
    
    def __getgust(self):
        return self.__gust
    def __setgust(self, gust):
        self.__gust = gust
    Gust = property(__getgust, __setgust)
    
    def __str__(self):
        return "avgwndspd: %i, domwnddir: %i, gust: %i" % (self.AverageWindSpeed, self.DominantWindDirection, self.Gust)

class SensorImage:
    
    def __init__(self):
        self.__wd = 0
        self.__ws = 0.0
        self.__itemp = 0.0
        self.__otemp = 0.0
    
    def __getws(self):
        return self.__ws
    def __setws(self, ws):
        self.__ws = ws
    WindSpeed = property(__getws, __setws)
    
    def __getwd(self):
        return self.__wd
    def __setwd(self, wd):
        self.__wd = wd
    WindDirection = property(__getwd, __setwd)
    
    def __getitemp(self):
        return self.__itemp
    def __setitemp(self, temp):
        self.__itemp = temp
    IndoorTemperature = property(__getitemp, __setitemp)
    
    def __getotemp(self):
        return self.__otemp
    def __setotemp(self, temp):
        self.__otemp = temp
    OutdoorTemperature = property(__getotemp, __setotemp)

    def __str__(self):
        return "itemp: %.2f\notemp: %.2f\nwd: %i\nws: %.2f" % (self.IndoorTemperature, self.OutdoorTemperature, self.WindDirection, self.WindSpeed)
