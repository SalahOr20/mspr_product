import time
import json
import pika
from prometheus_client import Counter, Histogram, Gauge
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

# Métriques Prometheus
http_requests_total = Counter(
    'http_requests_total',
    'Total des requêtes HTTP',
    ['method', 'endpoint', 'status_code', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Durée des requêtes HTTP',
    ['method', 'endpoint', 'service']
)

rabbitmq_messages_total = Counter(
    'rabbitmq_messages_total',
    'Total des messages RabbitMQ',
    ['queue', 'exchange', 'routing_key', 'action']
)

rabbitmq_queue_size = Gauge(
    'rabbitmq_queue_size',
    'Taille des files d\'attente RabbitMQ',
    ['queue']
)

api_calls_total = Counter(
    'api_calls_total',
    'Total des appels API externes',
    ['target_service', 'endpoint', 'status_code']
)

api_call_duration_seconds = Histogram(
    'api_call_duration_seconds',
    'Durée des appels API externes',
    ['target_service', 'endpoint']
)


class MetricsMiddleware(MiddlewareMixin):
    """Middleware pour collecter les métriques personnalisées"""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Métriques HTTP
            method = request.method
            endpoint = request.path
            status_code = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                service='product'
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
                service='product'
            ).observe(duration)
        
        return response


def track_rabbitmq_message(queue, exchange, routing_key, action):
    """Fonction pour tracker les messages RabbitMQ"""
    rabbitmq_messages_total.labels(
        queue=queue,
        exchange=exchange,
        routing_key=routing_key,
        action=action
    ).inc()


def track_api_call(target_service, endpoint, status_code, duration):
    """Fonction pour tracker les appels API externes"""
    api_calls_total.labels(
        target_service=target_service,
        endpoint=endpoint,
        status_code=status_code
    ).inc()
    
    api_call_duration_seconds.labels(
        target_service=target_service,
        endpoint=endpoint
    ).observe(duration)


def get_rabbitmq_queue_info():
    """Récupère les informations sur les files d'attente RabbitMQ"""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        
        # Récupérer les informations sur les files d'attente
        method = channel.queue_declare(queue='product_service_queue', passive=True)
        queue_size = method.method.message_count
        rabbitmq_queue_size.labels(queue='product_service_queue').set(queue_size)
        
        connection.close()
        return queue_size
    except Exception as e:
        print(f"Erreur lors de la récupération des infos RabbitMQ: {e}")
        return 0
