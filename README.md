# Web-based Tsinghua University Network Auto Login

Automatically log into the Tsinghua University campus network portal using Python and Selenium in headless mode.

## Features

- ✅ Headless browser automation (no GUI required)
- ✅ Command line interface
- ✅ Environment variable support for credentials
- ✅ Comprehensive logging
- ✅ Error handling and timeout management
- ✅ Automatic external network access (IPv4) checkbox selection

## Requirements

- Python 3.6+
- Chrome or Chromium browser
- Internet connection

## Installation

1. **Clone or download the project:**

   ```bash
   cd /root/tunet
   ```

2. **Run the setup script:**

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This will install all required Python packages and check for browser availability.

## Usage

### Method 1: Environment Variables (Recommended)

```bash
export TUNET_USERNAME='your_username'
export TUNET_PASSWORD='your_password'
python3 tunet_login.py
```

### Method 2: Command Line Arguments

```bash
python3 tunet_login.py -u your_username -p your_password
```

### Method 3: With Visible Browser (for debugging)

```bash
python3 tunet_login.py -u your_username -p your_password --no-headless
```

## Command Line Options

```shell
usage: tunet_login.py [-h] [-u USERNAME] [-p PASSWORD] [--no-headless] 
                      [--timeout TIMEOUT] [-v]

Tsinghua University Network Auto Login

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Campus network username
  -p PASSWORD, --password PASSWORD
                        Campus network password
  --no-headless         Run with visible browser window
  --timeout TIMEOUT     Timeout in seconds (default: 30)
  -v, --verbose         Enable verbose logging
```

## Automation

### Add to crontab for periodic login

```bash
# Edit crontab
crontab -e

# Add line to run every hour (adjust path as needed)
0 * * * * cd /root/tunet && python3 tunet_login.py
```

### Create a systemd service

1. Create service file:

```bash
sudo nano /etc/systemd/system/tunet-login.service
```

1. Add content:

```ini
[Unit]
Description=Tsinghua University Network Auto Login
After=network.target

[Service]
Type=oneshot
Environment=TUNET_USERNAME=your_username
Environment=TUNET_PASSWORD=your_password
WorkingDirectory=/root/tunet
ExecStart=/usr/bin/python3 tunet_login.py
User=root

[Install]
WantedBy=multi-user.target
```

1. Enable and start:

```bash
sudo systemctl enable tunet-login.service
sudo systemctl start tunet-login.service
```

## Security Notes

- **Environment Variables:** The most secure way to store credentials
- **File Permissions:** Ensure scripts have appropriate permissions
- **Password Storage:** Never commit passwords to version control

## Troubleshooting

### Chrome/ChromeDriver Issues

If you encounter ChromeDriver issues:

1. **Install ChromeDriver manually:**

   ```bash
   # Download ChromeDriver from https://chromedriver.chromium.org/
   # Or use package manager:
   sudo apt-get install chromium-chromedriver  # Ubuntu/Debian
   ```

1. **Use Selenium Manager (automatic, recommended):**

   ```bash
   # Selenium Manager (built into Selenium 4.6+) automatically handles driver downloads
   # No additional setup required - just ensure Chrome/Chromium is installed
   ```

### Network Issues

- Ensure you're connected to the Tsinghua University network
- Check if the portal URL is accessible: `curl http://auth6.tsinghua.edu.cn/`

### Common Error Messages

- **"Username and password must be provided"**: Set environment variables or use command line arguments
- **"Timeout waiting for page elements"**: Increase timeout with `--timeout 60`
- **"Failed to initialize Chrome driver"**: Install Chrome/Chromium and ChromeDriver

## Project Structure

```plaintext
/root/tunet/
├── tunet_login.py      # Main script
├── requirements.txt    # Python dependencies
├── setup.sh           # Installation script
└── README.md          # This file
```

## License

This project is for educational and personal use only. Please comply with Tsinghua University's network usage policies.
