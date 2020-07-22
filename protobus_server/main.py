#!/usr/bin/env python3

from . import __description__ as description

import argparse
import os
import sys


def main():
    # Add module paths and set environment to use the soon-to-be-default C++ ProtoBuf implementation
    sys.path.insert(0, os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(sys.path[0], "idl"))
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'cpp'

    from service import serve

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("--address", default="localhost:42000")
    parser.add_argument("--store-root", default=os.path.curdir)
    parser.add_argument("--store", nargs='+', default=["{topic}.log=.*"])
    parser.add_argument("--max-threads", type=int, default=101)

    args = parser.parse_args()

    serve(address=args.address,
          thread_pool_workers=args.max_threads,
          store_root=args.store_root,
          store_patterns=args.store)
