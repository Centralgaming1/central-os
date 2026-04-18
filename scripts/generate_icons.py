import os

output_dir = os.path.expanduser("~/.local/share/icons/central/48x48/apps")
os.makedirs(output_dir, exist_ok=True)

icons = {
    "files": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <rect x="8" y="6" width="22" height="28" rx="2" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <path d="M30 6l8 8h-8z" fill="#e8e8e8"/>
  <line x1="13" y1="18" x2="27" y2="18" stroke="#888" stroke-width="2" stroke-linecap="round"/>
  <line x1="13" y1="23" x2="27" y2="23" stroke="#888" stroke-width="2" stroke-linecap="round"/>
  <line x1="13" y1="28" x2="21" y2="28" stroke="#888" stroke-width="2" stroke-linecap="round"/>
  <rect x="14" y="32" width="22" height="12" rx="2" fill="#1a1a1a" stroke="#e8e8e8" stroke-width="2"/>
  <line x1="19" y1="38" x2="31" y2="38" stroke="#888" stroke-width="1.5" stroke-linecap="round"/>
</svg>''',

    "settings": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="5" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <path d="M24 6v4M24 38v4M6 24h4M38 24h4M10.1 10.1l2.8 2.8M35.1 35.1l2.8 2.8M10.1 37.9l2.8-2.8M35.1 12.9l2.8-2.8" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="24" cy="24" r="10" fill="none" stroke="#888" stroke-width="2" stroke-dasharray="4 3"/>
</svg>''',

    "terminal": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <rect x="4" y="8" width="40" height="32" rx="3" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <line x1="4" y1="16" x2="44" y2="16" stroke="#888" stroke-width="1.5"/>
  <path d="M11 24l6 4-6 4" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="21" y1="32" x2="32" y2="32" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    "browser": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="18" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <line x1="6" y1="24" x2="42" y2="24" stroke="#888" stroke-width="1.5"/>
  <path d="M24 6 C18 12 18 36 24 42" fill="none" stroke="#888" stroke-width="1.5"/>
  <path d="M24 6 C30 12 30 36 24 42" fill="none" stroke="#888" stroke-width="1.5"/>
  <line x1="9" y1="16" x2="39" y2="16" stroke="#888" stroke-width="1" stroke-dasharray="2 2"/>
  <line x1="9" y1="32" x2="39" y2="32" stroke="#888" stroke-width="1" stroke-dasharray="2 2"/>
</svg>''',

    "music": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="16" cy="34" r="6" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <circle cx="34" cy="30" r="6" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <line x1="22" y1="34" x2="22" y2="12" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="40" y1="30" x2="40" y2="8" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="22" y1="12" x2="40" y2="8" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
</svg>''',

    "calendar": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <rect x="6" y="10" width="36" height="32" rx="3" fill="none" stroke="#e8e8e8" stroke-width="2.5"/>
  <line x1="6" y1="20" x2="42" y2="20" stroke="#888" stroke-width="1.5"/>
  <line x1="16" y1="6" x2="16" y2="14" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="32" y1="6" x2="32" y2="14" stroke="#e8e8e8" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="16" cy="28" r="2" fill="#e8e8e8"/>
  <circle cx="24" cy="28" r="2" fill="#e8e8e8"/>
  <circle cx="32" cy="28" r="2" fill="#e8e8e8"/>
  <circle cx="16" cy="36" r="2" fill="#e8e8e8"/>
  <circle cx="24" cy="36" r="2" fill="#e8e8e8"/>
</svg>''',

    "folder": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <path d="M4 14 C4 12 5 11 7 11 L18 11 L22 15 L41 15 C43 15 44 16 44 18 L44 36 C44 38 43 39 41 39 L7 39 C5 39 4 38 4 36 Z" fill="none" stroke="#e8e8e8" stroke-width="2.5" stroke-linejoin="round"/>
</svg>''',

    "system-file-manager": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <path d="M4 14 C4 12 5 11 7 11 L18 11 L22 15 L41 15 C43 15 44 16 44 18 L44 36 C44 38 43 39 41 39 L7 39 C5 39 4 38 4 36 Z" fill="none" stroke="#e8e8e8" stroke-width="2.5" stroke-linejoin="round"/>
</svg>''',
}

for name, svg in icons.items():
    path = os.path.join(output_dir, f"{name}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print(f"Created {name}.svg")

index_dir = os.path.expanduser("~/.local/share/icons/central")
with open(os.path.join(index_dir, "index.theme"), "w") as f:
    f.write("""[Icon Theme]
Name=Central
Comment=Central OS Icon Theme
Inherits=hicolor
Directories=48x48/apps

[48x48/apps]
Size=48
Context=Applications
Type=Fixed
""")

print("Icon pack created at ~/.local/share/icons/central")
print("Go to System Settings > Appearance > Icons and select Central")
