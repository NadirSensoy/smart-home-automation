"""
Hata yakalama ve raporlama yardımcıları
"""
import sys
import traceback
import logging
from functools import wraps
from datetime import datetime

# Hata log yapılandırması
logger = logging.getLogger("ErrorHandler")

class SmartHomeError(Exception):
    """
    Akıllı ev otomasyon sistemine özel temel hata sınıfı
    """
    def __init__(self, message, module=None, error_code=None):
        self.message = message
        self.module = module
        self.error_code = error_code
        self.timestamp = datetime.now()
        super().__init__(self.message)
    
    def __str__(self):
        if self.module and self.error_code:
            return f"[{self.module}][{self.error_code}] {self.message}"
        elif self.module:
            return f"[{self.module}] {self.message}"
        else:
            return self.message

class DataProcessingError(SmartHomeError):
    """Veri işleme hatası"""
    def __init__(self, message, error_code=None):
        super().__init__(message, module="DataProcessing", error_code=error_code)

class ModelError(SmartHomeError):
    """Model hatası"""
    def __init__(self, message, error_code=None):
        super().__init__(message, module="Model", error_code=error_code)

class AutomationError(SmartHomeError):
    """Otomasyon hatası"""
    def __init__(self, message, error_code=None):
        super().__init__(message, module="Automation", error_code=error_code)

class SimulationError(SmartHomeError):
    """Simülasyon hatası"""
    def __init__(self, message, error_code=None):
        super().__init__(message, module="Simulation", error_code=error_code)

def error_handler(func):
    """
    Fonksiyon çağrılarını hata yakalama ile sarar.
    
    Args:
        func: Sarmalanacak fonksiyon
        
    Returns:
        Sarmalanmış fonksiyon
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SmartHomeError as e:
            # Zaten özel bir hata, tekrar sarma
            logger.error(f"Smart Home Error: {str(e)}")
            raise
        except Exception as e:
            # Genel hataları SmartHomeError'a çevir
            module_name = func.__module__.split('.')[-1] if func.__module__ else "unknown"
            error_msg = f"Beklenmeyen hata: {str(e)}"
            logger.error(f"{error_msg} in {func.__name__}")
            logger.error(traceback.format_exc())
            
            # Modüle göre özel hata sınıfı seç
            if 'data_processing' in func.__module__:
                raise DataProcessingError(error_msg) from e
            elif 'models' in func.__module__:
                raise ModelError(error_msg) from e
            elif 'automation' in func.__module__:
                raise AutomationError(error_msg) from e
            elif 'simulation' in func.__module__:
                raise SimulationError(error_msg) from e
            else:
                raise SmartHomeError(error_msg) from e
    return wrapper