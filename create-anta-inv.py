# Quick write up to create an anta inventory

from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
import yaml


dl = DataLoader()
im = InventoryManager(loader=dl, sources=["inventory.yml"])
vm = VariableManager(loader=dl, inventory=im)


"""
# Example
---
anta_inventory:
  hosts:
    - host: 172.100.100.11
      name: spine1
      tags: ["fabric", "spine"]
    - host: 172.100.100.13
      name: leaf1
      tags: ["fabric", "leaf", "pod1"]
    - host: 172.100.100.14
      name: leaf2
      tags: ["fabric", "leaf", "pod2"]
"""

inventory = {"anta_inventory": {"hosts": []}}

for host in im.get_hosts("all"):
    host_vars = vm.get_vars(host=host)
    inventory["anta_inventory"]["hosts"].append(
        {
            "host": str(host_vars["ansible_host"]),
            "name": str(host_vars["inventory_hostname"]),
            "tags": [str(x) for x in host_vars["group_names"]],
        }
    )


with open("anta-auto.yml", "w") as file:
    yaml.dump(inventory, file)
