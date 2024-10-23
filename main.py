import requests
import csv

def load_addresses(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def load_proxies(filename):
    proxies = []
    with open(filename, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            if line:
                proxies.append({
                    "http": f"http://{line}",
                    "https": f"http://{line}"
                })
    return proxies

def check_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    try:
        response = requests.get(test_url, proxies=proxy, timeout=10)
        if response.status_code == 200:
            proxy_ip = response.json().get("origin")
            return proxy_ip
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def fetch_data(wallet_address, proxy):
    url = f"https://api.orbiter.finance/points_system/v2/user/points?address={wallet_address}"
    try:
        response = requests.get(url, proxies=proxy, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_activity_points = data.get('data', {}).get('total')
            if total_activity_points is not None:
                return total_activity_points
            else:
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

addresses_file = 'addresses.txt'
proxies_file = 'proxies.txt'
wallet_addresses = load_addresses(addresses_file)
proxies = load_proxies(proxies_file)

output_file = 'results.csv'

used_ips = set()

with open(output_file, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Address", "O-Points"])

    for wallet_address in wallet_addresses:
        success = False
        for proxy in proxies[:]:
            proxy_ip = check_proxy(proxy)

            if proxy_ip and proxy_ip not in used_ips:
                result = fetch_data(wallet_address, proxy)
                if result is not None:
                    success = True
                    print(f'Address: {wallet_address} | used proxy: {proxy_ip} | O-points: {result}')
                    used_ips.add(proxy_ip)
                    proxies.remove(proxy)
                    writer.writerow([wallet_address, result])
                    break


