import protobus_server

import os
import setuptools
import sys
import glob

# Check if current IDL has been compiled
idl_in = "idl/"
idl_out = "protobus_server/idl/"
idl_files = glob.glob(os.path.join(idl_in, "*.proto"))
for idl_file in idl_files:
    idl_mtime = os.stat(idl_file).st_mtime
    for suffix in "_pb2.py", "_pb2_grpc.py":
        path = idl_file.replace(idl_in, idl_out).replace(".proto", suffix)
        if not os.path.exists(path) or os.stat(path).st_mtime < idl_mtime:
            cmd = f"{sys.executable} -m grpc_tools.protoc -I{idl_in} --python_out={idl_out} --grpc_python_out={idl_out} {os.path.join(idl_in, '*.proto')}"
            print(f"Please regenerate the interface files (requires the grpcio-tools package):", file=sys.stderr)
            print(cmd, file=sys.stderr)
            sys.exit(1)

# Read requirements and long description from files
requirements = open("requirements.txt", "r").readlines()
long_description = open("README.md", "r", encoding="utf-8").read()

# Define setup
setup_kwargs = {
    'name': "protobus-server",
    'version': protobus_server.__version__,
    'description': protobus_server.__description__,
    'long_description': long_description,
    'long_description_content_type': "text/markdown",
    'author': "The protobus developers",
    'author_email': "protobus@mpi-hd.mpg.de",
    'maintainer': "Felix Werner",
    'maintainer_email': "protobus-maintainer@mpi-hd.mpg.de",
    'url': "https://github.com/protobus/protobus-server",
    'license': 'MIT/Apache-2.0',
    'packages': setuptools.find_packages(),
    'classifiers': [
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
    'python_requires': '>=3.6',
    'install_requires': requirements,
    'entry_points': {'console_scripts': ["protobus-server = protobus_server.main:main"]}
}

setuptools.setup(**setup_kwargs)
