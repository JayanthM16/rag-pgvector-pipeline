# Kafka and Change Data Capture

Apache Kafka is a distributed event streaming platform. Events are written to topics, which are split into partitions. Ordering is guaranteed only within a single partition, and consumers in a consumer group share the partitions of a topic to scale reads. Consumers track their position using offsets.

Change data capture, or CDC, streams row-level changes from a database into Kafka. Debezium is a popular CDC tool that reads the database transaction log, such as the PostgreSQL write-ahead log, and publishes insert, update, and delete events. Each Debezium event contains the before and after state of the row, an operation code, and source metadata including the log sequence number.

Spark Structured Streaming can read these topics in micro-batches. Combining checkpointed offsets with an idempotent sink, such as a MERGE guarded by the log sequence number, gives effectively-once processing even when batches are retried.
