# PFS

The project is designed for secure one-time transmission of messages that should not remain in history anywhere.

## Usage

The sender of the message must have a white IP or server so that the recipient can go to their site and receive the encrypted message.

Messages are encrypted using the one-time pad principle. It takes 3 attempts to decrypt, after that the program automatically terminates, it also terminates after a correct decryption (after copying the result).

To run the program write:
```bash
python3 ./main.py --ip [IP] --port [PORT]
```

Or using scripts from the appropriate folder
```bash
fastshare --ip [IP] --port [PORT]
```

In place of IP - IP address for the site host, PORT - port for the site host.

Translated with DeepL.com (free version)