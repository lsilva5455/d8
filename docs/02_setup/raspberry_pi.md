# 🍓 Raspberry Pi 4 Deployment Guide

## Hardware Requirements

### ✅ Recommended: Raspberry Pi 4 (8GB RAM)
- **CPU:** Quad-core ARM Cortex-A72 @ 1.5GHz
- **RAM:** 8GB (ideal for 3-5 agents)
- **Storage:** 32GB+ MicroSD Class 10 or better
- **Power:** Official 5V 3A USB-C power supply

### ⚠️ Minimum: Raspberry Pi 4 (4GB RAM)
- Works but requires swap configuration
- Limit to 3 agents maximum
- Expect slower performance

---

## Pre-Installation Setup

### 1. OS Installation

```bash
# Use Raspberry Pi OS Lite (64-bit) for best performance
# Download: https://www.raspberrypi.com/software/

# Flash to SD card using Raspberry Pi Imager
# Enable SSH during setup
```

### 2. Initial Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git htop

# Configure swap (for 4GB model)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Mount tmpfs for logs (reduce SD card wear)
sudo mkdir -p /tmp/hive_logs
echo "tmpfs /tmp/hive_logs tmpfs defaults,noatime,size=100M 0 0" | sudo tee -a /etc/fstab
sudo mount -a
```

### 3. Install Python 3.10+

```bash
# Check version
python3 --version

# If < 3.10, install from source or use pyenv
```

---

## Installation

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/lsilva5455/d8.git
cd d8
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Use optimized requirements for Raspi
pip install --upgrade pip
pip install -r requirements.txt

# If ChromaDB fails to install, use pre-built wheel:
pip install chromadb --only-binary :all:
```

### 4. Configure Environment

```bash
# Copy Raspi-optimized config
cp config/raspi_optimized.env .env

# Edit and add your Groq API key
nano .env
# Set: GROQ_API_KEY=your_actual_key_here
```

---

## Running The Hive

### Standard Mode (Foreground)

```bash
source venv/bin/activate
python app/main.py
```

### Background Mode (Recommended)

```bash
# Install screen
sudo apt install screen -y

# Start in screen session
screen -S hive
source venv/bin/activate
python app/main.py

# Detach: Ctrl+A, then D
# Reattach: screen -r hive
```

### System Service (Auto-start on boot)

```bash
# Create service file
sudo nano /etc/systemd/system/hive.service
```

Paste:
```ini
[Unit]
Description=The Hive - Evolutionary AI Agents
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/d8
Environment="PATH=/home/pi/d8/venv/bin"
ExecStart=/home/pi/d8/venv/bin/python app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hive.service
sudo systemctl start hive.service

# Check status
sudo systemctl status hive.service

# View logs
sudo journalctl -u hive.service -f
```

---

## Performance Tuning

### 1. Monitor Resources

```bash
# Real-time monitoring
htop

# Memory usage
free -h

# Disk I/O
iostat -x 1

# Process-specific
ps aux | grep python
```

### 2. Optimize Configuration

Edit `.env`:
```bash
# Reduce population if RAM is tight
POPULATION_SIZE=2  # For 4GB model

# Lower temperature for determinism
TEMPERATURE=0.7

# Reduce max tokens
MAX_TOKENS=300

# Disable debug logging
LOG_LEVEL=WARNING
```

### 3. Reduce SD Card Wear

```bash
# Move ChromaDB to tmpfs (volatile, lost on reboot)
CHROMA_PERSIST_DIR=/tmp/chroma_db

# Or use USB drive
sudo mkdir -p /mnt/usb/chroma_db
CHROMA_PERSIST_DIR=/mnt/usb/chroma_db
```

---

## Testing

### 1. Health Check

```bash
curl http://localhost:5000/
```

Expected:
```json
{
  "status": "online",
  "project": "The Hive",
  "population_size": 3
}
```

### 2. List Agents

```bash
curl http://localhost:5000/api/agents
```

### 3. Trigger Evolution

```bash
curl -X POST http://localhost:5000/api/evolve
```

### 4. Monitor Logs

```bash
tail -f /tmp/hive_logs/hive.log
```

---

## Troubleshooting

### Issue: "Out of Memory"

**Solution:**
1. Reduce `POPULATION_SIZE` to 2
2. Enable swap (see setup above)
3. Close other services: `sudo systemctl stop bluetooth`

### Issue: "Groq API timeout"

**Solution:**
1. Check internet: `ping 8.8.8.8`
2. Verify API key: `echo $GROQ_API_KEY`
3. Test manually: `curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`

### Issue: "ChromaDB fails to start"

**Solution:**
```bash
# Remove corrupted DB
rm -rf data/chroma_db/*

# Restart
systemctl restart hive.service
```

### Issue: "High SD card I/O"

**Solution:**
1. Move logs to tmpfs (see setup)
2. Reduce logging: `LOG_LEVEL=ERROR`
3. Use USB drive for persistent data

---

## Cost Analysis (Raspi 4 8GB)

| Component | Cost |
|-----------|------|
| **Hardware** | |
| Raspberry Pi 4 8GB | $75 (one-time) |
| MicroSD 64GB | $15 (one-time) |
| Power supply | $10 (one-time) |
| Case + cooling | $10 (one-time) |
| **Running Costs** | |
| Electricity (~5W) | $0.50/month |
| Groq API (3 agents) | $8-15/month |
| **Total Monthly** | **$8.50-15.50** |

### ROI Calculation

**Sistema Autónomo (3 agentes):**
- Expected revenue: Variable según nichos descubiertos
- Costs: $15/month
- **Net profit: Depende de estrategia evolutiva**
- **ROI: Variable según autonomía**

**Break-even: Depende de descubrimientos autónomos**

---

## Remote Access

### 1. SSH Tunnel

```bash
# From your laptop
ssh -L 5000:localhost:5000 pi@raspberrypi.local

# Access: http://localhost:5000
```

### 2. Tailscale (Recommended)

```bash
# On Raspi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Access from anywhere: http://100.x.x.x:5000
```

### 3. Ngrok (Public URL)

```bash
# Install
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Start tunnel
ngrok http 5000

# Access: https://random-id.ngrok.io
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Backup .env and genomes
tar -czf backup_$(date +%Y%m%d).tar.gz .env data/genomes/

# Copy to cloud
scp backup_*.tar.gz user@server:/backups/
```

### Full SD Card Backup

```bash
# On laptop (with SD card reader)
sudo dd if=/dev/sdX of=raspi_backup.img bs=4M status=progress

# Restore
sudo dd if=raspi_backup.img of=/dev/sdX bs=4M status=progress
```

---

## Security Hardening

```bash
# Change default password
passwd

# Disable unused services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Firewall
sudo apt install ufw -y
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Flask (only if exposing externally)
sudo ufw enable

# Auto-updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Next Steps

1. **Test with minimal config** (3 agents)
2. **Monitor for 24 hours** (check memory, CPU)
3. **Scale up if stable** (add more agents)
4. **Implement revenue tracking** (connect to WordPress/Medium)
5. **Set up automated backups**

For questions, check logs or open an issue on GitHub.

**Good luck! 🍓🐝**
