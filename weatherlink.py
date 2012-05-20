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

from communication import Link

link = Link()

link.setArchiveTime(1)
link.setSampleTime(5)
print link.getArchiveImage()
print link.getSensorImage()
