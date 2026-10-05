# Apache Iceberg

Apache Iceberg is an open table format for huge analytic datasets. A table is described by metadata files that point to manifest lists, manifests, and finally data files. Every commit creates a new snapshot, so Iceberg supports time travel and rollback to any retained snapshot.

Iceberg has hidden partitioning: queries filter on normal columns and Iceberg maps those filters to partitions, so users do not need to know the physical layout. Partition layouts can evolve over time without rewriting existing data. Schema evolution is also safe, because columns are tracked by unique ids rather than by name or position, which means adding, dropping, or renaming columns does not corrupt older data.

Iceberg works with many engines including Spark, Flink, Trino, and Snowflake, which makes it popular in multi-engine and multi-cloud environments. Maintenance procedures such as rewrite_data_files and expire_snapshots compact small files and remove old snapshots.
