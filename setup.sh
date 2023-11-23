#!/bin/bash

echo "Installing Project Python Requirements"
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Development Python Requirements"
pip install -r requirements-dev.txt

echo "Installing Project Ansible Collection Requirements"
ansible-galaxy collection install -r requirements.yml --force-with-deps

echo "Installing Project Arista AVD Collection Python Requirements"
export ARISTA_AVD_DIR=$(ansible-galaxy collection list arista.avd --format yaml | head -1 | cut -d: -f1)
pip install -r ${ARISTA_AVD_DIR}/arista/avd/requirements.txt
