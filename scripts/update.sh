#/bin/bash
#
# Volume Be Gone - Update Script
#

echo "Updating Volume Be Gone..."

# Pull latest changes
git pull

# Update dependencies
sudo pip3 install -r requirements.txt --upgrade

# Copy updated files
sudo cp src/volumeBeGone.py /home/pi/volumebegone/
sudo cp -r resources/images /home/pi/volumebegone/

# Restart service if running
if systemctl is-active --quiet volumebegone; then
    echo "Restarting service..."
    sudo systemctl restart volumebegone
fi

echo "Update completed"
