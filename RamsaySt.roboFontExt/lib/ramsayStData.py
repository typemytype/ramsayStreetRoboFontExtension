from AppKit import NSColor, NSObject
from mojo.extensions import getExtensionDefault, setExtensionDefault, getExtensionDefaultColor, setExtensionDefaultColor

from constructions import readGlyphConstructions


class RamsayStDataItem(NSObject):

    def __new__(cls, *args, **kwargs):
        return cls.alloc().init()

    def __init__(self, glyphName, value):
        self._glyphName = glyphName
        self._value = list(value)

    def getRamsaySt(self):
        return self._value

    def glyphName(self):
        return self._glyphName

    def setGlyphName_(self, value):
        if value is None:
            return
        self._glyphName = value

    def left(self):
        return self._value[0]

    def setLeft_(self, value):
        if value is None:
            value = " "
        self._value[0] = value

    def right(self):
        return self._value[1]

    def setRight_(self, value):
        if value is None:
            value = " "
        self._value[1] = value


class RamsayStDataCollection(object):

    _fallBackFillColor = .34, .54, .92, .7
    _fallBackStrokeColor = 0, 0, 0, 1
    _fallbackData = {'-': ('n', 'H'), 'A': ('H', 'V'), 'C': ('c', 'G'), 'B': ('P', 'D'), 'E': ('B', 'F'), 'D': ('B', 'P'), 'G': ('C', 'O'), 'F': ('P', 'E'), 'I': ('J', 'H'), 'H': ('I', 'P'), 'K': ('k', 'I'), 'J': ('j', 'I'), 'M': ('H', 'N'), 'L': ('I', 'H'), 'O': ('C', 'o'), 'N': ('M', 'V'), 'Q': ('O', 'G'), 'P': ('R', 'p'), 'S': ('C', 's'), 'R': ('B', 'P'), 'U': ('u', 'H'), 'T': ('I', 'H'), 'W': ('w', 'V'), 'V': ('v', 'W'), 'Y': ('y', 'V'), 'X': ('x', 'Y'), 'Z': ('z', 'X'), 'a': ('n', 'e'), 'c': ('e', 'C'), 'b': ('d', 'p'), 'e': ('o', 'c'), 'd': ('q', 'b'), 'g': ('o', 'q'), 'f': ('i', 't'), 'i': ('period', 'j'), 'h': ('l', 'n'), 'k': ('h', 'K'), 'j': ('i', 'period'), 'm': ('n', 'w'), 'l': ('h', 'k'), 'o': ('c', 'O'), 'n': ('h', 'm'), 'q': ('d', 'p'), 'p': ('q', 'P'), 's': ('e', 'S'), 'r': ('s', 'n'), 'u': ('v', 'n'), 't': ('s', 'f'), 'w': ('v', 'W'), 'v': ('u', 'w'), 'y': ('v', 'Y'), 'x': ('y', 'X'), 'z': ('x', 'Z')}
    _fallbackShowNeighbours = True
    _fallbackShowPreview = True

    identifier = "com.typemytype.ramsaySt"
    fillColorDefaultKey = f"{identifier}.fillColor"
    strokeColorDefaultKey = f"{identifier}.strokeColor"
    showNeighboursDefaultKey = f"{identifier}.showNeighbours"
    showPreviewDefaultKey = f"{identifier}.showPreview"
    dataDefaultKey = f"{identifier}.data"

    changedEventName = f"{identifier}.settingChanged"

    def __init__(self):
        self.load()

    def load(self):
        self.fillColor = getExtensionDefault(self.fillColorDefaultKey, self._fallBackFillColor)
        self.strokeColor = getExtensionDefault(self.strokeColorDefaultKey, self._fallBackStrokeColor)
        self.showNeighbours = getExtensionDefault(self.showNeighboursDefaultKey, self._fallbackShowNeighbours)
        self.showPreview = getExtensionDefault(self.showPreviewDefaultKey, self._fallbackShowPreview)
        self.data = getExtensionDefault(self.dataDefaultKey, self._fallbackData)

    def save(self):
        setExtensionDefault(self.fillColorDefaultKey, self.fillColor)
        setExtensionDefault(self.strokeColorDefaultKey, self.strokeColor)
        setExtensionDefault(self.showNeighboursDefaultKey, self.showNeighbours)
        setExtensionDefault(self.showPreviewDefaultKey, self.showPreview)
        setExtensionDefault(self.dataDefaultKey, self.data)

    def keys(self):
        return self.data.keys()

    def clear(self):
        self.data.clear()

    def update(self, other):
        self.data.update(other)

    def __contains__(self, key):
        return key in self.data

    def get(self, value, fallback=("n", "n")):
        return self.data.get(value, fallback)

    def set(self, item):
        key = item.glyphName()
        if key is None:
            return
        self.data[key] = item.getRamsaySt()

    def setItems(self, data):
        self.data = dict()
        for item in data:
            self.data[item.glyphName()] = item.getRamsaySt()
        self.save()

    def getItems(self):
        keys = list(self.data.keys())
        keys.sort()
        return [RamsayStDataItem(key, self.data[key]) for key in keys]

    def newItem(self, glyphName):
        return RamsayStDataItem(glyphName, (" ", " "))

    accentsContstruction = readGlyphConstructions()

    def getBaseGlyph(self, name):
        construction = self.accentsContstruction.get(name)
        if construction is None:
            return name
        return construction[0]


RamsayStData = RamsayStDataCollection()
