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
    shutil.copy(f"{path}\\{module}", f"{path}\\cythonized\\pyx\\{module}x")

ext_modules = [
    Extension("achilles_controller", ["pyx\\achilles_controller.pyx"]),
    Extension("achilles_main", ["pyx\\achilles_main.pyx"]),
    Extension("achilles_node", ["pyx\\achilles_node.pyx"]),
    Extension("achilles_node2", ["pyx\\achilles_node2.pyx"]),
    Extension("achilles_node3", ["pyx\\achilles_node3.pyx"]),
    Extension("achilles_node4", ["pyx\\achilles_node4.pyx"]),
    Extension("achilles_server", ["pyx\\achilles_server.pyx"]),
]

setup(name="achilles", cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)
