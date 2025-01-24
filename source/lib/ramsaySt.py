from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, registerSubscriberEvent
from mojo.UI import appearanceColorKey, getDefault

from ramsayStData import RamsayStData


class RamsaySts(Subscriber):

    debug = False

    def build(self):
        glyphEditor = self.getGlyphEditor()
        previewFillColor = getDefault(
            appearanceColorKey("glyphViewPreviewFillColor"))
        self.leftGlyph = self.rightGlyph = None

        container = glyphEditor.extensionContainer(RamsayStData.identifier, location="middleground")
        self.leftGlyphContainer = container.appendPathSublayer(
            fillColor=RamsayStData.fillColor,
            strokeColor=RamsayStData.strokeColor,
            strokeWidth=1,
            visible=False
        )
        self.rightGlyphContainer = container.appendPathSublayer(
            fillColor=RamsayStData.fillColor,
            strokeColor=RamsayStData.strokeColor,
            strokeWidth=1,
            visible=False
        )

        previewContainer = glyphEditor.extensionContainer(RamsayStData.identifier, location="preview")
        self.previewLeftGlyphContainer = previewContainer.appendPathSublayer(
            fillColor=previewFillColor,
            visible=False
        )
        self.previewRightGlyphContainer = previewContainer.appendPathSublayer(
            fillColor=previewFillColor,
            visible=False
        )

        self.setGlyph(glyphEditor.getGlyph())

    def setGlyph(self, glyph):
        leftPath = rightPath = None
        self.leftGlyph = self.rightGlyph = None

        if glyph is not None:
            layer = glyph.layer
            if glyph.name in RamsayStData:
                # (composed) glyph + neighbors specified in RamsaySt settings
                leftGlyphName, rightGlyphName = RamsayStData.get(glyph.name)
            else:
                # fall back to base glyph (e.g. a for aacute), and show
                # neighbors for it (if assigned), or default neighbors n, n
                baseName = RamsayStData.getBaseGlyph(glyph.name)
                leftGlyphName, rightGlyphName = RamsayStData.get(baseName, ("n", "n"))

            if leftGlyphName and leftGlyphName in layer:
                self.leftGlyph = layer[leftGlyphName]
                leftPath = self.leftGlyph.getRepresentation("merz.CGPath")
                self.leftGlyphContainer.setPosition((-self.leftGlyph.width, 0))
                self.previewLeftGlyphContainer.setPosition((-self.leftGlyph.width, 0))

            if rightGlyphName and rightGlyphName in layer:
                self.rightGlyph = layer[rightGlyphName]
                rightPath = self.rightGlyph.getRepresentation("merz.CGPath")
                self.rightGlyphContainer.setPosition((glyph.width, 0))
                self.previewRightGlyphContainer.setPosition((glyph.width, 0))

        adjunctGlyphs = []
        if self.leftGlyph:
            adjunctGlyphs.append(self.leftGlyph)
        if self.rightGlyph:
            adjunctGlyphs.append(self.rightGlyph)

        self.setAdjunctObjectsToObserve(adjunctGlyphs)

        self.leftGlyphContainer.setPath(leftPath)
        self.rightGlyphContainer.setPath(rightPath)
        self.leftGlyphContainer.setVisible(RamsayStData.showNeighbours)
        self.rightGlyphContainer.setVisible(RamsayStData.showNeighbours)

        self.previewLeftGlyphContainer.setPath(leftPath)
        self.previewRightGlyphContainer.setPath(rightPath)
        self.previewLeftGlyphContainer.setVisible(RamsayStData.showPreview)
        self.previewRightGlyphContainer.setVisible(RamsayStData.showPreview)

    def glyphEditorDidSetGlyph(self, info):
        self.setGlyph(info["glyph"])

    def glyphEditorGlyphDidChangeMetrics(self, info):
        glyph = info["glyph"]
        self.rightGlyphContainer.setPosition((glyph.width, 0))
        self.previewRightGlyphContainer.setPosition((glyph.width, 0))

    def glyphEditorDidMouseDown(self, info):
        '''
        triple-click any neighbor glyph to jump directly to it
        '''
        if info["deviceState"]["clickCount"] == 3:
            x, y = info["locationInGlyph"]
            glyph = info["glyph"]

            if self.leftGlyph is not None:
                if self.leftGlyph.pointInside((x + self.leftGlyph.width, y)):
                    self.getGlyphEditor().setGlyph(self.leftGlyph)

            if self.rightGlyph is not None:
                if self.rightGlyph.pointInside((x - glyph.width, y)):
                    self.getGlyphEditor().setGlyph(self.rightGlyph)

    def adjunctGlyphDidChange(self, info):
        centerGlyph = self.getGlyphEditor().getGlyph()
        self.setGlyph(centerGlyph)

    def roboFontAppearanceChanged(self, info):
        rgba = getDefault(
            appearanceColorKey("glyphViewPreviewFillColor"))
        self.previewLeftGlyphContainer.setFillColor(rgba)
        self.previewRightGlyphContainer.setFillColor(rgba)

    def ramsayStSettingDidChange(self, info):
        self.leftGlyphContainer.setFillColor(RamsayStData.fillColor)
        self.leftGlyphContainer.setStrokeColor(RamsayStData.strokeColor)
        self.leftGlyphContainer.setVisible(RamsayStData.showNeighbours)
        self.rightGlyphContainer.setFillColor(RamsayStData.fillColor)
        self.rightGlyphContainer.setStrokeColor(RamsayStData.strokeColor)
        self.rightGlyphContainer.setVisible(RamsayStData.showNeighbours)

        self.previewLeftGlyphContainer.setPath(self.leftGlyphContainer.getPath())
        self.previewLeftGlyphContainer.setVisible(RamsayStData.showPreview)
        self.previewRightGlyphContainer.setPath(self.rightGlyphContainer.getPath())
        self.previewRightGlyphContainer.setVisible(RamsayStData.showPreview)


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
