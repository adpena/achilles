Make it so that arguments are streamed from cortex by default and not fed in one packet loaded from cortex_config.yaml - use cortex_config.yaml to define the args using python

Composable scalability - test generators in cortex_function.py and to define args in cortex - "What if I want to use this on a 1 TB file?"

---

Encryption/authentication/security concerns

Zip/compression

Cythonize - how to automate for each platform the cortex_server or cortex_node might be deployed on? Compile for common platforms and then test during runtime to determine whether CPython or Cython implementation should be used?

Rustify any remaining bottlenecks