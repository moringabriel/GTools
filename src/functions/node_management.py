# ....
import nuke

def deleteAllNodesOfAType():
    """ """
    nodeClass = 'Grade'
    nodes = nuke.allNodes(nodeClass)
    for node in nodes:
        node.setSelected('True')
        # nuke.dele

def removeDisconnectedNodes():
    """ """
    # Get the root node
    root = nuke.toNode('root')

    # Get all nodes in the node graph
    nodes = nuke.allNodes()

    # Iterate through each node in the node graph
    for node in nodes:

        # Skip Viewer objects
        if isinstance(node, nuke.Viewer):
            continue

        # Check if the node is connected to any other nodes
        inputs = node.inputs()
        outputs = node.dependent()

        # If the node has no input or output connections, delete it
        if not inputs and not outputs:
            nuke.delete(node)

def closeAllOpenNodesPanel():
    # print(nuke.openPanels())
    for node in nuke.openPanels():
        nuke.toNode(node).hideControlPanel()

def selectNodesWithAnimationKey():
    """ """
    # Close all open property panels
    for panel in nuke.allPaneTabs():
        for p in panel:
            p.hide()

    # Open property panels for nodes with animation
    nodesWithAnimation = []
    for node in nuke.allNodes():
        animated = False
        for knob in node.knobs():
            if node[knob].isAnimated() or node[knob].hasExpression():
                animated = True
                node.setSelected(True)
                break

        if animated and not node['disable'].value():
            nodesWithAnimation.append(node['name'].value())
            node.showControlPanel()

    print("Nodes with animation: ", nodesWithAnimation)



def addGUIExpressionToSelectedNodes():
    """ """
    node = nuke.selectedNode()
    knob = node['disable']

    if knob.hasExpression():
        knob.clearAnimated()
        nukescripts.toggle('disable')
    else:
        node['disable'].setExpression('$gui ? 1:0')

def removeItemsFromMenuNodes():
    """ """
    # import the nuke module
    import nuke

    # get the list of items in the "Nodes" menu
    menus = nuke.menu("Nodes").items()

    # get the value of the "item_name" knob of the currently selected node
    item_to_remove = nuke.selectedNode()['item_name'].value()

    # initialize an empty list to store the indices of items to remove
    index_to_remove = []

    # check if item_to_remove is empty and display a message if it is
    if item_to_remove == '':
        nuke.message('Input a menu name.')

    # if not empty run this code
    else:
        # loop through the menu items and add the index of any items with a matching name to index_to_remove
        for i, item in enumerate(menus):
            if item_to_remove == item.name():
                index_to_remove.append(i)
            else:
                pass

        # if no items with a matching name were found, display a message
        if index_to_remove == [] and item_to_remove != '':
            print("No {} menu".format(item_to_remove))
            nuke.message("No {} menu".format(item_to_remove))
        # otherwise, remove the items from the menu and display a confirmation message
        else:
            for index in index_to_remove:
                nuke.menu("Nodes").removeItem(menus[index].name())

            nuke.message('{} menu was temporarily removed'.format(item_to_remove))



