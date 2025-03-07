import logging
import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from typing import Dict, List, Any, Optional, Tuple

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Дані про відеокарти з посиланнями
gpu_data = [
    {"id": 1, "model": "NVIDIA GeForce GTX 1650", "performance": 30, "power": 75, "price": 7000, 
     "link": "https://megabit.ua/product/220612/videokarta-gf-gtx-1650-4gb-gddr6-tuf-gaming-v2-asus-tuf-gtx1650-4gd6-p-v2-gaming"},
    {"id": 2, "model": "AMD Radeon RX 6500 XT", "performance": 35, "power": 107, "price": 7200, 
     "link": "https://luckylink.kiev.ua/ua/powercolor-axrx-6500xt-4gbd6-dh-oc/"},
    {"id": 3, "model": "NVIDIA GeForce GTX 1660 Super", "performance": 45, "power": 125, "price": 8250, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-gtx-1660-super-gaming-x/"},
    {"id": 4, "model": "AMD Radeon RX 6600", "performance": 50, "power": 132, "price": 9660, 
     "link": "https://luckylink.kiev.ua/ua/asrock-radeon-rx-6600-challenger-d-8gb-rx6600-cld-8g/"},
    {"id": 5, "model": "NVIDIA GeForce RTX 3050", "performance": 55, "power": 130, "price": 10000, 
     "link": "https://luckylink.kiev.ua/ua/asus-dual-rtx3050-o8g-v2/"},
    {"id": 6, "model": "NVIDIA GeForce RTX 3060", "performance": 60, "power": 170, "price": 12000, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-geforce-rtx-3060-gaming-oc-8g-gv-n3060gaming-oc-8gd-2.0/"},
    {"id": 7, "model": "AMD Radeon RX 6700 XT", "performance": 65, "power": 230, "price": 15500, 
     "link": "https://luckylink.kiev.ua/ua/xfx-amd-radeon-rx-6700-xt-12gb-speedster-qick319-black-rx-67xtypbdp/"},
    {"id": 8, "model": "NVIDIA GeForce RTX 3060 Ti Founder Edition", "performance": 70, "power": 200, "price": 14500, 
     "link": "https://luckylink.kiev.ua/ua/nvidia-geforce-rtx-3060-ti-founders-edition-900-1g142-2520-000/"},
    {"id": 9, "model": "NVIDIA GeForce RTX 3070 Founders Edition", "performance": 75, "power": 220, "price": 17000, 
     "link": "https://luckylink.kiev.ua/ua/nvidia-geforce-rtx-3070-founders-edition-900-1g142-2510-000/"},
    {"id": 10, "model": "AMD Radeon RX 6800 XT", "performance": 80, "power": 250, "price": 22500, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-radeon-rx-6800-xt-gaming-oc-16g-gv-r68xtgaming-oc-16gd/"},
    {"id": 11, "model": "NVIDIA GeForce RTX 3070 Ti", "performance": 82, "power": 290, "price": 20250, 
     "link": "https://luckylink.kiev.ua/ua/palit-geforce-rtx-3070-ti-gamerock-oc-ned307tt19p2-1047g/"},
    {"id": 12, "model": "NVIDIA GeForce RTX 3080", "performance": 85, "power": 320, "price": 25000, 
     "link": "https://luckylink.kiev.ua/ua/inno3d-geforce-rtx-3080-ichill-x4-lhr-c30804-106xx-1810va36h/"},
    {"id": 13, "model": "AMD Radeon RX 6800 XT", "performance": 87, "power": 300, "price": 20750, 
     "link": "https://luckylink.kiev.ua/ua/powercolor-radeon-rx-6800-xt-16-gb-red-dragon-axrx-6800xt-16gbd6-3dhr-oc/"},
    {"id": 14, "model": "NVIDIA GeForce RTX 3080 Ti", "performance": 90, "power": 350, "price": 24500, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-3080-ti-gaming-x-trio-12g/"},
    {"id": 15, "model": "AMD Radeon RX 6900 XT", "performance": 92, "power": 300, "price": 23500, 
     "link": "https://luckylink.kiev.ua/ua/powercolor-radeon-rx-6900-xt-red-devil-axrx-6900xt-16gbd6-3dhe-oc/"},
    {"id": 16, "model": "NVIDIA GeForce RTX 3090 Founders Edition", "performance": 95, "power": 350, "price": 31500, 
     "link": "https://luckylink.kiev.ua/ua/nvidia-geforce-rtx-3090-24gb-founders-edition-900-1g136-2510-000/"},
    {"id": 17, "model": "NVIDIA GeForce RTX 3090 Ti", "performance": 97, "power": 450, "price": 36000, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-geforce-rtx-3090-ti-gaming-oc-24g-gv-n309tgaming-oc-24gd/"},
    {"id": 18, "model": "NVIDIA GeForce RTX 4070", "performance": 85, "power": 200, "price": 28000, 
     "link": "https://luckylink.kiev.ua/ua/asus-dual-rtx4070-o12g-evo/"},
    {"id": 19, "model": "NVIDIA GeForce RTX 4070 Ti", "performance": 90, "power": 285, "price": 38900, 
     "link": "https://luckylink.kiev.ua/ua/asus-proart-rtx4070ti-o12g/"},
    {"id": 20, "model": "NVIDIA GeForce RTX 4080", "performance": 95, "power": 320, "price": 48795, 
     "link": "https://luckylink.kiev.ua/ua/inno3d-geforce-rtx-4080-16-gb-x3-n40803-166x-187049n/"},
    {"id": 21, "model": "NVIDIA GeForce RTX 4090", "performance": 100, "power": 450, "price": 112000, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-4090-gaming-x-trio-24g/"},
    {"id": 22, "model": "AMD Radeon RX 7900 XT", "performance": 93, "power": 300, "price": 38250, 
     "link": "https://luckylink.kiev.ua/ua/sapphire-radeon-rx-7900-xt-vapor-x-20gb-nitro-11323-01-40g/"},
    {"id": 23, "model": "AMD Radeon RX 7900 XTX", "performance": 97, "power": 355, "price": 44250, 
     "link": "https://luckylink.kiev.ua/ua/dual-rx7900xtx-o24g/"},
    {"id": 24, "model": "NVIDIA GeForce RTX 4060", "performance": 70, "power": 115, "price": 14080, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-4060-ventus-2x-black-8g/"},
    {"id": 25, "model": "NVIDIA GeForce RTX 4060 Ti", "performance": 75, "power": 160, "price": 17300, 
     "link": "https://luckylink.kiev.ua/ua/asus-dual-rtx4060ti-o8g-evo/"},
    {"id": 26, "model": "AMD Radeon RX 7600", "performance": 68, "power": 165, "price": 11402, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-radeon-rx-7600-gaming-oc-8g-gv-r76gaming-oc-8gd/",
     "color": "black"},
    {"id": 27, "model": "NVIDIA GeForce RTX 3090", "performance": 95, "power": 350, "price": 30000, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-geforce-rtx-3090-gaming-oc-24g-gv-n3090gaming-oc-24gd/",
     "color": "black"},
    {"id": 28, "model": "MSI Geforce RTX 3070", "performance": 75, "power": 220, "price": 9000, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-3070-gaming-x-trio/",
     "color": "black"},
    {"id": 29, "model": "MSI GeForce RTX 3060 ti", "performance": 70, "power": 200, "price": 15750, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-3060-ti-gaming-x/",
     "color": "black"},
    {"id": 30, "model": "ASUS Rog strix-rtx4090", "performance": 105, "power": 200, "price": 123000, 
     "link": "https://luckylink.kiev.ua/ua/asus-rog-strix-rtx4090-o24g-gaming/",
     "color": "black"},
    {"id": 31, "model": "NVIDIA GeForce GTX 1660 Ti", "performance": 48, "power": 120, "price": 8800, 
     "link": "https://luckylink.kiev.ua/ua/arktek-geforce-gtx-1660-ti-6gb-akn1660tid6s6gh1/",
     "color": "black"},
    {"id": 32, "model": "AMD Radeon RX 5700 XT", "performance": 58, "power": 225, "price": 10750, 
     "link": "https://luckylink.kiev.ua/ua/msi-radeon-rx-5700-xt-gaming-x/",
     "color": "black"},
    {"id": 33, "model": "NVIDIA GeForce RTX 2080 Super", "performance": 80, "power": 250, "price": 17200, 
     "link": "https://luckylink.kiev.ua/ua/msi-geforce-rtx-2080-gaming-x-trio/",
     "color": "black"},
    {"id": 34, "model": "AMD Radeon RX 6700", "performance": 62, "power": 175, "price": 15950, 
     "link": "https://luckylink.kiev.ua/ua/xfx-radeon-rx-6700-xt-speedster-swft-309-core-gaming-rx-67xtyjfdv/",
     "color": "black"},
    {"id": 35, "model": "NVIDIA GeForce RTX 2070 Super", "performance": 70, "power": 215, "price": 13923, 
     "link": "https://luckylink.kiev.ua/ua/palit-geforce-rtx-2070-super-js-ne6207ss19p2-1040j/",
     "color": "black"},
    {"id": 46, "model": "ASUS ROG Strix GeForce RTX 3080 White OC Edition", "performance": 85, "power": 320, "price": 26000, 
     "link": "https://rog.asus.com/ua-ua/graphics-cards/graphics-cards/rog-strix/rog-strix-rtx3080-o10g-white-model/",
     "color": "white", "aesthetics": 9},
    {"id": 47, "model": "Gigabyte VISION GeForce RTX 3070", "performance": 75, "power": 220, "price": 16500, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-geforce-rtx-3070-vision-oc-8g-gv-n3070vision-oc-8gd/",
     "color": "white", "aesthetics": 8},
    {"id": 48, "model": "Zotak gaming Geforce RTX 3060 AMP White Edition", "performance": 60, "power": 170, "price": 23648, 
     "link": "https://luckylink.kiev.ua/ua/zotac-gaming-geforce-rtx-3060-amp-white-edition-zt-a30600f-10p/",
     "color": "white", "aesthetics": 8},
    {"id": 49, "model": "Sapphire NITRO+ AMD Radeon RX 6800 XT SE", "performance": 87, "power": 300, "price": 27000, 
     "link": "https://luckylink.kiev.ua/ua/sapphire-radeon-rx-6800-xt-se-16-gb-nitro-11304-01-20g/",
     "color": "black", "aesthetics": 9},
    {"id": 50, "model": "GIGABYTE Gaming GeForce RTX 3090", "performance": 95, "power": 350, "price": 30000, 
     "link": "https://luckylink.kiev.ua/ua/gigabyte-geforce-rtx-3090-gaming-oc-24g-gv-n3090gaming-oc-24gd/",
     "color": "black", "aesthetics": 7},
]

# Дані про процесори з посиланнями
cpu_data = [
    {"id": 1, "model": "Intel Celeron G5905", "performance": 10, "power": 58, "price": 1762, 
     "link": "https://luckylink.kiev.ua/ua/protsessor-intel-celeron-g5905-cm8070104292115/", "socket": "LGA1200", "generation": "10th Gen"},
    {"id": 2, "model": "AMD Athlon 3000G", "performance": 15, "power": 35, "price": 1621, 
     "link": "https://luckylink.kiev.ua/ua/md-athlon-300ge-pro-yd300bc6m2ofh/", "socket": "AM4", "generation": "Zen+"},
    {"id": 3, "model": "Intel Pentium Gold G6400", "performance": 25, "power": 58, "price": 3100, 
     "link": "https://luckylink.kiev.ua/ua/intel-pentium-gold-g7400-cm8071504651605/", "socket": "LGA1700", "generation": "10th Gen"},
    {"id": 4, "model": "AMD Ryzen 3 3200G", "performance": 30, "power": 65, "price": 2525, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-3-3200g-tray-yd3200c5m4mfh/", "socket": "AM4", "generation": "Zen+"},
    {"id": 5, "model": "Intel Core i3-10100", "performance": 37, "power": 65, "price": 4000, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i3-10100-bx8070110100/", "socket": "LGA1200", "generation": "10th Gen"},
    {"id": 6, "model": "AMD Ryzen 3 3100", "performance": 40, "power": 65, "price": 1873, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-3-3100-100-100000284box/", "socket": "AM4", "generation": "Zen 2"},
    {"id": 7, "model": "Intel Core i3-12100F", "performance": 45, "power": 58, "price": 3552, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i3-12100f-bx8071512100f/", "socket": "LGA1700", "generation": "12th Gen"},
    {"id": 8, "model": "AMD Ryzen 5 3600", "performance": 50, "power": 65, "price": 3500, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-5-3600-100-100000031box/", "socket": "AM4", "generation": "Zen 2"},
    {"id": 9, "model": "Intel Core i5-10400F", "performance": 55, "power": 65, "price": 3600, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i5-10400f-cm8070104290716/", "socket": "LGA1200", "generation": "10th Gen"},
    {"id": 10, "model": "AMD Ryzen 5 5600X", "performance": 60, "power": 65, "price": 4600, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-5-5600x-100-100000065box/", "socket": "AM4", "generation": "Zen 3"},
    {"id": 11, "model": "Intel Core i5-11400F", "performance": 65, "power": 65, "price": 4000, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i5-11400f-cm8070804497016/", "socket": "LGA1200", "generation": "11th Gen"},
    {"id": 12, "model": "AMD Ryzen 7 3700X", "performance": 70, "power": 65, "price": 4800, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-7-3700x-100-000000071/", "socket": "AM4", "generation": "Zen 2"},
    {"id": 13, "model": "Intel Core i5-12400F", "performance": 75, "power": 65, "price": 4851, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i5-12400f-bx8071512400f/", "socket": "LGA1700", "generation": "12th Gen"},
    {"id": 14, "model": "AMD Ryzen 7 5800X", "performance": 80, "power": 105, "price": 6765, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-7-5800x-100-100000063wof/", "socket": "AM4", "generation": "Zen 3"},
    {"id": 15, "model": "Intel Core i7-10700K", "performance": 85, "power": 125, "price": 11000, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i7-10700k-bx8070110700k/", "socket": "LGA1200", "generation": "10th Gen"},
    {"id": 16, "model": "AMD Ryzen 9 5900X", "performance": 90, "power": 105, "price": 12500, 
     "link": "http://luckylink.kiev.ua/processors/amd-ryzen-9-5900x", "socket": "AM4", "generation": "Zen 3",
     "color": "silver"},
    {"id": 17, "model": "Intel Core i7-11700K", "performance": 92, "power": 125, "price": 13000, 
     "link": "http://luckylink.kiev.ua/processors/intel-core-i7-11700k", "socket": "LGA1200", "generation": "11th Gen",
     "color": "silver"},
    {"id": 18, "model": "AMD Ryzen 9 5950X", "performance": 95, "power": 105, "price": 14676, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-9-5950x-100-100000059wof/", "socket": "AM4", "generation": "Zen 3",
     "color": "silver"},
    {"id": 19, "model": "Intel Core i9-11900K", "performance": 97, "power": 125, "price": 13500, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i9-11900k-bx8070811900k/", "socket": "LGA1200", "generation": "11th Gen",
     "color": "silver"},
    {"id": 20, "model": "AMD Ryzen 7 7700X", "performance": 80, "power": 105, "price": 14500, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-7-7700x-100-100000591wof/", "socket": "AM5", "generation": "Zen 4",
     "color": "silver"},
    {"id": 21, "model": "Intel Core i5-12600K", "performance": 85, "power": 125, "price": 7200, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i5-12600k-bx8071512600k/", "socket": "LGA1700", "generation": "12th Gen",
     "color": "silver"},
    {"id": 22, "model": "AMD Ryzen 9 7900X", "performance": 90, "power": 170, "price": 16273, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-9-7900x-100-100000589wof/", "socket": "AM5", "generation": "Zen 4",
     "color": "silver"},
    {"id": 23, "model": "Intel Core i7-12700K", "performance": 95, "power": 125, "price": 11132, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i7-12700k-bx8071512700k/", "socket": "LGA1700", "generation": "12th Gen",
     "color": "silver"},
    {"id": 24, "model": "AMD Ryzen 9 7950X", "performance": 98, "power": 170, "price": 23500, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-9-7950x-100-100000514wof/", "socket": "AM5", "generation": "Zen 4",
     "color": "silver"},
    {"id": 25, "model": "Intel Core i9-12900KF", "performance": 100, "power": 125, "price": 14318, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i9-12900kf-bx8071512900kf/", "socket": "LGA1700", "generation": "12th Gen",
     "color": "silver"},
    {"id": 26, "model": "AMD Ryzen Threadripper 3960X", "performance": 105, "power": 280, "price": 50000, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-threadripper-3960x-100-100000010wof/", "socket": "sTRX4", "generation": "Zen 2",
     "color": "silver"},
    {"id": 27, "model": "Intel Core i9-13900K", "performance": 110, "power": 125, "price": 17300, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i9-13900k-bx8071513900k/", "socket": "LGA1700", "generation": "13th Gen",
     "color": "silver"},
    {"id": 28, "model": "AMD Ryzen Threadripper 3970X", "performance": 115, "power": 280, "price": 70000, 
     "link": "https://luckylink.kiev.ua/ua/amd-ryzen-threadripper-3970x-100-100000011wof/", "socket": "sTRX4", "generation": "Zen 2",
     "color": "silver"},
    {"id": 29, "model": "Intel Core i9-14900K", "performance": 120, "power": 125, "price": 23000, 
     "link": "https://luckylink.kiev.ua/ua/intel-core-i9-14900k-bx8071514900k/", "socket": "LGA1700", "generation": "14th Gen",
     "color": "silver"},
    {"id": 30, "model": "AMD Ryzen Threadripper 3990X", "performance": 130, "power": 280, "price": 100000, 
     "link": "https://luckylink.kiev.ua/ua/protsesor-amd-ryzen-threadripper-3990x-100-100000163wof/", "socket": "sTRX4", "generation": "Zen 2",
     "color": "silver"},
]

# Дані про материнські плати
motherboard_data = {
    "budget": [
        {"model": "ASRock B360M Pro4 Socket 1151", "socket": "LGA1200", "chipset": "H510", "price": 3202, 
         "link": "https://luckylink.kiev.ua/ua/materinska-plata-asrock-b360m-pro4-socket-1151/", 
         "compatible_cpu": ["10th Gen", "11th Gen"], "ram_type": "DDR4", "max_ram": 64},
        {"model": "Gigabyte A520M DS3H V2", "socket": "AM4", "chipset": "A520", "price": 2869, 
         "link": "https://luckylink.kiev.ua/ua/materynska-plata-gigabyte-a520m-ds3h-v2-sam4-a520-4xddr4-m.2-hdmi-dp-matx-a520m_ds3h_v2/",
         "compatible_cpu": ["Zen 2", "Zen 3"], "ram_type": "DDR4", "max_ram": 64},
    ],
    "mid": [
        {"model": "GIGABYTE B560M DS3H V3", "socket": "LGA1200", "chipset": "B560", "price": 3150, 
         "link": "https://luckylink.kiev.ua/ua/gigabyte-b560m-ds3h-v3/",
         "compatible_cpu": ["10th Gen", "11th Gen"], "ram_type": "DDR4", "max_ram": 128},
        {"model": "ASUS TUF GAMING B550-PLUS", "socket": "AM4", "chipset": "B550", "price": 5155, 
         "link": "https://luckylink.kiev.ua/ua/asus-tuf-gaming-b550-plus/",
         "compatible_cpu": ["Zen 2", "Zen 3"], "ram_type": "DDR4", "max_ram": 128},
    ],
    "high": [
        {"model": "ASUS ROG STRIX Z590-E GAMING WIFI", "socket": "LGA1200", "chipset": "Z590", "price": 7500, 
         "link": "https://luckylink.kiev.ua/ua/asus-rog-strix-b560-e-gaming-wifi/",
         "compatible_cpu": ["10th Gen", "11th Gen"], "ram_type": "DDR4", "max_ram": 128},
        {"model": "ASUS ROG STRIX X570-E GAMING", "socket": "AM4", "chipset": "B550", "price": 10500, 
         "link": "https://luckylink.kiev.ua/ua/asus-rog-strix-b550-f-gaming/",
         "compatible_cpu": ["Zen 2", "Zen 3"], "ram_type": "DDR4", "max_ram": 128},
    ],
    "premium": [
        {"model": "Asrock Z690", "socket": "LGA1700", "chipset": "Z690", "price": 3500, 
         "link": "https://luckylink.kiev.ua/ua/asrock-z690-pg-riptide/56548/",
         "compatible_cpu": ["12th Gen", "13th Gen", "14th Gen"], "ram_type": "DDR4", "max_ram": 128},
        {"model": "GIGABYTE Z790 AERO G", "socket": "AM4", "chipset": "X570", "price": 100265, 
         "link": "https://luckylink.kiev.ua/ua/gigabyte-z790-aero-g/",
         "compatible_cpu": ["Zen 2", "Zen 3"], "ram_type": "DDR4", "max_ram": 128},
    ],
    "extreme": [
        {"model": "SROCK Z790 PG SONIC", "socket": "LGA1700", "chipset": "Z790", "price": 9177, 
         "link": "https://luckylink.kiev.ua/ua/asrock-z790-pg-sonic/",
         "compatible_cpu": ["12th Gen", "13th Gen", "14th Gen"], "ram_type": "DDR5", "max_ram": 192},
        {"model": "MSI MEG X670E CARBON WIFI", "socket": "AM5", "chipset": "X670E", "price": 22000, 
         "link": "https://luckylink.kiev.ua/ua/msi-mpg-x670e-carbon-wifi/",
         "compatible_cpu": ["Zen 4"], "ram_type": "DDR5", "max_ram": 128},
        {"model": "ASUS ROG ZENITH II EXTREME", "socket": "sTRX4", "chipset": "TRX40", "price": 30000, 
         "link": "https://rog.asus.com/ua-ua/motherboards/rog-zenith/rog-zenith-ii-extreme-model/",
         "compatible_cpu": ["Zen 2"], "ram_type": "DDR4", "max_ram": 256},
    ]
}

# Дані про оперативну пам'ять
ram_data = {
    "budget": [
        {"model": "Kingston FURY Beast DDR4-3200 16GB (2x8GB)", "type": "DDR4", "speed": 3200, "capacity": 16, "price": 2300, 
         "link": "https://luckylink.kiev.ua/ua/kingston-ddr4-16gb-2x8gb-3200mhz-fury-beast-rgb-special-edition-kf432c16bwak2-16/"},
        {"model": "Crucial Ballistix DDR4-3000 16GB (2x8GB)", "type": "DDR4", "speed": 3000, "capacity": 16, "price": 1100, 
         "link": "https://luckylink.kiev.ua/ua/g.skill-16-gb-2x8gb-ddr4-3000-mhz-aegis-f4-3000c16d-16gisb/"},
    ],
    "mid": [
        {"model": "G.Skill Ripjaws V DDR4-3600 32GB (2x16GB)", "type": "DDR4", "speed": 3600, "capacity": 32, "price": 2100, 
         "link": "https://luckylink.kiev.ua/ua/g.skill-ripjawsv-32gb-2x16-ddr4-3600mhz-f4-3600c18d-32gvw/"},
        {"model": "Corsair Vengeance RGB Pro DDR4-3200 32GB (2x16GB)", "type": "DDR4", "speed": 3200, "capacity": 32, "price": 4200, 
         "link": "https://luckylink.kiev.ua/ua/corsair-32gb-2x16gb-ddr4-3600mhz-vengeance-rgb-pro-sl-black-cmh32gx4m2d3600c18/"},
    ],
    "high": [
        {"model": "G.Skill Trident Z RGB DDR4-3600 64GB (2x32GB)", "type": "DDR5", "speed": 6000, "capacity": 64, "price": 9386, 
         "link": "https://luckylink.kiev.ua/ua/g.skill-trident-z5-rgb-black-ddr5-6000-64gb-kit-2x32gb-f5-6000j3238g32gx2-tz5nr/"},
        {"model": "Оперативна пам'ять Kingston FURY 64 GB (2x32GB)", "type": "DDR4", "speed": 3600, "capacity": 64, "price": 6651, 
         "link": "https://luckylink.kiev.ua/ua/kingston-fury-64-gb-2x32gb-ddr4-3600-mhz-renegade-rgb-kf436c18rb2ak2-64/"},
    ],
    "premium": [
        {"model": "G.Skill Trident Z5 RGB DDR5-6000 64GB (2x32GB)", "type": "DDR5", "speed": 6000, "capacity": 64, "price": 9359, 
         "link": "https://luckylink.kiev.ua/ua/g.skill-trident-z5-rgb-black-ddr5-6000-64gb-kit-2x32gb-f5-6000j3238g32gx2-tz5nr/"},
        {"model": "Оперативна пам'ять Kingston FURY 64 GB (2x32GB) DDR5 5600 MHz Beast RGB", "type": "DDR5", "speed": 5600, "capacity": 64, "price": 8135, 
         "link": "https://luckylink.kiev.ua/ua/kingston-fury-64-gb-2x32gb-ddr5-5600-mhz-beast-rgb-kf556c40bbak2-64/"},
    ],
    # Додаємо нові варіанти для потужних систем
    "extreme": [
        {"model": "Оперативна пам'ять Kingston FURY 128 GB", "type": "DDR5", "speed": 5600, "capacity": 128, "price": 15000, 
         "link": "https://luckylink.kiev.ua/ua/kingston-fury-128-gb-4x32gb-ddr5-5600-mhz-beast-white-kf556c40bwk4-128/"},
        {"model": "Оперативна пам'ять G.Skill Zeta R5 Neo DDR5-6400 192GB (4x48GB) ", "type": "DDR5", "speed": 6400, "capacity": 192, "price": 65700, 
         "link": "https://luckylink.kiev.ua/ua/g.skill-zeta-r5-neo-ddr5-6400-192gb-4x48gb-f5-6400r3239g48gq4-zr5nk/"},
    ]
}

# Дані про накопичувачі
storage_data = {
    "budget": [
        {"model": "Kingston A400 480GB 2.5\" SATA SSD", "type": "SSD", "interface": "SATA", "capacity": 480, "price": 1500, 
         "link": "https://luckylink.kiev.ua/ua/ssd-25-480gb-kingston-a400-sa400s37-480g-sata-iii-sata-ii-tlc/"},
        {"model": "Seagate Barracuda 1TB 7200rpm 3.5\" HDD", "type": "HDD", "interface": "SATA", "capacity": 1000, "price": 2200, 
         "link": "https://luckylink.kiev.ua/ua/zhorstkiy-disk-35-1tb-seagate-st1000dm010-sata-iii-7200-64mb-barracuda/"},
    ],
    "mid": [
        {"model": "Samsung 970 EVO Plus 1000GB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 1000, "price": 3000, 
         "link": "https://luckylink.kiev.ua/ua/samsung-970-evo-plus-1-tb-mz-v7s1t0bw/"},
        {"model": "WD Blue SN550 1TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 1000, "price": 2200, 
         "link": "https://luckylink.kiev.ua/ua/wibrand-caiman-1tb-m.2-nvme-wim.2ssd-ca1tb/"},
    ],
    "high": [
        {"model": "Samsung 980 PRO 1TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 1000, "price": 3975, 
         "link": "https://luckylink.kiev.ua/ua/samsung-980-pro-1-tb-mz-v8p1t0bw/"},
        {"model": "WD Black SN850 2TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 2000, "price": 6316, 
         "link": "https://luckylink.kiev.ua/ua/nakopytel-ssd-m.2-2280-2tb-sn850x-wd-wds200t2x0e/"},
    ],
    "premium": [
        {"model": "Samsung 990 PRO 2TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 2000, "price": 8585, 
         "link": "https://luckylink.kiev.ua/ua/samsung-990-pro-w-heatsink-2tb-mz-v9p2t0gw/"},
        {"model": "Corsair MP600 PRO XT 4TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 4000, "price": 99999, 
         "link": "https://luckylink.kiev.ua/ua/corsair-force-mp400-4-tb-cssd-f4000gbmp400/"},
    ],
    # Додаємо нові варіанти для потужних систем
    "extreme": [
        {"model": "Samsung 990 PRO 4TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 4000, "price": 13800, 
         "link": "https://luckylink.kiev.ua/ua/samsung-990-pro-4-tb-mz-v9p4t0bw/"},
        {"model": "Corsair MP600 PRO XT 8TB M.2 NVMe SSD", "type": "SSD", "interface": "NVMe", "capacity": 8000, "price": 23563, 
         "link": "https://luckylink.kiev.ua/ua/samsung-870-qvo-8-tb-mz-77q8t0bw/"},
    ]
}

# Дані про блоки живлення
psu_data = {
    "budget": [
        {"model": "Vinga 500W", "power": 500, "certification": "80+ Bronze", "price": 909, 
         "link": "https://luckylink.kiev.ua/ua/vinga-500w-psu-500-12/"},
        {"model": "Aerocool VX PLUS 600W", "power": 600, "certification": "None", "price": 1300, 
         "link": "https://luckylink.kiev.ua/ua/blok-pitaniya-aerocool-600w-kcas-600-kcas-600-plus/"},
    ],
    "mid": [
        {"model": "azza-psaz 650w rgb", "power": 650, "certification": "80+ Bronze", "price": 2050, 
         "link": "https://luckylink.kiev.ua/ua/azza-psaz-650w-rgb/"},
        {"model": "be quiet! System Power 9 700W", "power": 700, "certification": "80+ Bronze", "price": 2500, 
         "link": "https://luckylink.kiev.ua/ua/be-quiet-system-power-9-700w-bn248/"},
    ],
    "high": [
        {"model": "gigabyte ud750gm", "power": 750, "certification": "80+ Gold", "price": 3900, 
         "link": "https://luckylink.kiev.ua/ua/gigabyte-ud750gm-gp-ud750gm/"},
        {"model": "gigabyte ud850gm", "power": 850, "certification": "80+ Gold", "price": 5400, 
         "link": "https://luckylink.kiev.ua/ua/gigabyte-ud850gm-pg5-white-gp-ud850gm-pg5w/"},
    ],
    "premium": [
        {"model": "asus tuf gaming 1000w", "power": 1000, "certification": "80+ gold", "price": 8040, 
         "link": "https://luckylink.kiev.ua/ua/asus-tuf-gaming-1000w-80-plus-gold-90ye00s1-b0na00/"},
        {"model": "Zalman Terax 2", "power": 1200, "certification": "80+ Gold", "price": 6700, 
         "link": "https://luckylink.kiev.ua/ua/blok-zhyvlennia-zalman-teramax-2-1200w-90-80-gold-120mm-1xmb-28pin-1810-2xcpu-8pin44-3xmolex-12xsata-4xpcie-8pin62-1x12vhpwr-fully-modular-zm1200-tmx2/"},
    ],
    # Додаємо нові варіанти для потужних систем
    "extreme": [
        {"model": "Cougar Gex x2", "power": 1000, "certification": "80+ Gold", "price": 7100, 
         "link": "https://luckylink.kiev.ua/ua/cougar-gex-x2-1000/"},
        {"model": "be quiet! Dark Power Pro 12 1500W", "power": 1500, "certification": "80+ Titanium", "price": 14000, 
         "link": "http://luckylink.kiev.ua/psu/be-quiet-dark-power-pro-12-1500w"},
    ]
}

# Дані про корпуси
case_data = {
    "budget": [
        {"model": "Frontier pauni p05", "form_factor": "ATX", "price": 1200, 
         "link": "https://luckylink.kiev.ua/ua/frontier-pauni-p05/",
         "color": "black", "aesthetics": 5},
        {"model": "Aerocool Bolt", "form_factor": "ATX", "price": 1300, 
         "link": "https://luckylink.kiev.ua/ua/aerocool-bolt/",
         "color": "black", "aesthetics": 6},
        {"model": "GAMEMAX Abyss White", "form_factor": "ATX", "price": 1300, 
         "link": "https://luckylink.kiev.ua/ua/vinga-cloud/",
         "color": "white", "aesthetics": 6},
    ],
    "mid": [
        {"model": "GAMEMAX Defender TG", "form_factor": "ATX", "price": 2624, 
         "link": "https://luckylink.kiev.ua/ua/gamemax-defender-tg/",
         "color": "black", "aesthetics": 7},
        {"model": "QUBE Wizard" form_factor": "ATX", price: 2800, 
         "link": "https://luckylink.kiev.ua/ua/qube-wizard-wizard_fmnu3/",
         "color": "black", "aesthetics": 8},
        {"model": "PcCOOLER MASTER ME200W MESH", "form_factor": "ATX", "price": 3100, 
         "link": "https://luckylink.kiev.ua/ua/pccooler-master-me200w-mesh/",
         "color": "white", "aesthetics": 8},
    ],
    "high": [
        {"model": "Thermaltake View 31 Tempered Glass Edition", "form_factor": "ATX", "price": 3773,
         "link": "https://luckylink.kiev.ua/ua/thermaltake-view-31-tempered-glass-edition-ca-1h8-00m1wn-00/",
         "color": "black", "aesthetics": 9},
        {"model": "Modecom Siroco ARGB Flow Midi Black ", "form_factor": "ATX", "price": 4000,
         "link": "https://luckylink.kiev.ua/ua/modecom-siroco-argb-flow-midi-black-at-siroco-mg-10-00argb-00/",
         "color": "black", "aesthetics": 8},
        {"model": "Lian Li PC-O11 Dynamic White", "form_factor": "ATX", "price": 5200, 
         "link": "http://luckylink.kiev.ua/cases/lian-li-pc-o11-dynamic-white",
         "color": "white", "aesthetics": 9},
    ],
    "premium": [
        {"model": "Chieftec Stallion 3", "form_factor": "ATX", "price": 6000,
         "link": "https://luckylink.kiev.ua/ua/chieftec-stallion-3-gp-03b-uc-op/",
         "color": "black", "aesthetics": 9},
        {"model": "NZXT H5 Flow RGB Black with window", "form_factor": "ATX", "price": 6000,
         "link": "https://luckylink.kiev.ua/ua/nzxt-h5-flow-rgb-black-with-window-cc-h52fb-r1/",
         "color": "black", "aesthetics": 8},
        {"model": "iCUE 5000D RGB Airflow White ", "form_factor": "ATX", "price": 8200, 
         "link": "https://luckylink.kiev.ua/ua/corsair-cc-9011243-ww/",
         "color": "white", "aesthetics": 9},
    ]
}

# Дані про охолодження
cooling_data = {
    "budget": [
        {"model": "Deepcool GAMMAXX 400", "type": "Air", "price": 500, 
         "link": "https://luckylink.kiev.ua/ua/gammaxx-400-okhladitel-dlya-prots.-deepcool-2066-2011-v3-2011-1366-1150-51-55-56-775-am4-fm1-2-am2-2-am3-3-k8/"},
        {"model": "ID-COOLING SE-224-XT", "type": "Air", "price": 1000,
         "link": "https://luckylink.kiev.ua/ua/id-cooling-se-224-xts/"},
    ],
    "mid": [
        {"model": "be quiet! Pure Rock 2", "type": "Air", "price": 1600,
         "link": "https://luckylink.kiev.ua/ua/be-quiet-pure-rock-2-bk006/"},
        {"model": "Водяне охолодження Corsair H100 RGB ", "type": "Liquid", "price": 3675
         "link": "https://luckylink.kiev.ua/ua/corsair-h100-rgb-cw-9060053-ww/"},
    ],
    "high": [
        {"model": "Noctua NH-D15", "type": "Air", "price": 5200,
         "link": "https://luckylink.kiev.ua/ua/nh-d15-okhladitel-dlya-prots.-noctua-2066-2011-2011-v3-1150-1151-1155-1156-fm1-fm2-am2-am2-am3-am3/"},
        {"model": "Corsair H100i RGB PRO XT 240mm AIO", "type": "Liquid", "price": 5200,
         "link": "https://luckylink.kiev.ua/ua/corsair-icue-h100i-elite-capellix-xt-cw-9060068-ww/"},
    ],
    "premium": [
        {"model": "Водяне охолодження Corsair iCUE H150i Elite Capellix XT", "type": "Liquid", "price": 9500
         "link": "https://luckylink.kiev.ua/ua/corsair-icue-h150i-elite-capellix-xt-cw-9060073-ww/"},
        {"model": "Corsair iCUE H170i ELITE CAPELLIX 420mm AIO", "type": "Liquid", "price": 7300,
         "link": "https://luckylink.kiev.ua/ua/corsair-icue-h170i-elite-capellix-xt-cw-9060071-ww/"},
    ],
    # Додаємо нові варіанти для потужних систем
    "extreme": [
        {"model": "Водяне охолодження Corsair IUE H150i Elite Capellix XT", "type": "Liquid", "price": 9500,
         "link": "https://luckylink.kiev.ua/ua/corsair-icue-h150i-elite-capellix-xt-cw-9060073-ww/"},
        {"model": "Corsair iCUE H170i ELITE LCD 420mm AIO", "type": "Liquid", "price": 7340,
         "link": "https://luckylink.kiev.ua/ua/corsair-icue-h170i-elite-capellix-xt-cw-9060071-ww/"},
    ]
}

# Інші компоненти (приблизні ціни)
other_components = {
    "motherboard": {"budget": 00, "mid": 000, "high": 0000, "premium": 000, "extreme": 0000},
    "ram": {"budget": 000, "mid": 000, "high": 000, "premium": 000, "extreme": 0000},
    "storage": {"budget": 00, "mid": 000, "high": 000, "premium": 0000, "extreme": 0000},
    "psu": {"budget": 00, "mid": 000, "high": 000, "premium": 000, "extreme": 000},
    "case": {"budget": 00, "mid": 000, "high": 000, "premium": 000, "extreme": 0000},
    "cooling": {"budget": 00, "mid": 000, "high": 000, "premium": 000, "extreme": 0000},
}

# Зберігання сесій користувачів
user_sessions = {}

# Функція для перевірки сумісності процесора та материнської плати
def check_cpu_motherboard_compatibility(cpu, motherboard):
    # Перевіряємо сокет
    if cpu["socket"] != motherboard["socket"]:
        return False, f"Несумісний сокет: {cpu['socket']} (CPU) vs {motherboard['socket']} (Материнська плата)"
    
    # Перевіряємо покоління процесора
    if cpu["generation"] not in motherboard["compatible_cpu"]:
        return False, f"Несумісне покоління процесора: {cpu['generation']} не підтримується материнською платою"
    
    return True, "Сумісні"

# Функція для перевірки сумісності RAM і материнської плати
def check_ram_motherboard_compatibility(ram, motherboard):
    # Перевіряємо тип пам'яті
    if ram["type"] != motherboard["ram_type"]:
        return False, f"Несумісний тип пам'яті: {ram['type']} (RAM) vs {motherboard['ram_type']} (Материнська плата)"
    
    # Перевіряємо максимальний обсяг пам'яті
    if ram["capacity"] > motherboard["max_ram"]:
        return False, f"Перевищено максимальний обсяг пам'яті: {ram['capacity']}GB > {motherboard['max_ram']}GB"
    
    return True, "Сумісні"

# Функція для перевірки достатності потужності БЖ
def check_psu_sufficient(total_power, psu_power):
    # Рекомендований запас потужності - 30%
    recommended_power = total_power * 1.3
    
    if psu_power < total_power:
        return False, f"Недостатня потужність БЖ: {psu_power}Вт < {total_power}Вт (необхідно)"
    
    if psu_power < recommended_power:
        return True, f"Потужності БЖ достатньо, але рекомендується більший запас: {psu_power}Вт < {int(recommended_power)}Вт (рекомендовано)"
    
    return True, "Достатня потужність"

# Функція для визначення рівня компонентів на основі продуктивності GPU і CPU
def determine_component_level(gpu_performance, cpu_performance, remaining_budget):
    # Розраховуємо загальну продуктивність системи
    system_performance = (gpu_performance * 0.6) + (cpu_performance * 0.4)
    
    # Визначаємо рівень компонентів на основі продуктивності та бюджету
    if system_performance >= 95 and remaining_budget >= 40000:
        return "extreme"
    elif system_performance >= 85 and remaining_budget >= 25000:
        return "premium"
    elif system_performance >= 70 and remaining_budget >= 15000:
        return "high"
    elif system_performance >= 50 and remaining_budget >= 10000:
        return "mid"
    else:
        return "budget"

# Функція для пошуку компонентів в межах бюджету
def find_components_within_budget(budget, preferred_gpu="", preferred_cpu="", preferred_color="", preferred_aesthetics=False):
    # Резервуємо частину бюджету для інших компонентів
    other_components_min_cost = (
        other_components["motherboard"]["budget"] +
        other_components["ram"]["budget"] +
        other_components["storage"]["budget"] +
        other_components["psu"]["budget"] +
        other_components["case"]["budget"] +
        other_components["cooling"]["budget"]
    )

    max_component_budget = budget - other_components_min_cost

    if max_component_budget < 5000:
        return {"error": "Бюджет занадто малий для збірки ПК. Мінімальний рекомендований бюджет: 15000 грн."}

    # Знаходимо всі можливі комбінації CPU+GPU в межах бюджету
    combinations = []

    for gpu in gpu_data:
        # Пропускаємо, якщо не відповідає бажаній моделі GPU (якщо вказано)
        if preferred_gpu and preferred_gpu.lower() not in gpu["model"].lower():
            continue
        
        # Пропускаємо, якщо не відповідає бажаному кольору (якщо вказано)
        if preferred_color and "color" in gpu and gpu["color"] != preferred_color:
            continue
        
        # Пропускаємо, якщо користувач хоче красиву збірку, але естетика відеокарти низька
        if preferred_aesthetics and "aesthetics" in gpu and gpu["aesthetics"] < 7:
            continue
        
        for cpu in cpu_data:
            # Пропускаємо, якщо не відповідає бажаній моделі CPU (якщо вказано)
            if preferred_cpu and preferred_cpu.lower() not in cpu["model"].lower():
                continue
            
            if gpu["price"] + cpu["price"] <= max_component_budget:
                # Розраховуємо залишок бюджету для інших компонентів
                remaining_budget = budget - (gpu["price"] + cpu["price"])
                
                # Визначаємо рівень якості інших компонентів на основі продуктивності та залишку бюджету
                component_level = determine_component_level(gpu["performance"], cpu["performance"], remaining_budget)
                
                # Вибираємо материнську плату, сумісну з процесором
                compatible_motherboards = []
                for level in [component_level, "premium", "high", "mid", "budget"]:
                    if level not in motherboard_data:
                        continue
                    
                    for mb in motherboard_data[level]:
                        is_compatible, _ = check_cpu_motherboard_compatibility(cpu, mb)
                        if is_compatible:
                            compatible_motherboards.append((level, mb))
                
                if not compatible_motherboards:
                    continue  # Пропускаємо цю комбінацію, якщо немає сумісних материнських плат
                
                # Вибираємо найкращу сумісну материнську плату
                motherboard_level, motherboard = compatible_motherboards[0]
                
                # Вибираємо RAM, сумісну з материнською платою
                compatible_rams = []
                for level in [component_level, "premium", "high", "mid", "budget"]:
                    if level not in ram_data:
                        continue
                    
                    for ram_item in ram_data[level]:
                        is_compatible, _ = check_ram_motherboard_compatibility(ram_item, motherboard)
                        if is_compatible:
                            compatible_rams.append((level, ram_item))
                
                if not compatible_rams:
                    continue  # Пропускаємо цю комбінацію, якщо немає сумісної RAM
                
                # Вибираємо найкращу сумісну RAM
                ram_level, ram = compatible_rams[0]
                
                # Для потужних відеокарт (RTX 4080, 4090, 7900 XTX) вибираємо більше RAM і більший накопичувач
                if gpu["performance"] >= 95:
                    # Шукаємо RAM з більшою ємністю
                    for level in ["extreme", "premium", "high"]:
                        if level not in ram_data:
                            continue
                        
                        for ram_item in ram_data[level]:
                            if ram_item["capacity"] >= 64:  # Мінімум 64GB для топових відеокарт
                                is_compatible, _ = check_ram_motherboard_compatibility(ram_item, motherboard)
                                if is_compatible:
                                    ram = ram_item
                                    break
                
                # Вибираємо накопичувач відповідно до продуктивності системи
                storage_options = storage_data.get(component_level, storage_data["budget"])
                
                # Для потужних відеокарт вибираємо більший накопичувач
                if gpu["performance"] >= 95:
                    if "extreme" in storage_data:
                        storage = storage_data["extreme"][0]  # 4TB+ SSD для топових відеокарт
                    else:
                        storage = storage_data["premium"][0]  # 2TB+ SSD якщо немає extreme
                elif gpu["performance"] >= 85:
                    storage = storage_data["premium"][0]  # 2TB SSD для високопродуктивних відеокарт
                elif gpu["performance"] >= 70:
                    storage = storage_data["high"][0]  # 1TB NVMe SSD для середньо-високих відеокарт
                else:
                    storage = storage_options[0]
                
                # Розраховуємо загальну потужність системи
                total_power = gpu["power"] + cpu["power"] + 150  # Додаємо 150 Вт для інших компонентів
                
                # Вибираємо блок живлення з урахуванням потужності системи
                # Для потужних систем потрібен запас 50%, для інших - 30%
                required_psu_power = total_power * (1.5 if gpu["performance"] >= 90 else 1.3)
                
                # Шукаємо підходящий БЖ
                suitable_psu = None
                for level in ["extreme", "premium", "high", "mid", "budget"]:
                    if level not in psu_data:
                        continue
                    
                    for psu_item in psu_data[level]:
                        if psu_item["power"] >= required_psu_power:
                            suitable_psu = psu_item
                            break
                    
                    if suitable_psu:
                        break
                
                # Якщо не знайдено підходящий БЖ, використовуємо найпотужніший доступний
                if not suitable_psu:
                    for level in ["extreme", "premium", "high", "mid", "budget"]:
                        if level not in psu_data:
                            continue
                        
                        max_power_psu = max(psu_data[level], key=lambda x: x["power"])
                        if not suitable_psu or max_power_psu["power"] > suitable_psu["power"]:
                            suitable_psu = max_power_psu
                
                psu_item = suitable_psu
                
                # Вибираємо охолодження відповідно до TDP процесора
                if cpu["power"] >= 150:
                    if "extreme" in cooling_data:
                        cooling = cooling_data["extreme"][0]
                    else:
                        cooling = cooling_data["premium"][0]
                elif cpu["power"] >= 100:
                    cooling = cooling_data["premium"][0]
                elif cpu["power"] >= 75:
                    cooling = cooling_data["high"][0]
                else:
                    cooling = cooling_data.get(component_level, cooling_data["budget"])[0]
                
                # Вибираємо корпус
                case_options = [case for case in case_data.get(component_level, case_data["budget"]) 
                               if not preferred_color or case["color"] == preferred_color]
                
                # Якщо вказано естетику, вибираємо компоненти з високою естетикою
                if preferred_aesthetics:
                    case_options = [case for case in case_options if case["aesthetics"] >= 7]
                
                # Якщо немає відповідних корпусів, використовуємо перший доступний
                case = case_options[0] if case_options else case_data.get(component_level, case_data["budget"])[0]
                
                # Перевіряємо сумісність компонентів
                compatibility_issues = []
                
                # Перевірка сумісності CPU і материнської плати
                cpu_mb_compatible, cpu_mb_message = check_cpu_motherboard_compatibility(cpu, motherboard)
                if not cpu_mb_compatible:
                    compatibility_issues.append(cpu_mb_message)
                
                # Перевірка сумісності RAM і материнської плати
                ram_mb_compatible, ram_mb_message = check_ram_motherboard_compatibility(ram, motherboard)
                if not ram_mb_compatible:
                    compatibility_issues.append(ram_mb_message)
                
                # Перевірка достатності потужності БЖ
                psu_sufficient, psu_message = check_psu_sufficient(total_power, psu_item["power"])
                if not psu_sufficient:
                    compatibility_issues.append(psu_message)
                
                # Розраховуємо оцінку продуктивності (зважене середнє продуктивності CPU і GPU)
                performance_score = (gpu["performance"] * 0.6) + (cpu["performance"] * 0.4)
                
                # Розраховуємо оцінку співвідношення ціна/якість (продуктивність на гривню)
                total_cost = gpu["price"] + cpu["price"] + motherboard["price"] + ram["price"] + storage["price"] + psu_item["price"] + case["price"] + cooling["price"]
                value_score = performance_score / (total_cost / 1000)
                
                # Розраховуємо естетичну оцінку збірки
                aesthetics_score = 0
                if "aesthetics" in gpu:
                    aesthetics_score += gpu["aesthetics"]
                if "aesthetics" in case:
                    aesthetics_score += case["aesthetics"]
                aesthetics_score = aesthetics_score / 2 if aesthetics_score > 0 else 5  # Середнє значення або за замовчуванням 5
                
                combinations.append({
                    "gpu": gpu,
                    "cpu": cpu,
                    "motherboard": motherboard,
                    "ram": ram,
                    "storage": storage,
                    "psu": psu_item,
                    "case": case,
                    "cooling": cooling,
                    "component_level": component_level,
                    "total_cost": total_cost,
                    "performance_score": performance_score,
                    "value_score": value_score,
                    "total_power": total_power,
                    "aesthetics_score": aesthetics_score,
                    "remaining_budget": budget - total_cost,
                    "compatibility_issues": compatibility_issues
                })

    if not combinations:
        return {"error": "Не вдалося знайти відповідні компоненти в межах вашого бюджету або за вашими перевагами."}

    # Сортуємо за оцінкою продуктивності (за спаданням)
    # Якщо користувач хоче красиву збірку, враховуємо естетику при сортуванні
    if preferred_aesthetics:
        combinations.sort(key=lambda x: (x["aesthetics_score"] * 0.4 + x["performance_score"] * 0.6), reverse=True)
    else:
        combinations.sort(key=lambda x: x["performance_score"], reverse=True)

    # Повертаємо топ-3 комбінації
    return {
        "success": True,
        "combinations": combinations[:3]
    }

# Форматування повідомлення про збірку ПК
def format_pc_build(build, index):
    quality_map = {
        "budget": "Бюджетна",
        "mid": "Середня",
        "high": "Висока",
        "premium": "Преміум",
        "extreme": "Екстремальна"
    }

    aesthetics_info = ""
    if "aesthetics_score" in build:
        aesthetics_rating = "★" * int(round(build["aesthetics_score"]))
        aesthetics_info = f"\n*Естетична оцінка:* {aesthetics_rating}"

    color_info = ""
    if "case" in build and "color" in build["case"]:
        color_map = {"black": "Чорний", "white": "Білий"}
        color_info = f"\n*Колір корпусу:* {color_map.get(build['case']['color'], build['case']['color'].capitalize())}"
    
    compatibility_info = ""
    if "compatibility_issues" in build and build["compatibility_issues"]:
        compatibility_info = "\n\n⚠️ *Проблеми сумісності:*"
        for issue in build["compatibility_issues"]:
            compatibility_info += f"\n- {issue}"
    
    return f"""
🖥️ *Варіант збірки #{index}*

*Відеокарта:* {build['gpu']['model']} (Продуктивність: {build['gpu']['performance']}/100)
*Процесор:* {build['cpu']['model']} (Продуктивність: {build['cpu']['performance']}/100)
*Материнська плата:* {build['motherboard']['model']} (Сокет: {build['motherboard']['socket']})
*Оперативна пам'ять:* {build['ram']['model']} ({build['ram']['capacity']} ГБ)
*Накопичувач:* {build['storage']['model']} ({build['storage']['capacity']} ГБ)
*Блок живлення:* {build['psu']['model']} ({build['psu']['power']}Вт)
*Корпус:* {build['case']['model']}{color_info}
*Охолодження:* {build['cooling']['model']}

*Загальна продуктивність:* {round(build['performance_score'])}/100
*Співвідношення ціна/продуктивність:* {build['value_score']:.2f}{aesthetics_info}
*Необхідна потужність БЖ:* {build['total_power']}Вт
*Рівень компонентів:* {quality_map.get(build.get('component_level', 'budget'))}{compatibility_info}

*Загальна вартість:* {build['total_cost']:,} грн
*Залишок бюджету:* {build['remaining_budget']:,} грн
"""

# Функція для порівняння двох збірок
def compare_builds(build1, build2):
    comparison = f"""
📊 *Порівняння збірок*

*Відеокарти:*
- {build1['gpu']['model']} (Продуктивність: {build1['gpu']['performance']}/100)
- {build2['gpu']['model']} (Продуктивність: {build2['gpu']['performance']}/100)
Різниця: {abs(build1['gpu']['performance'] - build2['gpu']['performance'])} балів

*Процесори:*
- {build1['cpu']['model']} (Продуктивність: {build1['cpu']['performance']}/100)
- {build2['cpu']['model']} (Продуктивність: {build2['cpu']['performance']}/100)
Різниця: {abs(build1['cpu']['performance'] - build2['cpu']['performance'])} балів

*Оперативна пам'ять:*
- {build1['ram']['model']} ({build1['ram']['capacity']} ГБ)
- {build2['ram']['model']} ({build2['ram']['capacity']} ГБ)
Різниця: {abs(build1['ram']['capacity'] - build2['ram']['capacity'])} ГБ

*Накопичувач:*
- {build1['storage']['model']} ({build1['storage']['capacity']} ГБ)
- {build2['storage']['model']} ({build2['storage']['capacity']} ГБ)
Різниця: {abs(build1['storage']['capacity'] - build2['storage']['capacity'])} ГБ

*Загальна продуктивність:*
- Збірка 1: {round(build1['performance_score'])}/100
- Збірка 2: {round(build2['performance_score'])}/100
Різниця: {abs(round(build1['performance_score']) - round(build2['performance_score']))} балів

*Співвідношення ціна/продуктивність:*
- Збірка 1: {build1['value_score']:.2f}
- Збірка 2: {build2['value_score']:.2f}
Різниця: {abs(build1['value_score'] - build2['value_score']):.2f}

*Загальна вартість:*
- Збірка 1: {build1['total_cost']:,} грн
- Збірка 2: {build2['total_cost']:,} грн
Різниця: {abs(build1['total_cost'] - build2['total_cost']):,} грн

*Рекомендація:* {
    "Збірка 1 має краще співвідношення ціна/продуктивність" 
    if build1['value_score'] > build2['value_score'] 
    else "Збірка 2 має краще співвідношення ціна/продуктивність"
}
"""
    return comparison

# Функція для створення детальної інформації про компонент
def get_component_details(component):
    if "model" not in component:
        return "Інформація про компонент недоступна"
    
    details = f"*{component['model']}*\n\n"
    
    # Додаємо всі доступні характеристики
    for key, value in component.items():
        if key not in ["model", "photo", "link"]:
            if key == "price":
                details += f"*{key.capitalize()}:* {value:,} грн\n"
            else:
                details += f"*{key.capitalize()}:* {value}\n"
    
    # Додаємо посилання
    if "link" in component:
        details += f"\n[Посилання на товар]({component['link']})"
    
    return details

# Обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_sessions[user_id] = {"builds": [], "compare_mode": False}
    
    await update.message.reply_text(
        "Вітаю! Я бот для підбору комплектуючих ПК. Введіть ваш бюджет (у гривнях), щоб я допоміг вам підібрати оптимальну збірку. Наприклад: '30000'.\n\n"
        "Доступні команди:\n"
        "/help - Показати довідку\n"
        "/compare - Порівняти дві останні збірки\n"
        "/details - Показати детальну інформацію про компоненти останньої збірки"
    )

# Обробник команди /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Як користуватися ботом:\n\n"
        "1. Введіть ваш бюджет у гривнях (наприклад, '30000')\n"
        "2. За бажанням, вкажіть переваги щодо компонентів\n"
        "3. Я запропоную вам кілька варіантів збірки ПК\n\n"
        "Приклади команд:\n"
        "- '30000' - підібрати збірку за 30000 грн\n"
        "- '50000 RTX' - підібрати збірку за 50000 грн з відеокартою серії RTX\n"
        "- '40000 Ryzen' - підібрати збірку за 40000 грн з процесором Ryzen\n"
        "- '60000 білий' - підібрати збірку за 60000 грн з білим корпусом\n"
        "- '70000 красивий' - підібрати естетично привабливу збірку за 70000 грн\n"
        "- '80000 RTX білий' - підібрати збірку за 80000 грн з відеокартою RTX та білим корпусом\n\n"
        "Додаткові команди:\n"
        "/compare - Порівняти дві останні збірки\n"
        "/details - Показати детальну інформацію про компоненти останньої збірки"
    )

# Обробник команди /compare
async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or len(user_sessions[user_id]["builds"]) < 2:
        await update.message.reply_text(
            "Для порівняння потрібно мати щонайменше дві збірки. Спочатку створіть кілька збірок, ввівши різні бюджети."
        )
        return
    
    builds = user_sessions[user_id]["builds"]
    comparison = compare_builds(builds[-1], builds[-2])
    
    await update.message.reply_text(
        comparison,
        parse_mode=ParseMode.MARKDOWN
    )

# Обробник команди /details
async def details_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id]["builds"]:
        await update.message.reply_text(
            "Спочатку створіть збірку, ввівши бюджет."
        )
        return
    
    build = user_sessions[user_id]["builds"][-1]
    
    # Створюємо клавіатуру для вибору компонента
    keyboard = [
        [
            InlineKeyboardButton("Відеокарта", callback_data="details_gpu"),
            InlineKeyboardButton("Процесор", callback_data="details_cpu")
        ],
        [
            InlineKeyboardButton("Материнська плата", callback_data="details_motherboard"),
            InlineKeyboardButton("Оперативна пам'ять", callback_data="details_ram")
        ],
        [
            InlineKeyboardButton("Накопичувач", callback_data="details_storage"),
            InlineKeyboardButton("Блок живлення", callback_data="details_psu")
        ],
        [
            InlineKeyboardButton("Корпус", callback_data="details_case"),
            InlineKeyboardButton("Охолодження", callback_data="details_cooling")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Виберіть компонент для детальної інформації:",
        reply_markup=reply_markup
    )

# Обробник натискань на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id]["builds"]:
        await query.edit_message_text(
            "Сесія закінчилася. Будь ласка, створіть нову збірку."
        )
        return
    
    data = query.data.split("_")
    action = data[0]
    component_type = data[1]
    
    if len(data) > 2:
        build_index = int(data[2])
        if build_index >= len(user_sessions[user_id]["builds"]):
            await query.edit_message_text("Ця збірка більше не доступна.")
            return
        build = user_sessions[user_id]["builds"][build_index]
    else:
        build = user_sessions[user_id]["builds"][-1]
    
    if action == "details":
        if component_type in build:
            component = build[component_type]
            details = get_component_details(component)
            
            # Створюємо клавіатуру для повернення до збірки
            keyboard = [[InlineKeyboardButton("Повернутися до збірки", callback_data="back_to_build")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                details,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "Інформація про цей компонент недоступна."
            )
    elif action == "back_to_build":
        # Повертаємося до інформації про збірку
        build_index = user_sessions[user_id]["builds"].index(build)
        
        # Створюємо клавіатуру для збірки
        keyboard = [
            [
                InlineKeyboardButton("Деталі відеокарти", callback_data=f"details_gpu_{build_index}"),
                InlineKeyboardButton("Деталі процесора", callback_data=f"details_cpu_{build_index}")
            ],
            [
                InlineKeyboardButton("Деталі материнської плати", callback_data=f"details_motherboard_{build_index}"),
                InlineKeyboardButton("Деталі пам'яті", callback_data=f"details_ram_{build_index}")
            ],
            [
                InlineKeyboardButton("Деталі накопичувача", callback_data=f"details_storage_{build_index}"),
                InlineKeyboardButton("Деталі БЖ", callback_data=f"details_psu_{build_index}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            format_pc_build(build, build_index + 1),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif action == "compare":
        if len(user_sessions[user_id]["builds"]) < 2:
            await query.message.reply_text(
                "Для порівняння потрібно мати щонайменше дві збірки. Спочатку створіть ще одну збірку."
            )
            return
        
        builds = user_sessions[user_id]["builds"]
        comparison = compare_builds(builds[-1], builds[-2])
        
        await query.message.reply_text(
            comparison,
            parse_mode=ParseMode.MARKDOWN
        )

# Обробник текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Ініціалізуємо сесію користувача, якщо вона не існує
    if user_id not in user_sessions:
        user_sessions[user_id] = {"builds": [], "compare_mode": False}
    
    # Розбираємо введення - очікуємо бюджет і, можливо, бажані параметри
    parts = text.split()
    budget_str = parts[0]
    
    try:
        budget = int(budget_str)
    except ValueError:
        await update.message.reply_text(
            "Будь ласка, введіть ваш бюджет у гривнях. Наприклад: '30000'."
        )
        return
    
    # Перевіряємо наявність переваг
    preferred_gpu = ""
    preferred_cpu = ""
    preferred_color = ""
    preferred_aesthetics = False
    
    if len(parts) > 1:
        preferences = " ".join(parts[1:]).lower()
        
        # Перевіряємо наявність кольору
        if "білий" in preferences or "white" in preferences:
            preferred_color = "white"
        elif "чорний" in preferences or "black" in preferences:
            preferred_color = "black"
        
        # Перевіряємо наявність естетичних вподобань
        if any(word in preferences for word in ["красивий", "гарний", "стильний", "естетичний", "beautiful", "nice", "stylish"]):
            preferred_aesthetics = True
        
        # Перевіряємо наявність переваг щодо GPU
        gpu_keywords = ["rtx", "gtx", "radeon", "nvidia", "amd", "відеокарт", "geforce"]
        if any(keyword in preferences for keyword in gpu_keywords):
            for keyword in gpu_keywords:
                if keyword in preferences:
                    preferred_gpu = keyword
                    break
        
        # Перевіряємо наявність переваг щодо CPU
        cpu_keywords = ["intel", "ryzen", "core", "процесор", "threadripper", "pentium", "celeron", "athlon"]
        if any(keyword in preferences for keyword in cpu_keywords):
            for keyword in cpu_keywords:
                if keyword in preferences:
                    preferred_cpu = keyword
                    break
    
    # Знаходимо збірки ПК в межах бюджету
    result = find_components_within_budget(budget, preferred_gpu, preferred_cpu, preferred_color, preferred_aesthetics)
    
    if "error" in result:
        await update.message.reply_text(result["error"])
        return
    
    # Надсилаємо результати
    await update.message.reply_text(
        f"Знайдено {len(result['combinations'])} варіантів збірки ПК в межах бюджету {budget:,} грн:"
    )
    
    # Зберігаємо збірки в сесії користувача
    user_sessions[user_id]["builds"].extend(result["combinations"])
    
    # Надсилаємо кожну збірку окремим повідомленням
    for i, build in enumerate(result["combinations"]):
        # Створюємо клавіатуру для кожної збірки
        keyboard = [
            [
                InlineKeyboardButton("Деталі відеокарти", callback_data=f"details_gpu_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}"),
                InlineKeyboardButton("Деталі процесора", callback_data=f"details_cpu_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}")
            ],
            [
                InlineKeyboardButton("Деталі материнської плати", callback_data=f"details_motherboard_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}"),
                InlineKeyboardButton("Деталі пам'яті", callback_data=f"details_ram_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}")
            ],
            [
                InlineKeyboardButton("Деталі накопичувача", callback_data=f"details_storage_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}"),
                InlineKeyboardButton("Деталі БЖ", callback_data=f"details_psu_{len(user_sessions[user_id]['builds'])-len(result['combinations'])+i}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            format_pc_build(build, i + 1),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    # Додаємо фінальне повідомлення з рекомендаціями
    keyboard = [
        [
            InlineKeyboardButton("Порівняти збірки", callback_data="compare_builds")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Ось мої рекомендації! Якщо хочете інші варіанти, введіть інший бюджет або уточніть ваші переваги щодо компонентів.",
        reply_markup=reply_markup
    )

def main() -> None:
    # Отримуємо токен з середовища або запитуємо у користувача
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        token = input("Введіть ваш токен Telegram бота: ")
    
    # Створюємо додаток
    application = Application.builder().token(token).build()
    
    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("compare", compare_command))
    application.add_handler(CommandHandler("details", details_command))
    
    # Додаємо обробник натискань на кнопки
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Додаємо обробник текстових повідомлень
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаємо бота
    print("Бот запущено! Натисніть Ctrl+C для зупинки.")
    application.run_polling()

if __name__ == "__main__":
    main()