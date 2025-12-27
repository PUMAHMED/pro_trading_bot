"""
MEXC Pro Trading Bot - Exchange Configurations
Exchange-specific ayarlar ve konfigürasyonlar
"""

from typing import Dict, List

# MEXC Exchange yapılandırması
MEXC_CONFIG = {
    'name': 'MEXC',
    'api_url': 'https://api.mexc.com',
    'futures_api_url': 'https://contract.mexc.com',
    'websocket_url': 'wss://wbs.mexc.com/ws',
    
    # Rate limits
    'rate_limit_per_minute': 1000,
    'rate_limit_per_second': 20,
    
    # Trading pairs
    'supported_quote_currencies': ['USDT', 'USDC', 'BTC', 'ETH'],
    'default_quote': 'USDT',
    
    # Futures
    'futures_available': True,
    'max_leverage': 200,
    
    # Fees
    'maker_fee': 0.0002,  # 0.02%
    'taker_fee': 0.0006,  # 0.06%
    
    # Limits
    'min_order_amount': 0.00001,
    'max_order_amount': 1000000,
    
    # API Features
    'supports_stop_loss': True,
    'supports_take_profit': True,
    'supports_trailing_stop': False,
    'supports_oco': False,
}

# Binance Exchange yapılandırması
BINANCE_CONFIG = {
    'name': 'Binance',
    'api_url': 'https://api.binance.com',
    'futures_api_url': 'https://fapi.binance.com',
    'websocket_url': 'wss://stream.binance.com:9443/ws',
    
    # Rate limits
    'rate_limit_per_minute': 1200,
    'rate_limit_per_second': 50,
    
    # Trading pairs
    'supported_quote_currencies': ['USDT', 'BUSD', 'BTC', 'ETH', 'BNB'],
    'default_quote': 'USDT',
    
    # Futures
    'futures_available': True,
    'max_leverage': 125,
    
    # Fees
    'maker_fee': 0.0001,  # 0.01%
    'taker_fee': 0.0001,  # 0.01%
    
    # Limits
    'min_order_amount': 0.00001,
    'max_order_amount': 10000000,
    
    # API Features
    'supports_stop_loss': True,
    'supports_take_profit': True,
    'supports_trailing_stop': True,
    'supports_oco': True,
}

# Tüm exchange'ler
EXCHANGES = {
    'MEXC': MEXC_CONFIG,
    'Binance': BINANCE_CONFIG
}

def get_exchange_config(exchange_name: str) -> Dict:
    """Exchange config al"""
    return EXCHANGES.get(exchange_name, {})

def get_all_exchanges() -> List[str]:
    """Tüm exchange isimlerini al"""
    return list(EXCHANGES.keys())

def get_supported_quote_currencies(exchange_name: str) -> List[str]:
    """Exchange'in desteklediği quote currency'leri al"""
    config = get_exchange_config(exchange_name)
    return config.get('supported_quote_currencies', ['USDT'])
