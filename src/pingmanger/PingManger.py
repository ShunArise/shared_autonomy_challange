from pythonping import ping


class PingManager:
    def __init__(self, ip_addresses):
        self.ip_addresses = ip_addresses

    def ping_host(self, ip):
        try:
            response = ping(ip, count=4)
            return response.success()
        except Exception as e:
            print(f"Error pinging {ip}: {str(e)}")
            return False

    def get_reachable_ips(self):
        reachable_ips = []
        for ip in self.ip_addresses:
            if self.ping_host(ip):
                reachable_ips.append(ip)
        print(f"returned reachable_ips: ", reachable_ips)
        return reachable_ips
