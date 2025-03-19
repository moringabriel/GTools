import nuke
import math
import nukescripts

KNOB_NAME_PANEL = 'layer choice'
KNOB_NAME_PANEL_ENUMERATION = 'autoSelection'


def nodeSelected():
    analysedNode = nuke.selectedNodes()[:3]
    warningDict = {0: 'No node selected, please select one',
                   1: None,
                   2: 'Too many selected nodes, please chose only one :D!'
                   }
    warningMessage = warningDict[len(analysedNode)]
    if warningDict[len(analysedNode)]:
        nuke.message(warningMessage)
        return None
    else:
        return analysedNode[-1]


def getAlphaChannels(node):
    """
    Simple function to get alpha channels connected to a node that are in
    :param node: The Nuke node to sample channels
    :type node: :class:`nuke.Node`
    :return: List of probable alpha layers, or an empty list if None
    :rtype: list
    """
    nodeChannels = node.channels()
    forbiddenManualLayer = ['crypto', 'depth']
    alphaChans = ('alpha', 'a')
    alphaLayers = []

    for channel in nodeChannels:
        layer, chan = channel.split('.')
        if layer in forbiddenManualLayer:
            pass
        if chan in alphaChans:
            alphaLayers.append(layer)
    return alphaLayers


class layerPanel(nukescripts.PythonPanel):
    def __init__(self, node):
        nukescripts.PythonPanel.__init__(self, KNOB_NAME_PANEL)

        self.layerAvailable = getAlphaChannels(node)
        self._layerDict = createTagDict(self.layerAvailable)
        self.knobCreation()
        self.checkBox()

    def __repr__(self):
        return self._layerDict

    def knobCreation(self):
        pulldownCategoriesList = self._layerDict.keys()
        enumerationKnob = nuke.Enumeration_Knob(KNOB_NAME_PANEL_ENUMERATION,
                                                KNOB_NAME_PANEL_ENUMERATION,
                                                pulldownCategoriesList)
        boolCheckBoxList = [nuke.Boolean_Knob('{0}'.format(layer)) for layer in self.layerAvailable]

        knobs = [enumerationKnob] + boolCheckBoxList
        for knob in knobs:
            knob.setFlag(nuke.STARTLINE)
            self.addKnob(knob)

        self.boolCheckBoxList = boolCheckBoxList
        self.typeKnob = enumerationKnob

    def changeSelectionMemory(self, layerName):
        if layerName in self._layerDict[self.typeKnob.value()]:
            self._layerDict[self.typeKnob.value()].remove(layerName)
        else:
            self._layerDict[self.typeKnob.value()].append(layerName)

    def checkBox(self):
        for knob in self.boolCheckBoxList:
            checkLayer = knob.name()
            if checkLayer in self._layerDict[self.typeKnob.value()]:
                knob.setValue(True)
            else:
                knob.setValue(False)

    def knobChanged(self, knob):
        if isinstance(knob, nuke.Boolean_Knob):
            self.changeSelectionMemory(knob.name())
            self.checkBox()
        if isinstance(knob, nuke.Enumeration_Knob):
            self.checkBox()

    def returnLayerSelection(self):
        return [layer for layer in self._layerDict[self.typeKnob.value()]]


def panelLaunch(node):
    panelCreation = layerPanel(node)
    if panelCreation.showModalDialog():
        return panelCreation.returnLayerSelection()


def createNodes(node, layerSelection):
    """
    Create the nodes in the group.
    :param group: Roto_Combine node Object
    :type group: :class: `nuke.Group`
    :param amount: amount of creation loop
    :type amount: int
    :return: list of input nodes created,list of expression nodes created
    :rtype: list
    """
    dotNodes = []
    shufNodes = []
    DOT_DECAL, SHUF_DECAL = 34, 0
    amountCreation = len(layerSelection)
    initPosX, initPosY = node.xpos(), node.ypos()
    stepX, stepY = 100, 150

    typeclass = node.Class()
    if typeclass == 'Dot':
        DOT_DECAL, SHUF_DECAL = 0, -34

    rigthSide = int((math.floor(amountCreation / 2)) + 1)
    leftSide = int(rigthSide - amountCreation)

    for idx in range(leftSide, rigthSide):
        dotN = nuke.nodes.Dot()
        dotNodes.append(dotN)
        dotN.setXYpos((idx * stepX + initPosX + DOT_DECAL), (initPosY + stepY))

        shuffleN = nuke.nodes.Shuffle()
        shufNodes.append(shuffleN)
        shuffleN.setXYpos((idx * stepX + initPosX + SHUF_DECAL), (initPosY + stepY * 2))

    return dotNodes, shufNodes, amountCreation


def connectNodes(inputNodeName, dotNodesList, shufNodesList, amount):
    """
    Connect nodes in the group.
    :param group: Roto_Combine node Object
    :type group: :class: `nuke.Group`
    :param inputNodes: list of input nodes created
    :type inputNodes: list
    :param exprNodes: list of expression nodes created
    :type exprNodes: list
    :param amount: amount of creation loop
    :
 type amount: int
    """
    middleDotPosition = amount - (int((math.floor(amount / 2)) + 1))
    for idx, dotN in enumerate(dotNodesList):
        if idx < middleDotPosition:
            dotNodesList[idx].setInput(0, dotNodesList[idx + 1])
        if idx == middleDotPosition:
            dotNodesList[idx].setInput(0, inputNodeName)
        if idx > middleDotPosition:
            dotNodesList[idx].setInput(0, dotNodesList[idx - 1])

    for idx, shufN in enumerate(shufNodesList):
        shufN.setInput(0, dotNodesList[idx])


def setupShuffleNode(layerSelection, shufNodesList):
    for idx, sNode in enumerate(shufNodesList):
        sNode['in'].setValue(layerSelection[idx])
        sNode['label'].setValue('[value in]')


def launchCommand():
    NodeSelection = nodeSelected()
    if NodeSelection:
        layerSelection = panelLaunch(NodeSelection)
        if layerSelection:
            nodes = createNodes(NodeSelection, layerSelection)

    connectNodes(NodeSelection, nodes[0], nodes[1], nodes[2])
    setupShuffleNode(layerSelection, nodes[1])


def createTagDict(layerAvailable):
    dictByTag, dictRepetitiveTag = {}, {}
    thresh = 2
    dictRepetitiveTag['All'] = []
    dictRepetitiveTag['None'] = []

    for layer in layerAvailable:
        part = layer.split("_")
        for tag in part:
            if tag.isalpha():
                if tag in dictByTag:
                    dictByTag[tag] += [layer]
                else:
                    dictByTag[tag] = [layer]
    for tag in dictByTag:
        if len(dictByTag[tag]) >= thresh:
            dictRepetitiveTag[tag] = dictByTag[tag]

    for layer in layerAvailable:
        dictRepetitiveTag['All'].append(layer)

    return dictRepetitiveTag


launchCommand()






