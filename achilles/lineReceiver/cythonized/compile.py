from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import build_ext

import os
import shutil

path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

achilles_modules = [
    "achilles_server.py",
    "achilles_node.py",
    "achilles_node2.py",
    "achilles_node3.py",
    "achilles_node4.py",
    "achilles_controller.py",
    "achilles_main.py",
]

for module in achilles_modules:
    shutil.copy(f"{path}\\{module}", f"{path}\\cythonized\\{module}x")

ext_modules = [
    Extension("achilles_controller", ["achilles_controller.pyx"]),
    Extension("achilles_main", ["achilles_main.pyx"]),
    Extension("achilles_node", ["achilles_node.pyx"]),
    Extension("achilles_node2", ["achilles_node2.pyx"]),
    Extension("achilles_node3", ["achilles_node3.pyx"]),
    Extension("achilles_node4", ["achilles_node4.pyx"]),
    Extension("achilles_server", ["achilles_server.pyx"]),
]

setup(name="achilles", cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)
