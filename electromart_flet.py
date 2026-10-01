"""
ElectroMart — Electronics, Elevated.   (Python / Flet port)

A desktop (or web) marketplace app: buyers and sellers, a 100-item catalogue,
marketplace price comparison, cart + checkout, time-based order tracking,
delivery feedback and returns, seller listings + analytics, an admin console,
a support chat, and the project-documentation pages.

Run it
------
    pip install "flet>=1.0"
    python electromart_flet.py            # native desktop window
    flet run --web electromart_flet.py    # or in the browser

Data
----
Everything is stored in a JSON file next to this script (electromart_db.json),
standing in for the browser localStorage of the original HTML version.
Delete that file to reset the app. Set ELECTROMART_DB to use another path.

Demo admin login:  admin@electromart.demo  /  Admin#2026
"""

import asyncio
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import string
import time
from pathlib import Path

import flet as ft
import flet.canvas as cv

# ============================================================================
# Visual identity — indigo dusk, brass ironwork, awning rouge
# ============================================================================
PAPER = "#F7F2E6"
CARD = "#FFFFFF"
INK = "#1C2541"
INK_DIM = "#5C6584"
GOLD = "#B8923D"
GOLD_DIM = "#8F701F"
WINE = "#8C3B4A"
WINE_DIM = "#6E2E3A"
WHITE = "#FFFFFF"


def alpha(color, a):
    return ft.Colors.with_opacity(a, color)


LINE = alpha(INK, 0.15)
LINE_SOFT = alpha(INK, 0.08)

# System fonts (no network needed). Falls back gracefully on every OS.
DISPLAY = "Georgia"
MONO = "Consolas"
MONO_FALLBACK = ["Menlo", "Courier New", "monospace"]
DISPLAY_FALLBACK = ["Times New Roman", "serif"]

