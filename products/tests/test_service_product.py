from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from decimal import Decimal
import json
from products.service_product import (
    publish_product_created,
    publish_product_updated,
    publish_stock_updated,
    callback_order_created,
    callback_stock_updated
)
from products.models import Product

class PublishProductCreatedTest(TestCase):
    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_product_created_success(self, mock_connection):
        """Test de publication d'un produit créé"""
        # Mock de la connexion RabbitMQ
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        product_data = {
            'id': 1,
            'name': 'Test Product',
            'price': Decimal('19.99'),
            'stock': 10
        }
        
        publish_product_created(product_data)
        
        # Vérifier que l'exchange a été déclaré
        mock_channel.exchange_declare.assert_called_once_with(
            exchange='service_exchange',
            exchange_type='topic',
            durable=True
        )
        
        # Vérifier que le message a été publié
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]['exchange'], 'service_exchange')
        self.assertEqual(call_args[1]['routing_key'], 'product.created')
        
        # Vérifier le contenu du message
        message_body = json.loads(call_args[1]['body'])
        self.assertEqual(message_body['product_id'], 1)
        self.assertEqual(message_body['name'], 'Test Product')
        self.assertEqual(message_body['price'], 19.99)
        self.assertEqual(message_body['stock'], 10)
        self.assertIn('timestamp', message_body)
        
        # Vérifier que la connexion a été fermée
        mock_connection_instance.close.assert_called_once()

    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_product_created_connection_error(self, mock_connection):
        """Test de publication avec une erreur de connexion"""
        mock_connection.side_effect = Exception("Connection error")
        
        product_data = {
            'id': 1,
            'name': 'Test Product',
            'price': Decimal('19.99'),
            'stock': 10
        }
        
        # Ne devrait pas lever d'exception
        publish_product_created(product_data)

class PublishProductUpdatedTest(TestCase):
    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_product_updated_success(self, mock_connection):
        """Test de publication d'un produit mis à jour"""
        # Mock de la connexion RabbitMQ
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        product_data = {
            'id': 1,
            'name': 'Updated Product',
            'price': Decimal('25.50'),
            'stock': 15
        }
        
        publish_product_updated(product_data)
        
        # Vérifier que l'exchange a été déclaré
        mock_channel.exchange_declare.assert_called_once_with(
            exchange='service_exchange',
            exchange_type='topic',
            durable=True
        )
        
        # Vérifier que le message a été publié
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]['exchange'], 'service_exchange')
        self.assertEqual(call_args[1]['routing_key'], 'product.updated')
        
        # Vérifier le contenu du message
        message_body = json.loads(call_args[1]['body'])
        self.assertEqual(message_body['product_id'], 1)
        self.assertEqual(message_body['name'], 'Updated Product')
        self.assertEqual(message_body['price'], 25.50)
        self.assertEqual(message_body['stock'], 15)
        self.assertIn('timestamp', message_body)
        
        # Vérifier que la connexion a été fermée
        mock_connection_instance.close.assert_called_once()

    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_product_updated_connection_error(self, mock_connection):
        """Test de publication avec une erreur de connexion"""
        mock_connection.side_effect = Exception("Connection error")
        
        product_data = {
            'id': 1,
            'name': 'Updated Product',
            'price': Decimal('25.50'),
            'stock': 15
        }
        
        # Ne devrait pas lever d'exception
        publish_product_updated(product_data)

class PublishStockUpdatedTest(TestCase):
    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_stock_updated_success(self, mock_connection):
        """Test de publication d'une mise à jour de stock"""
        # Mock de la connexion RabbitMQ
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        product_id = 1
        new_stock = 5
        
        publish_stock_updated(product_id, new_stock)
        
        # Vérifier que l'exchange a été déclaré
        mock_channel.exchange_declare.assert_called_once_with(
            exchange='service_exchange',
            exchange_type='topic',
            durable=True
        )
        
        # Vérifier que le message a été publié
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]['exchange'], 'service_exchange')
        self.assertEqual(call_args[1]['routing_key'], 'stock.updated')
        
        # Vérifier le contenu du message
        message_body = json.loads(call_args[1]['body'])
        self.assertEqual(message_body['product_id'], 1)
        self.assertEqual(message_body['new_stock'], 5)
        self.assertIn('timestamp', message_body)
        
        # Vérifier que la connexion a été fermée
        mock_connection_instance.close.assert_called_once()

    @patch('products.service_product.pika.BlockingConnection')
    def test_publish_stock_updated_connection_error(self, mock_connection):
        """Test de publication avec une erreur de connexion"""
        mock_connection.side_effect = Exception("Connection error")
        
        product_id = 1
        new_stock = 5
        
        # Ne devrait pas lever d'exception
        publish_stock_updated(product_id, new_stock)

