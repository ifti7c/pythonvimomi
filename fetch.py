from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import csv

def connect_to_vcenter(vcenter_ip, username, password):
    try:
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

def write_to_csv(windows_hosts, output_file):
    try:
        with open(output_file, mode="w", newline="") as csvfile:
            fieldnames = ["Host Name", "Environment", "FQDN", "OS", "vCPU Count", "RAM (GB)"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for host in windows_hosts:
                writer.writerow({
                    "Host Name": host.name,
                    "Environment": host.summary.config.annotation,
                    "FQDN": host.summary.config.name,
                    "OS": host.summary.config.product.fullName,
                    "vCPU Count": host.hardware.cpuInfo.numCpuCores,
                    "RAM (GB)": round(host.hardware.memorySize / (1024 ** 3), 2)
                })
        print(f"Data exported to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {str(e)}")

def main():
    vcenter_ip = "vcenter.example.com"
    username = "your_username"
    password = "your_password"
    output_file = "windows_hosts.csv"  # Specify your desired output file name

    content = connect_to_vcenter(vcenter_ip, username, password)
    if content:
        windows_hosts = get_windows_hosts(content)
        write_to_csv(windows_hosts, output_file)

        # Disconnect from vCenter
        Disconnect(content)

if __name__ == "__main__":
    main()
