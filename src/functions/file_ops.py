# src/functions/file_ops.py
import nuke

def loadLatestCgRender():
    import os
    # import nuke
    from posixpath import join

    show = 'hrg'
    shot = '101_351720'
    sequence = shot[0:3]

    path = 'C:/shows/hrg/.published/101/101_341720/render'

    print()
    print(path)

    # print(os.listdir(path))
    render_layers = []
    readNodesName = []
    for folder_name in os.listdir(path):
        if "lig" in folder_name:
            render_layers.append(folder_name)
    print("These are the render layers:" + str(render_layers))

    for layer in render_layers:
        layer_path = os.path.join(path, layer)
        if len(os.listdir(layer_path)) == 0:
            print('yes')
            render_layers.remove(layer)

    # List of render layers
    layers = render_layers

    # Loop through each render layer
    for layer in layers:
        # List of versions for the current render layer
        versions = []
        # Loop through each version folder in the current render layer directory
        for version_folder in os.listdir(join(path, layer)):
            # Check if the file is a folder (by checking the file extension)
            if os.path.isdir(join(path, layer, version_folder)):
                # Get the version number from the folder name
                version = int(version_folder.split("v")[-1])
                # Add the version number to the list
                versions.append(version)

        # Get the latest version number
        latest_version = max(versions)
        # Get the path to the latest version files
        latest_path = join(path, layer, latest_version)
        # Get the latest image sequence
        latest_path_images = []
        for file in os.listdir(latest_path):
            if ".exr" in file:
                latest_path_images.append(file)
                # Get the first frame of the sequence
        first_frame = int(latest_path_images[0].split('.')[-2])
        print(first_frame)
        # Get the last frame of the sequence
        last_frame = int(latest_path_images[-1].split('.')[-2])
        # Create read node and set knobs
        # read = nuke.nodes.Read()
        """
        read = nuke.createNode('Read', inpanel=False)
        read['file'].setValue(join(latest_path, latest_path_images[0]))
        read['first'].setValue(first_frame)
        read['last'].setValue(last_frame)
        read['origfirst'].setValue(first_frame)
        read['origlast'].setValue(last_frame)
        nuke.autoplace(read)
        #

        readNodesName.append(read['name'].value())
        """


def load_latest_elements():
    def loadLatestCgRender():
        import os
        import nuke
        from posixpath import join

        show = 'hrg'
        shot = '101_350360'
        sequence = shot[0:3]

        # path = 'C:/shows/{}/.published/{}/{}/render/'.format(show,sequence,shot)
        # path = 'C:\\shows\\{}\\.published\\{}\\{}\\render'.format(show,sequence,shot)
        path = '/rdo/shows/hrg/.published/101/101_350360/render/'
        # path = 'C:\\shows\\hrg\\.published\\101\\101_341720\\render'

        # print()
        # print(path)

        # print(os.listdir(path))

        context = 'lig'

        # read_type = 'rdo'
        read_type = 'read'

        render_layers = []
        readNodesName = []
        for folder_name in os.listdir(path):
            if context in folder_name:
                render_layers.append(folder_name)
        print()
        # print("These are the render layers:")
        for layer in render_layers:
            # print(layer)
            pass

        # List of render layers
        layers = render_layers

        # Loop through each render layer
        for layer in layers:
            # List of versions for the current render layer
            versions = []
            # Loop through each version folder in the current render layer directory
            for version_folder in os.listdir(join(path, layer)):
                # Check if the file is a folder (by checking the file extension)
                if os.path.isdir(join(path, layer, version_folder)):
                    # Get the version number from the folder name
                    version = int(version_folder.split("v")[-1])
                    # Add the version number to the list
                    versions.append(version)
            # If there are no versions for the current layer, skip it and move on to the next layer
            if not versions:
                print("No versions found for layer", layer)
                continue
            # Get the latest version number
            latest_version = max(versions)
            # Get the path to the latest version files
            latest_path = join(path, layer, version_folder)
            # Get the latest image sequence
            latest_path_images = []
            for file in os.listdir(latest_path):
                if ".exr" in file:
                    latest_path_images.append(file)
                    # Get the first frame of the sequence
            first_frame = int(latest_path_images[0].split('.')[-2])
            # Get the last frame of the sequence
            last_frame = int(latest_path_images[-1].split('.')[-2])
            # Create read node and set knobs
            # read = nuke.nodes.Read()
            # read = nuke.createNode('ReadRdo', inpanel=False)

            path_images = join(latest_path, latest_path_images[0].split('.')[0]) + '.%04d.exr'
            # path_images = join(latest_path, latest_path_images[0])
            print()
            print(path_images)
            print()

            if read_type == 'rdo':
                read = nuke.createNode('ReadRdo', inpanel=False)
                read['file'].setValue(path_images)
            else:
                pass
            if read_type == 'read':
                read = nuke.createNode('Read', inpanel=False)
                read['file'].setValue(path_images)
                read['first'].setValue(first_frame)
                read['last'].setValue(last_frame)
                read['origfirst'].setValue(first_frame)
                read['origlast'].setValue(last_frame)
            else:
                print('ok')

            nuke.autoplace(read)
            #
            readNodesName.append(read['name'].value())

    loadLatestCgRender()

