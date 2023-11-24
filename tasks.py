#!/usr/bin/env python3

from invoke import task
import subprocess
import os


ANSIBLE_LOG_FILE = "ansible.log"
CEOS_VERSION = "4.30.2F"
CLAB_FILE = "lab.yml"
REQUIREMENTS_FILE_ANSIBLE = "requirements.yml"
REQUIREMENTS_FILE_PYTHON = "requirements.txt"
REQUIREMENTS_FILE_PYTHON_DEV = "requirements-dev.txt"


@task()
def setup_devcontainer(ctx):
    """
    Set up the development container environment.
    This task runs other tasks to install various requirements.
    """

    # Install Base Setup
    setup_base(ctx)

    # Install ContainerLab
    install_clab(ctx)


@task()
def setup_base(ctx):
    """
    Set up the development container environment.
    This task runs other tasks to install various requirements.
    """

    # Install Python project and development requirements
    install_python_reqs(ctx)
    install_python_reqs_dev(ctx)

    # Install Ansible collection requirements
    install_ansible_collections(ctx)


@task()
def install_python_reqs(ctx):
    """
    Install project Python requirements.
    """
    print("Installing Project Python Requirements")
    ctx.run("pip install --upgrade pip")
    ctx.run(f"pip install -r {REQUIREMENTS_FILE_PYTHON}")


@task()
def install_python_reqs_dev(ctx):
    """
    Install development Python requirements.
    """
    print("Installing Development Python Requirements")
    ctx.run(f"grep -v 'invoke' {REQUIREMENTS_FILE_PYTHON_DEV} | xargs pip install")


@task()
def install_ansible_collections(ctx):
    """
    Install Ansible collection requirements, including Arista AVD collection.
    """
    print("Installing Project Ansible Collection Requirements")
    ctx.run(
        f"ansible-galaxy collection install -r {REQUIREMENTS_FILE_ANSIBLE} --force-with-deps"
    )

    print("Installing Project Arista AVD Collection Python Requirements")
    # Run the command and capture its output
    result = subprocess.run(
        "ansible-galaxy collection list arista.avd --format yaml | head -1 | cut -d: -f1",
        shell=True,
        text=True,
        capture_output=True,
    )

    if result.returncode == 0:
        # Extract the output and remove any trailing newlines
        arista_avd_dir = result.stdout.strip()
        ctx.run(f"pip install -r {arista_avd_dir}/arista/avd/requirements.txt")
    else:
        print("Error obtaining ARISTA_AVD_DIR:", result.stderr)


@task()
def install_clab(ctx):
    """
    Install ContainerLab specifically for the devcontainer environment.
    """
    print("Installing ContainerLab")
    ctx.run(
        "echo 'deb [trusted=yes] https://apt.fury.io/netdevops/ /' | sudo tee -a /etc/apt/sources.list.d/netdevops.list"
    )
    ctx.run("sudo apt update && sudo apt install containerlab")


@task()
def clab_download_and_deploy(ctx, token=None):
    """
    Download cEOS and create ContainerLab Topology.
    """

    download_eos(ctx, token)

    clab_deploy(ctx)


@task()
def clab_deploy(ctx):
    """
    Create ContainerLab Topology.
    """
    print("Deploying ContainerLab Topology")
    ctx.run(f"sudo -S clab deploy -t {CLAB_FILE} --reconfigure")


@task()
def clab_destroy(ctx):
    """
    Destroy ContainerLab Topology.
    """
    print("Destroying ContainerLab Topology")
    ctx.run(f"sudo -S clab destroy -t {CLAB_FILE}")


@task()
def download_eos(ctx, token=None):
    """
    Download EOS.
    invoke download_eos --token=<insert token here>
    """
    if token:
        print("Downloading EOS image")
        ctx.run(
            f"ardl --token='{token}' get eos --version {CEOS_VERSION} --image-type cEOS --import-docker"
        )
    elif "ARISTA_TOKEN" in os.environ:
        print("Downloading EOS image")
        ctx.run(
            f"ardl get eos --version {CEOS_VERSION} --image-type cEOS --import-docker"
        )
    else:
        print(
            "Error: `--token=<insert token here>` argument or Environment VAR `ARISTA_TOKEN=<insert token here>` is required"
        )
        exit()


@task()
def ansible_clear_log(ctx):
    """
    Clear ansible.log file.
    """
    print("Clearing ansible log file")
    open(ANSIBLE_LOG_FILE, "w", encoding="utf-8").close()
