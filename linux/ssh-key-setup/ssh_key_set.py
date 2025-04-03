import os
import subprocess
import platform
import re
import time

def ping_host(host_ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host_ip]
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0

def is_valid_ip(ip):
    pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
    return bool(pattern.match(ip))

def confirm(prompt):
    answer = input(f"{prompt} (Y/N): ").strip().lower()
    return answer == 'y'

# --- User input ---
host_ip = input("Enter the full IP address of the target host (e.g., 192.168.1.50): ").strip()
ssh_alias = input("What should be the SSH alias (e.g., docker, server)? ").strip()
ssh_user = input("Enter the SSH username: ").strip()

if not host_ip or not is_valid_ip(host_ip):
    print("❌ Error: Valid IP address is required!")
    exit()

if not ssh_alias or not ssh_user:
    print("❌ Error: Alias and username are required!")
    exit()

if not ping_host(host_ip):
    print(f"❌ Error: Host at {host_ip} is unreachable. Check network or VPN.")
    exit()

# --- Prepare paths ---
safe_ip = host_ip.replace('.', '_')
ssh_dir = os.path.expanduser("~/.ssh")
public_key_path = os.path.join(ssh_dir, f"id_rsa_{safe_ip}.pub")
private_key_path = os.path.join(ssh_dir, f"id_rsa_{safe_ip}")
config_path = os.path.join(ssh_dir, "config")

# --- Existing key warning and optional deletion ---
if os.path.exists(private_key_path) or os.path.exists(public_key_path):
    print("⚠️ Warning: A key file already exists for this IP address:")
    if os.path.exists(private_key_path):
        print(f"  - Private key: {private_key_path} (modified: {time.ctime(os.path.getmtime(private_key_path))})")
    if os.path.exists(public_key_path):
        print(f"  - Public key: {public_key_path} (modified: {time.ctime(os.path.getmtime(public_key_path))})")

    # Check if this key is used in SSH config
    existing_entry_info = None
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_lines = f.readlines()

        current_alias = None
        for line in config_lines:
            if line.strip().startswith("Host "):
                current_alias = line.strip().split()[1]
            if f"IdentityFile {private_key_path}" in line:
                existing_entry_info = current_alias
                break

    if existing_entry_info:
        print(f"  🔍 This key is linked to the alias '{existing_entry_info}' in your SSH config.")

    print("ℹ️ If this key belongs to another VPN or alias, keep it. If it's broken, delete and regenerate.")
    if confirm("Delete the existing key files?"):
        if os.path.exists(private_key_path):
            os.remove(private_key_path)
        if os.path.exists(public_key_path):
            os.remove(public_key_path)
        print("🗑 Key files deleted.")
    else:
        print("❌ Aborted: keeping existing key files.")
        exit()

# --- Remove previous alias config if exists ---
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        lines = f.readlines()

    alias_exists = any(line.strip() == f"Host {ssh_alias}" for line in lines)

    if alias_exists:
        print(f"⚠️ Warning: The alias '{ssh_alias}' already exists in SSH config.")
        if confirm("Remove the existing alias block?"):
            with open(config_path, 'w') as f:
                skip = False
                for line in lines:
                    if line.strip().startswith("Host ") and line.strip() == f"Host {ssh_alias}":
                        skip = True
                    elif skip and line.strip().startswith("Host "):
                        skip = False
                        f.write(line)
                    elif not skip:
                        f.write(line)
            print("🗑 Old alias block removed.")
        else:
            print("❌ Aborted: alias block not modified.")
            exit()

# --- Generate new SSH key pair ---
print("🔐 Generating SSH key pair...")
subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", private_key_path, "-N", ""], check=True)
print("✅ Key pair generated successfully.")

# --- Update SSH config with new alias ---
ssh_config_entry = f"""
Host {ssh_alias}
    HostName {host_ip}
    User {ssh_user}
    IdentityFile {private_key_path}
    HostKeyAlias {ssh_alias}
    Port 22
"""

with open(config_path, 'a') as config_file:
    config_file.write(ssh_config_entry)
print(f"📝 Alias '{ssh_alias}' added to SSH config.")

# --- Upload public key to remote host via password SSH ---
print("🚀 Uploading public key to the remote host...")
try:
    with open(public_key_path, 'r') as key_file:
        public_key = key_file.read().strip()

    remote_command = (
        f"mkdir -p ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && "
        f"grep -qxF '{public_key}' ~/.ssh/authorized_keys || echo '{public_key}' >> ~/.ssh/authorized_keys"
    )

    subprocess.run(
        ["ssh", f"{ssh_user}@{host_ip}", remote_command],
        check=True
    )

    print("✅ Public key uploaded successfully.")
except subprocess.CalledProcessError as e:
    print(f"❌ Error while uploading key:
{e}")

# --- Test passwordless login ---
print("🔍 Testing passwordless SSH connection via alias...")
test_ssh_command = ["ssh", "-o", "BatchMode=yes", ssh_alias, "echo", "connection_successful"]
result = subprocess.run(test_ssh_command, capture_output=True, text=True)

if "connection_successful" in result.stdout:
    print("✅ Passwordless SSH login successful!")
else:
    print("⚠️ Passwordless login failed. Check key and permissions.")
