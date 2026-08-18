#!/usr/bin/env bash
# finish-setup.sh — Run this in YOUR OWN terminal to complete icloud-linux setup.
# This script requires a D-Bus session (i.e., a normal desktop terminal).

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo " icloud-linux — Final Setup Steps"
echo "======================================"
echo ""

echo "Step 1: Enter your Apple ID credentials"
bash "$REPO_DIR/icloudctl" configure
echo ""

echo "Step 2: Authenticate (2FA — you'll get a code on your Apple device)"
bash "$REPO_DIR/icloudctl" auth
echo ""

echo "Step 3: Install KDE Plasma integration"
bash "$REPO_DIR/icloudctl" install-ui
echo ""

echo "Step 4: Start the iCloud Drive service"
bash "$REPO_DIR/icloudctl" start
echo ""

echo "Step 5: Check the Plasma backend"
bash "$REPO_DIR/icloudctl" ui-status
echo ""

echo "======================================"
echo " Setup complete"
echo "======================================"
echo ""
echo " iCloud Drive will be mounted at:"
echo "   ~/iCloud"
echo ""
echo " KDE Plasma integration:"
echo "   - Plasma widget: org.icloudlinux.plasma"
echo "   - Backend service: icloud-linux-ui.service"
echo ""
echo " Useful commands:"
echo ""
echo "   Check iCloud service:"
echo "     ./icloudctl status"
echo ""
echo "   Follow iCloud service logs:"
echo "     ./icloudctl logs"
echo ""
echo "   Check Plasma backend:"
echo "     ./icloudctl ui-status"
echo ""
echo "   Follow Plasma backend logs:"
echo "     ./icloudctl ui-logs"
echo ""
echo "   Trigger an on-demand sync:"
echo "     ./icloudctl sync"
echo ""
echo "   Clear the local cache:"
echo "     ./icloudctl clear-cache"
echo ""
echo " To check how much local disk the cache is using:"
echo "   du -sh ~/.cache/icloud-linux/"
echo ""
echo "======================================"