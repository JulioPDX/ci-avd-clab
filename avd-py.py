import copy
import difflib
import io
import sys
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from rich.progress import Progress
from pyavd import (
    get_avd_facts,
    get_device_structured_config,
    get_device_config,
    validate_inputs,
)
from rich import print


# Recreating the inventory objects to be like  Ansible
dl = DataLoader()
im = InventoryManager(loader=dl, sources=["inventory.yml"])
vm = VariableManager(loader=dl, inventory=im)

hosts = {}

# grab all the hosts and add the hostname with relevant
# variables to the hosts dictionary
# deep copy required to make sure information is not overwritten
for host in im.get_hosts("all"):
    host_vars = vm.get_vars(host=host)
    hosts[str(host)] = copy.deepcopy(host_vars)

with Progress() as progress:
    # progress bars for pretty output
    total = len(hosts)
    task1 = progress.add_task("[red]facts...", total=1)
    task2 = progress.add_task("[blue]validate inputs...", total=total)
    task3 = progress.add_task("[yellow]structured config...", total=total)
    task4 = progress.add_task("[green]build config...", total=total)

    facts = get_avd_facts(hosts)
    progress.update(task1, advance=1)

    # loop to check the state of validate status and print
    # any errors
    for k, v in hosts.items():
        validate = validate_inputs(v)

        if validate.failed:
            print(f"The following validation errors were seen for {k}")
            for issue in validate.validation_errors:
                print(issue)
            sys.exit(1)
        progress.update(task2, advance=1)

        struct_conf = get_device_structured_config(k, v, facts)
        progress.update(task3, advance=1)

        config = get_device_config(struct_conf)
        buf = io.StringIO(config)
        print(k)
        try:
            with open(f"artifacts/intended/configs/{k}.cfg") as file:
                old = file.readlines()

            for line in difflib.unified_diff(old, buf.readlines(), lineterm=""):
                print(line)

            with open(f"artifacts/intended/configs/{k}.cfg", "w") as f:
                f.writelines(config)

        except FileNotFoundError:
            with open(f"artifacts/intended/configs/{k}.cfg", "w") as f:
                f.writelines(config)

        progress.update(task4, advance=1)
