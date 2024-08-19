import requests
import json
import websocket
import time
import random
from colorama import Fore, Style
import threading
print_lock = threading.Lock()  # Create a lock for printing

logUpdate = {}
previousUpdate = {}

def get_access_token(x_tg_data):
    url = 'https://miniapp-be.chickizen.com/auth'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://miniapp.chickizen.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://miniapp.chickizen.com/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'x-chain-id': '43113',
        'x-lang': 'en',
        'x-os': 'miniapp',
        'x-tg-data': x_tg_data
    }
    while True:
        try:
            response = requests.post(url, headers=headers, data='{}')
            response.raise_for_status()
            data = response.json()['data']
            return data['access_token'], data['user']['first_name']
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            with print_lock:
                print(f"[{threading.current_thread().name}] Error getting access token: {e}. Retrying...", end="\n", flush=True)
            time.sleep(2)

def read_queries(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]
    
def format_money(value):
    formatted_value = f"{value:,}".replace(",", ".")
    if value >= 1_000_000_000_000: #1.802.110.684.828 
        suffix = f"{value // 1_000_000_000_000:.3f}B"
    elif value >= 1_000_000_000:
        suffix = f"{value / 1_000_000_000:.3f}M"
    elif value >= 1_000_000:
        suffix = f"{value / 1_000_000:.3f}K"
    else:
        suffix = f"{formatted_value}"
    return f"{suffix}"
def get_sid():
    url = 'https://miniapp-ws.chickizen.com/socket.io/?EIO=4&transport=polling&t=P4r1i5c'
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            sid = json.loads(response.text.split('\n')[0][1:])['sid']
            return sid
        except (json.JSONDecodeError, KeyError, requests.RequestException) as e:
            with print_lock:
                print(f"[{threading.current_thread().name}] Error getting SID: {e}. Retrying...", end="\n", flush=True)
            time.sleep(5)


def process_chickens(chickens):
    seen = {}
    for i, num in sorted(enumerate(chickens), key=lambda x: x[1]):
        if num == 0:
            continue  # Skip processing if the number is 0
        if num in seen and seen[num] is not None:
            # Combine chickens at indices seen[num] and i with value num
            # print(f"Combining chickens at indices {seen[num]} and {i} with value {num}")
            chickens[seen[num]] = 0
            chickens[i] += 1
            seen[num] = None  # Mark as processed
        else:
            seen[num] = i

    # print(f"Processed chickens: {chickens}")
    return chickens

import ssl


def connect_and_listen(token, first_name, index, total):
    global logUpdate, previousUpdate
    while True:
        try:
            sid = get_sid()
            response = requests.post(
                f'https://miniapp-ws.chickizen.com/socket.io/?EIO=4&transport=polling&t=P4r1i6y&sid={sid}',
                headers={
                    'accept': '*/*',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
                },
                data=f'40{{"token":"{token}"}}'  # Use the provided token
            )
 
            ws = websocket.WebSocket()
            ws.connect(
                f'wss://miniapp-ws.chickizen.com/socket.io/?EIO=4&transport=websocket&sid={sid}',
                header=[
                    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
                ]
            )

            if ws.connected:
                with print_lock:
                    print(f"[{threading.current_thread().name}] Server connected", end="\n", flush=True)
                ws.send('2probe')
                response = ws.recv()
                if response == '3probe':
                    ws.send('5')
                    response = ws.recv()
                try:
                    message = ws.recv()
                    if '42["auth' in message:
                        with print_lock:
                            print(f"[{threading.current_thread().name}] Ready Boost Chicken", end="\n", flush=True)
                        time.sleep(1)
                        ws.send('42["update_coin",{"bonus":10000}]')
                        
                        while True:
                            ws.send('42["update_coin",{"bonus":10000}]')
                            message = ws.recv()
                            time.sleep(0.5)
                            # print(message)
                            if '42["game_info' in message:
                                data = json.loads(message[2:])[1]['data']['user']
                                colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
                                results = (
                                    f"{Fore.WHITE}{first_name} | "
                                    f"{random.choice(colors)}Level: {data['level']} | "
                                    f"{random.choice(colors)}Value: {data['chicken_value']} | "
                                    f"{random.choice(colors)}Token: {data['token']} | "
                                    f"{random.choice(colors)}Money: {format_money(data['money'])} | "
                                    f"{random.choice(colors)}Speed: {data['earn_speed']} | "
                                    f"{random.choice(colors)}Chicken: {data['chickens']}{Style.RESET_ALL}"
                                )
                                with print_lock:
                                    if threading.current_thread().name not in previousUpdate.values():
                                        previousUpdate[index] = threading.current_thread().name
                                        logUpdate[index] = {"Akun_Number": index+1, "Data": results}
                                    else:
                                        if len(logUpdate) >= total:
                                            print("\033c", end="")  # ANSI escape code to clear the screen
                                            logUpdate = dict(sorted(logUpdate.items()))
                                            print(f"\n".join([f"{v['Data']}" for k, v in logUpdate.items()]), end="\n", flush=True)
                                            logUpdate = {}
                                            previousUpdate = {}
                                        else:
                                            continue
                                chickens = data['chickens']
                        
                                processed_chickens = process_chickens(chickens)
                                ws.send(f'42["sync_chicken",' + json.dumps({"chickens": processed_chickens}) + ']')
                                message = ws.recv()
                                if '42["notification",{"success":false,"error":{"message":"Invalid chicken data, please wait for data sync"' in message:
                                    continue
                            elif '42["exception' in message:
                                with print_lock:
                                    print(f"[{threading.current_thread().name}] Server Down", end="")
                                    for _ in range(1):
                                        time.sleep(0.5)
                                        print(".....    ", end="", flush=True)
                                    print("\r", end="", flush=True)
                            else:
                                with print_lock:
                                    print(f"[{threading.current_thread().name}] {message}")
                    else:
                        ws.send('42["update_coin",{"bonus":10000}]')
                except websocket.WebSocketConnectionClosedException:
                    with print_lock:
                        print(f"[{threading.current_thread().name}] Connection lost. Reconnecting...", end="\n", flush=True)
                    ws.close()
                    time.sleep(1)
                except ssl.SSLEOFError as e:
                    with print_lock:
                        print(f"[{threading.current_thread().name}] SSL error: {e}. Reconnecting...", end="\n", flush=True)
                    ws.close()
                    time.sleep(1)
        except Exception as e:
            with print_lock:
                print(f"[{threading.current_thread().name}] Unexpected error: {e}. Reconnecting...", end="\n", flush=True)
            time.sleep(1)

def worker(x_tg_data, index, total):
    try:
        token, first_name = get_access_token(x_tg_data)
        # print(f"Access token for {x_tg_data}: {token}")
        # You can now use this token in your connect_and_listen function
        connect_and_listen(token,first_name, index, total)
    except Exception as e:
        with print_lock:
            print(f"[{threading.current_thread().name}] Error processing {x_tg_data}: {e}")

def main():
    queries = read_queries('query.txt')
    threads = []
    for i, query in enumerate(queries):
        thread = threading.Thread(target=worker, args=(query,i,len(queries)), name=f"Thread-{i+1}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()