# src/functions/channel_utils.py

import nuke
import random

rgbgrey = {'red': '#ff4040', 'green': '#40ff40', 'blue': '#4040ff', 'grey': '#808080'}


def shuffleReadLayers():
    import nuke

    # Get the selected node
    selected_node = nuke.selectedNode()

    # Deselect all nodes
    for node in nuke.allNodes():
        node.setSelected(False)

    # Get the name of the dependency node
    dependency_name = selected_node.dependencies()[0].name()

    # Get the layers from the dependency node
    layers = nuke.layers(nuke.toNode(dependency_name))

    # Get the prefix from the selected node
    prefix = selected_node['prefix_input'].value()

    # Check if prefix is present in the layers or is empty
    has_prefix_match = False
    for layer in layers:
        if prefix == '' or layer.startswith(prefix):
            has_prefix_match = True
            break

    if has_prefix_match:
        shuffle_list = []
        prefix_count = 0

        # Calculate new positions for nodes
        x_start = selected_node['xpos'].value()
        y_start = selected_node['ypos'].value()
        new_x = x_start
        new_y = y_start + 100

        # Create a Dot node if prefix is empty or present in layers
        if prefix == '' or has_prefix_match:
            dot = nuke.createNode('Dot', inpanel=False)
            dot['xpos'].setValue(x_start + 34)
            dot['ypos'].setValue(y_start)

            # Connect the Dot node to the first dependency node
            dot.setInput(0, nuke.toNode(dependency_name))

            # Create Shuffle nodes for each layer that matches the prefix
            print('\n')
            for i, layer in enumerate(layers):
                if prefix and not layer.startswith(prefix):
                    continue
                prefix_count += 1
                shuffle = nuke.createNode("Shuffle", inpanel=False)
                shuffle.setInput(0, dot)
                shuffle['in'].setValue(layer)
                shuffle['label'].setValue(layer)
                shuffle['xpos'].setValue(new_x)
                shuffle['ypos'].setValue(new_y)
                shuffle['postage_stamp'].setValue(True)
                shuffle_list.append(shuffle.name())
                new_x += 200

            # Show a message if no layers match the prefix
            if prefix_count == 0:
                raise ValueError("No layers match the prefix.")

            # Center the Shuffle nodes horizontally
            first_shuffle_xpos = nuke.toNode(shuffle_list[0])['xpos'].value()
            last_shuffle_xpos = nuke.toNode(shuffle_list[-1])['xpos'].value()
            x_diff = (last_shuffle_xpos - first_shuffle_xpos) / 2
            for shuffle in shuffle_list:
                shuffle_node = nuke.toNode(shuffle)
                new_xpos = shuffle_node['xpos'].value() - x_diff
                shuffle_node['xpos'].setValue(new_xpos)

            # Delete the selected node
            nuke.delete(selected_node)

        else:
            nuke.message("Prefix is not present in the layers. Input another prefix or no text.")
    else:
        nuke.message("No layers match the prefix. Input another prefix or no text.")

