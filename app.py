import os

from flask import Flask, render_template, request, jsonify
from flask_mqtt import Mqtt

app = Flask(__name__)  # Name the Flask Application instance

# Store secrets in the Environment or a .env file
app.config['MQTT_BROKER_URL'] = os.environ.get('MQTT_BROKER_URL', "127.0.0.1")
app.config['MQTT_BROKER_PORT'] = os.environ.get('MQTT_BROKER_PORT', 1883)
app.config['MQTT_USERNAME'] = os.environ.get('MQTT_USERNAME')
app.config['MQTT_PASSWORD'] = os.environ.get('MQTT_PASSWORD')
app.config['MQTT_KEEPALIVE'] = os.environ.get('MQTT_KEEPALIVE', 60)  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = os.environ.get('MQTT_TLS_ENABLED', False)  # If your server supports TLS, set it True

sub_feed_name = os.environ.get('MQTT_SUB_FEEDNAME', "test_feed")
pub_feed_name = os.environ.get('MQTT_PUB_FEEDNAME', "test_feed")

pub_topic = f"{app.config['MQTT_USERNAME']}/feeds/{pub_feed_name}"  # Feed name in adafruit
sub_topic = f"{app.config['MQTT_USERNAME']}/feeds/{sub_feed_name}"  # Feed name in adafruit

mqtt_client = Mqtt(app)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, result_code):
    # Brute force consumption of currently "ignored" parameters
    # ToDo: Investigate contents of these connection parameters
    _ = client
    _ = userdata
    _ = flags

    if result_code == 0:
        print('Connected successfully')
        mqtt_client.subscribe(sub_topic)  # subscribe topic
    else:
        print('Bad connection. Code:', result_code)
    # ToDo: Use JS to update part of page with MQTT status


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    # Brute force consumption of currently "ignored" parameters
    # ToDo: Investigate contents of these message parameters
    _ = client
    _ = userdata

    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    # ToDo: Use JS to update part of page with MESSAGES


@app.route('/publish', methods=['POST'])
def publish_message():
    """
        Send message onto to the pub_topic

        the request must be a POST, contain a topic and a msg
        the msg should be in the form of JSON data

    :return:
    """
    request_data = request.get_json()
    publish_result = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/passing')
@app.route('/passing/<name>')
def passing(name="frank"):
    name = name.capitalize()
    return render_template('passing.html', given_name=name)


@app.route('/test-fail')
def test_fail():
    return render_template('index-fail.html')


@app.route('/pycharm')
def pycharm():
    return render_template('pycharm.html')


@app.route('/')
def index():  # put application's code here
    # return 'Hello World!'
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
