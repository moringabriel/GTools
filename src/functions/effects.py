# src/functions/effects.py
import nuke

def gradeZ1():
    """"""
    n = nuke.selectedNode()
    z = n.input(0)
    width = n.width()
    height = n.height()

    maxVal = 0
    minVal = 100000000

    for x in range(0, width, int(n['width'].value())):
        for y in range(0, height, int(n['height'].value())):
            sample = nuke.sample(n, 'red', x, y)

            if sample > maxVal:
                maxVal = sample

            if sample < minVal:
                minVal = sample

    grade = nuke.createNode('Grade')
    grade['blackpoint'].setValue(minVal)
    grade['whitepoint'].setValue(maxVal)
    grade['gamma'].setValue(2.5)
    grade.setInput(0, z)

    n['max'].setValue(maxVal)
    n['min'].setValue(minVal)


def gradeZ():
    """Grade a Z depth pass"""
    n = nuke.selectedNode()
    z = n.input(0)
    width = n.width()
    height = n.height()

    maxVal = 0
    minVal = 100000000

    # Sample 10x10 points across the image
    step_x = max(1, width // 10)
    step_y = max(1, height // 10)

    for x in range(0, width, step_x):
        for y in range(0, height, step_y):
            sample = nuke.sample(n, 'red', x, y)

            if sample > maxVal:
                maxVal = sample

            if sample < minVal:
                minVal = sample

    grade = nuke.createNode('Grade')
    grade['blackpoint'].setValue(minVal)
    grade['whitepoint'].setValue(maxVal)
    grade['gamma'].setValue(2.5)
    grade.setInput(0, z)

    # Check if the node has max/min knobs before setting them
    if 'max' in n.knobs() and 'min' in n.knobs():
        n['max'].setValue(maxVal)
        n['min'].setValue(minVal)






