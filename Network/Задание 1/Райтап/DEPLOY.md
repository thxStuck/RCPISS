# CTF — Open VPN: Admin Deployment Guide

This document is for the **CTF organizer**. It covers everything needed to deploy,
configure, and maintain the "Open VPN" challenge on a fresh Linux server.

---

## Requirements

| Component | Minimum |
|-----------|---------|
| OS | Ubuntu 22.04 / Debian 12 (64-bit) |
| CPU | 1 vCPU |
| RAM | 1 GB |
| Disk | 5 GB free |
| Ports | **1194/UDP** (OpenVPN), **8080/TCP** (player portal) |
| Software | Docker ≥ 24, Docker Compose v2 (`docker compose`) |

> The challenge **cannot** run in an unprivileged container environment (LXC without
> `NET_ADMIN`, managed Kubernetes, etc.) because OpenVPN needs `/dev/net/tun` and
> the ability to create tap/bridge interfaces.

---

## Directory layout

```
ctf-vpn/                    ← project root (upload this to the server)
├── docker-compose.yml
├── .env                    ← secrets & tunables (edit before first run)
├── openvpn/
│   ├── Dockerfile
│   ├── server.conf
│   ├── entrypoint.sh
│   └── ccd/               ← per-player IP assignments (auto-managed by portal)
├── victim/
│   ├── Dockerfile
│   └── victim.py
├── flagserver/
│   ├── Dockerfile
│   └── server.py
├── portal/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       ├── index.html
│       └── admin.html
├── scripts/
│   ├── gen-pki.sh          ← one-time PKI bootstrap
│   ├── gen-client.sh       ← generate a single player config manually
│   └── add-player.sh       ← interactive helper
└── data/                   ← generated at runtime (PKI keys, player ovpn files)
```

---

## Step 1 — Upload the project

Copy the entire `ctf-vpn/` folder to the server (replace `YOUR_SERVER` with the IP):

```bash
scp -r ctf-vpn/ root@YOUR_SERVER:/opt/ctf-vpn
```

Or clone/unzip directly on the server.

---

## Step 2 — Install Docker

```bash
# On Ubuntu 22.04 / 24.04
curl -fsSL https://get.docker.com | sh

# Install Compose v2 plugin
apt-get install -y docker-compose-v2

# Verify
docker --version
docker compose version
```

---

## Step 3 — Configure `.env`

Edit `/opt/ctf-vpn/.env`:

```bash
# The flag players need to find
CTF_FLAG=CTF{passive_sniff_on_bridge_wins_42}

# How often (seconds) the victim broadcasts the flag
SEND_INTERVAL=30

# Public IP or hostname of this server
VPN_SERVER_ADDR=159.194.233.5

# Admin token to view the player list at /admin?token=...
ADMIN_TOKEN=ctf_admin_2026
```

> **Change `CTF_FLAG` and `ADMIN_TOKEN` before going live.**

---

## Step 4 — Generate the PKI (first time only)

The PKI (CA certificate, server cert, DH params, TLS auth key) must be generated
**once** before starting the containers. Run this on the server:

```bash
cd /opt/ctf-vpn

# Install easy-rsa on the host (only needed for this step)
apt-get install -y easy-rsa

# Bootstrap PKI
export EASYRSA=/usr/share/easy-rsa/easyrsa
export EASYRSA_PKI=/opt/ctf-vpn/data/pki
export EASYRSA_BATCH=1
export EASYRSA_KEY_SIZE=2048
export EASYRSA_CERT_EXPIRE=3650

$EASYRSA init-pki
EASYRSA_REQ_CN="CTF-CA" $EASYRSA build-ca nopass
$EASYRSA gen-dh
unset EASYRSA_REQ_CN
$EASYRSA build-server-full server nopass
openvpn --genkey secret $EASYRSA_PKI/ta.key
```

