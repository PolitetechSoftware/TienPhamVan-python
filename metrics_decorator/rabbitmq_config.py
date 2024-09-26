import pika


# Establish a connection with RabbitMQ server.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='metrics', durable=True)