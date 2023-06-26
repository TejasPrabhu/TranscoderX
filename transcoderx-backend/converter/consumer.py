import pika, sys, os, ssl
from pymongo import MongoClient
import gridfs
from utilities import to_mp3

username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")
cluster_uri = f"mongodb+srv://{username}:{password}@free-cluster.lrgadd3.mongodb.net/?retryWrites=true/"


def main():
    client = MongoClient(cluster_uri)
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
    RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")

    # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")

    rabbitmq_user = os.environ.get("RABBITMQ_USERNAME")
    rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")
    rabbitmq_broker_id = "b-cd2895f3-0f87-436c-a7fc-1907f94170d9"
    region = "us-east-1"
    # rabbitmq_port = os.environ.get("RABBITMQ_PORT")
    rabbitmq_url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@albatross.rmq.cloudamqp.com/{rabbitmq_user}"
    print(rabbitmq_url)

    # rabbitmq_url = "amqps://xgcrhxhs:PcL_RloAohAHvSoamIzKW3kbhVtAuQqr@albatross.rmq.cloudamqp.com/xgcrhxhs"


    rabbitmq_url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:5671"
    parameters = pika.URLParameters(rabbitmq_url)
    parameters.ssl_options = pika.SSLOptions(context=ssl_context)
    parameters.heartbeat = 600

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
