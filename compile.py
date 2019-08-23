from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import build_ext

ext_modules = [
    Extension("achilles_controller", ["achilles/lineReceiver/Cythonized/achilles_controller.py"]),
    Extension("achilles_node", ["achilles/lineReceiver/Cythonized/achilles_node.py"]),
    Extension("achilles_server", ["achilles/lineReceiver/Cythonized/achilles_server.py"]),
    Extension("achilles_server", ["achilles/lineReceiver/Cythonized/achilles_main.py"]),
]

setup(name="achilles", cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)
