from distutils.core import setup
from distutils.extension import  Extension
from Cython.Build import cythonize, build_ext

ext_modules = [
      Extension("cortex", ['cortex.py']),
      Extension("cortex_function", ["cortex_function.py"]),
      Extension("cortex_node", ["cortex_node.py"]),
      Extension("cortex_server", ["cortex_server.py"]),
]

setup(
      name='Cortex',
      cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules,
)

# python compile.py build_ext --inplace