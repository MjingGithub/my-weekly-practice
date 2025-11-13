# !/usr/bin/env python3
import importlib.metadata
import sys

def check_multiple_packages(packages):
    """批量检查多个包"""
    results = {}
    for package in packages:
        try:
            version = importlib.metadata.version(package)
            results[package] = {'installed': True, 'version': version}
        except importlib.metadata.PackageNotFoundError:
            results[package] = {'installed': False, 'version': None}
    return results

# 使用示例
packages_to_check = ['pandas', 'llama-index-vector-stores-chroma', 'llama-index-llms-openai-like', 'llama-index-embeddings-dashscope']
results = check_multiple_packages(packages_to_check)

for package, info in results.items():
    if info['installed']:
        print(f"✓ {package}: {info['version']}")
    else:
        print(f"✗ {package}: Not installed")