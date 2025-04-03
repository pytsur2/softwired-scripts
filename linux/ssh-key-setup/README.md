
# SSH Key Generator and Alias Configuration Script

This script generates an SSH key pair, configures a new alias in your SSH config file,  
and uploads the public key to the specified remote server.

## Usage

```
python3 ssh_key_set.py
```

## Warning

This script modifies your `~/.ssh/config` file and creates SSH key files.  
It asks for confirmation before performing any destructive actions.

## License

MIT