class CallbackOrderCreatedTest(TestCase):
    def test_callback_order_created_success(self):
        """Test du callback pour un événement de création de commande"""
        # Créer un message de test
        message = {
            'order_id': 1,
            'customer_id': 'test-customer-id',
            'products': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 2, 'quantity': 1}
            ]
        }
        
        # Mock des paramètres du callback
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Le callback ne devrait pas lever d'exception
        callback_order_created(ch, method, properties, body)

    def test_callback_order_created_invalid_json(self):
        """Test du callback avec un JSON invalide"""
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = b'invalid json'
        
        # Le callback devrait gérer l'erreur gracieusement
        callback_order_created(ch, method, properties, body)

    def test_callback_order_created_empty_message(self):
        """Test du callback avec un message vide"""
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = b'{}'
        
        # Le callback ne devrait pas lever d'exception
        callback_order_created(ch, method, properties, body)

class CallbackStockUpdatedTest(TestCase):
    def setUp(self):
        # Créer un produit de test
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('19.99'),
            stock=10
        )

    def test_callback_stock_updated_success(self):
        """Test du callback pour une mise à jour de stock"""
        # Créer un message de test
        message = {
            'product_id': self.product.id,
            'new_stock': 5
        }
        
        # Mock des paramètres du callback
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Exécuter le callback
        callback_stock_updated(ch, method, properties, body)
        
        # Vérifier que le stock a été mis à jour
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.stock, 5)

    def test_callback_stock_updated_same_stock(self):
        """Test du callback avec le même stock (pas de changement)"""
        # Créer un message avec le même stock
        message = {
            'product_id': self.product.id,
            'new_stock': 10  # Même stock qu'initialement
        }
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Exécuter le callback
        callback_stock_updated(ch, method, properties, body)
        
        # Le stock devrait rester le même
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.stock, 10)

    def test_callback_stock_updated_product_not_found(self):
        """Test du callback avec un produit inexistant"""
        # Créer un message avec un ID de produit inexistant
        message = {
            'product_id': 999,  # Produit inexistant
            'new_stock': 5
        }
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Le callback ne devrait pas lever d'exception
        callback_stock_updated(ch, method, properties, body)

    def test_callback_stock_updated_missing_product_id(self):
        """Test du callback sans product_id"""
        # Créer un message sans product_id
        message = {
            'new_stock': 5
        }
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Le callback ne devrait pas lever d'exception
        callback_stock_updated(ch, method, properties, body)

    def test_callback_stock_updated_missing_new_stock(self):
        """Test du callback sans new_stock"""
        # Créer un message sans new_stock
        message = {
            'product_id': self.product.id
        }
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Le callback ne devrait pas lever d'exception
        callback_stock_updated(ch, method, properties, body)

    def test_callback_stock_updated_invalid_json(self):
        """Test du callback avec un JSON invalide"""
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = b'invalid json'
        
        # Le callback devrait gérer l'erreur gracieusement
        callback_stock_updated(ch, method, properties, body)

    def test_callback_stock_updated_negative_stock(self):
        """Test du callback avec un stock négatif"""
        # Créer un message avec un stock négatif
        message = {
            'product_id': self.product.id,
            'new_stock': -5
        }
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps(message).encode('utf-8')
        
        # Exécuter le callback
        callback_stock_updated(ch, method, properties, body)
        
        # Vérifier que le stock a été mis à jour (même négatif)
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.stock, -5)
