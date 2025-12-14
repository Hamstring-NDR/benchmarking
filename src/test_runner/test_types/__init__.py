from src.base.utils import setup_config

config = setup_config()

PRODUCE_TO_TOPIC: str = config["environment"]["kafka_topics"]["pipeline"]["logserver_in"]
LATENCIES_COMPARISON_FILENAME: str = "latency_comparison.png"
MODULE_TO_CSV_FILENAME: dict[str, str] = {
    "Batch Handler": "batch_handler.csv",
    "Collector": "collector.csv",
    "Detector": "detector.csv",
    "Inspector": "inspector.csv",
    "Log Server": "logserver.csv",
    "Prefilter": "prefilter.csv",
}
CLICKHOUSE_CONTAINER_NAME: str = config["environment"]["monitoring"][
    "clickhouse_server"
]["hostname"]
