import ezui

from mojo.UI import PutFile, GetFile
from mojo.events import postEvent

from ramsayStData import RamsayStData


class RamsayStSettingsController(ezui.WindowController):

    def build(self):
        content = """
        * TwoColumnForm                 @form
        
        > : Show:
        > [X] Edit Mode                 @showNeighborsEditMode
        > [X] Preview Mode              @showNeighborsPreviewMode
        
        > : Fill Color:
        > * HorizontalStack             @fillColorStack
        >> * ColorWell                  @fillColorLight
        >> * ColorWell                  @fillColorDark
        
        > : Stroke Color:
        > * HorizontalStack             @strokeColorStack
        >> * ColorWell                  @strokeColorLight
        >> * ColorWell                  @strokeColorDark
        
        > :
        > * HorizontalStack
        >> Light                        @lightLabel
        >> Dark                         @darkLabel
        
        # > : Stroke Color:
        # > * ColorWell                 @strokeColor
        
        ---
        
        |-----------------------------|
        | left   | glyph   | right    | @table
        |--------|---------|----------|
        | A      | A       | A        |
        |        |         |          |
        |-----------------------------|
        > (+-)                          @tableAddRemove
        > (Import)                      @importButton
        > (Export)                      @exportButton
        """
        columnWidth = 80
        padding = 28
        formTitleWidth = columnWidth + 14
        formItemWidth = columnWidth*3 - formTitleWidth + padding*2
        buttonWidth = (formItemWidth - 10) / 2
        descriptionData = dict(
            form=dict(
                titleColumnWidth=columnWidth + 14,
                itemColumnWidth=formItemWidth,
            ),
            table=dict(
                width="fill",
                height="fill",
                items=[
                    {
                        "glyph_name": item.glyphName(),
                        "left": item.left(),
                        "right": item.right()
                    }
                    for item in RamsayStData.getItems()
                ],
                columnDescriptions=[
                    dict(
                        identifier="left",
                        title="Left",
                        width=columnWidth,
                        editable=True
                    ),
                    dict(
                        identifier="glyph_name",
                        title="Glyph Name",
                        width=columnWidth,
                        editable=True
                    ),
                    dict(
                        identifier="right",
                        title="Right",
                        width=columnWidth,
                        editable=True
                    ),
                ]
            ),
            fillColorLight=dict(
                color=(0,0,1,0.2),
                width=buttonWidth,
                height=20,
            ),
            fillColorDark=dict(
                color=(0,0,1,0.2),
                width=buttonWidth,
                height=20,
            ),
            strokeColorLight=dict(
                color=(0,0,1,0),
                width=buttonWidth,
                height=20,
            ),
            strokeColorDark=dict(
                color=(0,0,1,0),
                width=buttonWidth,
                height=20,
            ),
            lightLabel=dict(
                width=buttonWidth,
                sizeStyle="mini",
            ),
            darkLabel=dict(
                width=buttonWidth,
                sizeStyle="mini",
            ),
            importButton=dict(
                width=buttonWidth
            ),
            exportButton=dict(
                width=buttonWidth
            ),
        )
        self.w = ezui.EZPanel(
            title="Ramsay St. Settings",
            size=(columnWidth*3, 400),
            minSize=(columnWidth*3, 300),
            content=content,
            descriptionData=descriptionData,
            controller=self
        )

    def started(self):
        self.loadFromData()
        self.w.open()

    def formCallback(self, sender):
        self.saveSettingsData()

    def tableEditCallback(self, sender):
        self.saveTableData()
        
    def tableAddRemoveAddCallback(self, sender):
        table = self.w.getItem("table")
        item = table.makeItem(
            left="A",
            glyph_name="A",
            right="A"
        )
        table.appendItems([item])
        self.saveTableData()

    def tableAddRemoveRemoveCallback(self, sender):
        table = self.w.getItem("table")
        table.removeSelectedItems()
        self.saveTableData()

    def loadFromData(self):
        self.w.getItem("fillColorLight").set(RamsayStData.fillColorLight)
        self.w.getItem("fillColorDark").set(RamsayStData.fillColorDark)
        self.w.getItem("strokeColorLight").set(RamsayStData.strokeColorLight)
        self.w.getItem("strokeColorDark").set(RamsayStData.strokeColorDark)
        self.w.getItem("showNeighborsEditMode").set(RamsayStData.showNeighbours)
        self.w.getItem("showNeighborsPreviewMode").set(RamsayStData.showPreview)
        self.w.getItem("table").set([{"glyph_name": item.glyphName(), "left": item.left(), "right": item.right()} for item in RamsayStData.getItems()])

    def saveSettingsData(self):
        RamsayStData.fillColorLight = self.w.getItem("fillColorLight").get()
        RamsayStData.fillColorDark = self.w.getItem("fillColorDark").get()
        RamsayStData.strokeColorLight = self.w.getItem("strokeColorLight").get()
        RamsayStData.strokeColorDark = self.w.getItem("strokeColorDark").get()
        RamsayStData.showNeighbours = self.w.getItem("showNeighborsEditMode").get()
        RamsayStData.showPreview = self.w.getItem("showNeighborsPreviewMode").get()
        RamsayStData.save()
        postEvent(RamsayStData.changedEventName)

    def saveTableData(self):
        new_data = dict()
        for item in self.w.getItem("table").get():
            key = item.get("glyph_name")
            left = item.get("left")
            right = item.get("right")
            if key:
                new_data[key] = (left, right)
        RamsayStData.data = new_data
        RamsayStData.save()
        postEvent(RamsayStData.changedEventName)

    def importButtonCallback(self, sender):
        path = GetFile(
            message="Where would you like to import Ramsay St. settings from?", 
            title="Import Ramsay St. Settings",
            allowsMultipleSelection=False, 
            fileTypes=["ramsaySt"], 
        )
        self.importGlyphNames(path)

    def exportButtonCallback(self, sender):
        self.exportGlyphNames()
        
    def importGlyphNames(self, path):
        if path:
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
            self.w.getItem("table").set([{"glyph_name": item.glyphName(), "left": item.left(), "right": item.right()} for item in RamsayStData.getItems()])
            self.saveSettingsData()

    def exportGlyphNames(self):
        path = PutFile(
            message="Where would you like to save these Ramsay St. settings?", 
            fileName="Untitled.ramsaySt",   
        )
        if path is None:
            return

        output = [
            "# Ramsay St. Glyph List",
            "# Use _ as a placeholder for 'no glyph'",
            "# <glyphName> <leftGlyphName> <rightGlyphName>"
        ]
        for glyphName in sorted(RamsayStData.keys()):
            left, right = RamsayStData.get(glyphName, (None, None))
            if all([left is not None, right is not None]):
                if left in (' ', ''):
                    left = '_'
                if right in (' ', ''):
                    right = '_'
                output.append(f"{glyphName} {left} {right}")
        with open(path, "w") as blob:
            blob.write("\n".join(output))


RamsayStSettingsController()
