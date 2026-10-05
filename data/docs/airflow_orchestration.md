# Apache Airflow Orchestration

Apache Airflow is a workflow orchestrator where pipelines are defined as DAGs, directed acyclic graphs of tasks, written in Python. The scheduler triggers DAG runs according to a schedule, and workers execute the tasks. Each task can be retried automatically, and dependencies between tasks control the execution order.

Airflow supports sensors that wait for external conditions, XComs for passing small pieces of data between tasks, and the TaskFlow API that turns Python functions into tasks with a decorator. Setting catchup to false prevents Airflow from backfilling every missed interval when a DAG is first enabled. Setting max_active_runs to one prevents overlapping runs of the same DAG.

Good practice is to make tasks idempotent so that a retry or backfill produces the same result, and to fail a DAG run loudly when a data quality check does not pass.
