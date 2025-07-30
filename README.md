# Shell Material Assigner

**Shell Material Assigner** is a Python tool for Autodesk Maya that assigns random materials from a given list to each individual shell of the selected object.

<img width="243" height="221" alt="maya_fOsG6O9gHe" src="https://github.com/user-attachments/assets/3a6a6ea9-4980-40bd-8518-7a6123cd18ce" />

It’s useful for rapid visual prototyping, assets with many disconnected components, or imported meshes made of multiple shells.

---

## 🚀 How to Use

1. Run the script to open the tool's user interface.  
2. Select a polygonal object in your Maya scene.  
3. Enter the names of the materials you'd like to use (one per line).  
4. Click the "Assign Materials" button — each individual shell of the selected object will receive a random material from the list.


https://github.com/user-attachments/assets/bffca619-c687-4aa8-82b6-6eae441c9992


---

## 📁 Installation

1. Place `shell_material_assigner.py` in your Maya scripts folder or any accessible location  
   (for example: `C:\Users\user\Documents\maya\2019\scripts`).

2. In Maya’s Script Editor, run:

```python
import shell_material_assigner
shell_material_assigner.show_gui()
```
