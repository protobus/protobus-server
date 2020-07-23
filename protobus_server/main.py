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

"""Entry point for the protobus-server executable."""

import argparse
import logging
import os
import sys


def main():
    """Main entry point for the protobus-server executable. Sets up the environment for
    module-local imports, parses command-line parameters, and starts the service via
    service.server()."""

    # Add module paths and set environment to use the soon-to-be-default C++ ProtoBuf implementation
    sys.path.insert(0, os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(sys.path[0], "idl"))
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'cpp'

    # After setting up the path we can import the service -- this would not have worked at the top
    # level
    from service import serve  # pylint: disable=import-outside-toplevel
    from protobus_server import __description__ as description  # pylint: disable=import-outside-toplevel

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--log-level', default='INFO',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument("--address", default="localhost:42000", metavar="ADDRESS:PORT",
                        help="bind on ADDRESS and listen for gRPC connections on PORT; if ADDRESS "
                        "is omitted, listen on all interfaces (default: listen on port 42000 on "
                        "local interfaces)")
    parser.add_argument("--store-root", default="", metavar="PATH",
                        help="use PATH for the destination of the persistent data store; PATH is "
                        "considered relative to the current working directory (which is also the "
                        "default destination)")
    parser.add_argument("--store-pattern", nargs='+', default=["{topic}:.*"],
                        metavar="FILE_PREFIX:TOPIC_REGEX",
                        help="store topics matching the regular expression into a file with the "
                        "given prefix (default: one file per topic); any occurence of {topic} in "
                        "FILE_PREFIX will be replaced with the actual message topic; the argument "
                        "may be specified multiple times")
    parser.add_argument("--max-threads", type=int, default=101, metavar='N',
                        help="serve up to N channels; this limits the active publishers, "
                        "subscriptions, and file writers (default: 101)")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=args.log_level)

    return serve(address=args.address,
                 thread_pool_workers=args.max_threads,
                 store_root=os.path.join(os.path.curdir, args.store_root),
                 store_patterns=args.store_pattern)
