# src/functions/node_arrangement.py
import nuke

def connectSelectedNodesToLastSelectedNode():
    print(nuke.selectedNodes())

    base = nuke.selectedNodes()[0]

    for node in nuke.selectedNodes()[1:]:
        node.setInput(0, base)

def x_auto_place():
    """" """
    nodes = nuke.selectedNodes()

    xpos_dictionary = {}

    if nodes != []:
        for node in nodes:
            xpos = node['xpos'].value()
            xpos_dictionary[xpos] = node['name'].value()

        print(xpos_dictionary)
        sortedxposition = sorted(xpos_dictionary)

        newxposition = sortedxposition[0]
        print(newxposition)

        for position in sortedxposition[:]:
            newxposition = newxposition + 100
            nuke.toNode(xpos_dictionary[position])['xpos'].setValue(newxposition)
    else:
        print('No node is selected.')


def y_auto_place():
    """"to do review code for y axis """
    nodes = nuke.selectedNodes()

    xpos_dictionary = {}

    for node in nodes:
        xpos = node['xpos'].value()
        xpos_dictionary[xpos] = node['name'].value()

    print(xpos_dictionary)
    sortedxposition = sorted(xpos_dictionary)

    newxposition = sortedxposition[0]
    print(newxposition)

    for position in sortedxposition[:]:
        newxposition = newxposition + 100
        nuke.toNode(xpos_dictionary[position])['xpos'].setValue(newxposition)


def align_x_pos():
    """" """
    a = nuke.selectedNodes()
    listXpos = []
    for i in a:
        print(i.xpos())
        listXpos.append(i.xpos())

    listXpos.sort()

    for i in a:
        i['xpos'].setValue(listXpos[0])

def align_y_pos():
    """" """
    a = nuke.selectedNodes()
    listYpos = []
    for i in a:
        print(i.ypos())
        listYpos.append(i.ypos())

    listYpos.sort()

    for i in a:
        i['ypos'].setValue(listYpos[0])

def zoomOneByOneToSelectedNodes():
    """ """

def createBackdropNodeToPosition():
    """ Create a backdrop node with label to a pointed position
    parameter: Input string for label value
    """
    # text =
    width = len(text) * 64
    height = 140

    nuke.createNode('BackdropNode', 'label {} note_font_size 100 bdwidth {} bdheight {}'.format(text, width, height),
                    inpanel=False)

    bd = nuke.createNode('BackdropNode',
                         name='MyBackdrop',
                         label='My Backdrop',
                         bdwidth=300,
                         bdheight=200,
                         xpos=100,
                         ypos=100)


def enable_postage_stamp1():
    """Enable postage stamp knob"""
    # Check if there is a selection
    selection = nuke.selectedNodes()
    if selection:
        for node in selection:
            if node.knob('postage_stamp'):
                node['postage_stamp'].setValue(True)
    else:
        for node in nuke.allNodes():
            if node.knob('postage_stamp'):
                node['postage_stamp'].setValue(True)

def disable_postage_stamp1():
    """Disable postage stamp knob"""
    # Check if there is a selection
    selection = nuke.selectedNodes()
    if selection:
        for node in selection:
            if node.knob('postage_stamp'):
                node['postage_stamp'].setValue(False)
    else:
        for node in nuke.allNodes():
            if node.knob('postage_stamp'):
                node['postage_stamp'].setValue(False)


def toggle_postage_stamp(enable=True):
    """
    Toggle postage stamp visibility for selected or all nodes.

    Args:
        enable (bool, optional): True to enable, False to disable. Defaults to True.

    Returns:
        int: Number of nodes affected
    """
    try:
        # Determine which nodes to process
        nodes_to_process = nuke.selectedNodes() or nuke.allNodes()

        # Count of nodes modified
        modified_count = 0

        # Process each node
        for node in nodes_to_process:
            # Check if node has postage_stamp knob
            postage_stamp_knob = node.knob('postage_stamp')
            if postage_stamp_knob is not None:
                node['postage_stamp'].setValue(enable)
                modified_count += 1

        # Optional: Provide feedback
        if modified_count == 0:
            nuke.message("No nodes with postage stamp knob found.")

        return modified_count

    except Exception as e:
        nuke.message(f"Error toggling postage stamp: {str(e)}")
        print(f"Error toggling postage stamp: {str(e)}")
        return 0


def enable_postage_stamp():
    """Enable postage stamp for selected or all nodes."""
    return toggle_postage_stamp(enable=True)


def disable_postage_stamp():
    """Disable postage stamp for selected or all nodes."""
    return toggle_postage_stamp(enable=False)