def reloadAllReads():
    """relaodAllReads"""
    allNodes = nuke.allNodes()
    for node in allNodes:
        node.setSelected(False)

    for node in allNodes:
        if node.Class() == 'Read':
            node.setSelected(True)

    for node in nuke.selectedNodes():
        node['reload'].execute()
        print('test')

def setScriptFrameRangeToSelectedRead():
    """ Set the script frame range to the selected read node range."""
    selected_nodes = nuke.selectedNodes('Read')
    if len(selected_nodes) == 1:
        first_frame = selected_nodes[0]['first'].value()
        last_frame = selected_nodes[0]['last'].value()
        print(first_frame, last_frame)
        nuke.Root()['first_frame'].setValue(first_frame)
        nuke.Root()['last_frame'].setValue(last_frame)
    else:
        if len(selected_nodes) == 0:
            nuke.message('Please select a Read node.')
        else:
            nuke.message('Please select only one Read node.')



def openSelectedReadDir2():
    """Open selected read node path directory"""
    node = nuke.selectedNode()
    path = node['file'].value()
    pdir = (('/').join(path.split('/')[:-1]))
    os.startfile(pdir)


def openSelectedReadDir():
    """Open selected read nodes path directory. """
    nodes = nuke.selectedNodes()
    if len(nodes) != 0:
        for node in nodes:
            if node.Class() == 'Read':
                print('read node selected: ' + node['name'].value())
                path = node['file'].value()
                pdir = (('/').join(path.split('/')[:-1]))
                os.startfile(pdir)
            else:
                print('not a read node: ' + node['name'].value())
    else:
        nuke.message('No node selected')


def openCurrentNukeScriptDir1():
    """Open current nuke script directory"""
    nukeScriptName = nuke.Root()['name'].value()
    nukeScriptPath = ('/').join(nukeScriptName.split('/')[:-1])
    os.startfile(nukeScriptPath)


def openCurrentNukeScriptDir2():
    """Open current nuke script directory"""
    import platform
    nukeScriptName = nuke.Root()['name'].value()
    nukeScriptPath = ('/').join(nukeScriptName.split('/')[:-1])

    # Check operating system and open directory accordingly
    if platform.system() == 'Windows':
        os.startfile(nukeScriptPath)
    elif platform.system() == 'Linux':
        os.system('xdg-open "{}"'.format(nukeScriptPath))
    else:
        print('Unsupported operating system.')


def open_current_nuke_script_dir():
    """
    Open the directory of the current Nuke script.

    Raises:
    - ValueError: If the Nuke script has not been saved.
    - OSError: If there's an error opening the directory.
    """
    import os
    import platform
    import nuke

    # Check if the script has been saved
    nukeScriptName = nuke.Root()['name'].value()
    if nukeScriptName == 'Root':
        raise ValueError("Please save the Nuke script first before trying to open its directory.")

    try:
        # Get the directory path
        nukeScriptPath = os.path.dirname(nukeScriptName)

        # Check operating system and open directory accordingly
        if platform.system() == 'Windows':
            os.startfile(nukeScriptPath)
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{nukeScriptPath}"')
        elif platform.system() == 'Linux':
            os.system(f'xdg-open "{nukeScriptPath}"')
        else:
            raise OSError('Unsupported operating system.')

    except Exception as e:
        nuke.message(f"Error opening directory: {str(e)}")
        print(f"Error opening directory: {str(e)}")


def openUserDotNukeFolder():
    """Open user .nuke folder."""
    home_dir = os.path.expanduser("~")
    dot_nuke_folder = home_dir + '\.nuke'
    os.startfile(dot_nuke_folder)


def convert_text_and_jpeg():
    import base64

    def jpeg_to_text(jpeg_path, txt_path):
        with open(jpeg_path, 'rb') as jpeg_file:
            jpeg_bytes = jpeg_file.read()
            base64_bytes = base64.b64encode(jpeg_bytes)
            base64_string = base64_bytes.decode('utf-8')

        with open(txt_path, 'w') as txt_file:
            txt_file.write(base64_string)

    def text_to_jpeg(txt_path, jpeg_path):
        with open(txt_path, 'r') as txt_file:
            base64_string = txt_file.read()
            base64_bytes = base64_string.encode('utf-8')
            jpeg_bytes = base64.b64decode(base64_bytes)

        with open(jpeg_path, 'wb') as jpeg_file:
            jpeg_file.write(jpeg_bytes)

    # Convert a JPEG image to a text file
    jpeg_to_text('image.jpg', 'image.txt')

    # Convert a text file to a JPEG image
    text_to_jpeg('image.txt', 'image_new.jpg')
