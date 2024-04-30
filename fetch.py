from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def connect_to_vcenter(vcenter_ip, username, password):
    try:
        # Establish connection to vCenter
        si = SmartConnect(host=vcenter_ip, user=username, pwd=password)
        content = si.content
        return content
    except Exception as e:
        print(f"Error connecting to {vcenter_ip}: {str(e)}")
        return None

def get_windows_hosts(content):
    try:
        # Retrieve Windows hosts
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        hosts = container.view
        windows_hosts = [host for host in hosts if "Windows" in host.summary.config.product.fullName]
        return windows_hosts
    except Exception as e:
        print(f"Error fetching Windows hosts: {str(e)}")
        return []

def main():
    vcenter_ips = ["vcenter1.example.com", "vcenter2.example.com"]
    username = "your_username"
    password = "your_password"

    for vcenter_ip in vcenter_ips:
        content = connect_to_vcenter(vcenter_ip, username, password)
        if content:
            windows_hosts = get_windows_hosts(content)
            print(f"Windows hosts in {vcenter_ip}:")
            for host in windows_hosts:
                print(f"- {host.name}")

        # Disconnect from vCenter
        Disconnect(content)

if __name__ == "__main__":
    main()
