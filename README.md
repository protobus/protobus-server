# protobus-server

A minimalistic daemon providing a partitioned log message bus.

## Project goals

The aim of this project is to provide a lightweight alternative to existing log-based message brokers such as Apache Kafka, Amazon Kinesis Streams, or Twitter's DistributedLog. At this stage of the project we explicitly aim to support only a subset of the features of those enterprise systems, which should make it easier to understand, get started, deploy, and operate.

The main features we are aiming for are:

- topic-based publish/subscribe messaging system
- persistent, partitioned storage of messages on a local filesystem
  - configurable pattern matching rules define which topics go into which files
  - files may be auto-rotated at a configurable UTC offset and/or if exceeding a size limit
- opaque message payloads with a minimal set of properties to support filtering and observability
  - timestamps: client-specified event and transmit times, server-filled reception time; all three with nanosecond granularity
  - tags: an associative array (string keys, string values); for offline filtering
  - size: payload size; for observability
- in a single stream, subscribers may subscribe to multiple topics via pattern matching
- subscribers may start from a previous position in the history of a topic
- language-agnostic protocol definition

To keep the system simple we explicitly do *not* aim to support enterprise features such as:

- replication
- sharding

## Architecture

- the server spawns one thread for each subscription and each publishing channel
- each subscription
  - forwards the last known messages matching the subscription pattern to the subscriber
  - sets up a queue and forwards incoming messages to the subscriber (taking care to avoid race conditions)
- when a message is published it is pushed down all matching queues
- persistent storage is handled via the same mechanism: for each configured partition, a queue is setup with an associated writer thread

To limit process resources, a bounded thread pool is used. Since both publishers and subscribers may be long-lived processes, the size of the thread pool limits the maximum number of topics the server may handle.

## Installation

The latest version of protobus-server is published on the [Python package index](https://pypi.org/project/protobus-server/). You may use `pip3` to install or upgrade to the latest version:

```
pip3 install --user --upgrade protobus-server
```

If the location of the `protobus-server` executable is not in your shell's `PATH` environment variable, `pip` will emit a warning informing you where it has been installed. You can either launch `protobus-server` using its full path or add the parent `bin` directory to `PATH`.

## Usage

`protobus-server` may be started with the following arguments:

```
-h, --help            show this help message and exit
--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
--address ADDRESS:PORT
                      bind on ADDRESS and listen for gRPC connections on PORT; if ADDRESS is omitted, listen on all interfaces (default: listen on port 42000 on local interfaces)
--store-root PATH     use PATH for the destination of the persistent data store; PATH is considered relative to the current working directory (which is also the default destination)
--store-pattern FILE_PREFIX:TOPIC_REGEX [FILE_PREFIX:TOPIC_REGEX ...]
                      store topics matching the regular expression into a file with the given prefix (default: one file per topic); any occurence of {topic} in FILE_PREFIX will be
                      replaced with the actual message topic; the argument may be specified multiple times
--max-threads N       serve up to N channels; this limits the active publishers, subscriptions, and file writers (default: 101)
```

## Technological choices & limitations

The project is currently in a prototyping stage. The following choices have been made to minimise effort to reach an MVP:

- Google Protocol Buffers as serialisation framework (even though it adds considerable allocation overhead by design)
- gRPC as transport protocol (even though its HTTP transport adds considerable overhead and complexity)
- Python 3 as implementation language (even though its current gRPC implementation lacks parallelism)

The combination of these choices will likely limit the performance of the MVP to the order of 10,000 messages/s. For all of these technologies, more efficient alternatives exist—at a later stage, these will be considered.
