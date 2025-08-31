import json
import pika
import threading
import time
from django.conf import settings
from .models import Product


def publish_product_created(product_data):
    """Publie un événement de création de produit"""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange='service_exchange', exchange_type='topic', durable=True)

        message = {
            'product_id': product_data['id'],
            'name': product_data['name'],
            'price': float(product_data['price']),
            'stock': product_data['stock'],
            'timestamp': time.time()
        }

        channel.basic_publish(
            exchange='service_exchange',
            routing_key='product.created',
            body=json.dumps(message)
        )
        print(f"📤 Published product.created: {message}")
        connection.close()
    except Exception as e:
        print(f"❌ Failed to publish product.created: {e}")


def publish_product_updated(product_data):
    """Publie un événement de mise à jour de produit"""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange='service_exchange', exchange_type='topic', durable=True)

        message = {
            'product_id': product_data['id'],
            'name': product_data['name'],
            'price': float(product_data['price']),
            'stock': product_data['stock'],
            'timestamp': time.time()
        }

        channel.basic_publish(
            exchange='service_exchange',
            routing_key='product.updated',
            body=json.dumps(message)
        )
        print(f"📤 Published product.updated: {message}")
        connection.close()
    except Exception as e:
        print(f"❌ Failed to publish product.updated: {e}")


def publish_stock_updated(product_id, new_stock):
    """Publie un événement de mise à jour de stock"""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange='service_exchange', exchange_type='topic', durable=True)

        message = {
            'product_id': product_id,
            'new_stock': new_stock,
            'timestamp': time.time()
        }

        channel.basic_publish(
            exchange='service_exchange',
            routing_key='stock.updated',
            body=json.dumps(message)
        )
        print(f"📤 Published stock.updated: {message}")
        connection.close()
    except Exception as e:
        print(f"❌ Failed to publish stock.updated: {e}")


def callback_order_created(ch, method, properties, body):
    """Callback pour les événements de création de commande"""
    try:
        message = json.loads(body)
        print(f"📥 Order created event received: {message}")
        
        # Ici on pourrait ajouter de la logique métier
        # Par exemple, vérifier les stocks, envoyer des alertes, etc.
        
    except Exception as e:
        print(f"❌ Error processing order.created event: {e}")


def callback_stock_updated(ch, method, properties, body):
    """Callback pour les événements de mise à jour de stock"""
    try:
        message = json.loads(body)
        print(f"📥 Stock updated event received: {message}")
        
        # Synchronisation du stock si nécessaire
        product_id = message.get('product_id')
        new_stock = message.get('new_stock')
        
        if product_id and new_stock is not None:
            try:
                product = Product.objects.get(id=product_id)
                if product.stock != new_stock:
                    product.stock = new_stock
                    product.save()
                    print(f"✅ Stock synchronized for product {product_id}: {new_stock}")
            except Product.DoesNotExist:
                print(f"⚠️ Product {product_id} not found for stock sync")
        
    except Exception as e:
        print(f"❌ Error processing stock.updated event: {e}")


def consume_events():
    """Consomme les événements RabbitMQ"""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()
            
            # Déclaration de l'exchange
            channel.exchange_declare(exchange='service_exchange', exchange_type='topic', durable=True)
            
            # Déclaration de la queue pour les événements de commande
            channel.queue_declare(queue='product_service_order_queue', durable=True)
            channel.queue_bind(
                exchange='service_exchange', 
                queue='product_service_order_queue', 
                routing_key='order.created'
            )
            
            # Déclaration de la queue pour les événements de stock
            channel.queue_declare(queue='product_service_stock_queue', durable=True)
            channel.queue_bind(
                exchange='service_exchange', 
                queue='product_service_stock_queue', 
                routing_key='stock.updated'
            )
            
            # Configuration des callbacks
            channel.basic_consume(
                queue='product_service_order_queue', 
                on_message_callback=callback_order_created, 
                auto_ack=True
            )
            
            channel.basic_consume(
                queue='product_service_stock_queue', 
                on_message_callback=callback_stock_updated, 
                auto_ack=True
            )
            
            print("👂 Product service écoute les événements...")
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ Erreur RabbitMQ (consume_events) : {e}")
            time.sleep(5)


def start_consumer_thread():
    """Démarre le thread de consommation des événements"""
    thread = threading.Thread(target=consume_events, daemon=True)
    thread.start()
    print("🚀 Consumer thread démarré pour le service Product")
