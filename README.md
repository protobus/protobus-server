# protobus-server

A minimalistic daemon providing a partitioned log message bus.

# Project goals

The aim of this project is to provide a lightweight alternative to existing log-based message brokers such as Apache Kafka, Amazon Kinesis Streams, or Twitter's DistributedLog. At this stage of the project we explicitly aim to support only a subset of the features of enterprise systems, which should make it easier to understand, get started, deploy, and operate. The main features we are aiming for are:

- topic-based publish/subscribe system
- persistent, partitioned storage of messages on a local filesystem
  - configurable pattern matching rules define which topics go into which files
  - files may be auto-rotated at a specific UTC offset and/or if above a specific size
- opaque message payloads with a minimal set of properties
  - timestamps: client-specified ("event") time and reception time (filled by the server); both with nanosecond granularity
  - tags: an associative array (string keys, string values); for offline filtering
  - size: payload size; for observability
- in a single stream, subscribers may subscribe to multiple topics via pattern matching
- subscribers may begin from the last known message of a topic
- language-agnostic protocol definition

To keep the system simple we explicitly do *not* aim to support enterprise features such as:

- replication
- sharding