# ============================================================================
# Static data (generated from the original HTML: catalogue + documentation)
# ============================================================================
CATALOG = [
    {"id": "p1", "sku": "EMP-LT-01", "category": "Laptops", "icon": "💻", "name": "Aster 14 UltraBook", "price": 1085000, "stock": 6, "description": "A 14\" magnesium-alloy ultrabook built for travel — all-day battery, fanless in light use, and a display bright enough for Lagos afternoons.", "specs": {"Display": "14\" 2.8K OLED", "CPU": "8-core, 3.8GHz", "RAM": "16GB", "Storage": "512GB SSD", "Battery": "Up to 18h"}},
    {"id": "p2", "sku": "EMP-LT-02", "category": "Laptops", "icon": "💻", "name": "Forge 15 Creator", "price": 1640000, "stock": 3, "description": "A discrete-GPU workstation for editing, rendering and heavier creative work, with a colour-accurate panel out of the box.", "specs": {"Display": "15.6\" QHD 165Hz", "CPU": "8-core, 4.2GHz", "GPU": "8GB dedicated", "RAM": "32GB", "Storage": "1TB SSD"}},
    {"id": "p3", "sku": "EMP-LT-03", "category": "Laptops", "icon": "💻", "name": "Voyage Air 13", "price": 695000, "stock": 11, "description": "The lightest laptop in the lineup — 1.1kg, silent, and built for writers, students and anyone who lives out of a bag.", "specs": {"Display": "13.3\" FHD", "CPU": "6-core, 3.2GHz", "RAM": "8GB", "Storage": "256GB SSD", "Weight": "1.1kg"}},
    {"id": "p4", "sku": "EMP-PH-01", "category": "Smartphones", "icon": "📱", "name": "Lumen X7", "price": 820000, "stock": 14, "description": "Flagship cameras, a bright always-on display, and two full days of typical use on a single charge.", "specs": {"Display": "6.7\" AMOLED 120Hz", "Storage": "256GB", "RAM": "12GB", "Camera": "50MP triple", "Battery": "5000mAh"}},
    {"id": "p5", "sku": "EMP-PH-02", "category": "Smartphones", "icon": "📱", "name": "Lumen X7 mini", "price": 640000, "stock": 9, "description": "Same generation, smaller body — for anyone who wants flagship performance without a phablet in their pocket.", "specs": {"Display": "6.1\" AMOLED 120Hz", "Storage": "128GB", "RAM": "8GB", "Camera": "48MP dual", "Battery": "4200mAh"}},
    {"id": "p6", "sku": "EMP-PH-03", "category": "Smartphones", "icon": "📱", "name": "Fielder Rugged 5G", "price": 410000, "stock": 20, "description": "IP68-rated and drop-tested to 1.8m — built for construction sites, farms and anywhere a normal phone wouldn’t survive.", "specs": {"Display": "6.3\" LCD", "Storage": "128GB", "RAM": "6GB", "Rating": "IP68 / MIL-STD-810H", "Battery": "6000mAh"}},
    {"id": "p7", "sku": "EMP-AU-01", "category": "Audio", "icon": "🎧", "name": "Halo ANC Headphones", "price": 265000, "stock": 17, "description": "Over-ear noise cancelling headphones tuned for long commutes and open-plan offices, with 40 hours of playback.", "specs": {"Type": "Over-ear, ANC", "Battery": "40h", "Bluetooth": "5.3", "Weight": "250g"}},
    {"id": "p8", "sku": "EMP-AU-02", "category": "Audio", "icon": "🎧", "name": "Pebble True Wireless", "price": 98000, "stock": 26, "description": "Compact true-wireless earbuds with a stable fit for workouts and a case that tops up two extra full charges.", "specs": {"Type": "In-ear, ANC", "Battery": "6h + 24h case", "Bluetooth": "5.3", "Water rating": "IPX4"}},
    {"id": "p9", "sku": "EMP-AU-03", "category": "Audio", "icon": "🔊", "name": "Boombox Go Speaker", "price": 145000, "stock": 2, "description": "A rugged party-in-a-bag speaker with genuinely loud, bass-forward sound and 20 hours off one charge.", "specs": {"Output": "40W", "Battery": "20h", "Water rating": "IPX7", "Bluetooth": "5.2"}},
    {"id": "p10", "sku": "EMP-CM-01", "category": "Cameras", "icon": "📷", "name": "Frame One Mirrorless", "price": 1290000, "stock": 4, "description": "An APS-C mirrorless body for anyone moving up from phone photography — fast autofocus, and a kit lens included.", "specs": {"Sensor": "26MP APS-C", "Video": "4K 60fps", "Lens": "18-55mm kit", "Stabilisation": "5-axis IBIS"}},
    {"id": "p11", "sku": "EMP-CM-02", "category": "Cameras", "icon": "📹", "name": "Trailcam Action 4K", "price": 225000, "stock": 15, "description": "Waterproof to 10m without a housing — built for bikes, boats, and anywhere a regular camera can’t go.", "specs": {"Video": "4K 60fps", "Waterproof": "10m", "Battery": "2h continuous", "Mounts": "Standard action-cam"}},
    {"id": "p12", "sku": "EMP-GM-01", "category": "Gaming", "icon": "🎮", "name": "Ranger Pro Controller", "price": 78000, "stock": 22, "description": "A wireless controller with swappable stick modules and haptic triggers, compatible with PC and most consoles.", "specs": {"Connection": "Bluetooth + 2.4GHz dongle", "Battery": "30h", "Compatibility": "PC, most consoles"}},
    {"id": "p13", "sku": "EMP-GM-02", "category": "Gaming", "icon": "🖥️", "name": "Arc 27 Gaming Monitor", "price": 485000, "stock": 7, "description": "A 27\" 165Hz panel with a fast response time, tuned for competitive play without ghosting.", "specs": {"Size": "27\"", "Resolution": "2560x1440", "Refresh": "165Hz", "Panel": "IPS"}},
    {"id": "p14", "sku": "EMP-AC-01", "category": "Accessories", "icon": "🔌", "name": "PowerCube 100W GaN Charger", "price": 52000, "stock": 31, "description": "A pocket-sized four-port charger that can top up a laptop and two phones at once without melting your bag.", "specs": {"Output": "100W max", "Ports": "2x USB-C, 2x USB-A", "Tech": "GaN"}},
    {"id": "p15", "sku": "EMP-AC-02", "category": "Accessories", "icon": "🖱️", "name": "Glide Wireless Mouse", "price": 34000, "stock": 0, "description": "A quiet-click wireless mouse with a 6-month battery life and a scroll wheel that free-spins on demand.", "specs": {"Connection": "Bluetooth + 2.4GHz", "Battery": "6 months (AA)", "DPI": "up to 4000"}},
    {"id": "p16", "sku": "EMP-AC-03", "category": "Accessories", "icon": "🎒", "name": "Transit 20L Laptop Backpack", "price": 61000, "stock": 18, "description": "A weatherproof daily-carry bag with a padded 16\" laptop sleeve and a luggage strap for travel days.", "specs": {"Capacity": "20L", "Laptop sleeve": "Up to 16\"", "Material": "Water-resistant ripstop"}},
    {"id": "p17", "sku": "EMP-TB-01", "category": "Tablets", "icon": "📲", "name": "Slate 11 Tablet", "price": 545000, "stock": 9, "description": "An 11\" tablet fast enough for real productivity — split-screen apps, stylus support, and a display sharp enough for design work on the go.", "specs": {"Display": "11\" 2K LCD 120Hz", "CPU": "8-core", "RAM": "8GB", "Storage": "256GB", "Stylus": "Sold separately"}},
    {"id": "p18", "sku": "EMP-TB-02", "category": "Tablets", "icon": "📲", "name": "Slate 11 Keyboard Case", "price": 87000, "stock": 16, "description": "Turns the Slate 11 into a laptop-alike — magnetic attach, backlit keys, and a kickstand hinge that holds any angle.", "specs": {"Compatibility": "Slate 11 Tablet", "Keys": "Backlit, full-size", "Trackpad": "Yes"}},
    {"id": "p19", "sku": "EMP-TB-03", "category": "Accessories", "icon": "✏️", "name": "Slate Stylus Pen", "price": 56000, "stock": 24, "description": "A pressure-sensitive stylus for the Slate 11 with near-zero lag, magnetic charging, and tilt shading for sketching.", "specs": {"Compatibility": "Slate 11 Tablet", "Charging": "Magnetic, wireless", "Battery": "Up to 2 weeks"}},
    {"id": "p20", "sku": "EMP-WR-01", "category": "Wearables", "icon": "⌚", "name": "Pulse Fit Watch", "price": 265000, "stock": 13, "description": "A fitness-first smartwatch with round-the-clock heart rate, sleep tracking, and five days of battery between charges.", "specs": {"Display": "1.4\" AMOLED", "Battery": "5 days typical", "Water rating": "5ATM", "Sensors": "HR, SpO2, GPS"}},
    {"id": "p21", "sku": "EMP-WR-02", "category": "Accessories", "icon": "⌚", "name": "Pulse Fit Extra Strap", "price": 19000, "stock": 40, "description": "A spare silicone strap for the Pulse Fit Watch — quick-release pins mean no tools needed to swap it.", "specs": {"Compatibility": "Pulse Fit Watch", "Material": "Silicone", "Sizes": "S/M and M/L included"}},
    {"id": "p22", "sku": "EMP-WR-03", "category": "Accessories", "icon": "🔌", "name": "Pulse Fit Charging Dock", "price": 22000, "stock": 21, "description": "A magnetic charging puck for the Pulse Fit Watch that doubles as a bedside stand overnight.", "specs": {"Compatibility": "Pulse Fit Watch", "Cable": "USB-C, 1m included"}},
    {"id": "p23", "sku": "EMP-TV-01", "category": "TV & Home", "icon": "📺", "name": "Vista 55\" 4K Smart TV", "price": 1350000, "stock": 5, "description": "A 55\" 4K HDR panel with built-in streaming apps and three HDMI 2.1 ports for next-gen consoles.", "specs": {"Size": "55\"", "Resolution": "4K HDR", "Refresh": "120Hz", "HDMI": "3x HDMI 2.1"}},
    {"id": "p24", "sku": "EMP-TV-02", "category": "TV & Home", "icon": "🔊", "name": "Vista Soundbar 2.1", "price": 225000, "stock": 10, "description": "A wireless soundbar and subwoofer pair built to match the Vista TV, with a dedicated movie-dialogue mode.", "specs": {"Channels": "2.1", "Subwoofer": "Wireless", "Inputs": "HDMI ARC, optical, Bluetooth"}},
    {"id": "p25", "sku": "EMP-TV-03", "category": "Accessories", "icon": "📺", "name": "Tilt Wall Mount 32–65\"", "price": 38000, "stock": 27, "description": "A tilting wall bracket rated for TVs up to 65\", with cable channels built into the arm.", "specs": {"Compatibility": "32\"–65\" TVs", "Tilt": "-5° to +15°", "VESA": "up to 400x400"}},
    {"id": "p26", "sku": "EMP-SH-01", "category": "Smart Home", "icon": "🔈", "name": "Nimbus Smart Speaker", "price": 135000, "stock": 14, "description": "A voice-controlled speaker that doubles as a smart home hub — pairs with the Nimbus Smart Plugs out of the box.", "specs": {"Voice assistant": "Built-in", "Hub": "Zigbee + Wi-Fi", "Audio": "Full-range driver + tweeter"}},
    {"id": "p27", "sku": "EMP-SH-02", "category": "Accessories", "icon": "🔌", "name": "Nimbus Smart Plug (2-pack)", "price": 31000, "stock": 0, "description": "Wi-Fi smart plugs that work with the Nimbus Smart Speaker or standalone through the app — schedule anything with a wall outlet.", "specs": {"Compatibility": "Nimbus Smart Speaker or standalone", "Max load": "2300W", "Pack size": "2"}},
    {"id": "p28", "sku": "EMP-SH-03", "category": "Smart Home", "icon": "🔔", "name": "Aperture Video Doorbell", "price": 118000, "stock": 12, "description": "A battery or wired video doorbell with night vision and package-detection alerts sent straight to your phone.", "specs": {"Video": "1080p HDR", "Power": "Battery or wired", "Storage": "Local, no subscription required"}},
    {"id": "p29", "sku": "EMP-NW-01", "category": "Networking", "icon": "📶", "name": "Meshway 3-Pack Wi-Fi 6 Router", "price": 195000, "stock": 8, "description": "Whole-home mesh Wi-Fi 6 covering up to 550m² across three nodes, set up entirely from a phone app.", "specs": {"Standard": "Wi-Fi 6", "Coverage": "Up to 550m²", "Nodes": "3", "Ports": "2x Gigabit per node"}},
    {"id": "p30", "sku": "EMP-NW-02", "category": "Accessories", "icon": "🔌", "name": "Ethernet Cable 10m (Cat 6)", "price": 9500, "stock": 60, "description": "A 10-metre Cat 6 cable for running a wired backhaul between mesh nodes or to a games console.", "specs": {"Category": "Cat 6", "Length": "10m", "Shielding": "Unshielded (UTP)"}},
    {"id": "p31", "sku": "EMP-DR-01", "category": "Drones", "icon": "🚁", "name": "Skyframe Mini Drone", "price": 385000, "stock": 6, "description": "A sub-250g drone with a stabilised 4K camera and 30 minutes of flight time — light enough to skip some registration rules.", "specs": {"Weight": "249g", "Camera": "4K, 3-axis gimbal", "Flight time": "30 min", "Range": "10km"}},
    {"id": "p32", "sku": "EMP-DR-02", "category": "Accessories", "icon": "🔋", "name": "Skyframe Spare Battery", "price": 62000, "stock": 19, "description": "A drop-in spare battery for the Skyframe Mini Drone — keep one charging while the other flies.", "specs": {"Compatibility": "Skyframe Mini Drone", "Flight time added": "~30 min", "Charge time": "55 min"}},
    {"id": "p33", "sku": "EMP-DR-03", "category": "Accessories", "icon": "🎒", "name": "Skyframe Carry Case", "price": 29000, "stock": 23, "description": "A hard-shell case shaped for the Skyframe drone, its controller, and two spare batteries.", "specs": {"Compatibility": "Skyframe Mini Drone", "Capacity": "Drone + controller + 2 batteries", "Shell": "EVA hard-shell"}},
    {"id": "p34", "sku": "EMP-PR-01", "category": "Printers", "icon": "🖨️", "name": "InkFlow Home Printer", "price": 112000, "stock": 11, "description": "A compact wireless inkjet with refillable tanks, built to keep per-page cost low for everyday home printing.", "specs": {"Type": "Refillable-tank inkjet", "Connectivity": "Wi-Fi, USB", "Functions": "Print, scan, copy"}},
    {"id": "p35", "sku": "EMP-PR-02", "category": "Accessories", "icon": "🖨️", "name": "InkFlow Ink Refill Kit", "price": 16000, "stock": 34, "description": "A four-colour refill kit sized for the InkFlow Home Printer’s tanks, good for roughly 6,000 pages.", "specs": {"Compatibility": "InkFlow Home Printer", "Colours": "4 (CMYK)", "Page yield": "~6,000 pages"}},
    {"id": "p36", "sku": "EMP-AC-04", "category": "Accessories", "icon": "🔋", "name": "PowerBank 20000mAh", "price": 44000, "stock": 28, "description": "A slim 20,000mAh power bank with fast pass-through charging — enough for roughly three full phone charges.", "specs": {"Capacity": "20000mAh", "Output": "22.5W fast charge", "Ports": "1x USB-C, 1x USB-A"}},
    {"id": "p37", "sku": "EMP-AC-05", "category": "Accessories", "icon": "🛡️", "name": "Universal Screen Protector (2-pack)", "price": 8500, "stock": 45, "description": "Tempered-glass screen protectors with an oleophobic coating that resists fingerprints, fitted for most phone models.", "specs": {"Material": "Tempered glass", "Pack size": "2", "Coating": "Oleophobic (anti-fingerprint)"}},
    {"id": "p38", "sku": "EMP-AC-06", "category": "Accessories", "icon": "🔌", "name": "USB-C to HDMI Adapter", "price": 14500, "stock": 37, "description": "Mirrors a laptop or phone to any HDMI display or projector — handy for the Slate 11, Aster 14, or any USB-C phone.", "specs": {"Output": "HDMI, up to 4K@60Hz", "Compatibility": "Any USB-C device with DisplayPort Alt Mode"}},
    {"id": "p39", "sku": "EMP-LT-04", "category": "Laptops", "icon": "💻", "name": "Halcyon 16 Business", "price": 980000, "stock": 9, "description": "A matte-black 16\" business laptop with a spill-resistant keyboard and a fingerprint reader built into the power button.", "specs": {"Display": "16\" WQXGA", "CPU": "8-core, 3.6GHz", "RAM": "16GB", "Storage": "512GB SSD", "Security": "Fingerprint + TPM"}},
    {"id": "p40", "sku": "EMP-LT-05", "category": "Laptops", "icon": "💻", "name": "Nomad 2-in-1 Convertible", "price": 745000, "stock": 7, "description": "A 360-hinge convertible that folds flat into a tablet, with an active pen included for notes and sketches.", "specs": {"Display": "13.5\" 2K touch", "CPU": "6-core, 3.4GHz", "RAM": "16GB", "Storage": "512GB SSD", "Pen": "Included"}},
    {"id": "p41", "sku": "EMP-LT-06", "category": "Laptops", "icon": "💻", "name": "Ridge 17 Studio", "price": 1980000, "stock": 2, "description": "A 17\" content-creation laptop with a colour-calibrated panel and enough thermal headroom for sustained render jobs.", "specs": {"Display": "17\" 4K", "CPU": "10-core, 4.4GHz", "GPU": "12GB dedicated", "RAM": "32GB", "Storage": "2TB SSD"}},
    {"id": "p42", "sku": "EMP-PH-04", "category": "Smartphones", "icon": "📱", "name": "Lumen X7 Pro", "price": 1080000, "stock": 6, "description": "The top of the Lumen line — a periscope zoom lens, a titanium frame, and satellite SOS for off-grid emergencies.", "specs": {"Display": "6.8\" AMOLED 144Hz", "Storage": "512GB", "RAM": "16GB", "Camera": "50MP quad", "Battery": "5400mAh"}},
    {"id": "p43", "sku": "EMP-PH-05", "category": "Smartphones", "icon": "📱", "name": "Budget Wave 4G", "price": 225000, "stock": 31, "description": "An affordable everyday phone with a big battery and a display bright enough to read outdoors.", "specs": {"Display": "6.5\" HD+", "Storage": "64GB", "RAM": "4GB", "Camera": "13MP dual", "Battery": "5000mAh"}},
    {"id": "p44", "sku": "EMP-PH-06", "category": "Smartphones", "icon": "📱", "name": "Lumen Flip", "price": 890000, "stock": 8, "description": "A folding phone that closes to pocket-sized, with a cover screen for quick replies without opening it.", "specs": {"Display": "6.7\" foldable + 3.4\" cover", "Storage": "256GB", "RAM": "12GB", "Hinge rating": "300,000 folds"}},
    {"id": "p45", "sku": "EMP-AU-04", "category": "Audio", "icon": "🎙️", "name": "Broadcast USB Microphone", "price": 96000, "stock": 13, "description": "A cardioid USB condenser mic for streaming, voiceover and calls, with a built-in headphone jack for zero-latency monitoring.", "specs": {"Pattern": "Cardioid", "Connection": "USB-C", "Sample rate": "48kHz/24-bit", "Mount": "Desktop stand included"}},
    {"id": "p46", "sku": "EMP-AU-05", "category": "Audio", "icon": "🎧", "name": "Studio Reference Headphones", "price": 178000, "stock": 10, "description": "Wired over-ear monitors tuned flat for mixing, with a detachable cable and swappable earpads.", "specs": {"Type": "Over-ear, wired", "Impedance": "38 ohm", "Frequency range": "5Hz–40kHz", "Cable": "Detachable, 3m"}},
    {"id": "p47", "sku": "EMP-AU-06", "category": "Audio", "icon": "🔊", "name": "Bookshelf Speaker Pair", "price": 310000, "stock": 6, "description": "A powered bookshelf pair with a built-in amp — plug in a turntable, TV or phone and skip the separate receiver.", "specs": {"Power": "2x50W", "Inputs": "RCA, optical, Bluetooth", "Drivers": "5.25\" woofer + 1\" tweeter"}},
    {"id": "p48", "sku": "EMP-AU-07", "category": "Audio", "icon": "🎚️", "name": "2-Channel USB Audio Interface", "price": 86000, "stock": 14, "description": "A compact interface for recording vocals or instruments straight into a laptop, with phantom power for condenser mics.", "specs": {"Inputs": "2x XLR/TRS combo", "Phantom power": "48V", "Connection": "USB-C", "Monitoring": "Direct zero-latency"}},
    {"id": "p49", "sku": "EMP-CM-03", "category": "Cameras", "icon": "📷", "name": "Frame One Prime Lens 35mm", "price": 245000, "stock": 9, "description": "A fast prime lens for the Frame One system, ideal for low-light and portrait work with a smooth background blur.", "specs": {"Mount": "Frame One mount", "Aperture": "f/1.8", "Focal length": "35mm (APS-C)"}},
    {"id": "p50", "sku": "EMP-CM-04", "category": "Cameras", "icon": "📷", "name": "Pocket Vlog Camera", "price": 365000, "stock": 12, "description": "A palm-sized camera with a flip-out screen and built-in stabilisation, built for one-handed vlogging.", "specs": {"Sensor": "1\"-type", "Video": "4K 30fps", "Stabilisation": "Electronic + gimbal", "Screen": "Flip-out touch"}},
    {"id": "p51", "sku": "EMP-CM-05", "category": "Cameras", "icon": "📷", "name": "Studio Tripod 170cm", "price": 58000, "stock": 20, "description": "An aluminium tripod with a fluid head and quick-release plate, tall enough for standing shots without extending the legs fully.", "specs": {"Max height": "170cm", "Material": "Aluminium", "Head": "Fluid, quick-release plate", "Load capacity": "5kg"}},
    {"id": "p52", "sku": "EMP-GM-03", "category": "Gaming", "icon": "🎮", "name": "Mechanical Gaming Keyboard", "price": 96000, "stock": 18, "description": "A hot-swappable mechanical keyboard with per-key RGB and a detachable USB-C cable for travel.", "specs": {"Switches": "Hot-swappable mechanical", "Backlight": "Per-key RGB", "Connection": "USB-C, wired"}},
    {"id": "p53", "sku": "EMP-GM-04", "category": "Gaming", "icon": "🖱️", "name": "Precision Gaming Mouse", "price": 48000, "stock": 24, "description": "A lightweight gaming mouse with a high-accuracy sensor and side buttons that can be remapped per game profile.", "specs": {"Sensor": "26,000 DPI optical", "Weight": "62g", "Buttons": "6 programmable", "Connection": "Wired + 2.4GHz"}},
    {"id": "p54", "sku": "EMP-GM-05", "category": "Gaming", "icon": "🎧", "name": "Gaming Headset Surround", "price": 112000, "stock": 16, "description": "A closed-back gaming headset with virtual surround sound and a boom mic that flips up to mute.", "specs": {"Sound": "7.1 virtual surround", "Mic": "Flip-to-mute boom", "Connection": "USB / 3.5mm"}},
    {"id": "p55", "sku": "EMP-GM-06", "category": "Gaming", "icon": "🕹️", "name": "Arcade Fight Stick", "price": 135000, "stock": 5, "description": "A tournament-style fight stick with Sanwa-style parts, built for fighting-game players who want console-grade feel.", "specs": {"Buttons": "8 + start/select", "Stick": "Sanwa-style lever", "Compatibility": "PC, most consoles"}},
    {"id": "p56", "sku": "EMP-TB-04", "category": "Tablets", "icon": "📲", "name": "Slate 8 Mini Tablet", "price": 345000, "stock": 15, "description": "A pocketable 8\" tablet for reading, browsing and media, light enough to hold one-handed for hours.", "specs": {"Display": "8\" 2K LCD", "CPU": "6-core", "RAM": "6GB", "Storage": "128GB"}},
    {"id": "p57", "sku": "EMP-TB-05", "category": "Tablets", "icon": "📲", "name": "Slate 11 Pro", "price": 845000, "stock": 6, "description": "The higher-tier Slate with a brighter mini-LED display and a faster chip for multitasking-heavy workflows.", "specs": {"Display": "11\" mini-LED 120Hz", "CPU": "10-core", "RAM": "12GB", "Storage": "512GB"}},
    {"id": "p58", "sku": "EMP-WR-04", "category": "Wearables", "icon": "⌚", "name": "Pulse Kids Watch", "price": 98000, "stock": 17, "description": "A rugged, GPS-enabled smartwatch built for kids, with parent-controlled calling and a school-hours focus mode.", "specs": {"GPS": "Yes", "Calling": "Parent-approved contacts only", "Water rating": "IPX7", "Battery": "2 days typical"}},
    {"id": "p59", "sku": "EMP-WR-05", "category": "Wearables", "icon": "🕶️", "name": "Aura Smart Glasses", "price": 385000, "stock": 7, "description": "Everyday-looking glasses with open-ear audio and a voice assistant, built for calls and music without earbuds.", "specs": {"Audio": "Open-ear directional", "Battery": "6h continuous playback", "Weight": "45g", "Charging case": "Included"}},
    {"id": "p60", "sku": "EMP-TV-04", "category": "TV & Home", "icon": "📺", "name": "Vista 65\" 4K Smart TV", "price": 2150000, "stock": 3, "description": "The larger Vista panel, with the same HDR tuning and streaming apps as the 55\", built for bigger living rooms.", "specs": {"Size": "65\"", "Resolution": "4K HDR", "Refresh": "120Hz", "HDMI": "3x HDMI 2.1"}},
    {"id": "p61", "sku": "EMP-TV-05", "category": "TV & Home", "icon": "📽️", "name": "Beamline Mini Projector", "price": 268000, "stock": 9, "description": "A compact 1080p projector with autofocus and keystone correction, set up in under a minute on any wall.", "specs": {"Resolution": "1080p native", "Brightness": "700 ANSI lumens", "Autofocus": "Yes", "Speakers": "Built-in 2x5W"}},
    {"id": "p62", "sku": "EMP-TV-06", "category": "TV & Home", "icon": "🎬", "name": "Streaming Media Stick 4K", "price": 42000, "stock": 33, "description": "A 4K streaming stick with a voice remote, bringing every major app to any HDMI TV.", "specs": {"Resolution": "4K HDR", "Remote": "Voice-enabled", "Storage": "8GB internal"}},
    {"id": "p63", "sku": "EMP-SH-04", "category": "Smart Home", "icon": "💡", "name": "Nimbus Smart Bulb (4-pack)", "price": 36000, "stock": 29, "description": "Colour-changing Wi-Fi bulbs that work with the Nimbus Speaker or standalone, with schedules and scenes in the app.", "specs": {"Type": "Wi-Fi RGBW bulb", "Pack size": "4", "Compatibility": "Nimbus Speaker or standalone"}},
    {"id": "p64", "sku": "EMP-SH-05", "category": "Smart Home", "icon": "🌡️", "name": "Climate Smart Thermostat", "price": 142000, "stock": 8, "description": "A learning thermostat that builds a schedule around your habits and can be adjusted remotely from the app.", "specs": {"Learning mode": "Yes", "Connectivity": "Wi-Fi", "Compatibility": "Most central HVAC systems"}},
    {"id": "p65", "sku": "EMP-SH-06", "category": "Smart Home", "icon": "📷", "name": "Indoor Security Camera", "price": 76000, "stock": 22, "description": "A 1080p indoor camera with two-way audio and motion alerts sent straight to your phone.", "specs": {"Video": "1080p", "Audio": "Two-way", "Storage": "Local microSD, no subscription required", "Field of view": "130°"}},
    {"id": "p66", "sku": "EMP-NW-03", "category": "Networking", "icon": "📶", "name": "Pocket Wi-Fi Hotspot 5G", "price": 128000, "stock": 14, "description": "A pocket-sized 5G hotspot with a full day of battery, good for travel or as backup internet.", "specs": {"Standard": "5G / 4G LTE", "Battery": "Up to 12h", "Connected devices": "Up to 16"}},
    {"id": "p67", "sku": "EMP-NW-04", "category": "Networking", "icon": "🔌", "name": "8-Port Gigabit Switch", "price": 34000, "stock": 25, "description": "An unmanaged gigabit switch for expanding a home network — plug and play, no configuration needed.", "specs": {"Ports": "8x Gigabit", "Management": "Unmanaged, plug and play", "Power": "External adapter included"}},
    {"id": "p68", "sku": "EMP-DR-04", "category": "Drones", "icon": "🚁", "name": "Skyframe Pro Drone", "price": 780000, "stock": 4, "description": "A larger sibling to the Skyframe Mini with obstacle avoidance and a longer 40-minute flight time for serious aerial work.", "specs": {"Weight": "790g", "Camera": "4K, 3-axis gimbal", "Flight time": "40 min", "Obstacle avoidance": "4-directional"}},
    {"id": "p69", "sku": "EMP-PR-03", "category": "Printers", "icon": "🖨️", "name": "LabelFlow Compact Label Printer", "price": 54000, "stock": 18, "description": "A compact thermal label printer for parcels, pantry jars or barcodes, with no ink cartridges to replace.", "specs": {"Type": "Direct thermal, no ink", "Connectivity": "Bluetooth, USB", "Max label width": "4 inches"}},
    {"id": "p70", "sku": "EMP-AC-07", "category": "Accessories", "icon": "🎒", "name": "Everyday 15L Backpack", "price": 42000, "stock": 30, "description": "A slimmer daily bag with a padded 14\" laptop sleeve, built for commuting rather than travel.", "specs": {"Capacity": "15L", "Laptop sleeve": "Up to 14\"", "Material": "Water-resistant nylon"}},
    {"id": "p71", "sku": "EMP-AC-08", "category": "Accessories", "icon": "🔌", "name": "Car Fast Charger Dual-Port", "price": 15500, "stock": 42, "description": "A dual-port car charger with fast-charge on both ports, so driver and passenger can top up at once.", "specs": {"Output": "Total 45W", "Ports": "2x USB-C", "Compatibility": "12V/24V vehicles"}},
    {"id": "p72", "sku": "EMP-AC-09", "category": "Accessories", "icon": "🧴", "name": "Screen Cleaning Kit", "price": 7200, "stock": 52, "description": "A microfibre cloth and alcohol-free spray kit safe for phone, laptop and camera screens.", "specs": {"Includes": "Spray bottle + 2 microfibre cloths", "Safe for": "Coated and anti-glare screens"}},
    {"id": "p73", "sku": "EMP-AC-10", "category": "Accessories", "icon": "🔋", "name": "PowerBank 10000mAh Slim", "price": 26000, "stock": 38, "description": "A credit-card-thin power bank that slips into a pocket, good for one full phone charge.", "specs": {"Capacity": "10000mAh", "Output": "18W fast charge", "Thickness": "12mm"}},
    {"id": "p74", "sku": "EMP-AC-11", "category": "Accessories", "icon": "🖥️", "name": "Laptop Stand Adjustable", "price": 23000, "stock": 27, "description": "An aluminium laptop stand that raises the screen to eye level and folds flat for a bag.", "specs": {"Material": "Aluminium", "Adjustment": "6 height positions", "Foldable": "Yes"}},
    {"id": "p75", "sku": "EMP-AC-12", "category": "Accessories", "icon": "⌨️", "name": "Compact Wireless Keyboard", "price": 29000, "stock": 24, "description": "A tenkeyless wireless keyboard that pairs with up to three devices and switches between them with one key.", "specs": {"Layout": "Tenkeyless", "Connection": "Bluetooth, 3-device pairing", "Battery": "Up to 3 months"}},
    {"id": "p76", "sku": "EMP-AC-13", "category": "Accessories", "icon": "🎥", "name": "Webcam 1080p with Privacy Cover", "price": 38000, "stock": 21, "description": "A plug-and-play 1080p webcam with autofocus and a sliding privacy cover built into the housing.", "specs": {"Resolution": "1080p 30fps", "Field of view": "78°", "Mic": "Built-in stereo"}},
    {"id": "p77", "sku": "EMP-AC-14", "category": "Accessories", "icon": "🔦", "name": "Rechargeable LED Torch", "price": 13500, "stock": 33, "description": "A pocket torch with three brightness modes and a USB-C charging port, no batteries needed.", "specs": {"Brightness": "Up to 1000 lumens", "Charging": "USB-C", "Modes": "High / low / strobe"}},
    {"id": "p78", "sku": "EMP-AC-15", "category": "Accessories", "icon": "🧲", "name": "MagSafe-Style Wireless Charger", "price": 21000, "stock": 36, "description": "A magnetic wireless charging puck that snaps into place and charges compatible phones at full wireless speed.", "specs": {"Output": "15W max", "Alignment": "Magnetic snap-fit", "Cable": "USB-C, 1.2m included"}},
    {"id": "p79", "sku": "EMP-AC-16", "category": "Accessories", "icon": "🎒", "name": "Camera Sling Bag", "price": 48000, "stock": 14, "description": "A weatherproof sling bag with dividers for a camera body and two lenses, worn across the chest for quick access.", "specs": {"Capacity": "1 body + 2 lenses", "Material": "Water-resistant canvas", "Access": "Side quick-access zip"}},
    {"id": "p80", "sku": "EMP-AC-17", "category": "Accessories", "icon": "🔌", "name": "Universal Travel Adapter", "price": 19500, "stock": 40, "description": "A single adapter covering UK, EU, US and AU sockets, with two USB-A ports for charging small devices.", "specs": {"Sockets covered": "UK, EU, US, AU", "USB ports": "2x USB-A", "Rating": "Up to 2500W"}},
    {"id": "p81", "sku": "EMP-AC-18", "category": "Accessories", "icon": "🖱️", "name": "Vertical Ergonomic Mouse", "price": 36000, "stock": 19, "description": "A vertical mouse that keeps the wrist in a handshake position, aimed at reducing strain during long sessions.", "specs": {"Design": "Vertical, ergonomic", "Connection": "Wireless 2.4GHz", "DPI": "800/1200/1600 switchable"}},
    {"id": "p82", "sku": "EMP-AC-19", "category": "Accessories", "icon": "🧰", "name": "Precision Repair Tool Kit", "price": 32000, "stock": 17, "description": "A 32-piece kit with magnetic bits, spudgers and tweezers for phone, laptop and console repairs.", "specs": {"Pieces": "32", "Includes": "Bits, spudgers, tweezers, case", "Use": "Phone, laptop, console repair"}},
    {"id": "p83", "sku": "EMP-AC-20", "category": "Accessories", "icon": "🎧", "name": "In-Ear Monitor Earphones (Wired)", "price": 54000, "stock": 16, "description": "Wired in-ear monitors with a detachable cable, popular with musicians for stage and studio monitoring.", "specs": {"Type": "In-ear, wired", "Drivers": "Dual balanced armature", "Cable": "Detachable, 1.2m"}},
    {"id": "p84", "sku": "EMP-AC-21", "category": "Accessories", "icon": "📦", "name": "Cable Organiser Pouch", "price": 9800, "stock": 48, "description": "A padded zip pouch with elastic loops for cables, chargers and small adapters — keeps a bag tangle-free.", "specs": {"Compartments": "3 elastic loops + 1 mesh pocket", "Material": "Padded nylon"}},
    {"id": "p85", "sku": "EMP-AC-22", "category": "Accessories", "icon": "🔌", "name": "7-in-1 USB-C Hub", "price": 44000, "stock": 26, "description": "A compact hub adding HDMI, two USB-A ports, an SD card reader and pass-through charging to any USB-C laptop.", "specs": {"Ports": "HDMI, 2x USB-A, SD/microSD, USB-C PD", "Output": "HDMI up to 4K@30Hz"}},
    {"id": "p86", "sku": "EMP-AC-23", "category": "Accessories", "icon": "🎙️", "name": "Lavalier Clip Microphone", "price": 17500, "stock": 23, "description": "A clip-on lav mic with a long cable, suited to interviews and presentations recorded on a phone or camera.", "specs": {"Connection": "3.5mm TRRS", "Cable length": "6m", "Pickup pattern": "Omnidirectional"}},
    {"id": "p87", "sku": "EMP-AC-24", "category": "Accessories", "icon": "🖥️", "name": "Dual Monitor Arm", "price": 58000, "stock": 12, "description": "A gas-spring arm mounting two monitors side by side, freeing up desk space and allowing full height/tilt adjustment.", "specs": {"Mounts": "2 monitors up to 27\" each", "Adjustment": "Height, tilt, swivel", "Mount type": "Desk clamp + grommet"}},
    {"id": "p88", "sku": "EMP-AC-25", "category": "Accessories", "icon": "🧳", "name": "Hard-Shell Laptop Sleeve 14\"", "price": 19000, "stock": 31, "description": "A rigid-shell sleeve that protects a 14\" laptop from drops and knocks inside a bigger bag.", "specs": {"Fit": "Up to 14\" laptops", "Shell": "EVA hard case", "Interior": "Soft microfibre lining"}},
    {"id": "p89", "sku": "EMP-AC-26", "category": "Accessories", "icon": "🔋", "name": "Solar Power Bank 20000mAh", "price": 52000, "stock": 18, "description": "A rugged power bank with a fold-out solar panel for topping up slowly off-grid, plus a built-in torch.", "specs": {"Capacity": "20000mAh", "Solar input": "Trickle-charge panel", "Extras": "Built-in LED torch"}},
    {"id": "p90", "sku": "EMP-AC-27", "category": "Accessories", "icon": "🎮", "name": "Phone Gaming Controller Clip-On", "price": 39000, "stock": 20, "description": "A Bluetooth controller that clips around a phone, turning it into a handheld console for cloud and mobile gaming.", "specs": {"Connection": "Bluetooth", "Compatibility": "Most phones up to 8.5cm wide", "Battery": "20h"}},
    {"id": "p91", "sku": "EMP-AC-28", "category": "Accessories", "icon": "🧴", "name": "Laptop Cleaning & Care Kit", "price": 11500, "stock": 35, "description": "A keyboard-safe cleaning kit with a brush, air blower and screen-safe spray for regular laptop maintenance.", "specs": {"Includes": "Air blower, brush, spray, cloth", "Safe for": "Keyboards and coated screens"}},
    {"id": "p92", "sku": "EMP-AC-29", "category": "Accessories", "icon": "📱", "name": "Phone Ring Light Clip", "price": 8600, "stock": 44, "description": "A clip-on LED ring light with adjustable brightness, useful for video calls and content shot on a phone.", "specs": {"Power": "USB-C rechargeable", "Brightness levels": "3 (warm/cool/mixed)", "Clip range": "Up to 3cm thick"}},
    {"id": "p93", "sku": "EMP-AC-30", "category": "Accessories", "icon": "🔌", "name": "65W GaN Wall Charger Single Port", "price": 21500, "stock": 39, "description": "A compact single-port charger that can fast-charge a laptop or phone from one small brick.", "specs": {"Output": "65W max, USB-C PD", "Tech": "GaN", "Size": "Passport-sized"}},
    {"id": "p94", "sku": "EMP-AC-31", "category": "Accessories", "icon": "🎒", "name": "Camera Rain Cover", "price": 6500, "stock": 29, "description": "A lightweight rain cover that fits over most mirrorless cameras with a lens attached, packs down to pocket size.", "specs": {"Compatibility": "Most mirrorless bodies + lens", "Material": "Waterproof ripstop", "Packed size": "Pocket-sized"}},
    {"id": "p95", "sku": "EMP-AC-32", "category": "Accessories", "icon": "🖱️", "name": "Mouse Pad XL Desk Mat", "price": 12500, "stock": 37, "description": "An extra-large desk mat covering keyboard and mouse, with a stitched edge and non-slip rubber base.", "specs": {"Size": "900x400mm", "Surface": "Smooth cloth top", "Base": "Non-slip rubber"}},
    {"id": "p96", "sku": "EMP-AC-33", "category": "Accessories", "icon": "🔌", "name": "USB-C to USB-C Cable 2m (100W)", "price": 8200, "stock": 55, "description": "A braided 2-metre USB-C cable rated for 100W charging and fast data transfer between devices.", "specs": {"Length": "2m", "Power delivery": "Up to 100W", "Build": "Braided, reinforced ends"}},
    {"id": "p97", "sku": "EMP-AC-34", "category": "Accessories", "icon": "🎧", "name": "Headphone Stand with USB Hub", "price": 24500, "stock": 20, "description": "A weighted headphone stand with a built-in 3-port USB hub, keeping a desk tidy while headphones sit ready.", "specs": {"Ports": "3x USB-A", "Base": "Weighted, non-slip", "Compatibility": "Most headphone headbands"}},
    {"id": "p98", "sku": "EMP-AC-35", "category": "Accessories", "icon": "🔋", "name": "AA Rechargeable Battery Pack (8-pack)", "price": 14500, "stock": 41, "description": "Eight high-capacity rechargeable AA batteries with a compact charger, for controllers, mice and remotes.", "specs": {"Pack size": "8x AA", "Capacity": "2600mAh each", "Charger": "Included, 4-bay"}},
    {"id": "p99", "sku": "EMP-AC-36", "category": "Accessories", "icon": "🧳", "name": "Tech Travel Organiser Case", "price": 17000, "stock": 26, "description": "A compact case with elastic loops and mesh pockets for cables, dongles and a power bank, sized for a carry-on.", "specs": {"Compartments": "Elastic loops + 2 mesh pockets", "Material": "Water-resistant nylon"}},
    {"id": "p100", "sku": "EMP-AC-37", "category": "Accessories", "icon": "🖥️", "name": "Portable Monitor 15.6\" USB-C", "price": 215000, "stock": 9, "description": "A slim USB-C portable monitor that powers and displays from a single cable, folding flat with its cover for travel.", "specs": {"Size": "15.6\"", "Resolution": "1920x1080", "Connection": "USB-C (power + video)", "Weight": "780g"}},
]

