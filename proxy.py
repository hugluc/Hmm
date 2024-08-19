# proxy.py
import os
import subprocess

# Konfigurasi proxy
proxy = 'username:password@ip:port'

# Menetapkan variabel lingkungan untuk proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Jalankan bot.py dengan variabel lingkungan proxy yang telah diatur
subprocess.run(['python', '(ganti dengan nama bot yang mau dirunning).py'])
