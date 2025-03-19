def splitFrequenciesFromSelectedNode():
    """Start a split channels nodes assembly from a selected node. """

    selected_nodes = nuke.selectedNodes()
    spacing = 200
    if len(selected_nodes) == 1:

        node = selected_nodes[0]

        starting_xpos = node['xpos'].value()
        starting_ypos = node['ypos'].value()

        dot1 = nuke.createNode('Dot', inpanel=False)
        dot1['label'].setValue('FREQUENCIES SPLIT IN')
        dot1.setInput(0, None)

        dot2 = nuke.createNode('Dot', inpanel=False)
        dot2['label'].setValue('LOW FREQ')
        dot2.setInput(0, None)

        dot3 = nuke.createNode('Dot', inpanel=False)
        dot3['label'].setValue('MID FREQ')
        dot3.setInput(0, None)

        blurSource = nuke.createNode('Blur', inpanel=False)
        blurSource['size'].setValue(20)
        blurSource.setInput(0, None)

        subtractFreq = nuke.createNode('Merge2', inpanel=False)
        subtractFreq['operation'].setValue('from')
        subtractFreq['bbox'].setValue('union')
        subtractFreq.setInput(0, None)

        dot4 = nuke.createNode('Dot', inpanel=False)
        dot4.setInput(0, None)

        addFreq = nuke.createNode('Merge2', inpanel=False)
        addFreq['operation'].setValue('plus')
        addFreq['bbox'].setValue('union')
        addFreq.setInput(0, None)

        dot5 = nuke.createNode('Dot', inpanel=False)
        dot5['label'].setValue('FREQUENCIES MERGE OUT')
        dot5.setInput(0, None)

        dot1.setInput(0, node)
        dot2.setInput(0, dot1)
        dot3.setInput(0, dot1)

        subtractFreq.setInput(0, dot3)
        subtractFreq.setInput(1, blurSource)
        blurSource.setInput(0, dot2)
        dot4.setInput(0, blurSource)
        addFreq.setInput(0, subtractFreq)
        addFreq.setInput(1, dot4)
        dot5.setInput(0, addFreq)

        dot1['xpos'].setValue(starting_xpos)
        dot1['ypos'].setValue(starting_ypos + (spacing / 2))

        dot1X = dot1['xpos'].value() - 36
        dot1Y = dot1['ypos'].value()

        dot2['xpos'].setValue(dot1X - spacing + 36)
        dot2['ypos'].setValue(dot1Y + spacing)
        dot3['xpos'].setValue(dot1X + spacing + 36)
        dot3['ypos'].setValue(dot1Y + spacing)

        #dot2['xpos'].setValue(dot1X - (spacing - 36))
        #dot2['ypos'].setValue(dot1Y + (spacing * 2))

        subtractFreq['xpos'].setValue(dot1X + spacing)
        subtractFreq['ypos'].setValue(dot1Y + (spacing * 1.35) + 6)

        blurSource['xpos'].setValue(dot1X - spacing)
        blurSource['ypos'].setValue(dot1Y + (spacing * 1.35))

        dot4['xpos'].setValue(dot1X - spacing + 36)
        dot4['ypos'].setValue(dot1Y + (spacing * 3))

        addFreq['xpos'].setValue(dot1X + spacing)
        addFreq['ypos'].setValue(dot1Y + (spacing * 3))

        dot5['xpos'].setValue(dot1X + 36)
        dot5['ypos'].setValue(dot1Y + (spacing * 4))


    elif len(selected_nodes) > 1:
        nuke.message('Select only one node.')
    else:
        nuke.message('Select a node.')


splitFrequenciesFromSelectedNode()