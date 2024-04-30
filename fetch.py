from pyVim import connect
from csv import writer

def get_windows_host_details(service_instance):
  """
  Retrieves details of Windows hosts from the specified vCenter.

  Args:
      service_instance: A pyVimomi ServiceInstance object representing the vCenter.

  Returns:
      A list of dictionaries, where each dictionary contains information
      about a Windows host (name, model, CPU count, memory size, OS version).
  """
  content = service_instance.RetrieveContent()
  container_view = content.rootFolder
  view = content.viewManager.CreateContainerView(container_view, [vim.Host], True)
  hosts = view.view

  windows_hosts = []
  for host in hosts:
    if host.summary.guestOperatingSystem == "windows":
      summary = host.summary
      host_info = {
          "name": summary.config.name,
          "model": summary.hardware.hardwareVersion,
          "cpu_count": summary.hardware.cpuCount,
          "memory_size": summary.hardware.memorySize / (1024 * 1024 * 1024),
          "os_version": summary.guestOperatingSystem
      }
      windows_hosts.append(host_info)

  view.Destroy()
  return windows_hosts

def main():
  """
  Connects to multiple vCenters, fetches Windows host details, and exports to CSV.
  """
  vcenter_configs = [
      {"host": "vcenter1.example.com", "user": "username", "password": "password"},
      {"host": "vcenter2.example.com", "user": "username", "password": "password"},
      # ... Add additional vCenter configurations here
  ]

  all_windows_hosts = []
  for config in vcenter_configs:
    try:
      service_instance = connect.SmartConnectNoSSL(**config)
      windows_hosts = get_windows_host_details(service_instance)
      all_windows_hosts.extend(windows_hosts)
    except vim.fault.VimFaultException as e:
      print(f"Error connecting to vCenter {config['host']}: {e}")
    finally:
      connect.Disconnect(service_instance)

  # Export data to CSV
  with open("windows_hosts.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerow(["Name", "Model", "CPU Count", "Memory Size (GB)", "OS Version"])
    for host in all_windows_hosts:
      csv_writer.writerow([host[key] for key in host])

  print("Windows host details exported to windows_hosts.csv")

if __name__ == "__main__":
  main()