def splitChannelsFromSelectedNode():
    """Start a split channels nodes assembly from a selected node. """

    selected_nodes = nuke.selectedNodes()
    spacing = 200
    if len(selected_nodes) == 1:

        node = selected_nodes[0]

        starting_xpos = node['xpos'].value()
        starting_ypos = node['ypos'].value()

        dot1 = nuke.createNode('Dot', inpanel=False)
        dot1['label'].setValue('RGB SPLIT IN')
        dot1.setInput(0, None)

        redSplit = nuke.createNode('Shuffle', inpanel=False)
        redSplit['in'].setValue('rgba')
        redSplit['red'].setValue('red')
        redSplit['green'].setValue('black')
        redSplit['blue'].setValue('black')
        redSplit['alpha'].setValue('black')
        redSplit['label'].setValue('RED')
        redSplit['tile_color'].setValue(4278190335)
        redSplit.setInput(0, None)

        greenSplit = nuke.createNode('Shuffle', inpanel=False)
        greenSplit['in'].setValue('rgba')
        greenSplit['red'].setValue('black')
        greenSplit['green'].setValue('green')
        greenSplit['blue'].setValue('black')
        greenSplit['alpha'].setValue('black')
        greenSplit['label'].setValue('GREEN')
        greenSplit['tile_color'].setValue(16711935)
        greenSplit.setInput(0, None)

        blueSplit = nuke.createNode('Shuffle', inpanel=False)
        blueSplit['in'].setValue('rgba')
        blueSplit['red'].setValue('black')
        blueSplit['green'].setValue('black')
        blueSplit['blue'].setValue('blue')
        blueSplit['alpha'].setValue('black')
        blueSplit['label'].setValue('BLUE')
        blueSplit['tile_color'].setValue(65535)
        blueSplit.setInput(0, None)

        m1 = nuke.createNode('Merge2', inpanel=False)
        m1.setInput(0, None)
        m2 = nuke.createNode('Merge2', inpanel=False)
        m1.setInput(0, None)

        dot2 = nuke.createNode('Dot', inpanel=False)
        dot2.setInput(0, None)

        dot3 = nuke.createNode('Dot', inpanel=False)
        dot3.setInput(0, None)

        dot4 = nuke.createNode('Dot', inpanel=False)
        dot4['label'].setValue('RGB MERGE OUT')
        dot4.setInput(0, None)

        dot1.setInput(0, node)

        redSplit.setInput(0, dot1)
        greenSplit.setInput(0, dot1)
        blueSplit.setInput(0, dot1)

        dot2.setInput(0, redSplit)

        m1.setInput(0, greenSplit)
        m1.setInput(1, dot2)

        dot3.setInput(0, m1)

        m2.setInput(0, blueSplit)
        m2.setInput(1, dot3)

        dot4.setInput(0, m2)

        dot1['xpos'].setValue(starting_xpos + 36)
        dot1['ypos'].setValue(starting_ypos + (spacing / 2))

        dot1X = dot1['xpos'].value() - 36
        dot1Y = dot1['ypos'].value()

        redSplit['xpos'].setValue(dot1X - spacing)
        redSplit['ypos'].setValue(dot1Y + spacing)
        greenSplit['xpos'].setValue(dot1X)
        greenSplit['ypos'].setValue(dot1Y + spacing)
        blueSplit['xpos'].setValue(dot1X + spacing)
        blueSplit['ypos'].setValue(dot1Y + spacing)

        dot2['xpos'].setValue(dot1X - (spacing - 36))
        dot2['ypos'].setValue(dot1Y + (spacing * 2))

        m1['xpos'].setValue(dot1X)
        m1['ypos'].setValue(dot1Y + (spacing * 2))

        dot3['xpos'].setValue(dot1X + 36)
        dot3['ypos'].setValue(dot1Y + (spacing * 3))

        m2['xpos'].setValue(dot1X + spacing)
        m2['ypos'].setValue(dot1Y + (spacing * 3))

        dot4['xpos'].setValue(dot1X + 36)
        dot4['ypos'].setValue(dot1Y + (spacing * 4))

    elif len(selected_nodes) > 1:
        nuke.message('Select only one node.')
    else:
        nuke.message('Select a node.')

def split_frequencies_from_selected_node1():
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


