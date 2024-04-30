from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit
import csv

def connect_to_vcenter(vcenter_ip, username, password):
    try:
        # Disable SSL certificate verification
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE

        si = SmartConnect(host=vcenter_ip, user=username, pwd=password, sslContext=context)
        atexit.register(Disconnect, si)
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

def get_hard_disk_sizes(host):
    disk_sizes = []
    for datastore in host.datastore:
        for disk in datastore.info.vmfs.extent:
            disk_sizes.append(round(disk.capacity / (1024 ** 3), 2))  # Convert to GB
    return disk_sizes

def write_to_csv(windows_hosts, output_file):
    try:
        with open(output_file, mode="w", newline="") as csvfile:
            fieldnames = ["Host Name", "Environment", "FQDN", "OS", "vCPU Count", "RAM (GB)", "Hard Disk Sizes (GB)"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for host in windows_hosts:
                disk_sizes = get_hard_disk_sizes(host)
                row_data = {
                    "Host Name": host.name,
                    "Environment": host.summary.config.annotation,
                    "FQDN": host.summary.config.name,
                    "OS": host.summary.config.product.fullName,
                    "vCPU Count": host.hardware.cpuInfo.numCpuCores,
                    "RAM (GB)": round(host.hardware.memorySize / (1024 ** 3), 2),
                    "Hard Disk Sizes (GB)": ", ".join(map(str, disk_sizes))
                }
                # Fill empty fields with a placeholder
                for key in row_data:
                    if not row_data[key]:
                        row_data[key] = "N/A"
                writer.writerow(row_data)
        print(f"Data exported to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {str(e)}")

def main():
    vcenter_ip = "vcenter.example.com"
    username = "your_username"
    password = "your_password"
    output_file = "windows_hosts_details.csv"  # Specify your desired output file name

    content = connect_to_vcenter(vcenter_ip, username, password)
    if content:
        windows_hosts = get_windows_hosts(content)
        write_to_csv(windows_hosts, output_file)

if __name__ == "__main__":
    main()