POLICY = {
 "terms": {
  "title": "Terms & Conditions",
  "body": "These Terms & Conditions govern your use of ElectroMart and any order you place with us. By creating an account, browsing, or placing an order, you agree to be bound by them. If you do not agree, please do not use this site.\n\n- All prices are shown in Naira (₦), are inclusive of applicable taxes unless stated otherwise, and are subject to change without prior notice.\n- Orders are confirmed once payment is received; we reserve the right to refuse, limit, or cancel orders we suspect are fraudulent, erroneous, or in breach of these terms, with any payment taken refunded in full.\n- Product images, colours, and descriptions are for illustration only; slight variations from the physical product may occur.\n- Risk in goods passes to you on delivery; title passes once payment is received in full.\n- You must be at least 18 years old, or the age of majority in your jurisdiction, to place an order.\n- You agree to provide accurate, current delivery and contact details, and are responsible for keeping your account credentials confidential.\n- All content on this site — text, graphics, logos, and the ElectroMart brand mark — is our property or that of our licensors and may not be reproduced without permission.\n- To the fullest extent permitted by law, ElectroMart's liability for any claim relating to an order is limited to the value of that order.\n- These terms are governed by the laws of the Federal Republic of Nigeria. Continued use of this site constitutes acceptance of any future updates to these terms, which will be posted here with a revised effective date.\n"
 },
 "privacy": {
  "title": "Privacy Policy",
  "body": "This Privacy Policy explains how ElectroMart, as data controller, collects, uses, and protects your personal data. It is written to meet our obligations under the Nigeria Data Protection Act, 2023 (NDPA) and, for customers in the European Economic Area/UK, the General Data Protection Regulation (GDPR).\n\n**What we collect**\n\n- Identity and contact data: name, email, phone number, delivery address.\n- Order and transaction data: items purchased, order value, order history, tracking status.\n- Account data: login credentials (stored encrypted) and preferences.\n- Technical data collected automatically, such as device type and general usage patterns, to keep the service secure and working correctly.\n- We do not knowingly collect card or bank details directly — payments are handled by our payment processor under its own security and privacy standards.\n\n**Why we process it and our lawful basis**\n\n- To fulfil and deliver your orders and provide customer support — necessary for performance of a contract with you.\n- To detect and prevent fraud, and to meet tax, accounting, and other legal obligations — necessary for compliance with a legal obligation, and our legitimate interest in keeping the marketplace safe.\n- To send order and delivery updates — necessary for performance of a contract; to send optional marketing updates, only where you have given consent, which you may withdraw at any time.\n\n**Sharing and retention**\n\n- Your data is never sold. We share only what is necessary with delivery partners, payment processors, and IT service providers acting on our instructions, under written data-processing terms.\n- Where data is transferred outside Nigeria or the EEA/UK, we rely on adequate safeguards such as standard contractual clauses, consistent with NDPA and GDPR cross-border transfer requirements.\n- We keep personal data only as long as needed for the purposes above, or as required by tax and other applicable law, after which it is deleted or anonymised.\n\n**Your rights**\n\n- Subject to applicable law, you may request access to, correction of, erasure of, or a portable copy of your data, and may object to or ask us to restrict certain processing.\n- Where processing relies on consent (e.g. marketing), you can withdraw it at any time without affecting the lawfulness of processing already carried out.\n- Nigerian users may lodge a complaint with the Nigeria Data Protection Commission (NDPC); EEA/UK users may lodge a complaint with their local supervisory authority.\n- To exercise any of these rights, contact us via our WhatsApp customer care line or the email address on this site; we aim to respond within the timeframes required by applicable law.\n\n**Security and cookies**\n\n- We apply reasonable technical and organisational measures to protect your data and will notify affected users and, where required, the relevant regulator of any personal data breach as required by law.\n- This site uses essential cookies/local storage to keep you logged in and remember your cart; these do not track you across other sites.\n"
 },
 "returns": {
  "title": "Return & Refund Policy",
  "body": "We want you to be happy with your purchase. If an item arrives damaged, faulty, or different from what you ordered, or you simply change your mind, the options below apply in addition to your statutory consumer rights.\n\n- **Change of mind:** unopened, unused items in their original packaging may be returned within 7 days of delivery.\n- **Damaged, faulty, or incorrect items:** contact us within 7 days of delivery; once confirmed, we cover return shipping and you may choose a refund, replacement, or exchange.\n- Items must be unused, in original packaging with all accessories, and accompanied by proof of purchase (order ID or receipt).\n- For hygiene and safety reasons, opened consumables and earphones/earbuds with broken hygiene seals cannot be returned unless faulty.\n- Approved returns are refunded to the original payment method within 5–10 business days after the returned item is received and inspected; exchanges are dispatched once inspection is complete.\n- Delivery fees are non-refundable for change-of-mind returns, except where the item itself was faulty or incorrect.\n- This policy does not affect any other rights you have under applicable Nigerian consumer protection law.\n- Reach out on our WhatsApp customer care line to start a return or check its status.\n"
 },
 "requirements": {
  "title": "Functional & Non-Functional Requirements",
  "body": "ElectroMart is a monolithic marketplace application: the storefront UI, the buyer/seller logic, and the local data layer are shipped and run as a single deployable unit (this page), rather than as separate services. It supports two account types — Buyers and Sellers — trading electronics on one shared platform.\n\n**Functional Requirements**\n\n- **Account registration & role selection:** a visitor can register with a name, email, phone and password, choosing an account type of either Buyer (to purchase products) or Seller (to list products for sale).\n- **Authentication:** registered users can sign in and out; a signed-in session is remembered across page reloads.\n- **Product browsing:** buyers can browse the full catalogue, filter by category, and search by keyword.\n- **Marketplace price comparison:** each product shows its ElectroMart price alongside comparison prices from other marketplaces.\n- **Seller listings:** seller accounts can publish new product listings (name, category, icon, price, stock, description), which immediately appear in the shared product catalogue for buyers, tagged with the seller's name; sellers can view all products they have listed.\n- **Cart management:** buyers can add items to a cart, adjust quantities, remove items, and see a running subtotal, respecting available stock for both official and seller-listed products.\n- **Checkout & payment:** buyers can check out with a delivery address, phone number, and a choice of payment method (card, bank transfer, or pay on delivery), including card-detail and RRR-confirmation validation where applicable.\n- **Order placement & stock updates:** placing an order creates an order record, decrements stock for each purchased item — whether from the fixed catalogue or a seller listing — and generates a tracking ID.\n- **Order history & tracking:** buyers can view their past orders and their statuses, and track a package by tracking ID through a step-by-step delivery timeline that advances realistically over time rather than completing instantly.\n- **Post-delivery feedback:** once an order's tracking timeline reaches \"Delivered,\" the buyer is prompted to indicate whether they are satisfied with the order.\n- **Return & refund request:** if a buyer indicates dissatisfaction, they can submit a return & refund request (issue type, reason, notes, and confirmation of the item's condition), which is only accepted within the 7-day window and conditions set out in the Return & Refund Policy; the resulting request status is then visible on the order.\n- **Policies:** Terms and Conditions, Privacy Policy, and Return & Refund Policy are available from the footer at all times.\n\n**Non-Functional Requirements**\n\n- **Architecture:** the application is monolithic — a single self-contained web app bundling UI, application logic, and a local data layer, with no external service dependencies required to run.\n- **Performance:** product search and category filtering should feel instant to the user, with search input debounced to avoid excessive re-rendering while typing.\n- **Usability:** the interface should remain legible and operable on both desktop and mobile screen widths, with clear feedback (loading, error and success states) for every action.\n- **Reliability & data integrity:** stock levels must never go negative, an order should only be created once every line item's requested quantity has been validated against available stock, and an order's delivered date is fixed the first time it is observed as delivered so the return window cannot drift.\n- **Security:** passwords are required to meet a minimum length; a user can only view and manage their own cart, orders, listings, delivery feedback, and return requests, never another user's.\n- **Availability/persistence:** accounts, listings, stock levels, orders, delivery feedback, and return requests persist locally across browser sessions and reloads for the duration the browser data is retained.\n- **Maintainability:** functional areas (authentication, catalogue, cart, checkout, tracking, delivery feedback, returns, seller listings) are organised into distinct, clearly named functions to keep the single-file application easy to extend.\n- **Compatibility:** the application runs in modern evergreen browsers without requiring any additional plugins or installation.\n- **Legal & regulatory compliance:** data handling practices are documented in the Privacy Policy with reference to the Nigeria Data Protection Act, 2023 and, where applicable, the GDPR; return and refund handling is documented in, and enforced consistently with, the Return & Refund Policy.\n"
 },
 "standards": {
  "title": "Quality, Certification & Standards Compliance",
  "body": "ElectroMart designs, builds, and operates this platform, and sources the products listed on it, with reference to recognised international (ISO/IEC) standards and applicable Standards Organisation of Nigeria (SON) requirements.\n\n**Product certification (SON)**\n\n- Regulated electronics and electrical items listed on ElectroMart are expected to carry valid **SONCAP** (Standards Organisation of Nigeria Conformity Assessment Programme) certification before they may be imported into or sold within Nigeria.\n- Applicable locally manufactured items carry the **MANCAP** (Mandatory Conformity Assessment Programme) mark, and regulated products display the Nigerian Industrial Standard (NIS) reference relevant to their category.\n- Sellers listing regulated electronics warrant that their products meet the relevant NIS/SON product standard for that category, and ElectroMart may request certificates of conformity at any time.\n- A product's certification badge (where shown) indicates the category is subject to SON conformity requirements; it is not a substitute for checking the physical product's certification mark on arrival.\n\n**Quality management (ISO 9001)**\n\n- Platform processes — order handling, seller onboarding, returns, and customer support — are organised in line with the quality-management principles of **ISO 9001**: documented policies, defined responsibilities, and continual improvement based on customer feedback.\n\n**Information security (ISO/IEC 27001)**\n\n- Account, order, and payment-related data are handled with reference to the information-security management principles of **ISO/IEC 27001**: access is restricted to a user's own data, sessions are authenticated, and security practices are reviewed periodically.\n- This complements, and does not replace, the data-protection commitments set out in our Privacy Policy under the Nigeria Data Protection Act, 2023 and GDPR.\n\n**Software quality (ISO/IEC 25010)**\n\n- The application is developed with reference to the **ISO/IEC 25010** software quality model — covering functional suitability, reliability, usability, performance efficiency, and maintainability — as reflected in the Functional & Non-Functional Requirements document.\n\n**Accessibility (ISO/IEC 40500 · WCAG 2.1)**\n\n- The interface follows **ISO/IEC 40500** (which adopts the Web Content Accessibility Guidelines, WCAG 2.1), including a skip-to-content link, visible keyboard focus indicators, descriptive labels on icon-only controls, and dialog roles on modals and drawers so they work with screen readers and keyboard navigation.\n\nThis page is a good-faith statement of the standards this demo platform is designed with reference to; it is not a certification body and does not itself issue SONCAP, MANCAP, or ISO certificates.\n"
 },
 "problemStatement": {
  "title": "Problem Statement",
  "body": "Online electronics retail in Nigeria is fragmented across marketplaces — each with its own pricing, seller verification, and delivery process. Trust is the central psychological currency of e-commerce: a transaction happens under information asymmetry, spatial separation, and temporal separation between payment and delivery, so a buyer must trust a seller before the exchange completes — and in a fragmented market that trust has to be rebuilt from scratch on every platform.\n\nConcretely, a buyer shopping for electronics cannot, on one screen: compare a product's price against other marketplaces before committing; buy confidently from an independent seller with the same guarantees as buying from the platform itself; track and, if needed, return an order without leaving the platform; or confirm the platform handles their data and consumer rights in line with recognised law and standards.\n\nElectroMart's answer is a single marketplace where buyers and sellers share one catalogue, every product carries a price comparison against other marketplaces, every order is trackable and returnable in-app, and the platform's data-protection and standards posture is documented and visible — see **Requirements** and **Standards & Certification** below.\n"
 },
 "feasibility": {
  "title": "Feasibility Study",
  "body": "Assessed against SMART criteria at the start of the project:\n\n- **Specific:** one buyer/seller marketplace, with price comparison, cart/checkout, order tracking, returns, seller listings and analytics, documented against ISO/SON standards and NDPA/GDPR.\n- **Measurable:** every functional and non-functional requirement below has a corresponding working feature, tracked against a fixed test checklist.\n- **Achievable:** the whole app is a single static file with a simulated backend over local storage — no server, build step, or paid infrastructure needed to run or grade it.\n- **Relevant:** directly answers the course's applied e-commerce deliverable, built through Analysis → Design → Development → Testing → Deployment with an AI coding agent as the primary \"worker.\"\n- **Time-bound:** built incrementally, one feature at a time, so each increment stayed small enough to finish and verify before the next started.\n\nConclusion: feasible within the course's timeline and technology constraints; the main risk — scope creep — is managed by keeping the Requirements page as the single source of truth for what's in scope.\n"
 },
 "systemRequirements": {
  "title": "System Requirements",
  "body": "Distinct from the functional/non-functional requirements above, this covers what the system needs to run.\n\n**Client:** a modern evergreen browser with JavaScript and `localStorage` enabled; private/incognito windows that block storage will lose the cart and session on close. Responsive down to ~360px viewport widths. A network connection is only required once, to load the page and its fonts — everything after that runs locally.\n\n**Hosting:** no application server or database is required — any static file host serving HTTPS is sufficient, since the deliverable is a single static HTML file with no server-side configuration or secrets.\n\n**Data:** all state (accounts, listings, orders, cart, feedback, returns) lives in the browser's local storage, seeded on first load. This is local to one browser profile by explicit design for this course build, not an oversight — a production version would replace the local data layer with a real hosted API and database.\n\n**Dependencies:** Google Fonts is the only external dependency; there are no npm packages or JS frameworks.\n"
 },
 "design": {
  "title": "Design Overview",
  "body": "Design was split into three concerns, matching the course's Frontend / Logic / Backend design-document structure.\n\n**Frontend**\n\n- Paris/Eiffel Tower visual identity — indigo, brass gold, and wine-red accents on a warm paper background; Playfair Display for headings, Jost for UI text, JetBrains Mono for prices and specs.\n- Each screen (auth, catalogue, product detail, cart, checkout, tracking, seller dashboard, admin, chat) maps 1:1 to its own render function, all composed by one central render loop driven by app state.\n- WCAG 2.1 / ISO/IEC 40500: skip link, visible focus states, labelled icon-only controls, dialog roles with Escape-to-close.\n\n**Logic**\n\n- An indexed O(n + m) product lookup used at checkout, instead of a naive per-line-item scan.\n- A deterministic, seeded price-comparison algorithm so competitor prices are stable per product across reloads without being stored, clearly documented as illustrative rather than live-scraped data.\n- Order tracking progress derives from real elapsed time rather than jumping straight to \"Delivered,\" and the delivered timestamp is fixed on first reach so the return window can't drift.\n\n**Backend**\n\n- A single simulated API function routes every \"network\" call, validated against a small versioned JSON Schema contract, so swapping in a real hosted API later would not require changing anything above this layer.\n- Bearer-token auth scoped so every operation only ever touches the calling user's own data.\n"
 },
 "testing": {
  "title": "Testing Plan (Alpha / Beta / UAT)",
  "body": "**Alpha** — run inside the development environment after each change: registration/login, browsing/search/price comparison, cart and checkout across all three payment methods, order tracking and its time-based progress, post-delivery feedback and return requests, seller listing and analytics, admin moderation, and keyboard/screen-reader accessibility through a full purchase.\n\n**Beta** — run outside the development environment, after deployment: a full purchase flow on a second browser engine and on a real mobile device, a fresh browser profile seeding correctly, data surviving a real reload/restart, and page load over a throttled connection.\n\n**UAT** — a non-developer walks through the app against the Requirements above without being shown how to use it first: can they register and understand their role, understand the price-comparison badge, complete checkout without confusion, find and understand order tracking, locate the policy pages, and (as a seller) list a product and read their analytics.\n\nTesting is considered complete once every Alpha check passes, at least one full Beta pass is recorded, and UAT feedback — including friction points, not just a clean pass sheet — has been reviewed.\n"
 },
 "deployment": {
  "title": "Deployment Plan",
  "body": "As a single static file with no server-side code, ElectroMart fits any static host — GitHub Pages, Netlify/Vercel, or a cloud static bucket (AWS S3/CloudFront, Azure Static Web Apps). No build command, environment variables, or server configuration are required.\n\n**Process:** push the codebase to a Git repository, deploy to the host's preview/staging URL first, run the Beta checklist against that staging URL on a real device, then promote to the production URL/domain only once Beta passes.\n\n**Go-live checklist:** entry file correctly served, HTTPS active, Beta checklist passed on the live URL, all footer links (including this Project Docs section) verified on the deployed site, and a fresh browser profile confirmed to seed correctly.\n\n\"Production-ready\" here means reachable at a public HTTPS URL with the checklist complete and UAT feedback reviewed — not that it handles real payments or real user data; the simulated backend and local-only storage are explicit, documented limitations of this course build.\n"
 }
}

