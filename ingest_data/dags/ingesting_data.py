import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add plugins directory to Python path
AIRFLOW_HOME = Path("/opt/airflow")
sys.path.append(str(AIRFLOW_HOME))
from plugins.jobs.download import download_arxiv_papers
from plugins.jobs.embed_and_store import embed_and_store
from plugins.jobs.load_and_chunk import load_and_chunk

with DAG(
    dag_id="ingest_pipeline",
    schedule=None,
) as dag:

    download_arxiv_papers_task = PythonOperator(
        task_id="download_arxiv_papers",
        python_callable=download_arxiv_papers,
    )

    load_and_chunk_task = PythonOperator(
        task_id="load_and_chunk",
        python_callable=load_and_chunk,
    )

    embed_and_store_task = PythonOperator(
        task_id="embed_and_store",
        python_callable=embed_and_store,
    )

    _ = download_arxiv_papers_task >> load_and_chunk_task >> embed_and_store_task
