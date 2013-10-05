import os.path
from sio.workers import ft
from sio.workers.util import replace_invalid_UTF

import os
import stat
import py_compile

# This function should be registered in setuptools' entry_points,
# under group 'sio.compilers', with a meaningful name, which will
# be matched from environ['compiler']. Specifically if environ['compiler']
# contains a dot, only the prefix before the dot is matched to find
# a suitable compiler.
#
# Default compiler for file extension 'py' should also be registered under
# 'default-py'. Extensions are matched in lowercase. There is no need
# to register default compilers for upper-case extensions.
def run(environ):
    if environ['compiler'] not in ('pythoncompiler'):
        raise RuntimeError("Compiler '%s' not found.", environ['compiler'])
    input_file = ft.download(environ, 'source_file', 'a.py')
    print input_file
    environ['compiler_output'] = "Compiler successfully"
    try:
        py_compile.compile(input_file, doraise=True)
        # if compiled then generate a bang header so that
        # it can run directly on the shell
        size = os.path.getsize(input_file)
        out = open('compiled', 'w')
        out.write("#!/bin/env python\n")
        out.write("# Compiled using pythoncompiler compiler named %s\n" % environ['compiler'])
        out.write("#\n")
        out.write(open(input_file).read())
        out.close()
        # change mode to make it executable
        mode = os.stat('compiled').st_mode
        os.chmod('compiled', mode | stat.S_IXUSR)
        environ['result_code'] = 'OK'
        ft.upload(environ, 'out_file', 'compiled')
    except py_compile.PyCompileError, e:
        environ['result_code'] = 'CE'
        environ['compiler_output'] = replace_invalid_UTF(str(e))
    return environ

# This function is registered as default compiler for extension '.py'
def run_default(environ):
    environ['compiler'] = 'pythoncompiler'
    return run(environ)
