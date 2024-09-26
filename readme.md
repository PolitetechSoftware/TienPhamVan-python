# 1. Install packages
pip install -r requirements.txt

# 2. Run docker image RabbitMQ
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

# 3. Run worker
python metrics_decorator/worker.py

# 4. Run example
python example.py