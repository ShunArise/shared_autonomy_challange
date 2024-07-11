import subprocess

class PingManager:
    def __init__(self, ip_addresses):
        self.ip_addresses = ip_addresses

    def ping_host(self, ip):
        try:
            # Using subprocess to call the system's ping command
            response = subprocess.run(['ping', '-c', '4', ip], capture_output=True, text=True)
            return response.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {str(e)}")
            return False

    def get_reachable_ips(self):
        reachable_ips = []
        for ip in self.ip_addresses:
            if self.ping_host(ip):
                reachable_ips.append(ip)
        print(f"Returned reachable IPs: {reachable_ips}")
        return reachable_ips