CATALOG_BY_ID = {p["id"]: p for p in CATALOG}

MARKETPLACES = ["Konga", "Jumia", "AliExpress", "Slot", "Jiji"]
COMPARE_MARKUP = 0.16
BANK_TRANSFER_DETAILS = {
    "bankName": "Providus Bank",
    "accountName": "ElectroMart Nigeria Ltd",
    "accountNumber": "0123456789",
}
TRACKING_STEPS = ["Order placed", "Processing", "Shipped", "Out for delivery", "Delivered"]
TRACKING_STEP_MINUTES = [0, 3, 8, 14, 20]  # demo pacing: delivered within 20 minutes
RETURN_WINDOW_DAYS = 7
FREE_SHIPPING_FROM = 200000
SHIPPING_FEE = 3500
MIN_PASSWORD_LENGTH = 8
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

CATEGORY_ICONS = {
    "Laptops": ft.Icons.LAPTOP,
    "Smartphones": ft.Icons.SMARTPHONE,
    "Audio": ft.Icons.HEADPHONES,
    "Cameras": ft.Icons.CAMERA_ALT,
    "Drones": ft.Icons.FLIGHT,
    "Gaming": ft.Icons.SPORTS_ESPORTS,
    "Networking": ft.Icons.WIFI,
    "Printers": ft.Icons.PRINT,
    "Smart Home": ft.Icons.HOME,
    "TV & Home": ft.Icons.TV,
    "Tablets": ft.Icons.TABLET_MAC,
    "Wearables": ft.Icons.WATCH,
    "Accessories": ft.Icons.CABLE,
}

CHAT_QUICK = [
    ("track", "📦 Track my order"),
    ("return", "↩️ Return / refund"),
    ("payment", "💳 Payment issue"),
    ("seller", "🏪 Become a seller"),
    ("human", "🧑‍💼 Talk to a human"),
]
CHAT_TOPIC_REPLIES = {
    "track": "To track your order, open My orders (or Track package) and use your EMP-XXXXXX tracking ID. "
             "You'll see the live timeline: Placed → Processing → Shipped → Out for delivery → Delivered.",
    "return": "Once an order is delivered, tell us you're not satisfied on its card in My orders and you can start "
              "a return & refund request within the 7-day window in our Return & Refund Policy.",
    "payment": "For payment issues, check the order's payment status in My orders first. Card and bank-transfer "
               "orders get an RRR reference you must confirm. If a charge didn't confirm, please don't retry "
               "straight away — contact us with your order ID.",
    "seller": "Want to sell on ElectroMart? Create a Seller account, then use the Sell tab to list your first "
              "product. Listings go live in the marketplace immediately.",
    "human": "Got it — for a real person, message our WhatsApp customer care line (07043941075, see the footer). "
             "You can describe your issue here in the meantime.",
}


def chat_bot_reply(text):
    t = text.lower()
    if any(k in t for k in ("order", "track", "where")):
        return ('You can check live status any time on the "Track package" tab using your EMP-XXXXXX '
                "tracking ID from My orders.")
    if any(k in t for k in ("return", "refund")):
        return ("Returns open from a delivered order under My orders, within the return window in our "
                "Return & Refund Policy (footer link).")
    if any(k in t for k in ("payment", "pay", "card", "transfer")):
        return ("We accept card, bank transfer, and pay-on-delivery — pick one at checkout. Card/transfer "
                "orders get an RRR reference to confirm.")
    if any(k in t for k in ("human", "agent", "person")):
        return 'For a real person, message us on WhatsApp — the number is in the footer under "Customer care".'
    return ("Thanks for reaching out! A member of the ElectroMart team will get back to you shortly. "
            "The quick topics above cover most common questions.")


# ============================================================================
# Pure helpers (formatting, price comparison, validation)
# ============================================================================
def fmt(n):
    return "₦{:,.0f}".format(n)


def js_round(x):
    return math.floor(x + 0.5)


def compare_price_for(price):
    return js_round(price * (1 + COMPARE_MARKUP) / 1000) * 1000


def seeded_unit(seed):
    h = 0
    for ch in seed:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return (h % 1000) / 1000


def competitor_prices_for(product):
    """Illustrative competitor prices (+9% … +34% over ours) — NOT live data."""
    out = []
    for name in MARKETPLACES:
        markup = 0.09 + seeded_unit(product["id"] + "|" + name) * 0.25
        out.append({"name": name, "price": js_round(product["price"] * (1 + markup) / 500) * 500})
    return sorted(out, key=lambda c: c["price"])


def cheapest_competitor(product):
    return competitor_prices_for(product)[0]


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(str(email or "").strip()))


def password_strength(password):
    pw = str(password or "")
    classes = sum([
        bool(re.search(r"[a-z]", pw)),
        bool(re.search(r"[A-Z]", pw)),
        bool(re.search(r"[0-9]", pw)),
        bool(re.search(r"[^A-Za-z0-9]", pw)),
    ])
    if len(pw) < MIN_PASSWORD_LENGTH:
        return {"score": 0, "label": "too short", "classes": classes}
    if classes <= 1:
        return {"score": 1, "label": "weak", "classes": classes}
    if classes == 2 and len(pw) < 12:
        return {"score": 2, "label": "medium", "classes": classes}
    return {"score": 3, "label": "strong", "classes": classes}


def validate_credentials(email, password, check_strength=False):
    errors = []
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if check_strength:
        s = password_strength(password)
        if s["score"] == 0:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        elif s["score"] == 1:
            errors.append("Password is too weak — mix in uppercase, numbers, or symbols.")
    elif not password:
        errors.append("Password is required.")
    return errors


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def seller_label(product):
    return f"Sold by {product['sellerName']}" if product.get("sellerName") else "ElectroMart (official store)"


