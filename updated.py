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

def get_vcpu_and_ram(host):
    vcpu_count = host.summary.config.numCpu
    ram_mb = host.summary.config.memorySizeMB
    ram_gb = round(ram_mb / 1024, 2)  # Convert RAM from MB to GB
    return vcpu_count, ram_gb

def write_to_csv(windows_hosts, output_file):
    try:
        with open(output_file, mode="w", newline="") as csvfile:
            fieldnames = ["Host Name", "Environment", "FQDN", "OS", "vCPU Count", "RAM (GB)", "Hard Disk Sizes (GB)"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for host in windows_hosts:
                disk_sizes = get_hard_disk_sizes(host)
                vcpu_count, ram_gb = get_vcpu_and_ram(host)
                row_data = {
                    "Host Name": host.name,
                    "Environment": host.summary.config.annotation,
                    "FQDN": host.summary.config.name,
                    "OS": host.summary.config.product.fullName,
                    "vCPU Count": vcpu_count,
                    "RAM (GB)": ram_gb,
                    "Hard Disk Sizes (GB)": disk_sizes,
                }
                writer.writerow(row_data)
    except Exception as e:
        print(f"Error writing to CSV: {str(e)}")

# Call the functions with appropriate parameters
content = connect_to_vcenter("your_vcenter_ip", "your_username", "your_password")
if content:
    windows_hosts = get_windows_hosts(content)
    write_to_csv(windows_hosts, "output.csv")
