import vanilla
from AppKit import NSSegmentStyleSmallSquare

from defconAppKit.windows.baseWindow import BaseWindowController

from mojo.roboFont import OpenWindow
from mojo.UI import UpdateCurrentGlyphView
from mojo.extensions import NSColorToRgba, rgbaToNSColor
from mojo.events import postEvent

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
        self.w.closeButton.bind(chr(27), [])

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

        self.w.showNeighbours = vanilla.CheckBox((10, 10, -10, 22), "Show Neighbours", value=RamsayStData.showNeighbours, callback=self.showNeighboursCallback)
        self.w.showPreview = vanilla.CheckBox((10, 40, -10, 22), "Show In Preview Mode", value=RamsayStData.showPreview, callback=self.showPreviewCallback)

        self.w.fillColorText = vanilla.TextBox((10, 70, 110, 22), "Fill Color:")
        self.w.fillColor = vanilla.ColorWell((10, 90, 110, 40), color=rgbaToNSColor(RamsayStData.fillColor), callback=self.fillColorCallback)

        self.w.strokeColorText = vanilla.TextBox((130, 70, -10, 22), "Stroke Color:")
        self.w.strokeColor = vanilla.ColorWell((130, 90, -10, 40), color=rgbaToNSColor(RamsayStData.strokeColor), callback=self.strokeColorCallback)

        items = RamsayStData.getItems()
        columnDescriptions = [
            dict(title="Glyph Name", key="glyphName"),
            dict(title="Left", key="left"),
            dict(title="Right", key="right"),
        ]

        self.w.dataList = vanilla.List((10, 140, -10, -40), items, columnDescriptions=columnDescriptions, editCallback=self.dataListEditCallback)

        segmentDescriptions = [dict(title="+"), dict(title="-"), dict(title="import"), dict(title="export")]
        self.w.addDel = vanilla.SegmentedButton((12, -32, -140, 20), segmentDescriptions, selectionStyle="momentary", callback=self.addDelCallback)
        self.w.addDel.getNSSegmentedButton().setSegmentStyle_(NSSegmentStyleSmallSquare)

        self.w.okButton = vanilla.Button((-70, -30, -15, 20), "Apply", callback=self.okCallback, sizeStyle="small")

        self.w.setDefaultButton(self.w.okButton)

        self.w.closeButton = vanilla.Button((-140, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(chr(27), [])

        self.w.open()

    def showNeighboursCallback(self, sender):
        RamsayStData.showNeighbours = sender.get()
        RamsayStData.save()
        self.update()

    def showPreviewCallback(self, sender):
        RamsayStData.showPreview = sender.get()
        RamsayStData.save()
        self.update()

    def fillColorCallback(self, sender):
        RamsayStData.fillColor = NSColorToRgba(sender.get())
        RamsayStData.save()
        self.update()

    def strokeColorCallback(self, sender):
        RamsayStData.strokeColor = NSColorToRgba(sender.get())
        RamsayStData.save()
        self.update()

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
            items = self.w.dataList.get()
            for i in reversed(sel):
                del items[i]
            self.w.dataList.set(items)

    def importGlyphNames(self):
        self.showGetFile(["ramsaySt"], self._importGlyphNames)

    def _importGlyphNames(self, path):
        if path:
            path = path[0]
            with open(path, "r") as blob:
                lines = blob.read().splitlines()

            data = dict()
            for line in lines:
                if line.startswith("#"):
                    continue

                items = line.split()
                if len(items) == 3:
                    glyphName, leftGlyphName, rightGlyphName = items
                    if leftGlyphName == '_':
                        leftGlyphName = ' '
                    if rightGlyphName == '_':
                        rightGlyphName = ' '
                    data[glyphName] = leftGlyphName, rightGlyphName
                else:
                    continue

            RamsayStData.clear()
            RamsayStData.update(data)
            self.w.dataList.set(RamsayStData.getItems())
            self.update()

    def exportGlyphNames(self):
        self.showPutFile(["ramsaySt"], self._exportGlyphNames)

    def _exportGlyphNames(self, path):
        if path is None:
            return

        output = [
            "# Ramsay St. Glyph List",
            "# Use _ as a placeholder for 'no glyph'"
            "# <glyphName> <leftGlyphName> <rightGlyphName>"
        ]
        for glyphName in sorted(RamsayStData.keys()):
            left, right = RamsayStData.get(glyphName, (None, None))
            if all([left, right]):
                if left == ' ':
                    left = '_'
                if right == ' ':
                    right = '_'
                output.append(f"{glyphName} {left} {right}")

        with open(path, "w") as blob:
            blob.write("\n".join(output))

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
        self.update()

    def closeCallback(self, sender):
        self.w.close()

    def dataListEditCallback(self, sender):
        return

    def update(self):
        postEvent(RamsayStData.changedEventName)


OpenWindow(RamsayStSettingsWindowController)
