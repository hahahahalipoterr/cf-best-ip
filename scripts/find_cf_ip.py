import ipaddress
import socket
import time
import random
import urllib.request

IPV4_URL = "https://www.cloudflare.com/ips-v4"
TIMEOUT = 1
SAMPLE_PER_NET = 3
PORT = 443

def fetch_ip_ranges(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read().decode()
    return [line.strip() for line in data.splitlines() if line.strip()]


def tcp_ping(ip, port):
    start = time.time()
    try:
        sock = socket.create_connection((ip, port), timeout=TIMEOUT)
        sock.close()
        return int((time.time() - start) * 1000)
    except:
        return None

def sample_ips(cidr, count):
    net = ipaddress.ip_network(cidr, strict=False)
    hosts = list(net.hosts())
    if len(hosts) <= count:
        return [str(ip) for ip in hosts]
    return [str(ip) for ip in random.sample(hosts, count)]

# 👇 机场码规则（你可以随便改）
def airport_code(latency):
    if latency <= 30:
        return "CF-CN"
    elif latency <= 80:
        return "CF-HKG"
    elif latency <= 150:
        return "CF-SG"
    else:
        return "CF-US"

def main():
    cidrs = fetch_ip_ranges(IPV4_URL)
    results = []

    for cidr in cidrs:
        for ip in sample_ips(cidr, SAMPLE_PER_NET):
            latency = tcp_ping(ip, PORT)
            if latency is not None:
                code = airport_code(latency)
                results.append((ip, latency, code))

    results.sort(key=lambda x: x[1])

    with open("data/cf_best_ip.txt", "w") as f:
        for ip, latency, code in results[:20]:
            f.write(f"{code} | {ip}:{PORT} | {latency}ms\n")

    print("Done.")

if __name__ == "__main__":
    main()
