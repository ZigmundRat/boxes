#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
import math

class BinFrontEdge(edges.BaseEdge):
    char = "B"
    def __call__(self, length, **kw):
        f = self.settings.front
        a1 = math.degrees(math.atan(f/(1-f)))
        a2 = 45 + a1
        self.corner(-a1)
        for i, l in enumerate(self.settings.sy):
            self.edges["e"](l* (f**2+(1-f)**2)**0.5)
            self.corner(a2)            
            self.edges["f"](l*f*2**0.5)
            if i < len(self.settings.sy)-1:
                if self.char == "B":
                    self.polyline(0, 45, 0.5*self.settings.hi,
                                  -90, self.thickness, -90, 0.5*self.settings.hi, 90-a1)
                else:
                    self.polyline(0, -45, self.thickness, -a1)
            else:
                self.corner(-45)

    def margin(self):
        return max(self.settings.sy) * self.settings.front

class BinFrontSideEdge(BinFrontEdge):
    char = 'b'

class BinTray(Boxes):
    """A Type tray variant to be used up right with sloped walls in front"""

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("sx", "sy", "h", "outside")
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0,
                             surroundingspaces=0.5)
        self.argparser.add_argument(
            "--front", action="store", type=float, default=0.4,
            help="fraction of bin height covert with slope")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in self.sx:
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)
            
    def frontHoles(self, i):
        def CB():
            posx = -0.5 * self.thickness
            for x in self.sx[:-1]:
                posx += x + self.thickness
                self.fingerHolesAt(posx, 0, self.sy[i]*self.front*2**0.5)
        return CB

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def render(self):
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        hi = self.hi = h
        t = self.thickness

        self.open()

        self.addPart(BinFrontEdge(self, self))
        self.addPart(BinFrontSideEdge(self, self))

        edges.FingerJointSettings(self.thickness, True, angle=45).edgeObjects(self, chars="gGH")

        # outer walls
        e = ["F", "f", edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]

        self.rectangularWall(x, h, e, callback=[self.xHoles],  move="right")
        self.rectangularWall(y, h, "FFbF", callback=[self.yHoles, ], move="up")
        self.rectangularWall(y, h, "FFbF", callback=[self.yHoles, ])
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles, ], move="left")
        self.rectangularWall(y, h, "FFBF", move="up only")

        # floor
        self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots],move="right")
        # Inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, "f"), "f", "B", "f"]
            self.rectangularWall(y, hi, e, move="up")

        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, "f", slots=0.5 * hi), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]
            self.rectangularWall(x, hi, e, move="up")

        # Front walls
        for i in range(len(self.sy)):
            e = [edges.SlottedEdge(self, self.sx, "g"), "F", "e", "F"]
            self.rectangularWall(x, self.sy[i]*self.front*2**0.5, e, callback=[self.frontHoles(i)], move="up")

        self.close()


def main():
    b = BinTray()
    b.parseArgs()
    b.render()


if __name__ == '__main__':
    main()