from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import build_ext

ext_modules = [
      Extension("achilles_controller", ['lineReceiver/achilles_controller.py']),
      Extension("achilles_function", ["lineReceiver/achilles_function.py"]),
      Extension("achilles_node", ["lineReceiver/achilles_node.py"]),
      Extension("achilles_server", ["lineReceiver/achilles_server.py"]),
]

setup(
      name='achilles',
      cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules,
)
