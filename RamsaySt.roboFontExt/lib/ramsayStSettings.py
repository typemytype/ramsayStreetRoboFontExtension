from fontTools.misc.py23 import unichr

import vanilla
from AppKit import NSSegmentStyleSmallSquare

from defconAppKit.windows.baseWindow import BaseWindowController

from mojo.roboFont import OpenWindow
from mojo.UI import UpdateCurrentGlyphView

from ramsayStData import RamsayStData


class AddGlyphNameSheet(object):

    def __init__(self, parentWindow, callback=None):
        self.callback = callback

        self.w = vanilla.Sheet((350, 90), parentWindow=parentWindow)

        self.w.glyphNameText = vanilla.TextBox((10, 17, 100, 22), "Glyph Name:")
        self.w.glyphName = vanilla.EditText((100, 17, -10, 22))

        self.w.addButton = vanilla.Button((-70, -30, -10, 20), "Add", callback=self.addCallback, sizeStyle="small")
        self.w.setDefaultButton(self.w.addButton)

        self.w.closeButton = vanilla.Button((-150, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])

        self.w.open()

    def addCallback(self, sender):
        if self.callback:
            self.callback(self)
        self.closeCallback(sender)

    def closeCallback(self, sender):
        self.w.close()

    def get(self):
        return self.w.glyphName.get()


class RamsayStSettingsWindowController(BaseWindowController):

    def __init__(self):
        self.w = vanilla.FloatingWindow((310, 300), "Ramsay St. Settings", minSize=(310, 250), maxSize=(310, 700))

        self.w.showPreview = vanilla.CheckBox((10, 10, -10, 22), "Show Preview", value=RamsayStData.showPreview, callback=self.showPreviewCallback)

        self.w.fillColorText = vanilla.TextBox((10, 40, 110, 22), "Fill Color:")
        self.w.fillColor = vanilla.ColorWell((10, 60, 110, 40), color=RamsayStData.fillColor, callback=self.fillColorCallback)

        self.w.strokeColorText = vanilla.TextBox((130, 40, -10, 22), "Stroke Color:")
        self.w.strokeColor = vanilla.ColorWell((130, 60, -10, 40), color=RamsayStData.strokeColor, callback=self.strokeColorCallback)

        items = RamsayStData.getItems()
        columnDescriptions = [
                              dict(title="Glyph Name", key="glyphName"),
                              dict(title="Left", key="left"),
                              dict(title="Right", key="right"),
                              ]

        self.w.dataList = vanilla.List((10, 110, -10, -40), items, columnDescriptions=columnDescriptions, editCallback=self.dataListEditCallback)


        segmentDescriptions = [dict(title="+"), dict(title="-"), dict(title="import"), dict(title="export")]
        self.w.addDel = vanilla.SegmentedButton((12, -32, -140, 20), segmentDescriptions, selectionStyle="momentary", callback=self.addDelCallback)
        self.w.addDel.getNSSegmentedButton().setSegmentStyle_(NSSegmentStyleSmallSquare)

        self.w.okButton = vanilla.Button((-70, -30, -15, 20), "Apply", callback=self.okCallback, sizeStyle="small")

        self.w.setDefaultButton(self.w.okButton)

        self.w.closeButton = vanilla.Button((-140, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])

        self.w.open()

    def showPreviewCallback(self, sender):
        RamsayStData.showPreview = sender.get()
        RamsayStData.save()
        self.updateView()

    def fillColorCallback(self, sender):
        RamsayStData.fillColor = sender.get()
        RamsayStData.save()
        self.updateView()

    def strokeColorCallback(self, sender):
        RamsayStData.strokeColor = sender.get()
        RamsayStData.save()
        self.updateView()

    def _addGlyphName(self, sender):
        glyphName = sender.get()
        if glyphName in RamsayStData.keys():
            index = 0
            for item in self.w.dataList:
                if glyphName == item.glyphName():
                    break
                index += 1
            self.w.dataList.setSelection([index])
            return
        self.w.dataList.append(RamsayStData.newItem(glyphName))

    def addGlyphName(self):
        AddGlyphNameSheet(self.w, self._addGlyphName)

    def delGlyphName(self):
        sel = self.w.dataList.getSelection()
        if sel:
            index = sel[0]
            del self.w.dataList[index]

    def importGlyphNames(self):
        self.showGetFile(["ramsaySt"], self._importGlyphNames)

    def _importGlyphNames(self, path):
        if path:
            path = path[0]
            f = open(path, "r")
            lines = f.readlines()
            f.close()

            data = dict()
            for line in lines:
                if line.startswith("#"):
                    continue
                items = line.split()
                if len(items) != 3:
                    continue
                leftGlyphName, glyphName, rightGlyphName = items
                data[glyphName] = leftGlyphName, rightGlyphName

            RamsayStData.clear()
            RamsayStData.update(data)
            self.w.dataList.set(RamsayStData.getItems())
            self.updateView()

    def exportGlyphNames(self):
        self.showPutFile(["ramsaySt"], self._exportGlyphNames)

    def _exportGlyphNames(self, path):
        if path is None:
            return

        output = [
            "# Ramsay St. Glyph List",
            "# <glyphName> <leftGlyphName> <rightGlyphGlyphName>"
            ]
        for glyphName in sorted(RamsayStData.keys()):
            value = RamsayStData.get(glyphName, None)
            if value is not None:
                output.append("%s %s %s" % (glyphName, value[0], value[1]))

        f = open(path, "w")
        f.write("\n".join(output))
        f.close()

    def addDelCallback(self, sender):
        v = sender.get()
        if v == 0:
            # add
            self.addGlyphName()
        elif v == 1:
            # remove
            self.delGlyphName()
        elif v == 2:
            # import
            self.importGlyphNames()
        elif v == 3:
            # export
            self.exportGlyphNames()

    def okCallback(self, sender):
        RamsayStData.setItems(self.w.dataList)
        RamsayStData.save()
        self.updateView()

    def closeCallback(self, sender):
        self.w.close()

    def dataListEditCallback(self, sender):
        sel = sender.getSelection()
        for i in sel:
            item = sender[i]
            RamsayStData.set(item)

    def updateView(self):
        UpdateCurrentGlyphView()


OpenWindow(RamsayStSettingsWindowController)
