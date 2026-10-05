"""Hourly incremental ingestion + retrieval-quality gate. A failed gate fails the DAG run (and alerts)."""
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException


@dag(
    dag_id="rag_ingest",
    schedule="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["rag", "pgvector"],
)
def rag_ingest():
    @task
    def ingest() -> dict:
        from rag_pipeline.ingest import run
        return run()

    @task
    def quality_gate(stats: dict) -> dict:
        from rag_pipeline.evaluate import run_eval
        m = run_eval()
        if not m["passed"]:
            raise AirflowFailException(f"Retrieval quality gate failed: {m}")
        return {**m, **{f"ingest_{k}": v for k, v in stats.items()}}

    quality_gate(ingest())


rag_ingest()
