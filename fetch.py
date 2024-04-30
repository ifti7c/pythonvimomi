import csv
from pyVmomi import vmodl, vim
from tools import cli, service_instance  # Import external modules

def print_host_info_to_csv(host, csv_writer):
  """
  Extracts and writes information to the provided CSV writer.
  """
  summary = host.summary
  csv_writer.writerow([summary.config.name, summary.hardware.memorySize, summary.overallStatus])

def get_vcenter_servers(file_path):
  """
  Reads vCenter server URLs from a file and returns a list.
  """
  vcenters = []
  try:
    with open(file_path, 'r') as file:
      for line in file:
        vcenters.append(line.strip())  # Remove leading/trailing whitespaces
  except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
  except Exception as err:
    print(f"Error reading vCenter list file: {err}")
  return vcenters

def main():
  """
  Simple command-line program for listing host information in a CSV file, handling multiple vCenters from a file.
  """
  parser = cli.Parser()
  parser.add_argument('-o', '--output', required=True, help='Path to the output CSV file')
  parser.add_argument('-f', '--vcenter_file', required=True, help='Path to the file containing vCenter server URLs (one per line)')
  args = parser.get_args()

  # Read vCenter list from file
  vcenter_urls = get_vcenter_servers(args.vcenter_file)

  # Loop through each vCenter server URL
  for vcenter_url in vcenter_urls:
    try:
      si = service_instance.connect(vcenter_url)  # Connect to vCenter

      content = si.RetrieveContent()
      container = content.rootFolder
      view_type = [vim.HostSystem]  # Specify we want to view HostSystem objects
      recursive = True  # Search recursively through the inventory
      container_view = content.viewManager.CreateContainerView(container, view_type, recursive)
      children = container_view.view  # Get the list of hosts

      with open(args.output, 'a', newline='') as csvfile:  # Append mode for multiple vCenters
        csv_writer = csv.writer(csvfile)
        if vcenter_url == vcenter_urls[0]:  # Write header row only for the first vCenter
          csv_writer.writerow(['Hostname', 'Memory (MB)', 'Overall Status'])
        for child in children:
          print_host_info_to_csv(child, csv_writer)

    except vmodl.MethodFault as error:
      print(f"Caught vmodl fault for vCenter {vcenter_url}: {error.msg}")

  # Indicate program completion
  print("Finished processing vCenters.")

# Start program
if __name__ == "__main__":
  main()
