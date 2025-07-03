#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Loglama Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
import sys

class MYPLogger:
    """MYP Sağlık AI için özelleştirilmiş loglama sınıfı"""
    
    def __init__(self, name="MYP_HEALTH_AI", log_dir="outputs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Logger'ı oluştur
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Handler'ları temizle (çoklu çalıştırmada duplikasyon önlemi)
        self.logger.handlers.clear()
        
        # Formatları ayarla
        self.setup_formatters()
        
        # Handler'ları ekle
        self.setup_handlers()
        
    def setup_formatters(self):
        """Log formatlarını ayarla"""
        # Detaylı format (dosya için)
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Basit format (konsol için)
        self.simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # JSON format (yapılandırılmış loglar için)
        self.json_formatter = JsonFormatter()
    
    def setup_handlers(self):
        """Log handler'larını ayarla"""
        # Konsol handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)
        
        # Ana log dosyası handler
        main_log_file = self.log_dir / f"{self.name.lower()}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Hata log dosyası handler
        error_log_file = self.log_dir / f"{self.name.lower()}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # JSON log dosyası handler (analiz için)
        json_log_file = self.log_dir / f"{self.name.lower()}_structured.jsonl"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=3,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(self.json_formatter)
        self.logger.addHandler(json_handler)
    
    def get_logger(self):
        """Logger instance'ını al"""
        return self.logger
    
    def log_user_action(self, action, details=None, user_id=None):
        """Kullanıcı eylemlerini logla"""
        log_data = {
            'event_type': 'user_action',
            'action': action,
            'user_id': user_id,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"USER_ACTION: {action}", extra={'structured_data': log_data})
    
    def log_analysis_event(self, event_type, data=None, duration=None, success=True):
        """Analiz olaylarını logla"""
        log_data = {
            'event_type': 'analysis_event',
            'analysis_type': event_type,
            'success': success,
            'duration_seconds': duration,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if success else logging.ERROR
        message = f"ANALYSIS: {event_type} - {'SUCCESS' if success else 'FAILED'}"
        
        self.logger.log(level, message, extra={'structured_data': log_data})
    
    def log_system_event(self, event, details=None, severity='info'):
        """Sistem olaylarını logla"""
        log_data = {
            'event_type': 'system_event',
            'event': event,
            'severity': severity,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        level = level_map.get(severity.lower(), logging.INFO)
        self.logger.log(level, f"SYSTEM: {event}", extra={'structured_data': log_data})
    
    def log_performance_metric(self, metric_name, value, unit=None, context=None):
        """Performans metriklerini logla"""
        log_data = {
            'event_type': 'performance_metric',
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"METRIC: {metric_name} = {value} {unit or ''}", 
                        extra={'structured_data': log_data})
    
    def log_error_with_context(self, error, context=None, user_action=None):
        """Hataları bağlamla birlikte logla"""
        log_data = {
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user_action': user_action,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.error(f"ERROR: {type(error).__name__}: {str(error)}", 
                         extra={'structured_data': log_data}, exc_info=True)
    
    def create_session_logger(self, session_id):
        """Oturum bazlı logger oluştur"""
        session_logger = SessionLogger(self.logger, session_id)
        return session_logger
    
    def get_log_statistics(self):
        """Log istatistiklerini al"""
        try:
            stats = {
                'log_files': [],
                'total_size_mb': 0,
                'last_modified': None
            }
            
            for log_file in self.log_dir.glob("*.log*"):
                file_stats = log_file.stat()
                file_info = {
                    'name': log_file.name,
                    'size_mb': file_stats.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                }
                stats['log_files'].append(file_info)
                stats['total_size_mb'] += file_info['size_mb']
                
                if not stats['last_modified'] or file_stats.st_mtime > datetime.fromisoformat(stats['last_modified']).timestamp():
                    stats['last_modified'] = file_info['modified']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Log istatistikleri alınırken hata: {str(e)}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep=30):
        """Eski logları temizle"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cleaned_files = []
            for log_file in self.log_dir.glob("*.log*"):
                file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_modified < cutoff_date:
                    log_file.unlink()
                    cleaned_files.append(log_file.name)
            
            if cleaned_files:
                self.logger.info(f"Eski log dosyaları temizlendi: {len(cleaned_files)} dosya")
                return cleaned_files
            else:
                self.logger.info("Temizlenecek eski log dosyası bulunamadı")
                return []
                
        except Exception as e:
            self.logger.error(f"Log temizleme hatası: {str(e)}")
            return []

class JsonFormatter(logging.Formatter):
    """JSON formatında log çıktısı için formatter"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Yapılandırılmış veri varsa ekle
        if hasattr(record, 'structured_data'):
            log_entry.update(record.structured_data)
        
        # Exception bilgisi varsa ekle
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class SessionLogger:
    """Oturum bazlı loglama için wrapper sınıf"""
    
    def __init__(self, base_logger, session_id):
        self.base_logger = base_logger
        self.session_id = session_id
        self.session_start = datetime.now()
    
    def _add_session_context(self, extra=None):
        """Oturum bağlamını ekle"""
        session_context = {
            'session_id': self.session_id,
            'session_duration': (datetime.now() - self.session_start).total_seconds()
        }
        
        if extra:
            if 'structured_data' in extra:
                extra['structured_data'].update(session_context)
            else:
                extra['structured_data'] = session_context
        else:
            extra = {'structured_data': session_context}
        
        return extra
    
    def info(self, message, extra=None):
        """Info seviyesinde log"""
        extra = self._add_session_context(extra)
        self.base_logger.info(f"[{self.session_id}] {message}", extra=extra)
    
    def error(self, message, extra=None):
        """Error seviyesinde log"""
        extra = self._add_session_context(extra)
        self.base_logger.error(f"[{self.session_id}] {message}", extra=extra)
    
    def warning(self, message, extra=None):
        """Warning seviyesinde log"""
        extra = self._add_session_context(extra)
        self.base_logger.warning(f"[{self.session_id}] {message}", extra=extra)
    
    def debug(self, message, extra=None):
        """Debug seviyesinde log"""
        extra = self._add_session_context(extra)
        self.base_logger.debug(f"[{self.session_id}] {message}", extra=extra)

# Global logger instance
_global_logger = None

def get_logger(name=None):
    """Global logger instance'ını al"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = MYPLogger(name or "MYP_HEALTH_AI")
    
    return _global_logger.get_logger()

def setup_logging(name="MYP_HEALTH_AI", log_dir="outputs"):
    """Loglama sistemini ayarla"""
    global _global_logger
    _global_logger = MYPLogger(name, log_dir)
    return _global_logger.get_logger()