def split_frequencies_from_selected_node(low_freq_blur_size=20, spacing=200):
    """
    Create a frequency split node setup from a selected node.

    Args:
        low_freq_blur_size (float, optional): Blur size for low frequencies. Defaults to 20.
        spacing (float, optional): Horizontal and vertical spacing between nodes. Defaults to 200.

    Returns:
        nuke.Node or None: The final merged node, or None if operation fails.
    """
    try:
        # Validate node selection
        selected_nodes = nuke.selectedNodes()

        if len(selected_nodes) == 0:
            nuke.message('Please select a node.')
            return None

        if len(selected_nodes) > 1:
            nuke.message('Select only one node.')
            return None

        # Get the selected source node
        source_node = selected_nodes[0]

        # Store original node position
        starting_xpos = source_node['xpos'].value()
        starting_ypos = source_node['ypos'].value()

        # Create nodes with more descriptive creation
        def create_labeled_dot(label, input_node=None):
            dot = nuke.createNode('Dot', inpanel=False)
            dot['label'].setValue(label)
            if input_node:
                dot.setInput(0, input_node)
            return dot

        # Create frequency split node network
        # Input dot
        dot_input = create_labeled_dot('FREQUENCIES SPLIT IN', source_node)

        # Low and Mid Frequency Dots
        dot_low_freq = create_labeled_dot('LOW FREQ', dot_input)
        dot_mid_freq = create_labeled_dot('MID FREQ', dot_input)

        # Blur for Low Frequencies
        blur_low_freq = nuke.createNode('Blur', inpanel=False)
        blur_low_freq['size'].setValue(low_freq_blur_size)
        blur_low_freq.setInput(0, dot_low_freq)

        # Subtract Mid from Low Frequencies
        subtract_freq = nuke.createNode('Merge2', inpanel=False)
        subtract_freq['operation'].setValue('from')
        subtract_freq['bbox'].setValue('union')
        subtract_freq.setInput(0, dot_mid_freq)
        subtract_freq.setInput(1, blur_low_freq)

        # Dot after subtraction
        dot_post_subtract = create_labeled_dot('MID FREQ - LOW FREQ', blur_low_freq)

        # Add Frequencies Back
        add_freq = nuke.createNode('Merge2', inpanel=False)
        add_freq['operation'].setValue('plus')
        add_freq['bbox'].setValue('union')
        add_freq.setInput(0, subtract_freq)
        add_freq.setInput(1, dot_post_subtract)

        # Output Dot
        dot_output = create_labeled_dot('FREQUENCIES MERGE OUT', add_freq)

        # Positioning Calculations
        def offset_x(base_x, offset):
            return base_x + offset

        def offset_y(base_y, offset):
            return base_y + offset

        # Adjust node positions precisely
        dot_input['xpos'].setValue(starting_xpos)
        dot_input['ypos'].setValue(offset_y(starting_ypos, spacing / 2))

        # Calculate base x and y for other nodes
        base_x = dot_input['xpos'].value() - 36
        base_y = dot_input['ypos'].value()

        # Position Low and Mid Frequency Dots
        dot_low_freq['xpos'].setValue(offset_x(base_x, -spacing + 36))
        dot_low_freq['ypos'].setValue(offset_y(base_y, spacing))

        dot_mid_freq['xpos'].setValue(offset_x(base_x, spacing + 36))
        dot_mid_freq['ypos'].setValue(offset_y(base_y, spacing))

        # Position Blur node
        blur_low_freq['xpos'].setValue(offset_x(base_x, -spacing))
        blur_low_freq['ypos'].setValue(offset_y(base_y, spacing * 1.35))

        # Position Subtract Frequencies node
        subtract_freq['xpos'].setValue(offset_x(base_x, spacing))
        subtract_freq['ypos'].setValue(offset_y(base_y, spacing * 1.35 + 6))

        # Position Dot after Subtraction
        dot_post_subtract['xpos'].setValue(offset_x(base_x, -spacing + 36))
        dot_post_subtract['ypos'].setValue(offset_y(base_y, spacing * 3))

        # Position Add Frequencies node
        add_freq['xpos'].setValue(offset_x(base_x, spacing))
        add_freq['ypos'].setValue(offset_y(base_y, spacing * 3))

        # Position Output Dot
        dot_output['xpos'].setValue(offset_x(base_x, 36))
        dot_output['ypos'].setValue(offset_y(base_y, spacing * 4))

        return dot_output

    except Exception as e:
        nuke.message(f'Error in frequency split: {str(e)}')
        print(f'Error in frequency split: {str(e)}')
        return None


def rgbConstant(color_hex):
    """Creates a Constant node with red color."""
    # red = 'red'
    color = rgbgreyHexTorgba(color_hex)
    rgbconstant = nuke.createNode('Constant', inpanel=False)
    rgbconstant['color'].setValue(color)


def red_constant():
    """Create a constant node with red color"""
    rgbConstant('red')


def green_constant():
    """Create a constant node with green color"""
    rgbConstant('green')


def blue_constant():
    """Create a constant node with blue color"""
    rgbConstant('blue')


def grey_constant():
    """Create a constant node with grey color"""
    rgbConstant('grey')


def alpha_constant():
    """Creates a Constant node with alpha."""
    alphaconstant = nuke.createNode('Constant', inpanel=False)
    alphaconstant['channels'].setValue('alpha')
    # alphaconstant['color'].setValue([0,0,0,1])

def rgbgreyHexTorgba(color):
    """Converts a color name or hex value to an RGBA list."""
    constantColor = color

    rgbgrey = {'red': '#ff0000', 'green': '#00ff00', 'blue': '#0000ff', 'grey': '#808080'}

    hex_value = rgbgrey[constantColor]

    red = int(hex_value[1:3], 16)
    green = int(hex_value[3:5], 16)
    blue = int(hex_value[5:7], 16)
    rgba = [red / 255.0, green / 255.0, blue / 255.0, 0.0]

    return rgba

def create_checkerboard():
    """ """
    nuke.createNode('CheckerBoard2', inpanel=False)


def random_primary_color():
    """" """
    # colors = [[0,1,1,1], [1,0,1,1], [1,1,0,1], [1,0,0,1], [0,1,0,1], [0,0,1,1], [0,0,0,1], [1,1,1,1], [.18,.18,.18,1]]
    colors = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 0, 0], [0, 1, 1, 0], [1, 0, 1, 0]]
    con = nuke.createNode('Constant', inpanel=False)
    con['color'].setValue(random.choice(colors))
    # print(random.choice(colors))
    # return random.choice(colors)


