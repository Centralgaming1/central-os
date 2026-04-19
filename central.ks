repo --name=fedora --mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=fedora-41&arch=x86_64
repo --name=updates --mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=updates-released-f41&arch=x86_64

lang en_GB.UTF-8
keyboard gb
timezone Europe/London --utc
selinux --enforcing
firewall --enabled --service=ssh
bootloader --location=mbr
clearpart --none
autopart --type=plain

user --name=ashton --password=$6$xPC5YZ20w77UopQj$TLKub6LEqHJYoH.co7I7GXOePqOko1.8DVc2jxAsgp/fmHN1WgMFoizQYsjYoCSlg.TVD8j.2RA7FpKH1.Ard1 --iscrypted --groups=wheel
rootpw --lock

%packages
@base-x
@kde-desktop
firefox
git
vim
sddm
python3-pillow
python3-pyqt6
dracut-live
curl
%end

%post
# Install fonts
mkdir -p /usr/local/share/fonts
curl -L "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf" -o /usr/local/share/fonts/SpaceGrotesk.ttf
fc-cache -fv

# Set up SDDM theme
mkdir -p /usr/share/sddm/themes/central
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/themes/sddm/Main.qml" -o /usr/share/sddm/themes/central/Main.qml
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/themes/sddm/theme.conf" -o /usr/share/sddm/themes/central/theme.conf

# Set up colour scheme
mkdir -p /usr/share/color-schemes
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/themes/Central.colors" -o /usr/share/color-schemes/Central.colors

# Generate wallpaper and SDDM images
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/generate_central_images.py" -o /tmp/generate_central_images.py
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/generate_wallpaper.py" -o /tmp/generate_wallpaper.py
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/generate_icons.py" -o /tmp/generate_icons.py

python3 /tmp/generate_central_images.py
python3 /tmp/generate_wallpaper.py

# Copy wallpaper to system location
mkdir -p /usr/share/wallpapers/central
cp /root/central_wallpaper.png /usr/share/wallpapers/central/central_wallpaper.png

# Generate icons
python3 /tmp/generate_icons.py

# Install Central Files
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/central-files.py" -o /usr/local/bin/central-files
chmod +x /usr/local/bin/central-files
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/central-files.desktop" -o /usr/share/applications/central-files.desktop

# Install Central Terminal
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/central-terminal.py" -o /usr/local/bin/central-terminal
chmod +x /usr/local/bin/central-terminal
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/central-terminal.desktop" -o /usr/share/applications/central-terminal.desktop

# Install Central Store
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/scripts/central-store.py" -o /usr/local/bin/central-store
chmod +x /usr/local/bin/central-store
curl -L "https://raw.githubusercontent.com/Centralgaming1/central-os/main/central-store.desktop" -o /usr/share/applications/central-store.desktop

# SDDM config
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/central.conf << 'EOF'
[Theme]
Current=central
EOF

systemctl enable sddm
%end

reboot
