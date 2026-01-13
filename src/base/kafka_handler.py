import os

import kafka

from src.base.logging_config import get_logger
from src.base.setup_config import setup_config

LOGGER = get_logger()
CONFIG = setup_config()

HOSTNAME = os.getenv("HOSTNAME", "default_tid")
CONSUMER_GROUP_ID = os.getenv("GROUP_ID", "default_gid")
NUMBER_OF_INSTANCES = int(os.getenv("NUMBER_OF_INSTANCES", 1))
KAFKA_BROKERS = CONFIG["environment"]["kafka_brokers"]


class SimpleKafkaProduceHandler:
    """Simple Kafka Producer wrapper without Write-Exactly-Once semantics

    Provides basic message production capabilities with at-least-once delivery
    guarantees. This implementation prioritizes simplicity and performance over
    strict consistency guarantees.
    """

    def __init__(self):
        """Initializes the Kafka producer.

        Sets up a Kafka producer with standard configuration for simple message
        production without transactional guarantees. Broker addresses are
        automatically configured from the global KAFKA_BROKERS setting.
        """
        self.brokers = ",".join(
            [f"{broker['hostname']}:{broker['port']}" for broker in KAFKA_BROKERS]
        )

        conf = {
            "bootstrap_servers": self.brokers,
            "enable_idempotence": False,
            "acks": 1,
        }
        self.producer = kafka.KafkaProducer(**conf)

    def produce(self, topic: str, data: str, key: None | str = None) -> None:
        """Produce a message to the specified Kafka topic.

        Encodes and sends the provided data to the specified topic. The producer
        is flushed before sending to ensure message delivery. Empty data is
        silently ignored.

        Args:
            topic (str): Target Kafka topic name.
            data (str): Message data to send (ignored if empty).
            key (str, optional): Optional message key for partitioning.
                                 Default: None.

        Raises:
            KafkaException: If message production fails.
            BufferError: If the producer's message buffer is full.
        """
        if not data:
            return

        future = self.producer.send(
            topic=topic,
            key=key,
            value=data.encode(),
        )
        self.producer.flush()

        try:
            future.get(timeout=10)
        except Exception as e:
            LOGGER.error(f"Failed to send message to {topic}: {e}")

    def __del__(self) -> None:
        """Cleanup method called when the object is destroyed

        Ensures that all pending messages are flushed before the producer
        is destroyed, preventing message loss.
        """
        if hasattr(self, "producer"):
            self.producer.flush()
