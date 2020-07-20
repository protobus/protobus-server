# protobus-server

A minimalistic daemon providing a partitioned log message bus.

## Project goals

The aim of this project is to provide a lightweight alternative to existing log-based message brokers such as Apache Kafka, Amazon Kinesis Streams, or Twitter's DistributedLog. At this stage of the project we explicitly aim to support only a subset of the features of enterprise systems, which should make it easier to understand, get started, deploy, and operate.

The main features we are aiming for are:

- topic-based publish/subscribe system
- persistent, partitioned storage of messages on a local filesystem
  - configurable pattern matching rules define which topics go into which files
  - files may be auto-rotated at a configurable UTC offset and/or if exceeding a size limit
- opaque message payloads with a minimal set of properties to support filtering and observability
  - timestamps: client-specified event and transmit times, server-filled reception time; all three with nanosecond granularity
  - tags: an associative array (string keys, string values); for offline filtering
  - size: payload size; for observability
- in a single stream, subscribers may subscribe to multiple topics via pattern matching
- subscribers may begin from the last known message of a topic
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
