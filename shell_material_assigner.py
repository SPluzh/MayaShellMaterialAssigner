import maya.OpenMaya as om
import maya.cmds as cmds
import random
import time

def get_mesh_shells(obj_name):
    """
    Detects and returns a list of face groups (shells) for a given polygonal mesh object.

    Args:
        obj_name (str): The name of the mesh object.

    Returns:
        List[List[str]]: A list of face name lists, each representing a separate shell.
    """
    selection_list = om.MSelectionList()
    selection_list.add(obj_name)
    dag_path = om.MDagPath()
    component = om.MObject()
    selection_list.getDagPath(0, dag_path, component)
    dag_path.extendToShape()

    face_count = 0
    face_connections = {}

    # Iterate over all faces and build a map of connected faces
    iter_poly = om.MItMeshPolygon(dag_path, component)
    while not iter_poly.isDone():
        face_id = iter_poly.index()
        connected_faces = om.MIntArray()
        iter_poly.getConnectedFaces(connected_faces)
        face_connections[face_id] = [connected_faces[i] for i in range(connected_faces.length())]
        face_count += 1
        iter_poly.next()

    visited = set()
    shells = []

    # Perform BFS to collect all connected face groups (shells)
    for i in range(face_count):
        if i in visited:
            continue

        shell = []
        queue = [i]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            shell.append(current)
            neighbors = face_connections.get(current, [])
            for n in neighbors:
                if n not in visited:
                    queue.append(n)

        shells.append(shell)

    # Format result as list of face names
    result = []
    for shell_ids in shells:
        result.append(["%s.f[%d]" % (obj_name, fid) for fid in shell_ids])

    return result

def assign_random_materials_from_list(shells, material_list):
    """
    Assigns existing materials from a list randomly to each shell.
    Automatically creates a shading group if one doesn't exist.

    Args:
        shells (List[List[str]]): List of face groups (shells).
        material_list (List[str]): List of material names.
    """
    if not material_list:
        cmds.error("Material list is empty.")

    shading_groups = []

    for material in material_list:
        if not cmds.objExists(material):
            cmds.warning("Material does not exist: %s" % material)
            continue

        sgs = cmds.listConnections(material, type="shadingEngine")
        if sgs:
            shading_groups.append(sgs[0])
        else:
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=material + "SG")
            cmds.connectAttr(material + ".outColor", sg + ".surfaceShader", force=True)
            shading_groups.append(sg)

    if not shading_groups:
        cmds.error("No available shading groups for assignment.")

    for shell_faces in shells:
        sg = random.choice(shading_groups)
        cmds.sets(shell_faces, edit=True, forceElement=sg)

def select_object_button(*args):
    """
    Callback for the 'Select' button. Gets the currently selected object in the scene
    and stores it in the UI.
    """
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Nothing selected.")
        return
    selected_object[0] = sel[0]
    cmds.textField("objectField", edit=True, text=sel[0])

def apply_materials_button(*args):
    """
    Callback for 'Assign Materials to Shells' button.
    Extracts mesh shells and assigns materials from the list.
    """
    obj = cmds.textField("objectField", q=True, text=True)
    if not obj or not cmds.objExists(obj):
        cmds.warning("Object not selected or does not exist.")
        return

    if not cmds.objectType(obj, isType='transform') or not cmds.listRelatives(obj, shapes=True, type='mesh'):
        cmds.warning("Selected object is not polygonal geometry.")
        return

    material_list = cmds.textScrollList("materialList", query=True, allItems=True)

    start_shells = time.time()
    shells = get_mesh_shells(obj)
    end_shells = time.time()
    print("get_mesh_shells - %.4f sec" % (end_shells - start_shells))
    
    start_assign = time.time()
    assign_random_materials_from_list(shells, material_list)
    end_assign = time.time()
    print("assign_random_materials_from_list - %.4f sec" % (end_assign - start_assign))

def add_selected_materials():
    """
    Adds selected materials from the scene into the material list in the UI.
    Avoids duplicates.
    """
    selected = cmds.ls(selection=True, materials=True)
    if selected:
        existing = cmds.textScrollList("materialList", query=True, allItems=True) or []
        for mat in selected:
            if mat not in existing:
                cmds.textScrollList("materialList", edit=True, append=mat)

def show_gui():
    """
    Displays the main GUI window for the Shell Material Assigner.
    Allows users to:
    - Select an object
    - Add materials
    - Assign materials to mesh shells
    """
    if cmds.window("shellMatWin", exists=True):
        cmds.deleteUI("shellMatWin")

    cmds.window("shellMatWin", title="Shell Material Assigner", widthHeight=(350, 250))

    # Outer layout with padding
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center", columnAttach=('both', 5))

    cmds.frameLayout(labelVisible=False, marginWidth=5, marginHeight=5)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

    # Object selection
    cmds.text(label="1. Select the object with shells:", align="left")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1,
                   columnAttach=[(1, 'both', 0), (2, 'both', 5)], columnWidth2=(220, 100))
    cmds.textField("objectField", editable=False)
    cmds.button(label="Select", command=select_object_button, backgroundColor=(0.1, 0.5, 0.45))
    cmds.setParent("..")

    cmds.separator(style="in", height=10)

    # Material list
    cmds.text(label="2. Add materials to the list:", align="left")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1,
                   columnAttach=[(1, 'both', 0), (2, 'both', 5)], columnWidth2=(220, 100))
    cmds.textScrollList("materialList", allowMultiSelection=True, height=100)
    cmds.button(label="Add", command=lambda *_: add_selected_materials(), backgroundColor=(0.1, 0.5, 0.45))
    cmds.setParent("..")

    cmds.separator(style="in", height=10)

    # Apply button
    cmds.button(label="Assign Materials to Shells", height=40, command=apply_materials_button, backgroundColor=(0.1, 0.5, 0.45))

    cmds.setParent("..")  # frameLayout
    cmds.setParent("..")  # columnLayout

    cmds.showWindow("shellMatWin")


# Launch the UI
show_gui()
