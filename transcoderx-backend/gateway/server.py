import pika, json, os, ssl, gridfs, time
from pymongo import MongoClient
from flask import Flask, request, send_file
import util
from bson.objectid import ObjectId
from flask_cors import CORS

server = Flask(__name__)
CORS(server, origins=["http://trancoderx.site/"])


username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")
cluster_uri = f"mongodb+srv://{username}:{password}@free-cluster.lrgadd3.mongodb.net/?retryWrites=true/"

mongo_video = MongoClient(f"{cluster_uri}videos")

mongo_mp3 = MongoClient(f"{cluster_uri}mp3s")

fs_videos = gridfs.GridFS(mongo_video["videos"])
fs_mp3s = gridfs.GridFS(mongo_mp3["mp3s"])


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


def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}, retrying in 5 seconds...")
            time.sleep(5)


connection, channel = establish_connection()


@server.route("/api/login", methods=["POST"])
def login():
    token, err = util.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/api/upload", methods=["POST"])
def upload():
    global connection, channel
    access, err = util.token(request)
    print(f"{access=}")

    if err:
        print(err)
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        # Check if connection is still open, re-establish if not
        if not connection or not connection.is_open:
            print("Connection lost, re-establishing...")
            connection, channel = establish_connection()

        for _, f in request.files.items():
            try:
                err = util.upload(f, fs_videos, channel, access)
            except pika.exceptions.AMQPError as e:
                print(f"RabbitMQ error: {e}")
                # Connection might be in bad state, re-establish
                connection, channel = establish_connection()
                # Optionally, you might want to retry the upload after re-establishing the connection

            if err:
                print(err)
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/api/download", methods=["GET"])
def download():
    access, err = util.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
