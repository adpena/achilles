from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import build_ext

ext_modules = [
      Extension("cortex", ['new_lineReceiver/cortex.py']),
      Extension("cortex_function", ["new_lineReceiver/cortex_function.py"]),
      Extension("cortex_node", ["new_lineReceiver/cortex_node.py"]),
      Extension("cortex_server", ["new_lineReceiver/cortex_server.py"]),
]

setup(
      name='cortex',
      cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules,
)
