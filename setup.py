#!/usr/bin/env python3
#
# Copyright 2020 The protobus developers.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Package protobus-server via setuptools."""

import os
import sys
import glob

import setuptools

import protobus_server

# Check if current IDL has been compiled
IDL_IN = "idl/"
IDL_OUT = "protobus_server/idl/"
idl_files = glob.glob(os.path.join(IDL_IN, "*.proto"))
for idl_file in idl_files:
    idl_mtime = os.stat(idl_file).st_mtime
    for suffix in "_pb2.py", "_pb2_grpc.py":
        path = idl_file.replace(IDL_IN, IDL_OUT).replace(".proto", suffix)
        if not os.path.exists(path) or os.stat(path).st_mtime < idl_mtime:
            print("Please regenerate the interface files; if grpcio-tools is installed run:\n" +
                  f"{sys.executable} -m grpc_tools.protoc -I{IDL_IN} " +
                  f"--python_out={IDL_OUT} --grpc_python_out={IDL_OUT} " +
                  os.path.join(IDL_IN, '*.proto'), file=sys.stderr)
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