# ============================================================================
# Local backend — stands in for the server (JSON file instead of localStorage)
# ============================================================================
class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()

    # ---- persistence ----
    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        data.setdefault("users", [])
        data.setdefault("orders", [])
        data.setdefault("stock", {})
        data.setdefault("listings", [])
        data.setdefault("carts", {})
        if not any(u.get("role") == "admin" for u in data["users"]):
            data["users"].append({
                "id": "admin_1", "name": "Site Admin", "email": "admin@electromart.demo", "phone": "",
                "password": hash_password("Admin#2026"), "role": "admin", "disabled": False,
            })
        self.data = data
        self.save()
        return data

    def save(self):
        try:
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:  # read-only location etc. — keep running in memory
            print("[ElectroMart] could not save database:", exc)

    # ---- helpers ----
    @staticmethod
    def public_user(u):
        return {"id": u["id"], "name": u["name"], "email": u["email"],
                "phone": u.get("phone", ""), "role": u.get("role", "buyer")}

    def user_by_id(self, uid):
        return next((u for u in self.data["users"] if u["id"] == uid), None)

    def stock_for(self, product):
        return self.data["stock"].get(product["id"], product["stock"])

    def listings(self):
        return self.data["listings"]

    def all_products(self):
        cat = [dict(p, stock=self.stock_for(p)) for p in CATALOG]
        live = [dict(l) for l in self.listings() if not l.get("removed")]
        return cat + live

    def product_by_id(self, pid):
        return next((p for p in self.all_products() if p["id"] == pid), None)

    def products(self, category="All", q=""):
        combined = self.all_products()
        items = combined
        q = (q or "").strip().lower()
        if category and category != "All":
            items = [p for p in items if p["category"] == category]
        if q:
            items = [p for p in items if q in p["name"].lower() or q in p["description"].lower()
                     or q in p["category"].lower()]
        cats = sorted({p["category"] for p in combined}, key=lambda c: [p["category"] for p in combined].index(c))
        return items, cats

    # ---- auth ----
    def register(self, name, email, phone, password, role):
        name, email = (name or "").strip(), (email or "").strip()
        if not name or not email or not password:
            raise ApiError("Name, email and password are required.")
        errs = validate_credentials(email, password, check_strength=True)
        if errs:
            raise ApiError(errs[0])
        if any(u["email"].lower() == email.lower() for u in self.data["users"]):
            raise ApiError("An account with that email already exists — try signing in instead.")
        user = {"id": "u_" + secrets.token_hex(4), "name": name, "email": email,
                "phone": (phone or "").strip(), "password": hash_password(password),
                "role": "seller" if role == "seller" else "buyer", "disabled": False}
        self.data["users"].append(user)
        self.save()
        return self.public_user(user)

    def login(self, email, password):
        email = (email or "").strip()
        errs = validate_credentials(email, password, check_strength=False)
        if errs:
            raise ApiError(errs[0])
        user = next((u for u in self.data["users"] if u["email"].lower() == email.lower()), None)
        if not user or not verify_password(password, user["password"]):
            raise ApiError("Incorrect email or password.")
        if user.get("disabled"):
            raise ApiError("This account has been disabled by an administrator. "
                           "Contact support if you believe this is a mistake.", 403)
        return self.public_user(user)

    # ---- carts ----
    def get_cart(self, uid):
        return list(self.data["carts"].get(uid, []))

    def set_cart(self, uid, cart):
        self.data["carts"][uid] = cart
        self.save()

    # ---- seller listings & analytics ----
    def my_listings(self, uid):
        return sorted([l for l in self.listings() if l["sellerId"] == uid],
                      key=lambda l: l["createdAt"], reverse=True)

    def create_listing(self, uid, name, category, icon, price, stock, description):
        seller = self.user_by_id(uid)
        if not seller or seller["role"] != "seller":
            raise ApiError("Only seller accounts can list products for sale.", 403)
        name, category, description = (name or "").strip(), (category or "").strip(), (description or "").strip()
        if not name or not category or not description:
            raise ApiError("Please fill in the product name, category and description.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = float("nan")
        if not math.isfinite(price) or price <= 0:
            raise ApiError("Please enter a valid price.")
        try:
            stock = float(stock)
        except (TypeError, ValueError):
            stock = float("nan")
        if not math.isfinite(stock) or stock < 0:
            raise ApiError("Please enter a valid stock quantity.")
        listing = {
            "id": "l_" + secrets.token_hex(5),
            "sku": "SELLER-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            "category": category, "icon": (icon or "").strip() or "📦", "name": name,
            "price": int(price) if price == int(price) else price, "stock": int(stock),
            "description": description, "specs": {}, "sellerId": seller["id"],
            "sellerName": seller["name"], "createdAt": time.time(), "removed": False,
        }
        self.listings().append(listing)
        self.save()
        return listing

    def seller_analytics(self, uid):
        seller = self.user_by_id(uid)
        if not seller or seller["role"] != "seller":
            raise ApiError("Only seller accounts can view analytics.", 403)
        revenue = units = 0
        order_ids = set()
        by_listing = {}
        for order in self.data["orders"]:
            touched = False
            for line in order["items"]:
                if line.get("sellerName") != seller["name"]:
                    continue
                touched = True
                revenue += line["price"] * line["qty"]
                units += line["qty"]
                e = by_listing.setdefault(line["name"], {"units": 0, "revenue": 0})
                e["units"] += line["qty"]
                e["revenue"] += line["price"] * line["qty"]
            if touched:
                order_ids.add(order["id"])
        mine = [l for l in self.listings() if l["sellerId"] == seller["id"]]
        top = sorted(({"name": n, **v} for n, v in by_listing.items()), key=lambda x: -x["revenue"])[:6]
        return {
            "revenue": revenue, "unitsSold": units, "ordersCount": len(order_ids),
            "listingsCount": len(mine),
            "lowStock": sum(1 for l in mine if 0 < l["stock"] <= 3),
            "outOfStock": sum(1 for l in mine if l["stock"] == 0),
            "topListings": top, "maxRevenue": top[0]["revenue"] if top else 0,
        }

    # ---- orders ----
    @staticmethod
    def compute_progress(order):
        minutes = (time.time() - order["createdAt"]) / 60
        idx = 0
        for i in range(len(TRACKING_STEP_MINUTES) - 1, -1, -1):
            if minutes >= TRACKING_STEP_MINUTES[i]:
                idx = i
                break
        if idx == len(order["trackingSteps"]) - 1 and not order.get("deliveredAt"):
            order["deliveredAt"] = time.time()  # fixed once, so the return window can't drift
        order["trackingStepIndex"] = idx
        return idx

    def orders_for(self, uid):
        mine = [o for o in self.data["orders"] if o["userId"] == uid]
        for o in mine:
            self.compute_progress(o)
        self.save()
        return sorted(mine, key=lambda o: o["createdAt"], reverse=True)

    def place_order(self, uid, items, payment_method, address, phone):
        if not items:
            raise ApiError("Your cart is empty.")
        index = {p["id"]: p for p in CATALOG}
        listing_index = {l["id"]: l for l in self.listings()}
        lines = []
        for it in items:  # O(n + m): index built once, O(1) per line
            listing = listing_index.get(it["productId"])
            product = listing or index.get(it["productId"])
            if not product or (listing and listing.get("removed")):
                continue
            available = product["stock"] if listing else self.stock_for(product)
            qty = max(0, min(it["qty"], available))
            if qty <= 0:
                continue
            if listing:
                listing["stock"] = available - qty
            else:
                self.data["stock"][product["id"]] = available - qty
            lines.append({"name": product["name"], "price": product["price"], "qty": qty,
                          "sellerName": product.get("sellerName")})
        if not lines:
            raise ApiError("Those items just sold out — please review your cart.")
        subtotal = sum(l["price"] * l["qty"] for l in lines)
        shipping = 0 if subtotal >= FREE_SHIPPING_FROM else SHIPPING_FEE
        needs_rrr = payment_method in ("card", "transfer")
        order = {
            "id": "o_" + secrets.token_hex(4), "userId": uid,
            "trackingId": "EMP-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            "items": lines, "total": subtotal + shipping, "paymentMethod": payment_method,
            "rrr": str(secrets.randbelow(900_000_000_000) + 100_000_000_000) if needs_rrr else None,
            "paid": not needs_rrr, "address": address or "", "phone": phone or "",
            "status": "Pending" if needs_rrr else "Processing", "createdAt": time.time(),
            "trackingSteps": list(TRACKING_STEPS), "trackingStepIndex": 0, "deliveredAt": None,
            "feedback": None, "returnRequest": None,
        }
        self.data["orders"].append(order)
        self.save()
        return order

    def _own_order(self, uid, tracking_id):
        order = next((o for o in self.data["orders"]
                      if o["trackingId"] == tracking_id and o["userId"] == uid), None)
        if not order:
            raise ApiError("Order not found.", 404)
        return order

    def confirm_payment(self, uid, tracking_id, rrr):
        order = self._own_order(uid, tracking_id)
        if order["paid"]:
            return order
        if not order.get("rrr") or str(rrr or "").strip() != order["rrr"]:
            raise ApiError("That RRR number does not match this order. Please check and try again.")
        order["paid"] = True
        order["status"] = "Processing"
        self.save()
        return order

    def track(self, tracking_id):
        order = next((o for o in self.data["orders"] if o["trackingId"] == tracking_id), None)
        if not order:
            raise ApiError("No order found with that tracking ID.", 404)
        idx = self.compute_progress(order)
        self.save()
        return {
            "trackingId": order["trackingId"], "itemCount": sum(l["qty"] for l in order["items"]),
            "trackingSteps": order["trackingSteps"], "trackingStepIndex": idx,
            "deliveredAt": order["deliveredAt"], "feedback": order["feedback"],
            "returnRequest": order["returnRequest"],
        }

    def feedback(self, uid, tracking_id, satisfied):
        order = self._own_order(uid, tracking_id)
        self.compute_progress(order)
        if not order["deliveredAt"]:
            raise ApiError("This order has not been delivered yet.")
        order["feedback"] = {"satisfied": bool(satisfied), "comment": "", "submittedAt": time.time()}
        order["status"] = "Delivered — feedback received" if satisfied else "Delivered — return requested"
        self.save()
        return order

    def return_request(self, uid, tracking_id, rtype, reason, notes, agree):
        order = self._own_order(uid, tracking_id)
        self.compute_progress(order)
        if not order["deliveredAt"]:
            raise ApiError("This order has not been delivered yet.")
        if (time.time() - order["deliveredAt"]) / 86400 > RETURN_WINDOW_DAYS:
            raise ApiError(f"Sorry, the {RETURN_WINDOW_DAYS}-day return & refund window for this order has passed.")
        if not agree:
            raise ApiError("Please confirm the item meets the return conditions in our Return & Refund Policy.")
        order["returnRequest"] = {
            "type": "damaged_faulty" if rtype == "damaged_faulty" else "change_of_mind",
            "reason": (reason or "").strip(), "notes": (notes or "").strip(),
            "requestedAt": time.time(), "status": "Requested",
        }
        order["status"] = "Return requested"
        self.save()
        return order

    # ---- admin ----
    def _require_admin(self, uid):
        admin = self.user_by_id(uid)
        if not admin or admin["role"] != "admin":
            raise ApiError("Admin access required.", 403)

    def admin_report(self, uid):
        self._require_admin(uid)
        revenue = units = 0
        by_product = {}
        for order in self.data["orders"]:
            for line in order["items"]:
                revenue += line["price"] * line["qty"]
                units += line["qty"]
                e = by_product.setdefault(line["name"], {"units": 0, "revenue": 0})
                e["units"] += line["qty"]
                e["revenue"] += line["price"] * line["qty"]
        top = sorted(({"name": n, **v} for n, v in by_product.items()), key=lambda x: -x["revenue"])[:6]
        users = self.data["users"]
        return {
            "totalRevenue": revenue, "totalUnits": units, "ordersCount": len(self.data["orders"]),
            "usersCount": len(users),
            "buyersCount": sum(1 for u in users if u["role"] == "buyer"),
            "sellersCount": sum(1 for u in users if u["role"] == "seller"),
            "listingsCount": len(self.listings()),
            "flaggedCount": sum(1 for l in self.listings() if l.get("removed")),
            "topProducts": top,
        }

    def admin_listings(self, uid):
        self._require_admin(uid)
        return sorted(self.listings(), key=lambda l: l["createdAt"], reverse=True)

    def toggle_listing(self, uid, listing_id):
        self._require_admin(uid)
        listing = next((l for l in self.listings() if l["id"] == listing_id), None)
        if not listing:
            raise ApiError("Listing not found.", 404)
        listing["removed"] = not listing.get("removed")
        self.save()

    def admin_users(self, uid):
        self._require_admin(uid)
        return [u for u in self.data["users"] if u["role"] != "admin"]

    def toggle_user(self, uid, user_id):
        self._require_admin(uid)
        user = self.user_by_id(user_id)
        if not user:
            raise ApiError("User not found.", 404)
        if user["role"] == "admin":
            raise ApiError("Cannot disable an admin account.")
        user["disabled"] = not user.get("disabled")
        self.save()


# ============================================================================
# UI helpers
# ============================================================================
def txt(value, size=14, color=INK, weight=None, font=None, **kw):
    """Text with the ElectroMart type system. weight: 'b' bold, 's' semibold."""
    w = {"b": ft.FontWeight.W_700, "s": ft.FontWeight.W_600, None: None}.get(weight, weight)
    if font == "display":
        kw.setdefault("font_family", DISPLAY)
        kw.setdefault("font_family_fallback", DISPLAY_FALLBACK)
    elif font == "mono":
        kw.setdefault("font_family", MONO)
        kw.setdefault("font_family_fallback", MONO_FALLBACK)
    return ft.Text(str(value), size=size, color=color, weight=w, **kw)


def mono(value, size=11.5, color=INK_DIM, weight=None, **kw):
    return txt(value, size, color, weight, font="mono", **kw)


def display(value, size=24, color=INK, **kw):
    return txt(value, size, color, "b", font="display", **kw)


def tower(width, height, color):
    """The Eiffel Tower silhouette — the brand's signature motif."""
    pts = [(100, 0), (104, 112), (140, 112), (112, 190), (160, 320), (40, 320), (88, 190), (60, 112), (96, 112)]
    sx, sy = width / 200, height / 320
    elements = [cv.Path.MoveTo(pts[0][0] * sx, pts[0][1] * sy)]
    elements += [cv.Path.LineTo(x * sx, y * sy) for x, y in pts[1:]]
    elements.append(cv.Path.Close())
    return cv.Canvas(
        [cv.Path(elements, paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL))],
        width=width, height=height,
    )


def button(label, on_click=None, kind="gold", width=None, disabled=False, small=False, icon=None):
    bg, fg = {"gold": (GOLD, WHITE), "wine": (WINE, WHITE), "ink": (INK, WHITE)}.get(kind, (None, INK))
    side = ft.BorderSide(1, LINE) if kind == "ghost" else None
    style = ft.ButtonStyle(
        bgcolor=bg, color=fg, elevation=0, side=side,
        shape=ft.RoundedRectangleBorder(radius=4),
        padding=ft.Padding.symmetric(horizontal=10 if small else 18, vertical=7 if small else 12),
    )
    return ft.Button(
        content=txt(label, 12 if small else 14, fg, "s"), icon=icon, on_click=on_click,
        style=style, width=width, disabled=disabled,
    )


def link_button(label, on_click=None, color=INK_DIM, size=12.5, url=None):
    return ft.TextButton(
        content=txt(label, size, color, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        on_click=on_click, url=url,
        style=ft.ButtonStyle(padding=ft.Padding.symmetric(horizontal=4, vertical=2)),
    )


def field(label, value="", on_change=None, password=False, multiline=False, width=None,
          hint=None, on_submit=None, keyboard=None, max_length=None, expand=None):
    return ft.TextField(
        label=label, value=value, on_change=on_change, on_submit=on_submit,
        password=password, can_reveal_password=password,
        multiline=multiline, min_lines=3 if multiline else None, max_lines=5 if multiline else None,
        hint_text=hint, width=width, keyboard_type=keyboard, max_length=max_length, expand=expand,
        border_color=LINE, focused_border_color=GOLD, border_radius=4,
        filled=True, fill_color=PAPER, color=INK, text_size=14.5,
        label_style=ft.TextStyle(size=12, color=INK_DIM),
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=12),
    )


def dropdown(label, options, value, on_select=None, width=None):
    return ft.Dropdown(
        label=label, value=value, width=width, on_select=on_select,
        options=[ft.DropdownOption(key=k, text=t) for k, t in options],
        border_color=LINE, focused_border_color=GOLD, border_radius=4, filled=True, fill_color=PAPER,
        color=INK, text_size=14, label_style=ft.TextStyle(size=12, color=INK_DIM),
    )


def flash(message, ok=False):
    return ft.Container(
        content=mono(message, 12, GOLD_DIM if ok else WINE_DIM),
        bgcolor="#F1EFE0" if ok else "#FBEEEC",
        border=ft.Border.all(1, GOLD_DIM if ok else WINE),
        border_radius=4, padding=ft.Padding.symmetric(horizontal=12, vertical=10),
    )


def panel(content, padding=18, width=None, bgcolor=CARD, **kw):
    return ft.Container(
        content=content, padding=padding, width=width, bgcolor=bgcolor,
        border=ft.Border.all(1, LINE), border_radius=6, **kw,
    )


def spec_row(label, value, bold=False, value_color=None):
    c = INK if bold else INK_DIM
    return ft.Row(
        [mono(label, 11.5, c, "b" if bold else None, expand=True),
         mono(value, 11.5, value_color or INK, "b" if bold else None, text_align=ft.TextAlign.RIGHT)],
        spacing=10, vertical_alignment=ft.CrossAxisAlignment.START,
    )


def pill(text, bg=GOLD, color=WHITE, size=11):
    return ft.Container(
        content=mono(text, size, color), bgcolor=bg, border_radius=999,
        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
    )


def cert_badge(label):
    return ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.VERIFIED_USER_OUTLINED, size=11, color=WINE), mono(label, 9.5, WINE)],
                       spacing=4, tight=True),
        bgcolor=alpha(WINE, 0.08), border=ft.Border.all(1, alpha(WINE, 0.25)), border_radius=3,
        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
    )


def section_head(title, trailing=None):
    row = [display(title, 24)]
    if trailing is not None:
        row.append(trailing)
    return ft.Column([
        ft.Row(row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(width=38, height=3, border_radius=2, gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT, colors=[GOLD, WINE])),
        ft.Divider(height=14, color=LINE),
    ], spacing=6)


def stat_card(label, value, warn=False):
    return ft.Container(
        content=ft.Column([mono(label.upper(), 10, INK_DIM), display(value, 20, WINE if warn else INK)], spacing=6),
        bgcolor=CARD, border=ft.Border.all(1, WINE if warn else LINE), border_radius=6,
        padding=ft.Padding.symmetric(horizontal=16, vertical=14), width=178,
    )


def bar_row(name, meta, fraction):
    pct = max(4, round(fraction * 100)) if fraction else 0
    return ft.Column([
        ft.Row([txt(name, 12.5, INK, "s", expand=True), mono(meta, 11)]),
        ft.Container(
            height=8, border_radius=999, bgcolor=PAPER, border=ft.Border.all(1, LINE_SOFT),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Row([
                ft.Container(expand=pct, gradient=ft.LinearGradient(
                    begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT, colors=[GOLD, WINE])),
                ft.Container(expand=max(1, 100 - pct)),
            ], spacing=0),
        ),
    ], spacing=5)


def hover_lift(e):
    on = str(e.data).lower() == "true"
    e.control.scale = 1.02 if on else 1.0
    e.control.border = ft.Border.all(1, GOLD if on else LINE)
    e.control.update()


