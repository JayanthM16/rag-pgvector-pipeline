.PHONY: up ingest eval query test local-venv down clean
up:          ## start pgvector + Airflow (UI: http://localhost:8080)
	docker compose up -d --build
	@echo "Airflow admin password:  docker compose logs airflow | grep -i password"
ingest:      ## run ingestion from your laptop (needs: pip install -r requirements.txt)
	PG_DSN=postgresql://rag:rag@localhost:5433/rag python -m rag_pipeline.ingest
eval:
	PG_DSN=postgresql://rag:rag@localhost:5433/rag python -m rag_pipeline.evaluate
query:       ## make query Q="what is hidden partitioning?"
	PG_DSN=postgresql://rag:rag@localhost:5433/rag python -m rag_pipeline.query "$(Q)"
test:
	python -m pytest -q tests
down:
	docker compose down
clean:
	docker compose down -v
