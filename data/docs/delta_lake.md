# Delta Lake

Delta Lake is an open-source storage layer that adds ACID transactions to data lakes built on Parquet files. It keeps a transaction log, called the Delta log, that records every change made to a table. Because of this log, readers always see a consistent snapshot even while writers are updating the table.

Delta Lake supports MERGE statements for upserts, schema enforcement and evolution, and time travel, which lets you query an earlier version of a table by version number or timestamp. The OPTIMIZE command compacts small files, and Z-ORDER clusters data to speed up selective queries. VACUUM removes data files that are no longer referenced by the table and are older than the retention period.

On Databricks, Delta Lake is the default table format and works with Unity Catalog for governance, including access control and lineage.
