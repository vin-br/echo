# ARC Infrastructure as Code (IAC)

## General Overview
Provision a Fedora 40 virtual machine with Vagrant and Ansible to run the ARC backend application. 

The Ansible playbook automatically installs:
- Linux distribution
- Python package manager
- Python version
- All application dependencies (FastAPI, DuckDB, etc.)
- Systemd service for auto-start

## Technical Overview

- **VM**: Fedora 40 via `bento/fedora-40` box (works on x86_64 and ARM64)
- **Resources**: 2GB RAM, 2 CPUs
- **Python**: 3.14.2 (managed by uv)
- **Package manager**: uv
- **Init system**: systemd

## Features

1. *Synced folder*: the project is mounted at `/vagrant_data` in the VM
2. *Live updates*: Code changes locally appear instantly in the VM
3. *Systemd service*: Application runs as `arc-backend` service
4. *Port forwarding*: VM port 8000 → localhost:8080

## Installation

Install these tools on your machine:

- **[Vagrant](https://www.vagrantup.com/downloads)** - VM management
- **[VirtualBox](https://www.virtualbox.org/wiki/Downloads)** - VM provider
- **[Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)** - Provisioning tool

**macOS (using Homebrew):**
```bash
brew install --cask vagrant
brew install --cask virtualbox
brew install ansible
```

**Windows:** Download and install VirtualBox and Vagrant from their websites. For Ansible, use WSL2.


## Quick Start

```bash
cd iac
vagrant up
```

That's it! The VM will:
- Download Fedora 40
- Install Python 3.14.2 and dependencies using uv
- Start the application on port 8000 (forwarded to your port 8080)
- Run a health check

**Access the app:** http://localhost:8080

## Common Commands

```bash
vagrant up        # Start the VM
vagrant halt      # Stop the VM
vagrant ssh       # Connect to the VM
vagrant destroy   # Delete the VM completely
vagrant provision # Re-run Ansible without recreating VM
```

## Checking the Application

```bash
# View application logs
vagrant ssh -c "sudo journalctl -u arc-backend -f"

# Check service status:
vagrant ssh -c "sudo systemctl status arc-backend"

# Restart the application:
vagrant ssh -c "sudo systemctl restart arc-backend"
```

## Troubleshooting

```bash
# For verbose output
vagrant up --debug
```
