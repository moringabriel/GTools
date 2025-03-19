import os


def readFile_python_script(path):
    files = path
    with open(files, 'r') as f:
        script_contents = f.read()

    print(script_contents)

def print_dir_list():
    for item in os.listdir(dir_path):
        print(item)

def abc():
    import rdo_comp_pipeline

    path = rdo_comp_pipeline.__file__
    path = path[:-11]

    print(path)

    import os
    import subprocess
    import platform

    def open_file_explorer(path):
        if platform.system() == "Windows":
            subprocess.Popen('explorer /select,"{}"'.format(path))
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', '-R', path])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(path)])

def my_function():
    """TESt"""
    print("This is a function in the GTools package.")