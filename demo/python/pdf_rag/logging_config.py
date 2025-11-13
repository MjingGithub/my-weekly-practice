# !/usr/bin/env python3
import logging
import logging.config
import os

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    全局日志配置
    """
    # 创建日志目录
    if log_file:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # 配置字典
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            'dashscope': {
                'level': 'INFO',  # 禁用 chromadb 的 debug 日志
            },
            # 'llama_index': {
            #     'level': 'INFO',     # 限制 llama_index 的日志级别
            # },
            'pdfminer': {
                'level': 'INFO',
            },
            'httpcore': {
                'level': 'INFO',
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console'],
        },
    }

    # 如果指定了日志文件，添加文件处理器
    if log_file:
        config['handlers']['file'] = {
            'level': log_level,
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'detailed',
            'encoding': 'utf-8',
        }
        config['root']['handlers'].append('file')

    logging.config.dictConfig(config)

# 全局日志配置初始化
setup_logging()
