from flask import Flask
from flask_mail import Mail, Message
import pika, sys, os, ssl, json

app = Flask(__name__)
app.config["MAIL_SERVER"] = "sandbox.smtp.mailtrap.io"
app.config["MAIL_PORT"] = 2525
app.config["MAIL_USERNAME"] = "94bf8cea2c7689"
app.config["MAIL_PASSWORD"] = "4e87924a3bfba4"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)


def notification(message):
    message = json.loads(message)
    mp3_fid = message["mp3_fid"]
    sender_address = os.environ.get("GMAIL_ADDRESS")
    receiver_address = message["username"]

    msg = Message("MP3 Download", sender=sender_address, recipients=[receiver_address])
    msg.body = f"mp3 file_id: {mp3_fid} is now ready!"

    with app.app_context():
        mail.send(msg)

    print("Mail Sent")


def main():
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
    # rabbitmq_url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@albatross.rmq.cloudamqp.com/{rabbitmq_user}"

    # rabbitmq_url = "amqps://xgcrhxhs:PcL_RloAohAHvSoamIzKW3kbhVtAuQqr@albatross.rmq.cloudamqp.com/xgcrhxhs"


    rabbitmq_url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:5671"
    parameters = pika.URLParameters(rabbitmq_url)
    parameters.ssl_options = pika.SSLOptions(context=ssl_context)
    parameters.heartbeat = 600

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback
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
