from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, registerSubscriberEvent
from mojo.UI import SetCurrentGlyphByName

from ramsayStData import RamsayStData


class RamsaySts(Subscriber):

    debub = False

    def build(self):
        glyphEditor = self.getGlyphEditor()
        self.leftGlyph = self.rightGlyph = None

        container = glyphEditor.extensionContainer(RamsayStData.identifier, location="foreground")
        self.leftGlyphContainer = container.appendPathSublayer(
            fillColor=RamsayStData.fillColor,
            strokeColor=RamsayStData.strokeColor,
            strokeWidth=1
        )
        self.rightGlyphContainer = container.appendPathSublayer(
            fillColor=RamsayStData.fillColor,
            strokeColor=RamsayStData.strokeColor,
            strokeWidth=1
        )

        previewContainer = glyphEditor.extensionContainer(RamsayStData.identifier, location="preview")
        self.previewLeftGlyphContainer = previewContainer.appendPathSublayer(
            fillColor=(0, 0, 0, 1)
        )
        self.previewRightGlyphContainer = previewContainer.appendPathSublayer(
            fillColor=(0, 0, 0, 1)
        )

        self.setGlyph(glyphEditor.getGlyph())

    def setGlyph(self, glyph):
        leftPath = rightPath = None
        self.leftGlyph = self.rightGlyph = None

        if glyph is not None:
            layer = glyph.layer
            baseName = RamsayStData.getBaseGlyph(glyph.name)
            leftGlyphName, rightGlyphName = RamsayStData.get(baseName, ("n", "n"))

            if leftGlyphName in layer:
                self.leftGlyph = layer[leftGlyphName]
                leftPath = self.leftGlyph.getRepresentation("merz.CGPath")
                self.leftGlyphContainer.setPosition((-self.leftGlyph.width, 0))
                if RamsayStData.showPreview:
                    self.previewLeftGlyphContainer.setPosition((-self.leftGlyph.width, 0))

            if rightGlyphName in layer:
                self.rightGlyph = layer[rightGlyphName]
                rightPath = self.rightGlyph.getRepresentation("merz.CGPath")
                self.rightGlyphContainer.setPosition((glyph.width, 0))
                if RamsayStData.showPreview:
                    self.previewRightGlyphContainer.setPosition((glyph.width, 0))

        self.leftGlyphContainer.setPath(leftPath)
        self.rightGlyphContainer.setPath(rightPath)

        if not RamsayStData.showPreview:
            leftPath = rightPath = None
        self.previewLeftGlyphContainer.setPath(leftPath)
        self.previewRightGlyphContainer.setPath(rightPath)

    def glyphEditorDidSetGlyph(self, info):
        self.setGlyph(info["glyph"])

    def glyphEditorDidMouseDown(self, info):
        if info["deviceState"]["clickCount"] == 3:
            x, y = info["locationInGlyph"]
            glyph = info["glyph"]

            if self.leftGlyph is not None:
                if self.leftGlyph.pointInside((x + self.leftGlyph.width, y)):
                    self.getGlyphEditor().setGlyph(self.leftGlyph)

            if self.rightGlyph is not None:
                if self.rightGlyph.pointInside((x - glyph.width, y)):
                    print("set ", self.rightGlyph)
                    self.getGlyphEditor().setGlyph(self.rightGlyph)

    def ramsayStSettingDidChange(self, info):
        self.leftGlyphContainer.setFillColor(RamsayStData.fillColor)
        self.leftGlyphContainer.setStrokeColor(RamsayStData.strokeColor)

        self.rightGlyphContainer.setFillColor(RamsayStData.fillColor)
        self.rightGlyphContainer.setStrokeColor(RamsayStData.strokeColor)

        if not RamsayStData.showPreview:
            self.previewLeftGlyphContainer.setPath(None)
            self.previewRightGlyphContainer.setPath(None)


registerSubscriberEvent(
    subscriberEventName=RamsayStData.changedEventName,
    methodName="ramsayStSettingDidChange",
    lowLevelEventNames=[RamsayStData.changedEventName],
    dispatcher="roboFont",
    documentation="Send when RamsaySt setting did change.",
    delay=0,
    debug=True
)


registerGlyphEditorSubscriber(RamsaySts)
