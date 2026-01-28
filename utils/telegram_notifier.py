"""
Telegram Bot Notification Utility
Sends reorder notifications via Telegram
"""
import os
import logging
import requests
from datetime import datetime
from typing import Optional
from pathlib import Path


# Setup logging
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'telegram_notifications.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('telegram_notifier')


# Telegram Bot Configuration
# Set these environment variables or replace with your actual values
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8246612968:AAEm6tVrdHKzUTDh_ZjN5Rzd28rjGWw02KE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7487990456')


def send_telegram_message(message: str, parse_mode: str = 'HTML') -> dict:
    """
    Send a message via Telegram Bot API
    
    Args:
        message: The message text to send
        parse_mode: Message format ('HTML' or 'Markdown')
    
    Returns:
        dict with success status and response/error
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            'success': False,
            'error': 'Telegram credentials not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.'
        }
    
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            message_id = response_data.get('result', {}).get('message_id')
            logger.info(f"Message sent successfully | Message ID: {message_id}")
            return {
                'success': True,
                'message_id': message_id
            }
        else:
            error_msg = response_data.get('description', 'Unknown error')
            logger.error(f"Failed to send message | Error: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    except requests.exceptions.Timeout:
        logger.error("Failed to send message | Error: Request timed out")
        return {
            'success': False,
            'error': 'Request timed out'
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message | Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def send_reorder_notification(
    store_id: str,
    sku: str,
    order_qty: int,
    current_stock: int,
    forecasted_demand: float,
    risk_level: str,
    safety_stock: Optional[float] = None
) -> dict:
    """
    Send a reorder notification via Telegram
    
    Args:
        store_id: Store identifier
        sku: Product SKU
        order_qty: Quantity being ordered
        current_stock: Current stock level
        forecasted_demand: Forecasted demand
        risk_level: Risk level (HIGH/MED/LOW)
        safety_stock: Safety stock level (optional)
    
    Returns:
        dict with success status and response/error
    """
    # Risk level emoji
    risk_emoji = {
        'HIGH': '🔴',
        'MED': '🟡',
        'LOW': '🟢'
    }.get(risk_level, '⚪')
    
    # Format the message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""📦 <b>REORDER PLACED</b>

🏪 <b>Store:</b> {store_id}
🏷️ <b>SKU:</b> {sku}
📊 <b>Order Quantity:</b> {order_qty:,} units

{risk_emoji} <b>Risk Level:</b> {risk_level}

<b>Inventory Details:</b>
• Current Stock: {current_stock:,} units
• Forecasted Demand: {forecasted_demand:.0f} units"""
    
    if safety_stock is not None:
        message += f"\n• Safety Stock: {safety_stock:.0f} units"
    
    message += f"""

⏰ <b>Timestamp:</b> {timestamp}

<i>— DemandIQ System</i>"""
    
    # Log the reorder notification
    logger.info(f"REORDER | Store: {store_id} | SKU: {sku} | Qty: {order_qty} | Risk: {risk_level} | Current Stock: {current_stock} | Forecast: {forecasted_demand:.0f}")
    
    return send_telegram_message(message)


def test_telegram_connection() -> dict:
    """
    Test the Telegram bot connection
    
    Returns:
        dict with success status and bot info or error
    """
    if not TELEGRAM_BOT_TOKEN:
        return {
            'success': False,
            'error': 'TELEGRAM_BOT_TOKEN not configured'
        }
    
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe'
    
    try:
        response = requests.get(url, timeout=10)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            bot_info = response_data.get('result', {})
            return {
                'success': True,
                'bot_name': bot_info.get('first_name'),
                'bot_username': bot_info.get('username')
            }
        else:
            return {
                'success': False,
                'error': response_data.get('description', 'Unknown error')
            }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    # Test the connection
    print("Testing Telegram connection...")
    result = test_telegram_connection()
    
    if result['success']:
        print(f"✅ Connected to bot: @{result['bot_username']} ({result['bot_name']})")
        
        # Send a test message
        print("\nSending test reorder notification...")
        test_result = send_reorder_notification(
            store_id='STORE-001',
            sku='SKU-MILK-001',
            order_qty=150,
            current_stock=50,
            forecasted_demand=180.5,
            risk_level='HIGH',
            safety_stock=36.1
        )
        
        if test_result['success']:
            print(f"✅ Test message sent successfully! Message ID: {test_result['message_id']}")
        else:
            print(f"❌ Failed to send message: {test_result['error']}")
    else:
        print(f"❌ Connection failed: {result['error']}")
        print("\nTo configure:")
        print("1. Create a Telegram bot via @BotFather")
        print("2. Set TELEGRAM_BOT_TOKEN environment variable")
        print("3. Set TELEGRAM_CHAT_ID environment variable (your chat ID or group ID)")