# ============================================================================
# The application
# ============================================================================
class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Store(os.environ.get("ELECTROMART_DB") or Path(__file__).with_name("electromart_db.json"))

        # session
        self.user = None
        self.view = "shop"
        self.auth_mode = "login"

        # shop
        self.category = "All"
        self.search = ""
        self.cart = []
        self.cart_open = False

        # checkout
        self.payment_method = "card"
        self.address = self.phone = self.card_name = self.card_number = self.card_expiry = self.card_cvv = ""
        self.checkout_error = ""
        self.checkout_busy = False
        self.checkout_dlg = None

        # orders / tracking
        self.orders = []
        self.last_order = None
        self.rrr_drafts, self.rrr_errors = {}, {}
        self.return_forms, self.return_errors = {}, {}
        self.track_input = ""
        self.track_result = None
        self.track_error = ""

        # seller / admin
        self.my_listings = []
        self.analytics = None
        self.admin_tab = "reports"
        self.admin_report = None
        self.admin_listings = []
        self.admin_users = []

        # dialogs
        self.product_dlg = None
        self.product_dlg_pid = None

        # chat
        self.chat_open = False
        self.chat_unread = 1
        self.chat_messages = [("bot", "Hi there! 👋 I'm the ElectroMart quick-response assistant. "
                                      "Pick a topic below or type your question.")]

        self.build_shell_layers()
        self.show_auth()

    # ------------------------------------------------------------------ layers
    def build_shell_layers(self):
        p = self.page
        p.title = "ElectroMart — Electronics, Elevated"
        p.bgcolor = PAPER
        p.padding = 0
        p.theme_mode = ft.ThemeMode.LIGHT
        p.theme = ft.Theme(color_scheme_seed=GOLD)
        try:
            p.window.width, p.window.height = 1280, 860
            p.window.min_width, p.window.min_height = 760, 600
        except Exception:
            pass

        self.screen = ft.Container(left=0, top=0, right=0, bottom=0, bgcolor=PAPER)
        self.cart_scrim = ft.Container(left=0, top=0, right=0, bottom=0, bgcolor=alpha(INK, 0.5),
                                       visible=False, on_click=lambda e: self.close_cart())
        self.cart_drawer = ft.Container(top=0, right=0, bottom=0, width=400, bgcolor=CARD, visible=False,
                                        border=ft.Border.only(left=ft.BorderSide(1, LINE)))

        # chat widget (lives above everything, on the auth screen too)
        self.chat_thread = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, auto_scroll=True, expand=True)
        self.chat_input = ft.TextField(
            hint_text="Type a message…", on_submit=lambda e: self.send_chat_from_input(), expand=True,
            border_radius=20, border_color=LINE, focused_border_color=GOLD, filled=True, fill_color=PAPER,
            text_size=13, color=INK, content_padding=ft.Padding.symmetric(horizontal=14, vertical=8))
        self.chat_panel = ft.Container(
            right=24, bottom=94, width=340, height=470, visible=False, bgcolor=CARD,
            border=ft.Border.all(1, LINE), border_radius=6, clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(blur_radius=40, color=alpha(INK, 0.28), offset=ft.Offset(0, 20)),
            content=ft.Column([
                ft.Container(
                    bgcolor=INK, padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                    content=ft.Row([
                        tower(16, 24, GOLD),
                        ft.Column([
                            txt("ElectroMart Support", 15, WHITE, "b", font="display"),
                            ft.Row([ft.Container(width=7, height=7, border_radius=4, bgcolor="#3FC97A"),
                                    mono("Quick Response — replies instantly", 10.5, alpha(WHITE, 0.7))],
                                   spacing=5),
                        ], spacing=2, expand=True),
                        ft.IconButton(ft.Icons.CLOSE, icon_color=WHITE, icon_size=18,
                                      on_click=lambda e: self.toggle_chat()),
                    ], spacing=10)),
                ft.Container(content=self.chat_thread, bgcolor=PAPER, expand=True,
                             padding=ft.Padding.all(14)),
                ft.Container(bgcolor=PAPER, padding=ft.Padding.only(left=14, right=14, bottom=10),
                             content=ft.Row(
                                 [ft.Container(
                                     content=txt(label, 12, INK), bgcolor=CARD, border=ft.Border.all(1, LINE),
                                     border_radius=999, padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                                     on_click=lambda e, k=key, l=label: self.page.run_task(self.chat_quick, k, l))
                                  for key, label in CHAT_QUICK],
                                 wrap=True, spacing=6, run_spacing=6)),
                ft.Container(
                    padding=ft.Padding.all(12), border=ft.Border.only(top=ft.BorderSide(1, LINE)),
                    content=ft.Row([self.chat_input,
                                    ft.IconButton(ft.Icons.SEND, icon_color=WHITE, bgcolor=WINE, icon_size=16,
                                                  on_click=lambda e: self.send_chat_from_input())], spacing=8)),
            ], spacing=0),
        )
        self.chat_badge = ft.Container(right=-3, top=-3, width=18, height=18, border_radius=9, bgcolor=WINE,
                                       alignment=ft.Alignment.CENTER, border=ft.Border.all(2, PAPER),
                                       content=mono("1", 10, WHITE, "b"))
        self.chat_icon = ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=WHITE, size=24)
        self.chat_fab = ft.Container(
            right=24, bottom=24, width=58, height=58, border_radius=29, bgcolor=INK,
            shadow=ft.BoxShadow(blur_radius=26, color=alpha(INK, 0.35), offset=ft.Offset(0, 10)),
            on_click=lambda e: self.toggle_chat(), tooltip="Quick response chat",
            content=ft.Stack([ft.Container(left=0, top=0, right=0, bottom=0, alignment=ft.Alignment.CENTER,
                                           content=self.chat_icon), self.chat_badge]))
        self.fill_chat_thread()

        p.add(ft.Stack([self.screen, self.cart_scrim, self.cart_drawer, self.chat_panel, self.chat_fab],
                       expand=True))

    # -------------------------------------------------------------------- chat
    def fill_chat_thread(self):
        self.chat_thread.controls = [self.chat_bubble(who, text) for who, text in self.chat_messages]

    @staticmethod
    def chat_bubble(who, text):
        bot = who == "bot"
        return ft.Row([ft.Container(
            content=txt(text, 13, INK if bot else WHITE, selectable=True),
            bgcolor=CARD if bot else INK, border=ft.Border.all(1, LINE) if bot else None,
            border_radius=ft.BorderRadius(12, 12, 3 if bot else 12, 12 if bot else 3),
            padding=ft.Padding.symmetric(horizontal=12, vertical=9), width=250 if len(text) > 34 else None,
        )], alignment=ft.MainAxisAlignment.START if bot else ft.MainAxisAlignment.END)

    def toggle_chat(self):
        self.chat_open = not self.chat_open
        self.chat_panel.visible = self.chat_open
        self.chat_icon.icon = ft.Icons.CLOSE if self.chat_open else ft.Icons.CHAT_BUBBLE_OUTLINE
        if self.chat_open:
            self.chat_unread = 0
        self.chat_badge.visible = self.chat_unread > 0 and not self.chat_open
        self.page.update()

    def add_chat(self, who, text):
        self.chat_messages.append((who, text))
        self.chat_thread.controls.append(self.chat_bubble(who, text))
        self.chat_thread.update()

    async def chat_quick(self, key, label):
        self.add_chat("user", label)
        await asyncio.sleep(0.45)
        self.add_chat("bot", CHAT_TOPIC_REPLIES.get(key, "Thanks — someone will follow up shortly!"))

    def send_chat_from_input(self):
        text = (self.chat_input.value or "").strip()
        if not text:
            return
        self.chat_input.value = ""
        self.chat_input.update()
        self.page.run_task(self.chat_free_text, text)

    async def chat_free_text(self, text):
        self.add_chat("user", text)
        await asyncio.sleep(0.45)
        self.add_chat("bot", chat_bot_reply(text))

    # -------------------------------------------------------------------- auth
    def show_auth(self):
        self.user = None
        self.cart_scrim.visible = self.cart_drawer.visible = False
        self.auth_flash = ft.Container(visible=False)
        self.auth_busy = False
        login = self.auth_mode == "login"

        self.a_name = field("Full name", hint="Ada Lovelace", width=340)
        self.a_email = field("Email", hint="you@example.com", width=340, keyboard=ft.KeyboardType.EMAIL,
                             on_submit=lambda e: self.submit_auth())
        self.a_phone = field("Phone (optional)", hint="080...", width=340, keyboard=ft.KeyboardType.PHONE)
        self.a_pass = field("Password", hint="At least 8 characters", password=True, width=340,
                            on_submit=lambda e: self.submit_auth())
        self.a_role = dropdown("Account type", [("buyer", "Buyer — I want to buy products"),
                                                ("seller", "Seller — I want to sell products")], "buyer", width=340)
        self.a_btn = button("Sign in" if login else "Create account", lambda e: self.submit_auth(), width=340)

        fields = [self.a_email, self.a_pass] if login else [self.a_name, self.a_email, self.a_phone, self.a_pass,
                                                            self.a_role]
        stripe = ft.Row([ft.Container(width=410 / 33, height=5, bgcolor=GOLD if i % 2 == 0 else WINE)
                         for i in range(33)], spacing=0)
        switch = ft.Row([
            txt("New here?" if login else "Already have an account?", 12.5, INK_DIM),
            link_button("Create an account" if login else "Sign in", lambda e: self.switch_auth(),
                        color=WINE, size=12.5),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
        hint = ft.Container(
            visible=login, border=ft.Border.all(1, LINE), border_radius=4,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            content=mono("Demo tip: register a fresh account for buyer/seller access. To view the Admin dashboard, "
                         "sign in with admin@electromart.demo / Admin#2026. Everything (accounts, orders, stock) "
                         "is saved to electromart_db.json next to this script.", 11))
        card = ft.Container(
            width=410, bgcolor=CARD, border=ft.Border.all(1, LINE), border_radius=6,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(blur_radius=46, color=alpha(INK, 0.14), offset=ft.Offset(0, 18)),
            content=ft.Column([
                stripe,
                ft.Container(padding=ft.Padding.only(left=34, right=34, top=26, bottom=30), content=ft.Column([
                    ft.Row([tower(20, 28, GOLD), display("ElectroMart", 23)], spacing=10),
                    mono("ÉLECTRONIQUE · CURATED TECH, DELIVERED ACROSS NIGERIA", 10, INK_DIM),
                    ft.Container(height=6),
                    self.auth_flash, *fields, self.a_btn, switch, hint,
                ], spacing=14)),
            ], spacing=0),
        )
        self.screen.content = ft.Stack([
            ft.Container(right=-50, bottom=-30, opacity=0.06, content=tower(420, 560, INK)),
            ft.Container(left=0, top=0, right=0, bottom=0, alignment=ft.Alignment.CENTER,
                         content=ft.Column([card], scroll=ft.ScrollMode.AUTO, tight=True,
                                           horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
        ], expand=True)
        self.screen.bgcolor = PAPER
        self.page.update()

    def switch_auth(self):
        self.auth_mode = "register" if self.auth_mode == "login" else "login"
        self.show_auth()

    def auth_error(self, message):
        self.auth_flash.content = flash(message)
        self.auth_flash.visible = True
        self.auth_flash.update()

    def submit_auth(self):
        self.auth_flash.visible = False
        try:
            if self.auth_mode == "login":
                user = self.db.login(self.a_email.value, self.a_pass.value)
            else:
                user = self.db.register(self.a_name.value, self.a_email.value, self.a_phone.value,
                                        self.a_pass.value, self.a_role.value)
        except ApiError as exc:
            self.auth_error(exc.message)
            return
        self.user = user
        self.cart = self.db.get_cart(user["id"])
        self.view = "shop"
        self.category, self.search = "All", ""
        self.last_order = None
        self.show_shell()

    def logout(self):
        self.user = None
        self.cart, self.orders, self.last_order = [], [], None
        self.cart_open = False
        self.auth_mode = "login"
        self.show_auth()

    # ------------------------------------------------------------------- shell
    def show_shell(self):
        self.search_field = ft.TextField(
            hint_text="Search products…", prefix_icon=ft.Icons.SEARCH, value=self.search, dense=True,
            on_change=self.on_search, on_submit=lambda e: self.go("shop") if self.view != "shop" else None,
            border_color=LINE, focused_border_color=GOLD, border_radius=4, filled=True, fill_color=CARD,
            text_size=13.5, color=INK, content_padding=ft.Padding.symmetric(horizontal=8, vertical=8), expand=True)
        self.header = ft.Container(bgcolor=alpha(PAPER, 0.94), border=ft.Border.only(bottom=ft.BorderSide(1, LINE)),
                                   padding=ft.Padding.symmetric(horizontal=26, vertical=12))
        self.body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self.screen.content = ft.Column([self.header, self.body], spacing=0, expand=True)
        self.screen.bgcolor = PAPER
        self.fill_header()
        self.fill_body()
        self.page.update()

    def fill_header(self):
        def nav(label, view):
            active = self.view == view
            return ft.Container(
                content=mono(label.upper(), 12, INK if active else INK_DIM), on_click=lambda e: self.go(view),
                bgcolor=CARD if active else None, border=ft.Border.all(1, LINE if active else "transparent"),
                border_radius=4, padding=ft.Padding.symmetric(horizontal=12, vertical=7))

        tabs = [nav("Electronics", "shop"), nav("My orders", "orders"), nav("Track package", "track")]
        if self.user["role"] == "seller":
            tabs += [nav("Sell", "sell"), nav("Analytics", "analytics")]
        if self.user["role"] == "admin":
            tabs.append(nav("Admin", "admin"))

        self.cart_badge_text = mono(str(self.cart_count()), 10, WHITE, "b")
        self.cart_badge = ft.Container(content=self.cart_badge_text, bgcolor=WINE, border_radius=999,
                                       padding=ft.Padding.symmetric(horizontal=6, vertical=1),
                                       visible=self.cart_count() > 0)
        cart_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=17, color=INK), txt("Cart", 13),
                            self.cart_badge], spacing=6, tight=True),
            border=ft.Border.all(1, LINE), border_radius=4, on_click=lambda e: self.open_cart(),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8))
        role = "Seller account" if self.user["role"] == "seller" else \
            "Admin" if self.user["role"] == "admin" else "Buyer account"
        signout = ft.Container(content=txt("Sign out", 13), border=ft.Border.all(1, LINE), border_radius=4,
                               padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                               on_click=lambda e: self.logout())
        self.header.content = ft.Row([
            ft.Row([tower(18, 26, GOLD), display("ElectroMart", 20)], spacing=10),
            ft.Row(tabs, spacing=4),
            ft.Container(content=self.search_field, expand=True),
            mono(f"Hello, {self.user['name']} · {role}", 11.5),
            cart_btn, signout,
        ], spacing=18, vertical_alignment=ft.CrossAxisAlignment.CENTER, wrap=True, run_spacing=8)

    def go(self, view):
        self.view = view
        if view == "orders" and not self.last_order:
            self.orders = self.db.orders_for(self.user["id"])
        elif view == "sell":
            self.my_listings = self.db.my_listings(self.user["id"])
        elif view == "analytics":
            self.analytics = self.safe(lambda: self.db.seller_analytics(self.user["id"]))
        elif view == "admin":
            self.load_admin()
        self.fill_header()
        self.fill_body()
        self.page.update()

    def refresh_view(self):
        self.fill_body()
        self.body.update()

    @staticmethod
    def safe(fn):
        try:
            return fn()
        except ApiError:
            return None

    def fill_body(self):
        builders = {"shop": self.view_shop, "orders": self.view_orders, "track": self.view_track,
                    "sell": self.view_sell, "analytics": self.view_analytics, "admin": self.view_admin}
        content = builders.get(self.view, self.view_shop)()
        self.body.controls = [
            ft.Container(padding=ft.Padding(26, 30, 26, 40), content=content),
            self.footer(),
        ]

    # ------------------------------------------------------------------ footer
    def footer(self):
        def doc(label, key):
            return link_button(label, lambda e: self.open_info(key))

        def row(items):
            return ft.Row(items, alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=2, run_spacing=0)

        return ft.Container(
            border=ft.Border.only(top=ft.BorderSide(1, LINE)), padding=ft.Padding.all(28),
            content=ft.Column([
                ft.Row([txt("Customer care number for WhatsApp only:", 13.5),
                        link_button("07043941075", color=WINE, size=13.5, url="https://wa.me/2347043941075")],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                row([doc("Terms and Conditions", "terms"), doc("Privacy Policy", "privacy"),
                     doc("Return and Refund Policy", "returns"), doc("Requirements", "requirements"),
                     doc("Standards & Certification", "standards")]),
                row([mono("PROJECT DOCS", 11, WINE), doc("Problem Statement", "problemStatement"),
                     doc("Feasibility Study", "feasibility"), doc("System Requirements", "systemRequirements"),
                     doc("Design Overview", "design"), doc("Testing Plan", "testing"),
                     doc("Deployment Plan", "deployment")]),
                mono("ElectroMart — a demo marketplace built for a software engineering coursework exercise. "
                     "Not a real store. Prices shown for Konga, Jumia, AliExpress, Slot, and Jiji are "
                     "illustrative estimates for comparison purposes only, not live data pulled from those "
                     "retailers.", 11, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8))

    # --------------------------------------------------------------- info docs
    def open_info(self, key):
        doc = POLICY.get(key)
        if not doc:
            return
        dlg = ft.AlertDialog(
            bgcolor=CARD, shape=ft.RoundedRectangleBorder(radius=8),
            title=ft.Row([display(doc["title"], 20, expand=True),
                          ft.IconButton(ft.Icons.CLOSE, icon_size=18, on_click=lambda e: self.page.pop_dialog())]),
            content=ft.Container(width=680, height=500, content=ft.Column([
                ft.Markdown(doc["body"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            auto_follow_links=True)], scroll=ft.ScrollMode.AUTO)),
        )
        self.page.show_dialog(dlg)

    # -------------------------------------------------------------------- shop
    def view_shop(self):
        hero = ft.Container(
            height=190, border_radius=8, clip_behavior=ft.ClipBehavior.HARD_EDGE,
            gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
                                       colors=[INK, "#2A3763"]),
            content=ft.Stack([
                ft.Container(left=-60, top=-90, width=280, height=280, border_radius=140,
                             bgcolor=alpha(GOLD, 0.22)),
                ft.Container(right=20, bottom=-16, opacity=0.9, content=tower(165, 210, "#F3EFE2")),
                ft.Container(left=30, top=0, bottom=0, width=520, alignment=ft.Alignment.CENTER_LEFT,
                             content=ft.Column([
                                 mono("NOUVELLE COLLECTION", 11, GOLD),
                                 display("Electronics, elevated.", 30, "#F3EFE2"),
                                 txt("Curated phones, laptops, audio and smart-home gear — sourced carefully, "
                                     "delivered fast, tracked every step of the way.", 14, "#D9D6C8"),
                             ], spacing=6, tight=True)),
            ]))
        self.cat_col = ft.Column(spacing=3)
        self.count_text = mono("", 11.5)
        self.grid_holder = ft.Container()
        self.fill_shop()
        sidebar = ft.Container(width=210, content=ft.Column([
            mono("CATEGORIES", 10.5), self.cat_col], spacing=10))
        return ft.Column([
            hero, ft.Container(height=14), section_head("Electronics"),
            ft.Row([sidebar, ft.Column([self.count_text, self.grid_holder], expand=True, spacing=12)],
                   vertical_alignment=ft.CrossAxisAlignment.START, spacing=28),
        ], spacing=6)

    def fill_shop(self):
        products, cats = self.db.products(self.category, self.search)

        def cat_btn(label, key):
            active = self.category == key
            return ft.Container(
                content=mono(label, 12.5, INK if active else INK_DIM, "b" if active else None),
                bgcolor=CARD if active else None, border_radius=4, on_click=lambda e: self.set_category(key),
                border=ft.Border(left=ft.BorderSide(3, GOLD if active else "transparent"),
                                 top=ft.BorderSide(1, LINE if active else "transparent"),
                                 right=ft.BorderSide(1, LINE if active else "transparent"),
                                 bottom=ft.BorderSide(1, LINE if active else "transparent")),
                padding=ft.Padding.symmetric(horizontal=10, vertical=8))

        self.cat_col.controls = [cat_btn("All products", "All")] + [cat_btn(c, c) for c in cats]
        n = len(products)
        self.count_text.value = f"{n} item{'' if n == 1 else 's'} found"
        if products:
            self.grid_holder.content = ft.Row([self.product_card(p) for p in products], wrap=True,
                                              spacing=16, run_spacing=18)
        else:
            self.grid_holder.content = ft.Container(
                padding=ft.Padding.symmetric(vertical=60), alignment=ft.Alignment.CENTER,
                content=mono("No products match your search. Try a different category or keyword.", 13))

    def refresh_shop(self):
        self.fill_shop()
        self.cat_col.update()
        self.count_text.update()
        self.grid_holder.update()

    def set_category(self, cat):
        self.category = cat
        if self.view == "shop":
            self.refresh_shop()

    def on_search(self, e):
        self.search = e.control.value or ""
        if self.view == "shop":
            self.refresh_shop()

    def product_card(self, p):
        comp = cheapest_competitor(p)
        out = p["stock"] == 0
        extras = []
        if p["stock"] <= 5:
            extras.append(mono("Sold out" if out else f"Only {p['stock']} left", 10, WINE, "b"))
        return ft.Container(
            width=252, padding=14, bgcolor=CARD, border=ft.Border.all(1, LINE), border_radius=6,
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT), on_hover=hover_lift,
            on_click=lambda e, pid=p["id"]: self.open_product(pid),
            content=ft.Column([
                ft.Row([mono(p["sku"], 9.5, PAPER)], alignment=ft.MainAxisAlignment.END),
                ft.Container(height=64, alignment=ft.Alignment.CENTER, bgcolor=PAPER, border_radius=4,
                             border=ft.Border.all(1, LINE_SOFT), content=ft.Text(p["icon"], size=34)),
                mono((p["category"] + (f" · Sold by {p['sellerName']}" if p.get("sellerName") else "")).upper(),
                     10, WINE),
                txt(p["name"], 13.5, INK, "s"),
                *extras,
                ft.Row([mono(comp["name"].upper(), 9.5), mono(fmt(comp["price"]), 11, INK_DIM,
                                                                style=ft.TextStyle(
                                                                    decoration=ft.TextDecoration.LINE_THROUGH))],
                       spacing=5),
                cert_badge("SON · ISO 9001"),
                ft.Divider(height=8, color=LINE),
                ft.Row([mono(fmt(p["price"]), 14.5, GOLD_DIM, "b"),
                        button("Out of stock" if out else "Add", lambda e, pid=p["id"]: self.add_to_cart(pid),
                               kind="ink", small=True, disabled=out)],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=7, tight=True),
        )

    # ----------------------------------------------------------- product modal
    def open_product(self, pid):
        p = self.db.product_by_id(pid)
        if not p:
            return
        if self.product_dlg is not None:  # switching sellers: reuse the open dialog
            self.product_dlg_pid = pid
            self.product_dlg.content = self.product_content(p)
            self.product_dlg.update()
            return
        self.product_dlg_pid = pid
        self.product_dlg = ft.AlertDialog(
            bgcolor=CARD, shape=ft.RoundedRectangleBorder(radius=8), content_padding=0,
            content=self.product_content(p), on_dismiss=self.on_product_dismiss)
        self.page.show_dialog(self.product_dlg)

    def on_product_dismiss(self, e=None):
        self.product_dlg = None
        self.product_dlg_pid = None

    def close_product(self):
        self.product_dlg = None
        self.product_dlg_pid = None
        self.page.pop_dialog()

    def product_content(self, p):
        comp = cheapest_competitor(p)
        save = round((1 - p["price"] / comp["price"]) * 100)
        in_cart = next((l["qty"] for l in self.cart if l["productId"] == p["id"]), 0)
        others = sorted(
            [q for q in self.db.all_products()
             if q["id"] != p["id"] and q["name"].strip().lower() == p["name"].strip().lower()],
            key=lambda q: q["price"])
        cheapest_internal = min([p["price"]] + [q["price"] for q in others])

        def mp_row(name, price, us=False, badge=False, on_click=None):
            label = [txt(name, 12.5, INK if us else INK_DIM, "b" if us else None, font="mono")]
            if badge:
                label.append(ft.Container(content=mono("LOWEST PRICE", 9, WHITE, "b"), bgcolor=WINE,
                                          border_radius=3, padding=ft.Padding.symmetric(horizontal=6, vertical=2)))
            return ft.Container(
                content=ft.Row([ft.Row(label, spacing=8, expand=True),
                                mono(fmt(price), 14 if us else 12.5, GOLD_DIM if us else INK_DIM, "b" if us else None)]),
                bgcolor=alpha(GOLD, 0.12) if us else None, border_radius=4, on_click=on_click,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8))

        market = panel(ft.Column([
            mono("PRICE COMPARISON ACROSS MARKETPLACES", 10.5),
            mp_row("ElectroMart", p["price"], us=True, badge=True),
            *[mp_row(c["name"], c["price"]) for c in competitor_prices_for(p)],
            txt("Illustrative estimates for comparison only — not live prices pulled from these marketplaces.",
                10.5, INK_DIM),
        ], spacing=4), bgcolor=PAPER, padding=14)

        internal = panel(ft.Column([
            mono("OTHER ELECTROMART SELLERS OF THIS PRODUCT", 10.5),
            mp_row(seller_label(p), p["price"], us=True, badge=bool(others) and p["price"] == cheapest_internal),
            *[mp_row(seller_label(q), q["price"], badge=q["price"] == cheapest_internal,
                     on_click=lambda e, qid=q["id"]: self.open_product(qid)) for q in others],
            txt("Tap another seller to view their listing." if others else
                "No other ElectroMart sellers are currently listing this exact product.", 10.5, INK_DIM),
        ], spacing=4), bgcolor=PAPER, padding=14)

        specs = panel(ft.Column([spec_row(k, str(v)) for k, v in (p.get("specs") or {}).items()] or
                                [mono("No specifications listed.", 11.5)], spacing=4), padding=ft.Padding.all(12))
        add_row = ft.Row([
            button("Out of stock" if p["stock"] == 0 else "Add to cart", lambda e: self.add_to_cart(p["id"]),
                   disabled=p["stock"] == 0),
            mono(f"In stock: {p['stock']}" if p["stock"] else "", 12),
            mono(f"· {in_cart} in your cart" if in_cart else "", 12, WINE, "b"),
        ], spacing=14)
        return ft.Container(width=640, content=ft.Column([
            ft.Container(padding=ft.Padding.all(26), content=ft.Column([
                ft.Row([
                    ft.Container(width=170, height=170, alignment=ft.Alignment.CENTER, bgcolor=PAPER, border_radius=6,
                                 border=ft.Border.all(1, LINE_SOFT), content=ft.Text(p["icon"], size=60)),
                    ft.Column([
                        mono((f"{p['category']} · {p['sku']}" +
                              (f" · Sold by {p['sellerName']}" if p.get("sellerName") else "")).upper(), 10.5, WINE),
                        display(p["name"], 21),
                        mono(f"Cheapest elsewhere: {comp['name']} {fmt(comp['price'])}", 12),
                        ft.Row([mono(fmt(p["price"]), 19, GOLD_DIM, "b"), txt(f"Save {save}%", 12, WINE, "s")],
                               spacing=10),
                        txt(p["description"], 13.5, INK_DIM),
                    ], spacing=6, expand=True),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=18, on_click=lambda e: self.close_product()),
                ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=22),
                market, internal, specs,
                ft.Row([cert_badge("SONCAP Certified"), cert_badge("ISO 9001"),
                        link_button("View standards & certification info",
                                    lambda e: self.open_info("standards"), color=WINE, size=11)],
                       wrap=True, spacing=8),
                add_row,
            ], spacing=16)),
        ], scroll=ft.ScrollMode.AUTO, tight=True))

    # -------------------------------------------------------------------- cart
    def cart_count(self):
        return sum(l["qty"] for l in self.cart)

    def cart_subtotal(self):
        return sum(l["price"] * l["qty"] for l in self.cart)

    def persist_cart(self):
        if self.user:
            self.db.set_cart(self.user["id"], self.cart)
        self.cart_badge_text.value = str(self.cart_count())
        self.cart_badge.visible = self.cart_count() > 0
        self.cart_badge.update()
        if self.cart_open:
            self.fill_cart_drawer()
            self.cart_drawer.update()
        if self.product_dlg is not None and self.product_dlg_pid:
            p = self.db.product_by_id(self.product_dlg_pid)
            if p:
                self.product_dlg.content = self.product_content(p)
                self.product_dlg.update()

    def add_to_cart(self, pid):
        p = self.db.product_by_id(pid)
        if not p or p["stock"] <= 0:
            return
        line = next((l for l in self.cart if l["productId"] == pid), None)
        if line:
            if line["qty"] < p["stock"]:
                line["qty"] += 1
            line["stock"] = p["stock"]
        else:
            self.cart.append({"productId": pid, "name": p["name"], "price": p["price"], "qty": 1,
                              "stock": p["stock"]})
        self.persist_cart()

    def change_qty(self, pid, delta):
        line = next((l for l in self.cart if l["productId"] == pid), None)
        if not line:
            return
        line["qty"] += delta
        if line["qty"] <= 0:
            self.cart = [l for l in self.cart if l["productId"] != pid]
        elif line["qty"] > line["stock"]:
            line["qty"] = line["stock"]
        self.persist_cart()

    def remove_line(self, pid):
        self.cart = [l for l in self.cart if l["productId"] != pid]
        self.persist_cart()

    def open_cart(self):
        self.cart_open = True
        self.fill_cart_drawer()
        self.cart_scrim.visible = self.cart_drawer.visible = True
        self.page.update()

    def close_cart(self):
        self.cart_open = False
        self.cart_scrim.visible = self.cart_drawer.visible = False
        self.page.update()

    def fill_cart_drawer(self):
        sub = self.cart_subtotal()
        ship = 0 if sub >= FREE_SHIPPING_FROM or sub == 0 else SHIPPING_FEE

        def line(l):
            return ft.Container(
                padding=ft.Padding.symmetric(vertical=10), border=ft.Border.only(bottom=ft.BorderSide(1, LINE)),
                content=ft.Row([
                    ft.Column([txt(l["name"], 13, INK, "s"), mono(f"{fmt(l['price'])} each", 11)], spacing=2,
                              expand=True),
                    ft.Row([
                        ft.IconButton(ft.Icons.REMOVE, icon_size=14, tooltip="Decrease quantity",
                                      on_click=lambda e, pid=l["productId"]: self.change_qty(pid, -1)),
                        mono(str(l["qty"]), 13, INK, "b"),
                        ft.IconButton(ft.Icons.ADD, icon_size=14, tooltip="Increase quantity",
                                      on_click=lambda e, pid=l["productId"]: self.change_qty(pid, 1)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=WINE, tooltip="Remove",
                                      on_click=lambda e, pid=l["productId"]: self.remove_line(pid)),
                    ], spacing=0, tight=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER))

        def sum_row(label, value, total=False):
            return ft.Row([mono(label, 15 if total else 13, INK if total else INK_DIM, "b" if total else None,
                                expand=True),
                           mono(value, 15 if total else 13, INK if total else INK_DIM, "b" if total else None)])

        items = [line(l) for l in self.cart] or [ft.Container(
            padding=ft.Padding.symmetric(vertical=44), alignment=ft.Alignment.CENTER,
            content=mono("Your cart is empty. Browse the boutique to add items.", 13))]
        self.cart_drawer.content = ft.Column([
            ft.Container(padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                         border=ft.Border.only(bottom=ft.BorderSide(1, LINE)),
                         content=ft.Row([display("Your cart", 18),
                                         ft.IconButton(ft.Icons.CLOSE, icon_size=18,
                                                       on_click=lambda e: self.close_cart())],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
            ft.Container(expand=True, padding=ft.Padding.symmetric(horizontal=20, vertical=6),
                         content=ft.Column(items, scroll=ft.ScrollMode.AUTO)),
            ft.Container(padding=20, border=ft.Border.only(top=ft.BorderSide(1, LINE)), content=ft.Column([
                sum_row("Subtotal", fmt(sub)),
                sum_row("Shipping", "Free" if ship == 0 else fmt(ship)),
                sum_row("Total", fmt(sub + ship), total=True),
                button("Checkout", lambda e: self.open_checkout(), width=360, disabled=not self.cart),
            ], spacing=8)),
        ], spacing=0)

    # ---------------------------------------------------------------- checkout
    def open_checkout(self):
        self.checkout_error = ""
        self.close_cart()
        self.checkout_dlg = ft.AlertDialog(
            bgcolor=CARD, shape=ft.RoundedRectangleBorder(radius=8), content_padding=0,
            content=self.checkout_content())
        self.page.show_dialog(self.checkout_dlg)

    def refresh_checkout(self):
        if self.checkout_dlg is not None:
            self.checkout_dlg.content = self.checkout_content()
            self.checkout_dlg.update()

    def set_attr(self, name):
        return lambda e: setattr(self, name, e.control.value or "")

    def select_payment(self, method):
        self.payment_method = method
        self.refresh_checkout()

    def checkout_content(self):
        sub = self.cart_subtotal()
        ship = 0 if sub >= FREE_SHIPPING_FROM else SHIPPING_FEE
        savings = sum(compare_price_for(l["price"]) * l["qty"] for l in self.cart) - sub
        methods = [("card", "💳 Debit / credit card"), ("transfer", "🏦 Bank transfer"),
                   ("cod", "📦 Cash on delivery")]

        def pay_opt(key, label):
            active = self.payment_method == key
            return ft.Container(
                content=txt(label, 13), on_click=lambda e: self.select_payment(key),
                bgcolor="#FBF6EA" if active else None, border_radius=5,
                border=ft.Border.all(1, GOLD if active else LINE), padding=ft.Padding.symmetric(horizontal=13, vertical=11))

        extra = []
        if self.payment_method == "card":
            extra = [
                field("Name on card", self.card_name, self.set_attr("card_name"), hint="As printed on the card"),
                field("Card number", self.card_number, self.set_attr("card_number"), hint="1234 5678 9012 3456",
                      keyboard=ft.KeyboardType.NUMBER, max_length=19),
                ft.Row([field("Expiry (MM/YY)", self.card_expiry, self.set_attr("card_expiry"), hint="MM/YY",
                              max_length=5, expand=True),
                        field("CVV", self.card_cvv, self.set_attr("card_cvv"), hint="123", password=True,
                              keyboard=ft.KeyboardType.NUMBER, max_length=4, expand=True)], spacing=12),
            ]
        elif self.payment_method == "transfer":
            extra = [
                panel(ft.Column([spec_row("Bank", BANK_TRANSFER_DETAILS["bankName"]),
                                 spec_row("Account name", BANK_TRANSFER_DETAILS["accountName"]),
                                 spec_row("Account number", BANK_TRANSFER_DETAILS["accountNumber"])], spacing=4),
                      padding=12),
                mono('Transfer the order total to the account above, then tap "Place order". '
                     "Your order is confirmed once payment reflects.", 10.5),
            ]
        form = ft.Column([
            field("Delivery address", self.address, self.set_attr("address"), hint="Street, city, state",
                  multiline=True),
            field("Phone number", self.phone, self.set_attr("phone"), hint="080...", keyboard=ft.KeyboardType.PHONE),
            mono("PAYMENT METHOD", 10.5),
            *[pay_opt(k, l) for k, l in methods], *extra,
        ], spacing=12, expand=True)

        def sum_row(label, value, total=False, color=None):
            c = color or (INK if total else INK_DIM)
            return ft.Row([mono(label, 15 if total else 13, c, "b" if total else None, expand=True),
                           mono(value, 15 if total else 13, c, "b" if total else None)])

        summary = panel(ft.Column([
            sum_row("Subtotal", fmt(sub)), sum_row("Shipping", "Free" if ship == 0 else fmt(ship)),
            sum_row("Total", fmt(sub + ship), total=True),
            sum_row("Est. savings", fmt(savings), color=GOLD_DIM) if savings > 0 else ft.Container(),
            mono("Best Price Guarantee — found this item cheaper elsewhere? Show us and we'll match it. Savings "
                 "shown are estimates vs. Konga, Jumia, AliExpress, Slot, and Jiji pricing, not live competitor "
                 "data.", 10),
            button("Placing order…" if self.checkout_busy else "Place order", lambda e: self.place_order(),
                   width=290, disabled=self.checkout_busy),
        ], spacing=8), width=320)
        return ft.Container(width=760, padding=26, content=ft.Column([
            ft.Row([display("Checkout", 21),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=18, on_click=lambda e: self.page.pop_dialog())],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            flash(self.checkout_error) if self.checkout_error else ft.Container(),
            ft.Row([form, summary], vertical_alignment=ft.CrossAxisAlignment.START, spacing=26),
        ], scroll=ft.ScrollMode.AUTO, tight=True, spacing=12))

    def checkout_fail(self, message):
        self.checkout_error = message
        self.refresh_checkout()

    def place_order(self):
        if not self.address.strip():
            return self.checkout_fail("Please enter a delivery address.")
        if not self.phone.strip():
            return self.checkout_fail("Please enter a phone number for the delivery.")
        if self.payment_method == "card":
            digits = re.sub(r"\s+", "", self.card_number)
            if not self.card_name.strip():
                return self.checkout_fail("Please enter the name on the card.")
            if not re.fullmatch(r"\d{13,19}", digits):
                return self.checkout_fail("Please enter a valid card number.")
            if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", self.card_expiry.strip()):
                return self.checkout_fail("Please enter the card expiry as MM/YY.")
            if not re.fullmatch(r"\d{3,4}", self.card_cvv.strip()):
                return self.checkout_fail("Please enter a valid CVV.")
        try:
            order = self.db.place_order(
                self.user["id"], [{"productId": l["productId"], "qty": l["qty"]} for l in self.cart],
                self.payment_method, self.address, self.phone)
        except ApiError as exc:
            return self.checkout_fail(exc.message)
        self.last_order = order
        self.cart = []
        self.db.set_cart(self.user["id"], [])
        self.cart_badge_text.value, self.cart_badge.visible = "0", False
        self.address = self.phone = self.card_name = self.card_number = self.card_expiry = self.card_cvv = ""
        self.checkout_dlg = None
        self.page.pop_dialog()
        self.go("orders")

    # ------------------------------------------------------------ orders views
    def steps_timeline(self, steps, index):
        rows = []
        for i, label in enumerate(steps):
            done, current = i < index, i == index
            color = GOLD if done else WINE if current else WHITE
            border = GOLD if done else WINE if current else LINE
            rows.append(ft.Row([
                ft.Column([
                    ft.Container(width=18, height=18, border_radius=9, bgcolor=color,
                                 border=ft.Border.all(2, border)),
                    ft.Container(width=2, height=22, bgcolor=LINE) if i < len(steps) - 1 else ft.Container(),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                txt(label, 13, INK if (done or current) else INK_DIM, "s"),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START))
        return ft.Column(rows, spacing=0)

    def apply_updated(self, order):
        self.orders = [order if o["trackingId"] == order["trackingId"] else o for o in self.orders]
        if self.last_order and self.last_order["trackingId"] == order["trackingId"]:
            self.last_order = order
        if self.track_result and self.track_result["trackingId"] == order["trackingId"]:
            self.track_result.update({
                "feedback": order["feedback"], "returnRequest": order["returnRequest"],
                "trackingStepIndex": order["trackingStepIndex"], "deliveredAt": order["deliveredAt"]})

    def payment_confirm_block(self, o):
        if o["paid"] or not o.get("rrr"):
            return ft.Container()
        tid = o["trackingId"]
        err = self.rrr_errors.get(tid)

        def on_confirm(e):
            rrr = (self.rrr_drafts.get(tid) or "").strip()
            if not rrr:
                self.rrr_errors[tid] = "Enter the RRR number to confirm your payment."
            else:
                try:
                    self.apply_updated(self.db.confirm_payment(self.user["id"], tid, rrr))
                    self.rrr_drafts.pop(tid, None)
                    self.rrr_errors.pop(tid, None)
                except ApiError as exc:
                    self.rrr_errors[tid] = exc.message
            self.refresh_view()

        return ft.Column([
            panel(spec_row("RRR (Remita Retrieval Reference)", o["rrr"]), padding=12),
            field("Confirm payment — enter RRR", self.rrr_drafts.get(tid, ""),
                  lambda e: self.rrr_drafts.__setitem__(tid, e.control.value or ""),
                  hint="Enter the RRR above to confirm", on_submit=on_confirm),
            flash(err) if err else ft.Container(),
            button("Confirm payment", on_confirm),
        ], spacing=10)

    def delivery_feedback(self, o):
        steps = o["trackingSteps"]
        if not (o["trackingStepIndex"] == len(steps) - 1 and o.get("deliveredAt")):
            return ft.Container()
        tid = o["trackingId"]
        err = self.return_errors.get(tid)

        def answer(satisfied):
            try:
                self.apply_updated(self.db.feedback(self.user["id"], tid, satisfied))
                self.return_errors.pop(tid, None)
                if not satisfied:
                    self.return_forms[tid] = {"type": "change_of_mind", "reason": "", "notes": "", "agree": False}
            except ApiError as exc:
                self.return_errors[tid] = exc.message
            self.refresh_view()

        if not o.get("feedback"):
            return ft.Column([
                panel(txt("Delivered — are you satisfied with this order?", 13, INK, "b"), padding=12),
                flash(err) if err else ft.Container(),
                ft.Row([button("🙂 Yes, satisfied", lambda e: answer(True)),
                        button("🙁 Not satisfied", lambda e: answer(False), kind="ghost")], spacing=10),
            ], spacing=8)
        if o["feedback"]["satisfied"]:
            return flash("Thanks for letting us know you're happy with this order! 🎉", ok=True)

        rr = o.get("returnRequest")
        if rr:
            kind = "Damaged / faulty / incorrect item" if rr["type"] == "damaged_faulty" else "Change of mind"
            return ft.Column([
                panel(ft.Column([txt("Return & refund requested", 13, WINE, "b"), spec_row("Type", kind),
                                 spec_row("Reason", rr["reason"]), spec_row("Status", rr["status"])],
                                spacing=4), padding=12),
                flash("We've logged your return request. Reach out on our WhatsApp customer care line to track it "
                      "— approved returns are refunded within 5–10 business days after we receive and inspect "
                      "the item, per our Return & Refund Policy."),
                link_button("Return & Refund Policy", lambda e: self.open_info("returns"), color=WINE),
            ], spacing=8)

        if (time.time() - o["deliveredAt"]) / 86400 > RETURN_WINDOW_DAYS:
            return ft.Column([flash("Sorry, this order is outside the 7-day return & refund window."),
                              link_button("Return & Refund Policy", lambda e: self.open_info("returns"),
                                          color=WINE)], spacing=4)

        form = self.return_forms.setdefault(tid, {"type": "change_of_mind", "reason": "", "notes": "",
                                                  "agree": False})

        def submit(e):
            if not form["reason"].strip():
                self.return_errors[tid] = "Please tell us briefly what went wrong."
            elif not form["agree"]:
                self.return_errors[tid] = "Please confirm the item meets our Return & Refund Policy conditions."
            else:
                try:
                    self.apply_updated(self.db.return_request(
                        self.user["id"], tid, form["type"], form["reason"], form["notes"], form["agree"]))
                    self.return_forms.pop(tid, None)
                    self.return_errors.pop(tid, None)
                except ApiError as exc:
                    self.return_errors[tid] = exc.message
            self.refresh_view()

        return ft.Column([
            panel(txt("Sorry to hear that. Let's start a return & refund request.", 13, WINE, "b"), padding=12),
            dropdown("What's the issue?", [("change_of_mind", "Change of mind"),
                                           ("damaged_faulty", "Damaged, faulty, or incorrect item")],
                     form["type"], lambda e: form.__setitem__("type", e.control.value)),
            field("Briefly, what went wrong?", form["reason"], lambda e: form.__setitem__("reason", e.control.value or ""),
                  hint="e.g. Item arrived with a cracked screen"),
            field("Additional notes (optional)", form["notes"], lambda e: form.__setitem__("notes", e.control.value or ""),
                  hint="Anything else we should know"),
            ft.Checkbox(label="The item is unused, in its original packaging with all accessories, and I have "
                              "proof of purchase, per the Return & Refund Policy.",
                        value=form["agree"], active_color=GOLD,
                        on_change=lambda e: form.__setitem__("agree", bool(e.control.value))),
            link_button("Read the Return & Refund Policy", lambda e: self.open_info("returns"), color=WINE),
            flash(err) if err else ft.Container(),
            button("Submit return & refund request", submit),
        ], spacing=10)

    def view_orders(self):
        if self.last_order:
            o = self.last_order
            return ft.Column([
                section_head("Order confirmed"),
                panel(ft.Column([
                    flash("Thank you! Your order has been placed.", ok=True),
                    spec_row("Tracking ID", o["trackingId"]),
                    spec_row("Delivery address", o["address"] or "—"), spec_row("Phone", o["phone"] or "—"),
                    spec_row("Total", fmt(o["total"])), spec_row("Payment", o["paymentMethod"]),
                    self.payment_confirm_block(o),
                    self.steps_timeline(o["trackingSteps"], o["trackingStepIndex"]),
                    self.delivery_feedback(o),
                    ft.Row([button("Refresh status", lambda e: self.refresh_orders(), kind="ghost"),
                            button("View all orders", lambda e: self.dismiss_confirmation(), kind="ghost")],
                           spacing=10),
                ], spacing=10), width=580),
            ], spacing=6)
        cards = []
        for o in self.orders:
            lines = [spec_row(f"{i['name']}" + (f" (sold by {i['sellerName']})" if i.get("sellerName") else "") +
                              f" × {i['qty']}", fmt(i["price"] * i["qty"])) for i in o["items"]]
            extra = []
            if o["paid"] or not o.get("rrr"):
                extra = [self.steps_timeline(o["trackingSteps"], o["trackingStepIndex"]), self.delivery_feedback(o)]
            date = time.strftime("%d %b %Y", time.localtime(o["createdAt"]))
            cards.append(panel(ft.Column([
                ft.Row([mono(f"{o['trackingId']} · {date}", 11.5, expand=True),
                        pill(o["status"], WINE if o["status"] == "Pending" else GOLD)]),
                *lines, spec_row("Delivery", o["address"] or "—"), spec_row("Phone", o["phone"] or "—"),
                spec_row("Total", fmt(o["total"]), bold=True),
                self.payment_confirm_block(o), *extra,
            ], spacing=6)))
        if not cards:
            cards = [ft.Container(padding=ft.Padding.symmetric(vertical=60), alignment=ft.Alignment.CENTER,
                                  content=mono("You haven't placed any orders yet.", 13))]
        return ft.Column([
            section_head("My orders", button("Refresh status", lambda e: self.refresh_orders(), kind="ghost",
                                             small=True)),
            *cards,
        ], spacing=12)

    def refresh_orders(self):
        if self.last_order:
            fresh = next((o for o in self.db.orders_for(self.user["id"])
                          if o["trackingId"] == self.last_order["trackingId"]), None)
            if fresh:
                self.last_order = fresh
        else:
            self.orders = self.db.orders_for(self.user["id"])
        self.refresh_view()

    def dismiss_confirmation(self):
        self.last_order = None
        self.orders = self.db.orders_for(self.user["id"])
        self.refresh_view()

    # ------------------------------------------------------------------- track
    def view_track(self):
        self.track_field = field("Tracking ID", self.track_input, lambda e: setattr(self, "track_input", e.control.value or ""),
                                 hint="e.g. EMP-A1B2C3", on_submit=lambda e: self.do_track())
        r = self.track_result
        result = []
        if r:
            result = [ft.Container(height=6),
                      spec_row("Tracking ID", r["trackingId"]), spec_row("Items", str(r["itemCount"])),
                      self.steps_timeline(r["trackingSteps"], r["trackingStepIndex"]),
                      self.delivery_feedback(r)]
        return ft.Column([
            section_head("Track package"),
            panel(ft.Column([
                self.track_field,
                flash(self.track_error) if self.track_error else ft.Container(),
                button("Track shipment", lambda e: self.do_track()),
                *result,
            ], spacing=12), width=520),
        ], spacing=6)

    def do_track(self):
        self.track_error, self.track_result = "", None
        try:
            self.track_result = self.db.track((self.track_input or "").strip().upper())
        except ApiError as exc:
            self.track_error = exc.message
        self.refresh_view()

    # -------------------------------------------------------------------- sell
    def view_sell(self):
        ref_cards = ft.Row([
            ft.Container(
                width=100, padding=ft.Padding.symmetric(horizontal=8, vertical=12), bgcolor=CARD,
                border=ft.Border.all(1, LINE), border_radius=6, on_hover=hover_lift,
                animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                on_click=lambda e, c=cat: self.pick_category(c),
                content=ft.Column([ft.Icon(icon, size=30, color=INK), mono(cat.upper(), 9.5, INK_DIM,
                                                                          text_align=ft.TextAlign.CENTER)],
                                  spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            for cat, icon in CATEGORY_ICONS.items()], wrap=True, spacing=10, run_spacing=10)

        by_cat = {}
        for p in CATALOG:
            by_cat.setdefault(p["category"], []).append(p)
        pic_ref = panel(ft.Column([
            mono("PICTURE REFERENCE — EVERY PRODUCT, BY CATEGORY", 10.5),
            *[ft.Column([
                ft.Row([ft.Icon(CATEGORY_ICONS.get(cat, ft.Icons.CATEGORY), size=20, color=GOLD),
                        display(cat, 15)], spacing=8),
                ft.Row([ft.Container(
                    content=ft.Row([ft.Text(p["icon"], size=16), txt(p["name"], 12)], spacing=6, tight=True),
                    bgcolor=CARD, border=ft.Border.all(1, LINE), border_radius=999,
                    padding=ft.Padding.only(left=8, right=12, top=5, bottom=5)) for p in by_cat[cat]],
                    wrap=True, spacing=8, run_spacing=8),
            ], spacing=8) for cat in CATEGORY_ICONS if cat in by_cat],
        ], spacing=16))

        self.listing_flash = ft.Container(visible=False)
        self.l_name = field("Product name", hint="e.g. Refurbished Aster 14 UltraBook")
        self.l_category = dropdown("Category", [(c, c) for c in sorted(CATEGORY_ICONS)], "Accessories")
        self.l_icon = field("Icon (single emoji, optional)", hint="💻")
        self.l_price = field("Price (₦)", hint="e.g. 450000", keyboard=ft.KeyboardType.NUMBER)
        self.l_stock = field("Stock quantity", hint="e.g. 5", keyboard=ft.KeyboardType.NUMBER)
        self.l_desc = field("Description", hint="Describe the product buyers will see", multiline=True)
        form = panel(ft.Column([
            mono("LIST A NEW PRODUCT", 10.5), self.listing_flash, self.l_name, self.l_category, self.l_icon,
            self.l_price, self.l_stock, self.l_desc, button("Publish listing", lambda e: self.submit_listing()),
        ], spacing=12), expand=True)

        mine = [panel(ft.Column([
            ft.Row([txt(f"{l['icon']} {l['name']}", 13, INK, "s", expand=True),
                    pill("Sold out" if l["stock"] == 0 else f"{l['stock']} in stock", WINE if l["removed"] else GOLD)]),
            mono(f"{l['category']} · {fmt(l['price'])}" + (" · removed by admin" if l.get("removed") else ""), 11.5),
        ], spacing=4), padding=14) for l in self.my_listings] or \
               [mono("You haven't listed any products yet.", 12.5)]
        listings = panel(ft.Column([mono("YOUR LISTINGS", 10.5), *mine], spacing=10), expand=True)

        return ft.Column([
            section_head("Sell on ElectroMart"), ref_cards, ft.Container(height=8), pic_ref, ft.Container(height=8),
            ft.Row([form, listings], vertical_alignment=ft.CrossAxisAlignment.START, spacing=26),
        ], spacing=10)

    def pick_category(self, cat):
        self.l_category.value = cat
        self.l_category.update()

    def submit_listing(self):
        try:
            self.db.create_listing(self.user["id"], self.l_name.value, self.l_category.value, self.l_icon.value,
                                   self.l_price.value, self.l_stock.value, self.l_desc.value)
        except ApiError as exc:
            self.listing_flash.content = flash(exc.message)
            self.listing_flash.visible = True
            self.listing_flash.update()
            return
        self.my_listings = self.db.my_listings(self.user["id"])
        self.refresh_view()
        self.listing_flash.content = flash("Listing published — it now appears in the marketplace for buyers "
                                           "to purchase.", ok=True)
        self.listing_flash.visible = True
        self.listing_flash.update()

    # --------------------------------------------------------------- analytics
    def view_analytics(self):
        a = self.analytics
        if not a:
            return ft.Column([section_head("Analytics"), mono("Loading your dashboard…", 13)])
        top = [bar_row(l["name"], f"{fmt(l['revenue'])} · {l['units']} sold",
                       l["revenue"] / a["maxRevenue"] if a["maxRevenue"] else 0) for l in a["topListings"]] or \
              [mono("No sales yet — once buyers order your listings, they'll show up here.", 12.5)]
        return ft.Column([
            section_head("Analytics"),
            ft.Row([stat_card("Revenue", fmt(a["revenue"])), stat_card("Orders", str(a["ordersCount"])),
                    stat_card("Units sold", str(a["unitsSold"])), stat_card("Listings", str(a["listingsCount"])),
                    stat_card("Low stock", str(a["lowStock"]), warn=a["lowStock"] > 0),
                    stat_card("Out of stock", str(a["outOfStock"]), warn=a["outOfStock"] > 0)],
                   wrap=True, spacing=12, run_spacing=12),
            ft.Container(height=6),
            panel(ft.Column([mono("TOP LISTINGS BY REVENUE", 10.5), *top], spacing=14)),
        ], spacing=10)

    # ------------------------------------------------------------------- admin
    def load_admin(self):
        uid = self.user["id"]
        self.admin_report = self.safe(lambda: self.db.admin_report(uid))
        self.admin_listings = self.safe(lambda: self.db.admin_listings(uid)) or []
        self.admin_users = self.safe(lambda: self.db.admin_users(uid)) or []

    def admin_action(self, fn, *args):
        try:
            fn(self.user["id"], *args)
        except ApiError:
            pass
        self.load_admin()
        self.refresh_view()

    def view_admin(self):
        r = self.admin_report
        if not r:
            return ft.Column([section_head("Admin"), mono("Loading platform data…", 13)])

        def tab(label, key):
            active = self.admin_tab == key
            return ft.Container(
                content=mono(label.upper(), 12, INK if active else INK_DIM), bgcolor=CARD if active else None,
                border=ft.Border.all(1, LINE if active else "transparent"), border_radius=4,
                padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                on_click=lambda e: self.set_admin_tab(key))

        def table(columns, rows):
            return ft.Row([ft.DataTable(
                columns=[ft.DataColumn(mono(c.upper(), 10.5)) for c in columns], rows=rows,
                column_spacing=28, heading_row_height=36, data_row_min_height=44)], scroll=ft.ScrollMode.AUTO)

        if self.admin_tab == "reports":
            maxrev = r["topProducts"][0]["revenue"] if r["topProducts"] else 0
            top = [bar_row(p["name"], f"{fmt(p['revenue'])} · {p['units']} sold",
                           p["revenue"] / maxrev if maxrev else 0) for p in r["topProducts"]] or \
                  [mono("No orders placed yet.", 12.5)]
            content = ft.Column([
                ft.Row([stat_card("Total revenue", fmt(r["totalRevenue"])), stat_card("Orders", str(r["ordersCount"])),
                        stat_card("Units sold", str(r["totalUnits"])),
                        stat_card("Users (buyers / sellers)", f"{r['buyersCount']} / {r['sellersCount']}"),
                        stat_card("Seller listings", str(r["listingsCount"])),
                        stat_card("Removed listings", str(r["flaggedCount"]), warn=r["flaggedCount"] > 0)],
                       wrap=True, spacing=12, run_spacing=12),
                panel(ft.Column([mono("TOP-SELLING PRODUCTS (PLATFORM-WIDE)", 10.5), *top], spacing=14)),
            ], spacing=16)
        elif self.admin_tab == "listings":
            rows = [ft.DataRow(cells=[
                ft.DataCell(txt(l["name"], 13)), ft.DataCell(txt(l.get("sellerName", ""), 13)),
                ft.DataCell(mono(fmt(l["price"]), 12, INK)), ft.DataCell(mono(str(l["stock"]), 12, INK)),
                ft.DataCell(txt("Removed" if l.get("removed") else "Live", 13)),
                ft.DataCell(button("Restore" if l.get("removed") else "Remove",
                                   lambda e, lid=l["id"]: self.admin_action(self.db.toggle_listing, lid),
                                   kind="gold" if l.get("removed") else "wine", small=True)),
            ]) for l in self.admin_listings]
            content = panel(ft.Column([
                mono("SELLER LISTINGS", 10.5),
                table(["Product", "Seller", "Price", "Stock", "Status", ""], rows) if rows
                else mono("No seller listings yet.", 12.5)], spacing=10))
        else:
            rows = [ft.DataRow(cells=[
                ft.DataCell(txt(u["name"], 13)), ft.DataCell(txt(u["email"], 13)), ft.DataCell(txt(u["role"], 13)),
                ft.DataCell(txt("Disabled" if u.get("disabled") else "Active", 13)),
                ft.DataCell(button("Re-enable" if u.get("disabled") else "Disable",
                                   lambda e, uid=u["id"]: self.admin_action(self.db.toggle_user, uid),
                                   kind="gold" if u.get("disabled") else "wine", small=True)),
            ]) for u in self.admin_users]
            content = panel(ft.Column([
                mono("REGISTERED USERS", 10.5),
                table(["Name", "Email", "Role", "Status", ""], rows) if rows
                else mono("No buyers or sellers yet.", 12.5)], spacing=10))
        return ft.Column([
            section_head("Admin"),
            ft.Row([tab("Reports", "reports"), tab("Listing moderation", "listings"),
                    tab("User moderation", "users")], spacing=4),
            ft.Container(height=4), content,
        ], spacing=10)

    def set_admin_tab(self, key):
        self.admin_tab = key
        self.refresh_view()


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.run(main)