After this step `data/pki/` should contain:
```
ca.crt  dh.pem  issued/server.crt  private/server.key  ta.key
```

---

## Step 5 — Start all services

```bash
cd /opt/ctf-vpn
docker compose up -d
```

Check that all four containers are running:

```bash
docker compose ps
```

Expected output:
```
NAME             STATUS
ctf_openvpn      Up
ctf_victim       Up
ctf_flagserver   Up
ctf_portal       Up
```

---

## Step 6 — Verify the setup

### OpenVPN is listening on 1194/UDP

```bash
ss -lunp | grep 1194
```

### Player portal is reachable

```bash
curl -s http://localhost:8080 | grep -o '<title>[^<]*</title>'
```

### Victim is broadcasting

```bash
docker logs ctf_victim 2>&1 | tail -5
```

Expected:
```
00:01:23 [victim] Broadcast flag -> 10.8.0.255:80
```

### Quick functional test — download a config and sniff the flag

```bash
# Install openvpn + tcpdump locally
apt-get install -y openvpn tcpdump

# Register a test player
curl -s http://localhost:8080/register -d 'name=admin_test' -o /dev/null
# Go to http://YOUR_SERVER:8080, download admin_test.ovpn

# Connect
sudo openvpn --config admin_test.ovpn --daemon --log /tmp/vpn-test.log
sleep 10

# Sniff flag
sudo tcpdump -i tap0 -A 'udp and dst port 80' 2>/dev/null | grep -o 'CTF{[^}]*}'
# → CTF{passive_sniff_on_bridge_wins_42}

# Clean up
sudo pkill openvpn
```

---

## Operations

### View registered players (admin panel)

```
http://YOUR_SERVER:8080/admin?token=<ADMIN_TOKEN>
```

### View live logs

```bash
docker compose logs -f            # all services
docker compose logs -f openvpn    # just OpenVPN
docker compose logs -f victim     # just victim bot
```

### Restart a single service

```bash
docker compose restart victim
```

### Restart everything

```bash
docker compose down && docker compose up -d
```

### Change the flag without rebuilding

Edit `.env`, then:

```bash
docker compose up -d --force-recreate victim
```

---

## Firewall rules

Make sure the following ports are open:

| Port | Protocol | Purpose |
|------|----------|---------|
| 1194 | UDP | OpenVPN (players connect here) |
| 8080 | TCP | Player portal (config download) |
| 22   | TCP | SSH (admin access) |

Example with `ufw`:

```bash
ufw allow 1194/udp
ufw allow 8080/tcp
ufw allow 22/tcp
ufw enable
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ctf_openvpn` keeps restarting | PKI not generated | Run Step 4 |
| Players connect but get no flag | Victim not running | `docker compose restart victim` |
| Portal returns 502 | Portal crashed | `docker compose restart portal` |
| Port 8080 not reachable | Firewall blocking | `ufw allow 8080/tcp` |
| `br-ctfvpn` device not found | Docker network not created | `docker compose down && docker compose up -d` |

---

## Architecture summary

```
Internet
   │ UDP 1194
   ▼
[HOST: br-ctfvpn bridge, ageing_time=0 (hub mode)]
   ├── veth ── ctf_victim       10.8.0.2    (broadcasts flag every 30s)
   ├── veth ── ctf_flagserver   10.8.0.254  (receives & logs)
   ├── veth ── ctf_portal       (web UI, any IP)
   └── tap0 ── ctf_openvpn      (OpenVPN reads/writes Ethernet frames)
                   │
         VPN tunnel (AES-256-GCM)
                   │
            Player's tap0
            10.8.0.10–200
         (sees all broadcast frames)
```

---

## Files NOT to share with players

- `data/pki/` — CA private key, server cert/key
- `.env` — flag value, admin token
- `Writeup/` — solution

Files that **are** shared with players (via portal only):

- Individual `.ovpn` configs (generated on registration)
- `Tasks/README.md` — challenge description
