# -*- coding: utf-8 -*-
"""
Встроенные функции HackLang
"""

import os
import sys
import json
import time
import math
import random
import string
import hashlib
import base64
import threading
import socket
import urllib.request
import urllib.error

try:
    from Crypto.Cipher import AES
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# ------------------------------------------------------------
# Базовые
def builtin_print(*args):
    print(*args)

def builtin_len(obj):
    return len(obj)

def builtin_type(obj):
    return type(obj).__name__

def builtin_input(prompt=""):
    return input(prompt)

# ------------------------------------------------------------
# Работа с файлами
def builtin_file_read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения файла: {e}")

def builtin_file_write(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        return True
    except Exception as e:
        raise RuntimeError(f"Ошибка записи файла: {e}")

def builtin_file_append(path, data):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(data)
        return True
    except Exception as e:
        raise RuntimeError(f"Ошибка добавления в файл: {e}")

def builtin_file_exists(path):
    return os.path.exists(path)

def builtin_file_delete(path):
    try:
        os.remove(path)
        return True
    except Exception as e:
        raise RuntimeError(f"Ошибка удаления файла: {e}")

def builtin_dir_list(path="."):
    try:
        return os.listdir(path)
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения директории: {e}")

def builtin_system(cmd):
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

# ------------------------------------------------------------
# JSON
def builtin_json_encode(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка JSON encode: {e}")

def builtin_json_decode(s):
    try:
        return json.loads(s)
    except Exception as e:
        raise RuntimeError(f"Ошибка JSON decode: {e}")

# ------------------------------------------------------------
# Время
def builtin_time_now():
    return time.time()

def builtin_time_format(timestamp=None, fmt="%Y-%m-%d %H:%M:%S"):
    if timestamp is None:
        timestamp = time.time()
    try:
        return time.strftime(fmt, time.localtime(timestamp))
    except Exception as e:
        raise RuntimeError(f"Ошибка форматирования времени: {e}")

def builtin_sleep(seconds):
    time.sleep(seconds)

# ------------------------------------------------------------
# Математика
def builtin_sin(x): return math.sin(x)
def builtin_cos(x): return math.cos(x)
def builtin_tan(x): return math.tan(x)
def builtin_sqrt(x): return math.sqrt(x)
def builtin_log(x): return math.log(x)
def builtin_log10(x): return math.log10(x)
def builtin_pow(x, y): return math.pow(x, y)
def builtin_rand(): return random.random()
def builtin_randint(a, b): return random.randint(a, b)

# ------------------------------------------------------------
# Строки
def builtin_str_upper(s): return s.upper()
def builtin_str_lower(s): return s.lower()
def builtin_str_replace(s, old, new): return s.replace(old, new)
def builtin_str_split(s, delim=None): return s.split(delim) if delim else s.split()
def builtin_str_join(lst, delim): return delim.join(lst)
def builtin_str_contains(s, sub): return sub in s
def builtin_str_strip(s): return s.strip()

# ------------------------------------------------------------
# Криптография (упрощённо, если библиотеки нет)
def builtin_hash_sha256(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def builtin_base64_encode(data):
    return base64.b64encode(data.encode('utf-8')).decode('ascii')

def builtin_base64_decode(data):
    return base64.b64decode(data).decode('utf-8', errors='ignore')

def builtin_aes_encrypt(data, key):
    if not CRYPTO_AVAILABLE:
        return f"[AES encrypt mock: {data} with key {key}]"
    try:
        key = key.encode('utf-8').ljust(32, b'\0')[:32]
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('ascii')
    except Exception as e:
        raise RuntimeError(f"AES encrypt error: {e}")

def builtin_aes_decrypt(data, key):
    if not CRYPTO_AVAILABLE:
        return f"[AES decrypt mock: {data} with key {key}]"
    try:
        raw = base64.b64decode(data)
        nonce = raw[:16]
        tag = raw[16:32]
        ciphertext = raw[32:]
        key = key.encode('utf-8').ljust(32, b'\0')[:32]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plain = cipher.decrypt_and_verify(ciphertext, tag)
        return plain.decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"AES decrypt error: {e}")

def builtin_rsa_generate_keys():
    if not CRYPTO_AVAILABLE:
        return ("[RSA pub mock]", "[RSA priv mock]")
    try:
        key = RSA.generate(2048)
        private_key = key.export_key().decode('ascii')
        public_key = key.publickey().export_key().decode('ascii')
        return (public_key, private_key)
    except Exception as e:
        raise RuntimeError(f"RSA generate error: {e}")

def builtin_rsa_encrypt(data, public_key_str):
    if not CRYPTO_AVAILABLE:
        return f"[RSA encrypt mock: {data}]"
    try:
        public_key = RSA.import_key(public_key_str)
        cipher = PKCS1_OAEP.new(public_key)
        encrypted = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('ascii')
    except Exception as e:
        raise RuntimeError(f"RSA encrypt error: {e}")

def builtin_rsa_decrypt(data, private_key_str):
    if not CRYPTO_AVAILABLE:
        return f"[RSA decrypt mock: {data}]"
    try:
        private_key = RSA.import_key(private_key_str)
        cipher = PKCS1_OAEP.new(private_key)
        encrypted = base64.b64decode(data)
        decrypted = cipher.decrypt(encrypted)
        return decrypted.decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"RSA decrypt error: {e}")

# ------------------------------------------------------------
# Многопоточность (простейшая)
_threads = {}
_thread_counter = 0
_thread_lock = threading.Lock()

def builtin_thread_start(func, *args):
    global _thread_counter
    def wrapper():
        try:
            func(*args)
        except Exception as e:
            print(f"Thread error: {e}")
    t = threading.Thread(target=wrapper)
    with _thread_lock:
        _thread_counter += 1
        tid = _thread_counter
        _threads[tid] = t
    t.start()
    return tid

def builtin_thread_join(tid):
    t = _threads.get(tid)
    if t:
        t.join()
        return True
    return False

def builtin_lock_create():
    return threading.Lock()

def builtin_lock_acquire(lock):
    return lock.acquire()

def builtin_lock_release(lock):
    lock.release()

# ------------------------------------------------------------
# Сеть (TCP/UDP)
def builtin_tcp_send(host, port, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        s.close()
        return True
    except Exception as e:
        raise RuntimeError(f"TCP send error: {e}")

def builtin_udp_send(host, port, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(data.encode('utf-8'), (host, port))
        s.close()
        return True
    except Exception as e:
        raise RuntimeError(f"UDP send error: {e}")

def builtin_http_get(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HackLang/0.1'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"HTTP error: {e}"

# ------------------------------------------------------------
# Прокси (VPN) функции – будут в vpn.py, но можно и тут
# (перенесём в builtins для простоты)
def builtin_vpn_set_proxy(runtime, proxy_string):
    runtime.set_proxy(proxy_string)
    return True

def builtin_vpn_clear_proxy(runtime):
    runtime.clear_proxy()
    return True

def builtin_vpn_status(runtime):
    return runtime.proxy

def builtin_vpn_list_proxies():
    return [
        "http://185.46.212.88:80",
        "socks5://51.158.108.41:1080",
        "http://47.91.102.95:80",
        "http://118.69.50.155:80",
        "socks4://45.76.62.74:1080",
    ]

# ------------------------------------------------------------
# Импорт библиотек на HackLang
def builtin_import(runtime, filename):
    # Поиск файла в lib_path
    paths = [os.path.join(runtime.lib_path, filename), filename]
    for path in paths:
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            # Временно сохраняем старый глобальный контекст? 
            # Просто выполним в текущем runtime
            from .lexer import Lexer
            from .parser import Parser
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            prog = parser.parse_program()
            runtime.run(prog)
            return True
    raise RuntimeError(f"Библиотека не найдена: {filename}")

# ------------------------------------------------------------
# Регистрация всех встроенных функций
def register_all(runtime):
    # Базовые
    runtime.register_builtin('print', builtin_print)
    runtime.register_builtin('len', builtin_len)
    runtime.register_builtin('type', builtin_type)
    runtime.register_builtin('input', builtin_input)

    # Файлы
    runtime.register_builtin('file_read', builtin_file_read)
    runtime.register_builtin('file_write', builtin_file_write)
    runtime.register_builtin('file_append', builtin_file_append)
    runtime.register_builtin('file_exists', builtin_file_exists)
    runtime.register_builtin('file_delete', builtin_file_delete)
    runtime.register_builtin('dir_list', builtin_dir_list)
    runtime.register_builtin('system', builtin_system)

    # JSON
    runtime.register_builtin('json_encode', builtin_json_encode)
    runtime.register_builtin('json_decode', builtin_json_decode)

    # Время
    runtime.register_builtin('time_now', builtin_time_now)
    runtime.register_builtin('time_format', builtin_time_format)
    runtime.register_builtin('sleep', builtin_sleep)

    # Математика
    runtime.register_builtin('sin', builtin_sin)
    runtime.register_builtin('cos', builtin_cos)
    runtime.register_builtin('tan', builtin_tan)
    runtime.register_builtin('sqrt', builtin_sqrt)
    runtime.register_builtin('log', builtin_log)
    runtime.register_builtin('log10', builtin_log10)
    runtime.register_builtin('pow', builtin_pow)
    runtime.register_builtin('rand', builtin_rand)
    runtime.register_builtin('randint', builtin_randint)

    # Строки
    runtime.register_builtin('str_upper', builtin_str_upper)
    runtime.register_builtin('str_lower', builtin_str_lower)
    runtime.register_builtin('str_replace', builtin_str_replace)
    runtime.register_builtin('str_split', builtin_str_split)
    runtime.register_builtin('str_join', builtin_str_join)
    runtime.register_builtin('str_contains', builtin_str_contains)
    runtime.register_builtin('str_strip', builtin_str_strip)

    # Криптография
    runtime.register_builtin('hash_sha256', builtin_hash_sha256)
    runtime.register_builtin('base64_encode', builtin_base64_encode)
    runtime.register_builtin('base64_decode', builtin_base64_decode)
    runtime.register_builtin('aes_encrypt', builtin_aes_encrypt)
    runtime.register_builtin('aes_decrypt', builtin_aes_decrypt)
    runtime.register_builtin('rsa_generate_keys', builtin_rsa_generate_keys)
    runtime.register_builtin('rsa_encrypt', builtin_rsa_encrypt)
    runtime.register_builtin('rsa_decrypt', builtin_rsa_decrypt)

    # Многопоточность
    runtime.register_builtin('thread_start', builtin_thread_start)
    runtime.register_builtin('thread_join', builtin_thread_join)
    runtime.register_builtin('lock_create', builtin_lock_create)
    runtime.register_builtin('lock_acquire', builtin_lock_acquire)
    runtime.register_builtin('lock_release', builtin_lock_release)

    # Сеть
    runtime.register_builtin('tcp_send', builtin_tcp_send)
    runtime.register_builtin('udp_send', builtin_udp_send)
    runtime.register_builtin('http_get', builtin_http_get)

    # VPN/прокси (замыкаем на runtime)
    runtime.register_builtin('vpn_set_proxy', lambda p: builtin_vpn_set_proxy(runtime, p))
    runtime.register_builtin('vpn_clear_proxy', lambda: builtin_vpn_clear_proxy(runtime))
    runtime.register_builtin('vpn_status', lambda: builtin_vpn_status(runtime))
    runtime.register_builtin('vpn_list_proxies', builtin_vpn_list_proxies)

    # Импорт библиотек на HackLang
    runtime.register_builtin('__import__', lambda f: builtin_import(runtime, f))