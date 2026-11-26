import base64, ctypes, shutil, io, json, msvcrt, os, random, re, socket, subprocess, sys, threading, time, traceback, uuid, winreg, winsound, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import requests

os.system("")
SEARCH_QUERIES_EN = [
    "vless reality subscription", "vless trojan free", "hysteria2 tuic vless free",
    "shadowsocks vless nodes", "xray singbox config", "v2ray free subscription",
    "clash meta vless", "vless grpc ws reality", "free proxy vless trojan",
    "v2rayng free nodes", "nekobox vless reality", "hysteria2 subscription",
    "tuic v5 free nodes", "shadowsocks 2022 free", "xray reality configs",
    "sing-box outbound vless", "vless xtls-rprx-vision", "free v2ray sub link",
    "clash verge vless", "trojan gfw free nodes", "vless cdn cloudflare",
    "xray json subscription", "v2ray collector vless", "proxy aggregator vless",
    "subconverter vless trojan"
]
SEARCH_QUERIES_RU = [
    "vless ru", "vless reality ru", "whitelist vless",
    "vless обход рф", "бесплатный впн vless", "vless подписка",
    "белые списки vless", "vless reality обход", "vless для россии",
    "обход блокировок vless", "vless sni yandex vk", "бесплатные ключи vless",
    "v2rayn подписка рф", "hysteria2 обход рф", "sing-box конфиг рф"
]
PINNED_REPOS_RU = [
    "kort0881/vpn-vless-configs-russia",
    "FLAT447/v2ray-lists",
    "histeenn/VLESS-PO-BRIBI",
    "jsxta/whitelist-russia"
]
WHITELIST_SNI = (
    "yandex.ru", "ya.ru", "yandex.net", "yastatic.net", "vk.com", "vk.ru", "userapi.com", "vkuservideo.net",
    "mail.ru", "imgsmail.ru", "ok.ru", "dzen.ru", "gosuslugi.ru", "sberbank.ru", "tbank.ru", "ozon.ru",
    "wildberries.ru", "wb.ru", "avito.ru", "kinopoisk.ru", "rutube.ru", "2gis.ru", "mts.ru", "megafon.ru", "beeline.ru", "tele2.ru", "rt.ru"
)
BLOCKED_COUNTRIES = ("RU",)
TCP_WORKERS = 300
SPEED_URL = "https://cloudflare.com"
IPIFY_URL = "https://icanhazip.com"
TIMEOUT = 4.0

GH_HOST = "https://" + "github.com"
GH = "https://" + "://github.com"
RAW = "https://" + "://githubusercontent.com"
JSDELIVR = "https://" + "cdn.jsdelivr.net/gh"
STATICALLY = "https://" + "cdn.statically.io/gh"
TG_WEB = "https://" + "t.me/s/"

DEFAULT_TG = ["vless_free", "v2ray_configs_pool", "FreeV2rayVPN", "v2rayng_vpn_free", "Outline_Vpn_Free", "v2ray_free_conf", "PrivateVPNs", "vless_vmess"]
WEB_NODES = [
    ("kort0881", "vpn-vless-configs-russia", "main", "subscribed/vless.txt"),
    ("FLAT447", "v2ray-lists", "main", "vless.txt"),
    ("jsxta", "whitelist-russia", "main", "whitelist.txt"),
    ("rtwo2", "FastNodes", "main", "All_Configs_Sub.txt"),
    ("AmirrezaFarnamTaheri", "HUNTX", "main", "All_Configs_Sub.txt"),
    ("peasoft", "NoMoreWalls", "master", "list_raw.txt"),
    ("Pawdroid", "Free-servers", "main", "sub"),
    ("mfuu", "v2ray", "master", "v2ray"),
    ("aiboboxx", "v2rayfree", "main", "v2"),
    ("freefq", "free", "master", "v2"),
    ("Mahdi0024", "ProxyCollector", "master", "sub/proxies.txt"),
    ("ermaozi", "get_subscribe", "main", "subscribe/v2ray.txt")
]
DEFAULT_WEB = [f"{GH_HOST}/{o}/{r}/blob/{b}/{p}" for o, r, b, p in WEB_NODES]
RU_BYPASS_DOMAINS = [".ru", ".xn--p1ai", ".su", "yandex.ru", "ya.ru", "vk.com", "vk.ru", "mail.ru", "gosuslugi.ru", "sberbank.ru", "tbank.ru", "ozon.ru", "wildberries.ru", "avito.ru", "kinopoisk.ru"]
CUSTOM_FILE, BL_FILE, CFG_FILE, FAV_FILE, CACHE_FILE, STATS_FILE, LOG_FILE = "custom_sources.txt", "netpulse_blacklist.json", "netpulse_config.json", "favorites.txt", "alive_cache.json", "sources_stats.json", "netpulse_vpn.log"
CFG = {"lang": "RU", "color": "\033[38;2;157;78;221m", "cname": "#9D4EDD", "countries": set(), "proto": "", "src": 0, "gh_lang": 0, "wl_mode": 0, "use_px": False, "px_port": 10809, "sub_port": 18080, "tun": False, "failover": True, "blacklist": True, "geoip": True, "strict_ip": True, "auto_scan_min": 0, "speed": True, "mode": 3, "repos": 40, "batch_cap": 3500, "limit": 40, "min_speed": 0.0, "max_ping": 0, "font": 1, "tstyle": 1, "winfont": "Consolas", "compact": False, "overlay": False, "grad": 1, "user_presets": {}, "token": "", "bg": 6, "target": 1, "xray": r"C:\vpns\v2rayN-windows-64\bin\xray\xray.exe", "singbox": ""}
TARGETS = {1: ("https://icanhazip.com", "Basic HTTPS / Базовый IP"), 2: ("https://youtube.com", "YouTube / Google"), 3: ("https://discord.com", "Discord / OpenAI")}
def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            if isinstance(data.get("proto"), int):
                data["proto"] = {1: "vless", 2: "trojan", 3: "ss", 4: "hy2+tuic"}.get(data["proto"], "")
            CFG.update(data)
            CFG["countries"] = set(data.get("countries", list()))
        except Exception: pass
    if not os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, "w", encoding="utf-8") as f:
                f.write("# Добавьте сюда свои Telegram-каналы (без @), репозитории (автор/репа) или прямые ссылки\n")
        except Exception: pass

def save_cfg():
    try:
        out = dict(CFG)
        out["countries"] = list(CFG["countries"])
        with open(CFG_FILE, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
    except Exception: pass

def get_px():
    if not CFG.get("use_px", False): return None
    p = CFG.get("px_port", 10809)
    try:
        with socket.create_connection(("127.0.0.1", p), timeout=0.08):
            return {"http": f"http://127.0.0.1:{p}", "https": f"http://127.0.0.1:{p}"}
    except Exception: return None

def load_bl():
    if os.path.exists(BL_FILE):
        try:
            with open(BL_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            now = time.time()
            return {k: v for k, v in data.items() if v > now}
        except Exception: pass
    return {}

def save_bl(bl):
    try:
        with open(BL_FILE, "w", encoding="utf-8") as f: json.dump(bl, f, ensure_ascii=False, indent=2)
    except Exception: pass

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            if isinstance(data, dict) and data.get("nodes"): return data
        except Exception: pass
    return {"nodes": list(), "offset": 0, "ts": 0}

def save_cache(nodes, offset=0):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f: json.dump({"nodes": nodes, "offset": offset, "ts": time.time()}, f)
    except Exception: pass

def load_src_db():
    db = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: db = json.load(f)
        except Exception: db = {}
    for r in PINNED_REPOS_RU:
        k = f"gh:{r}"
        if k not in db: db[k] = {"collected": 0, "working": 0, "prio": True}
    return db

def save_src_db(db):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception: pass

def find_cores():
    x_ok, s_ok = os.path.exists(CFG.get("xray", "")), os.path.exists(CFG.get("singbox", ""))
    if x_ok and s_ok: return CFG["xray"], CFG["singbox"]
    for root in [os.getcwd(), os.path.join(os.getcwd(), "cores"), r"C:\vpns", r"C:\Program Files", os.path.expanduser("~")]:
        if not os.path.exists(root): continue
        for dp, _, fn in os.walk(root):
            if not x_ok and "xray.exe" in fn: CFG["xray"] = os.path.join(dp, "xray.exe"); x_ok = True
            if not s_ok and "sing-box.exe" in fn: CFG["singbox"] = os.path.join(dp, "sing-box.exe"); s_ok = True
            if x_ok and s_ok: break
            if dp.count(os.sep) - root.count(os.sep) > 3: del _[:]
    save_cfg()
    return CFG.get("xray", ""), CFG.get("singbox", "")

def get_hdr():
    h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NetPulse/6.2"}
    if CFG.get("token"): h["Authorization"] = f"Bearer {CFG['token']}"
    return h

def download_cores(force=False):
    c, core_dir = CFG["color"], os.path.abspath("cores")
    os.makedirs(core_dir, exist_ok=True)
    x_bin, s_bin = find_cores()
    tasks = list()
    if force or not x_bin or not os.path.exists(x_bin): tasks.append(("Xray-core", "XTLS/Xray-core", "xray-windows-64.zip", "xray.exe", "xray"))
    if force or not s_bin or not os.path.exists(s_bin): tasks.append(("sing-box", "SagerNet/sing-box", "windows-amd64.zip", "sing-box.exe", "singbox"))
    if not tasks: print(f"{c}[+] Оба ядра уже установлены!{RST}"); return True
    for title, repo, kw, exe_name, cfg_key in tasks:
        print(f"\n{c}[*] Загрузка {title} ({repo})...{RST}")
        try:
            r = requests.get(f"{GH}/repos/{repo}/releases/latest", headers=get_hdr(), proxies=get_px(), timeout=15)
            r.raise_for_status()
            dl_url = next((a.get("browser_download_url", "") for a in r.json().get("assets", list()) if kw in a.get("name", "").lower() and a.get("name", "").lower().endswith(".zip")), "")
            if not dl_url: continue
            t_dl = time.time()
            with requests.get(dl_url, proxies=get_px(), stream=True, timeout=(10, 60)) as z_res:
                z_res.raise_for_status()
                tot = int(z_res.headers.get("content-length", 0))
                buf, cur = io.BytesIO(), 0
                for ch in z_res.iter_content(65536):
                    if ch:
                        buf.write(ch); cur += len(ch)
                        if tot > 0: draw_bar(cur, tot, f"| {cur // 1048576} MB", t_dl)
            with zipfile.ZipFile(buf) as zf:
                for member in zf.namelist():
                    if member.lower().endswith(exe_name):
                        dst = os.path.join(core_dir, exe_name)
                        with zf.open(member) as src_f, open(dst, "wb") as out_f: out_f.write(src_f.read())
                        CFG[cfg_key] = dst; save_cfg(); print(f"{c}[+] {title} установлен: {dst}{RST}"); break
        except Exception as e: print(f"\033[91m[!] Ошибка {title}: {e}\033[0m")
    x_ok, _ = find_cores()
    return bool(x_ok and os.path.exists(x_ok))
load_cfg()
find_cores()
COLORS = {
    "1": ("\033[92m", "Green / Изумрудный"), "2": ("\033[96m", "Cyan / Неоновый"),
    "3": ("\033[95m", "Purple / Киберпанк"), "4": ("\033[93m", "Amber / Янтарный"),
    "5": ("\033[97m", "White / Белый"), "6": ("\033[91m", "Red / Красный"),
    "7": ("\033[38;5;39m", "Ice Blue / Ледяной синий"), "8": ("\033[38;5;48m", "Mint / Мятный"),
    "9": ("\033[38;5;208m", "Orange / Оранжевый"), "10": ("\033[38;5;198m", "Hot Pink / Неоновый розовый"),
    "11": ("\033[38;2;138;43;226m", "Violet / Ультрафиолет"), "12": ("\033[38;2;255;215;0m", "Gold / Золотой"),
    "13": ("\033[38;2;0;255;170m", "Aqua / Аквамарин"), "14": ("\033[38;2;255;80;80m", "Coral / Коралловый")
}
BANNERS = {
    1: ("Block 3D", [
        "  ███╗   ██╗███████╗████████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗",
        "  ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝",
        "  ██╔██╗ ██║█████╗     ██║   ██████╔╝██║   ██║██║     ███████╗█████╗  ",
        "  ██║╚██╗██║██╔══╝     ██║   ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  ",
        "  ██║ ╚████║███████╗   ██║   ██║     ╚██████╔╝███████╗███████║███████╗",
        "  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝"
    ]),
    2: ("Cyber Slant", [
        "     _   __ ______ ______ ____   __  __ __    _____  ______",
        "    / | / // ____//_  __// __ \\ / / / // /   / ___/ / ____/",
        "   /  |/ // __/    / /  / /_/ // / / // /    \\__ \\ / __/   ",
        "  / /|  // /___   / /  / ____// /_/ // /___ ___/ // /___   ",
        " /_/ |_//_____/  /_/  /_/     \\____//_____//____//_____/   ",
        "                                                           "
    ]),
    3: ("Double Neon", [
        "  ╔═╗ ╔═╗╔════╗╔══════╗╔═════╗ ╔═╗ ╔═╗╔═╗     ╔═════╗╔════╗",
        "  ║ ╚╗║ ║║ ╔══╝╚═╗  ╔═╝║ ╔═╗ ║ ║ ║ ║ ║║ ║     ║ ╔═══╝║ ╔══╝",
        "  ║  ╚╝ ║║ ╚══╗  ║  ║  ║ ╚═╝ ║ ║ ║ ║ ║║ ║     ║ ╚═══╗║ ╚══╗",
        "  ║ ╔╗  ║║ ╔══╝  ║  ║  ║ ╔═══╝ ║ ║ ║ ║║ ║     ╚═══╗ ║║ ╔══╝",
        "  ║ ║╚╗ ║║ ╚══╗  ║  ║  ║ ║     ║ ╚═╝ ║║ ╚════╗╔═══╝ ║║ ╚══╗",
        "  ╚═╝ ╚═╝╚════╝  ╚══╝  ╚═╝     ╚═════╝╚══════╝╚═════╝╚════╝"
    ]),
    4: ("Cyber Blade", [
        "  /|  / / //   / / /__  ___/ //   ) ) //   / / / /     //   ) ) //   / /",
        " //| / / //____      / /    //___/ / //   / / / /     ((       //____   ",
        "// |/ / / ____      / /    / ____ / //   / / / /        \\\\    / ____    ",
        "//  / / //         / /    //       //   / / / /           ) ) //        ",
        "//  / / //____/ / / /    //       ((___/ / / /____/ / ((___/ / //____/ / ",
        "                                                                         "
    ]),
    5: ("Heavy Block", [
        "  █▄  █ ████ ▀▀█▀▀ █▀▀▄ █  █ █    ▄▀▀▀ ████",
        "  █ █ █ █▄▄    █   █▄▄▀ █  █ █    ▀▀▀█ █▄▄ ",
        "  █  ▀█ █▄▄▄   █   █    ▀▄▄▀ █▄▄▄ ▄▄▄▀ █▄▄▄",
        "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "        [ NETPULSE KERNEL ENGINE V1.6.8 ]    ",
        "                                           "
    ])
}
COUNTRIES_INFO = [("DE", "Германия / Germany"), ("NL", "Нидерланды / Netherlands"), ("ES", "Испания / Spain"), ("FI", "Финляндия / Finland"), ("SE", "Швеция / Sweden"), ("PL", "Польша / Poland"), ("GB", "Британия / UK"), ("US", "США / USA"), ("TR", "Турция / Turkey"), ("KZ", "Казахстан / Kazakhstan"), ("AE", "ОАЭ / UAE"), ("SG", "Сингапур / Singapore"), ("JP", "Япония / Japan")]
RST, DIM = "\033[0m", "\033[2m"

TXT = {
    "RU": {"sub": "Умный агрегатор и VPN-менеджер V1.6.8", "auth": "Авторы: Gemini & Glitch", "m1": "1. Запустить поиск / Допроверить кэш", "m2": "2. Проверить буфер обмена (Clipboard Scan)", "m3": "3. Менеджер серверов (VPN / TUN / Трафик-лог)", "m4": "4. Рейтинг репозиториев и Приоритет скана", "m5": "5. Защита от белых списков (CDN + RU-SNI)", "m6": "6. Источники / Язык баз / Карантин", "m7": "7. Прокси v2rayN для парсинга", "m8": "8. Страны и Протокол поиска (без RU)", "m9": "9. GeoIP / Strict Anti-DPI (Смена IP)", "m10": "10. Цель проверки (Сайт)", "m11": "11. Замер скорости / Нагрузка на ЦП", "m12": "12. Лимиты / Мин.Скорость / Макс.Пинг", "m13": "13. Кастомизация (Цвет, Фон и Шрифт)", "m14": "14. Язык / Ярлык / Ядра / Токен / Порт", "m15": "15. Авто-проверка по расписанию (Таймер)", "m0": "0. Выход  |  [W] Свернуть в системный трей", "ask": "Выберите пункт меню > ", "all": "ВСЕ (без RU)", "on": "ВКЛ", "off": "ВЫКЛ", "unit": "узл/с", "wl_m": {0: "АВТО (CDN)", 1: "Приоритет RU-SNI", 2: "Строго RU-SNI"}, "srcs": {0: "ВСЕ (GH+TG+Web)", 1: "Только GH", 2: "Только TG+Web", 3: "GH+Web"}, "gh_l": {0: "RU+EN", 1: "Только RU", 2: "Только EN"}, "bgs": {1: "Пульс", 2: "Матрица", 3: "Поток", 4: "Звезды", 5: "Радар", 6: "ДНК", 7: "Дождь", 8: "Волны", 9: "Искры", 10: "Сканер", 0: "Выкл"}, "modes": {1: "2x20", 2: "4x25", 3: "6x25"}, "s1": "[1/5] Сбор источников (GitHub / CDN / TG / Web)...", "s2": "[2/5] Скачивание и парсинг", "s3": "[3/5] Умный фильтр и TCP-отсев", "s4": "[4/5] Турбо-проверка (Ctrl+C = Стоп)", "s5": "[5/5] Замер скорости скачивания", "done": "Готово! Рабочих серверов:", "url": "Подписки:", "back": "Нажмите Enter для возврата в меню...", "bat_ok": "[+] Ярлык NETPULSE.bat создан на Рабочем столе!", "no_xray": "[!] Ядра не найдены! Скачать автоматически с GitHub? (Y/N) > "},
    "EN": {"sub": "Smart Aggregator & VPN Manager V1.6.8", "auth": "Authors: Gemini & Glitch", "m1": "1. Start Scan / Resume TCP Cache", "m2": "2. Clipboard Scan (Paste & Test)", "m3": "3. Server Manager (VPN / TUN / Traffic Log)", "m4": "4. Repo Leaderboard & Scan Priority", "m5": "5. Whitelist Shield (CDN + RU-SNI)", "m6": "6. Sources / Repo Lang / Quarantine", "m7": "7. v2rayN Proxy for Scraping", "m8": "8. Countries & Protocol (No RU)", "m9": "9. GeoIP / Strict Anti-DPI (IP Check)", "m10": "10. Validation Target Site", "m11": "11. Speed Test / CPU Load Mode", "m12": "12. Repos / [4/5] Cap / Limit", "m13": "13. Customization (RGB Color & 10 BGs)", "m14": "14. Lang / Shortcut / Cores / Token / Port", "m15": "15. Scheduled Auto-Scan (Timer)", "m0": "0. Exit  |  [W] Minimize to System Tray", "ask": "Select option > ", "all": "ALL (No RU)", "on": "ON", "off": "OFF", "unit": "nodes/s", "wl_m": {0: "AUTO (CDN)", 1: "Priority RU-SNI", 2: "Strict RU-SNI"}, "srcs": {0: "ALL (GH+TG+Web)", 1: "GH Only", 2: "TG+Web Only", 3: "GH+Web"}, "gh_l": {0: "RU+EN", 1: "RU Only", 2: "EN Only"}, "bgs": {1: "Pulse", 2: "Matrix", 3: "Stream", 4: "Stars", 5: "Radar", 6: "DNA", 7: "Rain", 8: "Sine", 9: "Sparks", 10: "Laser", 0: "Off"}, "modes": {1: "2x20", 2: "4x25", 3: "6x25"}, "s1": "[1/5] Collecting sources (GitHub / CDN / TG / Web)...", "s2": "[2/5] Downloading & parsing", "s3": "[3/5] Smart filter & TCP check", "s4": "[4/5] Turbo batch check (Ctrl+C = Stop)", "s5": "[5/5] Measuring download speed", "done": "Done! Working servers:", "url": "Subscriptions:", "back": "Press Enter to return to menu...", "bat_ok": "[+] Shortcut NETPULSE.bat created on Desktop!", "no_xray": "[!] Cores not found! Download automatically from GitHub? (Y/N) > "}
}

SUB_MAP, SRC_STATS, CHECKED, FOUND_COUNT, STOP_EVENT, LOCK, PROC_FLAGS = {}, {}, 0, 0, threading.Event(), threading.Lock(), 0
ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH, REAL_HOME_IP = None, "", "", "", ""
ACTIVE_START, ACTIVE_IP, ACTIVE_CC, FAILOVER_CNT = 0.0, "", "", 0
VPN_LOG, LOG_LOCK = list(), threading.Lock()
NEXT_AUTO_SCAN, SCAN_BUSY, TRAY_HIDDEN = 0.0, False, False
RU_EN_MAP = str.maketrans("йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ", "qwertyuiop[]asdfghjkl;'zxcvbnm,.QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>")
def ru2en(txt):
    return str(txt).translate(RU_EN_MAP)

first = lambda s, d="": next(iter(s), d) if s else d
tr = lambda k: TXT[CFG["lang"]][k]

def add_log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_LOCK:
        VPN_LOG.append(line)
        if len(VPN_LOG) > 60: VPN_LOG.pop(0)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")
        except Exception: pass

def load_favs():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f: return [ln.strip() for ln in f if ln.strip()]
        except Exception: pass
    return list()

def save_favs(favs):
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f: f.write("\n".join(favs))
    except Exception: pass

def draw_bar(cur, tot, extra="", t0=None):
    if tot <= 0 or TRAY_HIDDEN: return
    ratio = min(1.0, max(0.0, cur / tot))
    pct = ratio * 100.0
    width = 28
    blocks = " ▏▎▍▌▋▊▉█"
    exact = ratio * width
    full = int(exact)
    rem = int((exact - full) * 8)
    if full >= width: bar = "█" * width
    else:
        tip = blocks[rem] if rem > 0 else "▸"
        bar = ("█" * full) + tip + (f"{DIM}━{RST}{CFG['color']}" * (width - full - 1))
    tm = f" {time.time() - t0:.1f}s" if t0 else ""
    sys.stdout.write(f"\r\033[K  {CFG['color']}┫{bar}┣ {pct:5.1f}% ({cur}/{tot}){tm} {extra}{RST}")
    sys.stdout.flush()
    if cur >= tot: print()
def b64_dec(s):
    s = unquote(s.strip()).replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * (-len(s) % 4)).decode("utf-8", errors="ignore")

def parse_ss(uri):
    try:
        body = first(uri.split("#"), uri)[5:]
        body = first(body.split("?"), body)
        if "@" not in body: body = b64_dec(body)
        if "@" not in body: return None
        cred, hp = body.rsplit("@", 1)
        if ":" not in cred: cred = b64_dec(cred)
        if ":" not in cred or ":" not in hp: return None
        m, pwd = cred.split(":", 1)
        h, pt = hp.rsplit(":", 1)
        return h.strip("[]"), int(pt), m.strip(), pwd
    except Exception: return None

def make_gh_mirrors(o, n, b, p):
    return [f"{GH_HOST}/{o}/{n}/blob/{b}/{p}", f"{JSDELIVR}/{o}/{n}@{b}/{p}", f"{RAW}/{o}/{n}/{b}/{p}"]

def get_files(repo):
    o, n, b = repo.get("owner", {}).get("login"), repo.get("name"), repo.get("default_branch") or "main"
    tag, urls = f"gh:{o}/{n}", list()
    try:
        r = requests.get(f"{GH}/repos/{o}/{n}/git/trees/{b}", params={"recursive": "1"}, headers=get_hdr(), proxies=get_px(), timeout=3.5)
        if r.status_code == 200:
            for i in r.json().get("tree", list()):
                p = i.get("path", "")
                if i.get("type") == "blob" and (p.endswith((".txt", ".list", ".sub", ".conf", ".yaml", ".yml")) or "." not in p.split("/").pop()):
                    if not any(x in p.lower() for x in ("readme", "license", ".git")):
                        urls.append((tag, make_gh_mirrors(o, n, b, p)))
            if urls: return urls
    except Exception: pass
    try:
        hr = requests.get(f"{GH_HOST}/{o}/{n}", headers={"User-Agent": "Mozilla/5.0"}, proxies=get_px(), timeout=6)
        if hr.status_code == 200:
            br_m = re.search(r'"defaultBranch":"([^"]+)"', hr.text)
            if br_m: b = br_m.group(1)
            seen_p, dirs = set(), list()
            for p, ctype in re.findall(r'"path":"([^"]+)","contentType":"(file|directory)"', hr.text):
                if ctype == "directory" and len(dirs) < 4:
                    dirs.append(p)
                elif ctype == "file" and p not in seen_p:
                    seen_p.add(p)
                    if p.endswith((".txt", ".list", ".sub", ".conf", ".yaml", ".yml")) or "." not in p.split("/").pop():
                        if not any(x in p.lower() for x in ("readme", "license", ".git", "contributing", "security")):
                            urls.append((tag, make_gh_mirrors(o, n, b, p)))
            for d in dirs:
                try:
                    dr = requests.get(f"{GH_HOST}/{o}/{n}/tree/{b}/{d}", headers={"User-Agent": "Mozilla/5.0"}, proxies=get_px(), timeout=5)
                    if dr.status_code == 200:
                        for p, ctype in re.findall(r'"path":"([^"]+)","contentType":"file"', dr.text):
                            if p not in seen_p:
                                seen_p.add(p)
                                if p.endswith((".txt", ".list", ".sub", ".conf", ".yaml", ".yml")) or "." not in p.split("/").pop():
                                    urls.append((tag, make_gh_mirrors(o, n, b, p)))
                except Exception: pass
    except Exception: pass
    return urls

def get_tg_and_web(bl):
    items, src_mode = list(), CFG.get("src", 0)
    channels = list(DEFAULT_TG) if src_mode in (0, 2) else list()
    web_urls = list(DEFAULT_WEB) if src_mode in (0, 2, 3) else list()
    if os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
                for ln in f:
                    s = ln.strip()
                    if not s or s.startswith("#"): continue
                    if s.startswith(("http://", "https://")):
                        if src_mode in (0, 2, 3): web_urls.append(s)
                    elif "/" in s and not s.startswith("@"): pass
                    elif src_mode in (0, 2): channels.append(s.lstrip("@"))
        except Exception: pass
    for u in dict.fromkeys(web_urls):
        if not CFG.get("blacklist", True) or u not in bl: items.append((u, [u]))
    for ch in dict.fromkeys(channels):
        tag = f"tg:{ch}"
        if not CFG.get("blacklist", True) or tag not in bl: items.append((tag, [f"{TG_WEB}{ch}"]))
    return items

def parse_text(txt):
    m_raw = re.search(r'"rawLines":\[(.*?)\]', txt, flags=re.DOTALL)
    if m_raw:
        joined = "\n".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m_raw.group(1)))
        try: txt = joined.encode("utf-8").decode("unicode_escape")
        except Exception: txt = joined
    clean = re.sub(r'<[^>]+>', '\n', txt)
    pat = re.compile(r'(?:vless|trojan|ss|hy2|hysteria2|tuic)://[^\s"\'<>\\]+')
    m = pat.findall(clean)
    if not m:
        stripped = "".join(clean.split())
        if len(stripped) >= 40 and re.fullmatch(r'[A-Za-z0-9+/=_-]+', stripped):
            try: m.extend(pat.findall(b64_dec(stripped)))
            except Exception: pass
        if not m:
            for b64_chunk in re.findall(r'[A-Za-z0-9+/=_-]{60,}', clean):
                try: m.extend(pat.findall(b64_dec(b64_chunk)))
                except Exception: pass
    return m

def get_hp(uri):
    clean = first(uri.split("#"), uri)
    sc = first(clean.split("://"), "").lower()
    if sc == "hysteria2": sc = "hy2"
    if sc == "ss":
        res = parse_ss(clean)
        if not res: return sc, None, None
        h, pt, _, _ = res
        return sc, h, pt
    p = urlparse(clean)
    return sc, p.hostname, int(p.port) if p.port else None

def is_whitelist_sni(uri):
    try:
        clean = first(uri.split("#"), uri)
        q = parse_qs(urlparse(clean).query)
        for target in (first(q.get("sni"), "").lower().strip(), first(q.get("host"), "").lower().strip()):
            if target and any(target == d or target.endswith("." + d) for d in WHITELIST_SNI): return True
    except Exception: pass
    return False

def parse_proto_set(val):
    if isinstance(val, int): return {1: {"vless"}, 2: {"trojan"}, 3: {"ss"}, 4: {"hy2", "tuic"}}.get(val, set())
    if not val: return set()
    res = set()
    for tok in re.split(r'[,+\s/|]+', str(val).lower().strip()):
        if tok in ("vless", "trojan", "ss", "hy2", "tuic"): res.add(tok)
        elif tok == "hysteria2": res.add("hy2")
        elif tok == "shadowsocks": res.add("ss")
    return res

def smart_prefilter(raw_list):
    uniq, subnets = {}, {}
    bad_hosts = ("127.0.0.1", "0.0.0.0", "localhost", "example.com", "://cloudflare.com")
    allowed_protos = parse_proto_set(CFG.get("proto", ""))
    wl_mode = CFG.get("wl_mode", 0)
    for src, uri in raw_list:
        try:
            sc, h, pt = get_hp(uri)
            if not h or not pt or not (1 <= pt <= 65535) or h.lower() in bad_hosts: continue
            if allowed_protos and sc not in allowed_protos: continue
            if sc == "vless" and "security=none" in uri.lower(): continue
            if wl_mode == 2 and not is_whitelist_sni(uri): continue
            key = f"{sc}:{h}:{pt}"
            if key in uniq: continue
            parts = h.split(".")
            if len(parts) == 4 and all(x.isdigit() for x in parts):
                sub24 = ".".join(parts[:3])
                if subnets.get(sub24, 0) >= 4: continue
                subnets[sub24] = subnets.get(sub24, 0) + 1
            uniq[key] = (src, uri)
        except Exception: continue
    return list(uniq.values())

def tcp_ok(item):
    src, uri = item
    try:
        sc, h, pt = get_hp(uri)
        if not h or not pt: return None
        if sc in ("hy2", "tuic"): return (src, uri) if CFG.get("singbox") and os.path.exists(CFG.get("singbox", "")) else None
        with socket.create_connection((h, pt), timeout=0.9): return (src, uri)
    except Exception: return None
VALID_SS_METHODS = {"aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305", "chacha20-poly1305", "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm", "2022-blake3-chacha20-poly1305", "none", "plain"}

def is_valid_uuid(val):
    try: uuid.UUID(str(val).strip()); return True
    except Exception: return False

def is_valid_reality(pbk, sid):
    if not pbk or not (42 <= len(pbk) <= 44): return False
    try:
        if len(base64.urlsafe_b64decode(pbk + "=" * (-len(pbk) % 4))) != 32: return False
    except Exception: return False
    if sid and (len(sid) > 16 or len(sid) % 2 != 0 or not re.fullmatch(r'[0-9a-fA-F]+', sid)): return False
    return True

def build_out(uri, tag="proxy"):
    try:
        uri = first(uri.split("#"), uri)
        sc = first(uri.split("://"), "").lower()
        if sc == "ss":
            res = parse_ss(uri)
            if not res: return None
            h, pt, m, pwd = res
            if m.lower() not in VALID_SS_METHODS or not pwd: return None
            return {"tag": tag, "protocol": "shadowsocks", "settings": {"servers": list(({"address": h, "port": pt, "method": m.lower(), "password": pwd},))}}
        p, q = urlparse(uri), parse_qs(urlparse(uri).query)
        if not p.hostname or not p.port: return None
        net = first(q.get("type"), "tcp")
        if net not in ("tcp", "ws", "grpc", "xhttp", "splithttp", "httpupgrade"): return None
        if sc == "vless":
            if not is_valid_uuid(p.username): return None
            sec = first(q.get("security"), "none")
            if sec not in ("tls", "reality"): return None
            flow = first(q.get("flow"), "")
            if flow and flow not in ("xtls-rprx-vision", "xtls-rprx-vision-udp443"): flow = ""
            out = {"tag": tag, "protocol": "vless", "settings": {"vnext": list(({"address": p.hostname, "port": int(p.port), "users": list(({"id": str(p.username).strip(), "encryption": "none", "flow": flow},))},))}, "streamSettings": {"network": net, "security": sec}}
        elif sc == "trojan":
            if not p.username: return None
            sec = first(q.get("security"), "tls")
            if sec not in ("tls", "reality"): return None
            out = {"tag": tag, "protocol": "trojan", "settings": {"servers": list(({"address": p.hostname, "port": int(p.port), "password": unquote(p.username)},))}, "streamSettings": {"network": net, "security": sec}}
        else: return None
        if sec == "reality":
            pbk, sid, sni = first(q.get("pbk"), "").strip(), first(q.get("sid"), "").strip(), first(q.get("sni"), "").strip()
            if not sni or not is_valid_reality(pbk, sid): return None
            out["streamSettings"]["realitySettings"] = {"serverName": sni, "fingerprint": first(q.get("fp"), "chrome") or "chrome", "publicKey": pbk, "password": pbk, "shortId": sid, "spiderX": unquote(first(q.get("spx"), "/"))}
        elif sec == "tls":
            out["streamSettings"]["tlsSettings"] = {"serverName": first(q.get("sni"), p.hostname), "allowInsecure": first(q.get("allowInsecure"), "0") in ("1", "true")}
        if net == "ws": out["streamSettings"]["wsSettings"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
        elif net == "grpc": out["streamSettings"]["grpcSettings"] = {"serviceName": first(q.get("serviceName"), "")}
        return out
    except Exception: return None

def build_sb_out(uri, tag="proxy"):
    try:
        uri = first(uri.split("#"), uri)
        sc = first(uri.split("://"), "").lower()
        if sc == "hysteria2": sc = "hy2"
        if sc == "ss":
            res = parse_ss(uri)
            if not res: return None
            h, pt, m, pwd = res
            if m.lower() not in VALID_SS_METHODS or not pwd: return None
            return {"type": "shadowsocks", "tag": tag, "server": h, "server_port": pt, "method": m.lower(), "password": pwd}
        p, q = urlparse(uri), parse_qs(urlparse(uri).query)
        if not p.hostname or not p.port: return None
        if sc == "hy2":
            tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname), "insecure": first(q.get("insecure"), "0") in ("1", "true")}
            out = {"type": "hysteria2", "tag": tag, "server": p.hostname, "server_port": int(p.port), "password": unquote(p.username or ""), "tls": tls}
            if q.get("obfs"): out["obfs"] = {"type": first(q.get("obfs"), ""), "password": first(q.get("obfs-password"), "")}
            return out
        if sc == "tuic":
            if not is_valid_uuid(p.username): return None
            tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname), "insecure": first(q.get("allow_insecure"), "0") in ("1", "true"), "alpn": ["h3"]}
            return {"type": "tuic", "tag": tag, "server": p.hostname, "server_port": int(p.port), "uuid": str(p.username).strip(), "password": unquote(p.password or ""), "congestion_control": first(q.get("congestion_control"), "bbr"), "tls": tls}
        net = first(q.get("type"), "tcp")
        if net not in ("tcp", "ws", "grpc", "httpupgrade"): return None
        if sc == "vless":
            if not is_valid_uuid(p.username): return None
            sec = first(q.get("security"), "none")
            if sec not in ("tls", "reality"): return None
            out = {"type": "vless", "tag": tag, "server": p.hostname, "server_port": int(p.port), "uuid": str(p.username).strip(), "flow": first(q.get("flow"), "")}
        elif sc == "trojan":
            if not p.username: return None
            sec = first(q.get("security"), "tls")
            out = {"type": "trojan", "tag": tag, "server": p.hostname, "server_port": int(p.port), "password": unquote(p.username)}
        else: return None
        if sec in ("tls", "reality"):
            tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname)}
            if sec == "reality":
                pbk, sid, sni = first(q.get("pbk"), "").strip(), first(q.get("sid"), "").strip(), first(q.get("sni"), "").strip()
                if not sni or not is_valid_reality(pbk, sid): return None
                tls["utls"] = {"enabled": True, "fingerprint": first(q.get("fp"), "chrome") or "chrome"}
                tls["reality"] = {"enabled": True, "public_key": pbk, "short_id": sid}
            out["tls"] = tls
        if net == "ws": out["transport"] = {"type": "ws", "path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
        elif net == "grpc": out["transport"] = {"type": "grpc", "service_name": first(q.get("serviceName"), "")}
        return out
    except Exception: return None
def build_clash_proxy(uri, name):
    uri = first(uri.split("#"), uri)
    sc = first(uri.split("://"), "").lower()
    if sc == "hysteria2": sc = "hy2"
    if sc == "ss":
        res = parse_ss(uri)
        if not res: return None
        h, pt, m, pwd = res
        return {"name": name, "type": "ss", "server": h, "port": pt, "cipher": m, "password": pwd, "udp": True}
    p, q = urlparse(uri), parse_qs(urlparse(uri).query)
    if sc == "hy2":
        px = {"name": name, "type": "hysteria2", "server": p.hostname, "port": int(p.port), "password": unquote(p.username or ""), "sni": first(q.get("sni"), p.hostname), "skip-cert-verify": first(q.get("insecure"), "0") in ("1", "true")}
        if q.get("obfs"): px["obfs"] = first(q.get("obfs"), ""); px["obfs-password"] = first(q.get("obfs-password"), "")
        return px
    if sc == "tuic":
        return {"name": name, "type": "tuic", "server": p.hostname, "port": int(p.port), "uuid": p.username, "password": unquote(p.password or ""), "sni": first(q.get("sni"), p.hostname), "congestion-controller": first(q.get("congestion_control"), "bbr"), "alpn": ["h3"]}
    net = first(q.get("type"), "tcp")
    if sc == "vless":
        sec = first(q.get("security"), "none")
        if sec == "none": return None
        px = {"name": name, "type": "vless", "server": p.hostname, "port": int(p.port), "uuid": p.username, "network": net, "tls": True, "udp": True, "servername": first(q.get("sni"), p.hostname)}
        if q.get("flow"): px["flow"] = first(q.get("flow"), "")
        if sec == "reality": px["client-fingerprint"], px["reality-opts"] = first(q.get("fp"), "chrome"), {"public-key": first(q.get("pbk"), ""), "short-id": first(q.get("sid"), "")}
    elif sc == "trojan":
        px = {"name": name, "type": "trojan", "server": p.hostname, "port": int(p.port), "password": unquote(p.username or ""), "network": net, "udp": True, "sni": first(q.get("sni"), p.hostname)}
    else: return None
    if net == "ws": px["ws-opts"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
    elif net == "grpc": px["grpc-opts"] = {"grpc-service-name": first(q.get("serviceName"), "")}
    return px

def build_clash_sub(uris):
    proxies, names = list(), list()
    for i, u in enumerate(uris, 1):
        nm = f"{i:02d}_{u.split('#').pop() if '#' in u else 'NODE'}"
        px = build_clash_proxy(u, nm)
        if px: proxies.append(px); names.append(nm)
    if not proxies: return ""
    return json.dumps({"mixed-port": 7890, "allow-lan": False, "mode": "rule", "log-level": "info", "proxies": proxies, "proxy-groups": [{"name": "NETPULSE-SELECT", "type": "select", "proxies": ["AUTO-BEST"] + names}, {"name": "AUTO-BEST", "type": "url-test", "proxies": names, "url": "http://gstatic.com", "interval": 300}], "rules": ["DOMAIN-SUFFIX,ru,DIRECT", "DOMAIN-SUFFIX,xn--p1ai,DIRECT", "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve", "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve", "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve", "MATCH,NETPULSE-SELECT"]}, ensure_ascii=False, indent=2)

def build_sb_sub(uris):
    outs, tags = list(), list()
    for i, u in enumerate(uris, 1):
        tg = f"{i:02d}_{u.split('#').pop() if '#' in u else 'NODE'}"
        o = build_sb_out(u, tg)
        if o: outs.append(o); tags.append(tg)
    if not outs: return ""
    return json.dumps({"log": {"level": "info"}, "dns": {"servers": [{"tag": "remote", "type": "https", "server": "1.1.1.1", "detour": "proxy"}, {"tag": "local", "type": "local"}], "rules": [{"domain_suffix": RU_BYPASS_DOMAINS, "server": "local"}]}, "inbounds": [{"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 2080}], "outbounds": [{"type": "selector", "tag": "proxy", "outbounds": ["auto"] + tags}, {"type": "urltest", "tag": "auto", "outbounds": tags, "url": "http://gstatic.com", "interval": "5m"}] + outs + [{"type": "direct", "tag": "direct"}], "route": {"rules": [{"action": "sniff"}, {"protocol": "dns", "action": "hijack-dns"}, {"domain_suffix": RU_BYPASS_DOMAINS, "outbound": "direct"}, {"ip_is_private": True, "outbound": "direct"}], "auto_detect_interface": True, "default_domain_resolver": "local"}}, ensure_ascii=False, indent=2)

GEO_CACHE, GEO_LOCK = {}, threading.Lock()
def wait_port(port, tries=35):
    for _ in range(tries):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.05): return True
        except Exception: time.sleep(0.02)
    return False

def get_free_ports(n):
    socks, ports = list(), list()
    for _ in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.bind(("127.0.0.1", 0))
        _, pt = s.getsockname()
        ports.append(pt); socks.append(s)
    for s in socks: s.close()
    return ports

def lookup_ip_cc(ip, px=None):
    if not ip: return "UN"
    with GEO_LOCK:
        if ip in GEO_CACHE: return GEO_CACHE[ip]
    sess = requests.Session(); sess.trust_env = False
    for prx in (px, None):
        for url, key in [(f"http://ip-api.com{ip}?fields=countryCode", None), (f"https://country.is{ip}", "country"), (f"https://ipwho.is{ip}", "country_code"), (f"https://ipinfo.io{ip}/country", None)]:
            try:
                r = sess.get(url, proxies=prx, timeout=2.5)
                if r.status_code == 200:
                    code = (r.json().get(key, "") if key else r.text).strip().upper()
                    if len(code) == 2 and code.isalpha():
                        with GEO_LOCK: GEO_CACHE[ip] = code
                        return code
            except Exception: pass
        if prx is None: break
    return "UN"

def fetch_trace_info(px=None, tout=TIMEOUT, need_cc=True):
    sess = requests.Session(); sess.trust_env = False
    for url, ip_k, cc_k in [("http://ip-api.com", "query", "countryCode"), ("https://country.is", "ip", "country"), ("https://ipwho.is", "ip", "country_code"), ("https://ifconfig.co", "ip", "country_iso")]:
        try:
            t0 = time.time(); res = sess.get(url, proxies=px, headers={"User-Agent": "curl/8.0"}, timeout=tout); ms = int((time.time() - t0) * 1000)
            if res.status_code == 200:
                data = res.json(); ip, cc = str(data.get(ip_k, "")).strip(), str(data.get(cc_k, "")).strip().upper()
                if ip and ("." in ip or ":" in ip):
                    if len(cc) == 2 and cc.isalpha():
                        with GEO_LOCK: GEO_CACHE[ip] = cc
                        return cc, ip, ms
                    return (lookup_ip_cc(ip, px) if need_cc else "OK"), ip, ms
        except Exception: continue
    return "UN", "", None

def probe_local_port(port, speed_mode=False, cc_mode=False):
    try:
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        if cc_mode: cc, _, _ = fetch_trace_info(px, TIMEOUT, True); return cc
        sess = requests.Session(); sess.trust_env = False; t0 = time.time()
        if not speed_mode:
            res = sess.get(first(TARGETS.get(CFG.get("target", 1), ("https://icanhazip.com", "")), "https://icanhazip.com"), proxies=px, timeout=TIMEOUT)
            return int((time.time() - t0) * 1000) if res.status_code in (200, 204) else None
        dl = 0
        with sess.get(SPEED_URL, proxies=px, stream=True, timeout=(5, 12)) as r:
            for ch in r.iter_content(65536):
                dl += len(ch)
                if dl >= 5242880 or (time.time() - t0) > 8: break
        return round((dl * 8) / (max(time.time() - t0, 0.01) * 1000000), 1)
    except Exception: return "UN" if cc_mode else (0.0 if speed_mode else None)

def run_single_test(uri, speed_mode=False, cc_mode=False):
    proc, tmp_cfg = None, ""
    try:
        clean_uri = first(uri.split("#"), uri); sc, _, _ = get_hp(clean_uri); port = first(get_free_ports(1), 0)
        if sc in ("hy2", "tuic"):
            sb_bin, out = CFG.get("singbox", ""), build_sb_out(clean_uri, "proxy")
            if not sb_bin or not os.path.exists(sb_bin) or not out: return "UN" if cc_mode else None
            tmp_cfg = os.path.abspath(f"tmp_sb_{port}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump({"log": {"level": "panic"}, "inbounds": [{"type": "http", "listen": "127.0.0.1", "listen_port": port}], "outbounds": [out]}, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            out = build_out(clean_uri, "proxy")
            if not out: return "UN" if cc_mode else None
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps({"log": {"loglevel": "none"}, "dns": {"servers": ["localhost"]}, "inbounds": [{"port": port, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}], "outbounds": [out]}).encode("utf-8")); proc.stdin.close()
        if not wait_port(port): return "UN" if cc_mode else (0.0 if speed_mode else None)
        return probe_local_port(port, speed_mode, cc_mode)
    except Exception: return "UN" if cc_mode else (0.0 if speed_mode else None)
    finally:
        if proc:
            try: proc.kill()
            except Exception: pass
        if tmp_cfg and os.path.exists(tmp_cfg):
            try: os.remove(tmp_cfg)
            except Exception: pass
def deep_test_node(uri):
    proc, tmp_cfg = None, ""
    try:
        clean_uri = first(uri.split("#"), uri); sc, _, _ = get_hp(clean_uri); port = first(get_free_ports(1), 0)
        if sc in ("hy2", "tuic"):
            sb_bin, out = CFG.get("singbox", ""), build_sb_out(clean_uri, "proxy")
            if not sb_bin or not os.path.exists(sb_bin) or not out: return None
            tmp_cfg = os.path.abspath(f"tmp_deep_{port}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump({"log": {"level": "panic"}, "inbounds": [{"type": "http", "listen": "127.0.0.1", "listen_port": port}], "outbounds": [out]}, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            out = build_out(clean_uri, "proxy")
            if not out: return None
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps({"log": {"loglevel": "none"}, "dns": {"servers": ["localhost"]}, "inbounds": [{"port": port, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}], "outbounds": [out]}).encode("utf-8")); proc.stdin.close()
        if not wait_port(port, 45): return None
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        sess = requests.Session(); sess.trust_env = False
        pings = list()
        for _ in range(3):
            try:
                t0 = time.time()
                r = sess.get("https://gstatic.com", proxies=px, timeout=3.5)
                if r.status_code in (200, 204): pings.append(int((time.time() - t0) * 1000))
            except Exception: pass
        if not pings: return None
        avg_ms = sum(pings) // len(pings)
        jitter = max(pings) - min(pings)
        yt_ok, ai_ok = False, False
        try: yt_ok = sess.get("https://youtube.com", proxies=px, timeout=4.5).status_code == 200
        except Exception: pass
        try: ai_ok = sess.get("https://chatgpt.com", proxies=px, timeout=4.5).status_code in (200, 403)
        except Exception: pass
        return {"ok": len(pings), "avg": avg_ms, "jitter": jitter, "yt": yt_ok, "ai": ai_ok}
    except Exception: return None
    finally:
        if proc:
            try: proc.kill()
            except Exception: pass
        if tmp_cfg and os.path.exists(tmp_cfg):
            try: os.remove(tmp_cfg)
            except Exception: pass

def run_batch_group(items, is_sb=False):
    if not items: return list()
    ports = get_free_ports(len(items)); inbs, outs, rules, valid_map = list(), list(), list(), list()
    for idx, ((src, uri), pt) in enumerate(zip(items, ports)):
        tg = f"p_{idx}"; out = build_sb_out(uri, tg) if is_sb else build_out(uri, tg)
        if not out: continue
        if is_sb: inbs.append({"type": "http", "tag": f"in_{idx}", "listen": "127.0.0.1", "listen_port": pt}); rules.append({"inbound": [f"in_{idx}"], "outbound": tg})
        else: inbs.append({"tag": f"in_{idx}", "port": pt, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}); rules.append({"type": "field", "inboundTag": [f"in_{idx}"], "outboundTag": tg})
        outs.append(out); valid_map.append((src, uri, pt))
    if not valid_map: return list()
    proc, tmp_cfg, found_batch = None, "", list()
    try:
        _, _, first_pt = first(valid_map); _, _, last_pt = valid_map[-1]
        if is_sb:
            sb_bin = CFG.get("singbox", "")
            if not sb_bin or not os.path.exists(sb_bin): return list()
            tmp_cfg = os.path.abspath(f"tmp_batch_{first_pt}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump({"log": {"level": "panic"}, "inbounds": inbs, "outbounds": outs, "route": {"rules": rules}}, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps({"log": {"loglevel": "none"}, "dns": {"servers": ["localhost"]}, "inbounds": inbs, "outbounds": outs, "routing": {"domainStrategy": "AsIs", "rules": rules}}).encode("utf-8")); proc.stdin.close()
        if not wait_port(last_pt, 50): return list()
        def test_slot(slot):
            if STOP_EVENT.is_set(): return None
            src, uri, pt = slot; strict, need_geo = CFG.get("strict_ip", True) and bool(REAL_HOME_IP), bool(CFG["countries"]) or CFG.get("geoip", True); need_trace, cc = need_geo or strict, "FAST"
            if need_trace and CFG.get("target", 1) == 1:
                tr_cc, tr_ip, ms = fetch_trace_info({"http": f"http://127.0.0.1:{pt}", "https": f"http://127.0.0.1:{pt}"}, TIMEOUT, need_geo)
                if ms is None or (strict and (not tr_ip or tr_ip == REAL_HOME_IP)) or tr_cc in BLOCKED_COUNTRIES or (CFG["countries"] and tr_cc not in CFG["countries"]): return None
                if need_geo: cc = tr_cc
            else:
                ms = probe_local_port(pt, False, False)
                if ms is None: return None
                if need_trace:
                    tr_cc, tr_ip, _ = fetch_trace_info({"http": f"http://127.0.0.1:{pt}", "https": f"http://127.0.0.1:{pt}"}, TIMEOUT, need_geo)
                    if (strict and (not tr_ip or tr_ip == REAL_HOME_IP)) or tr_cc in BLOCKED_COUNTRIES or (CFG["countries"] and tr_cc not in CFG["countries"]): return None
                    if need_geo: cc = tr_cc
            max_p = CFG.get("max_ping", 0)
            if max_p > 0 and ms > max_p: return None
            sc, _, _ = get_hp(uri)
            return (src, ms, cc, f"{first(uri.split('#'), uri)}#{sc.upper()}_{cc}{'_WL' if is_whitelist_sni(uri) else ''}_{ms}ms")
        with ThreadPoolExecutor(max_workers=len(valid_map)) as ex:
            for res in ex.map(test_slot, valid_map):
                if res: found_batch.append(res)
    except Exception: pass
    finally:
        if proc:
            try: proc.kill()
            except Exception: pass
        if tmp_cfg and os.path.exists(tmp_cfg):
            try: os.remove(tmp_cfg)
            except Exception: pass
    return found_batch

class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", wintypes.BYTE * 8)]

class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("hWnd", wintypes.HWND), ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT), ("uCallbackMessage", wintypes.UINT), ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128), ("dwState", wintypes.DWORD), ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256), ("uTimeout", wintypes.UINT), ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD), ("guidItem", GUID), ("hBalloonIcon", wintypes.HICON)
    ]

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HICON), ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)
    ]

def switch_next_vpn():
    if not os.path.exists("best_configs.txt"): return False
    try:
        with open("best_configs.txt", "r", encoding="utf-8") as f: rows = [ln.strip() for ln in f if ln.strip()]
        if not rows: return False
        bases = [first(ln.split("#"), ln) for ln in rows]
        start = (bases.index(ACTIVE_URI) + 1) % len(rows) if ACTIVE_URI in bases else 0
        for step in range(len(rows)):
            idx = (start + step) % len(rows)
            b, sc, cc, _, _, _ = parse_row_info(rows[idx])
            if connect_vpn(b, f"#{idx + 1} {sc}_{cc}"): return True
    except Exception: pass
    return False

def minimize_to_tray():
    global TRAY_HIDDEN
    u32, k32, s32 = ctypes.windll.user32, ctypes.windll.kernel32, ctypes.windll.shell32
    u32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    u32.DefWindowProcW.restype = ctypes.c_longlong
    hwnd_target = u32.GetForegroundWindow() or k32.GetConsoleWindow()
    if not hwnd_target: return
    TRAY_HIDDEN = True
    u32.ShowWindow(hwnd_target, 0)
    hinst, cls_name, WM_TRAY = k32.GetModuleHandleW(None), f"NetPulseTray_{int(time.time() * 1000)}", 0x0400 + 20
    def restore_win(h_w):
        global TRAY_HIDDEN
        nid = NOTIFYICONDATAW(cbSize=ctypes.sizeof(NOTIFYICONDATAW), hWnd=h_w, uID=1)
        s32.Shell_NotifyIconW(2, ctypes.byref(nid))
        global TRAY_HWND
        TRAY_HIDDEN, TRAY_HWND = False, None
        u32.ShowWindow(hwnd_target, 9)
        u32.SetForegroundWindow(hwnd_target)
        u32.PostQuitMessage(0)
    def wnd_proc(h_w, msg, wp, lp):
        if msg == WM_TRAY:
            ev = lp & 0xFFFF
            if ev in (0x0202, 0x0203):
                restore_win(h_w)
                return 0
            elif ev in (0x0205, 0x007B):
                hmenu = u32.CreatePopupMenu()
                u32.AppendMenuW(hmenu, 0, 1001, "Открыть NETPULSE / Show")
                u32.AppendMenuW(hmenu, 0, 1002, "Следующий сервер / Next VPN")
                u32.AppendMenuW(hmenu, 0, 1003, "Отключить VPN / Disconnect")
                u32.AppendMenuW(hmenu, 0x0800, 0, None)
                u32.AppendMenuW(hmenu, 0, 1004, "Выход / Exit")
                pt = wintypes.POINT()
                u32.GetCursorPos(ctypes.byref(pt))
                u32.SetForegroundWindow(h_w)
                cmd = u32.TrackPopupMenu(hmenu, 0x0100, pt.x, pt.y, 0, h_w, None)
                u32.DestroyMenu(hmenu)
                u32.PostMessageW(h_w, 0, 0, 0)
                if cmd == 1001: restore_win(h_w)
                elif cmd == 1002: threading.Thread(target=switch_next_vpn, daemon=True).start()
                elif cmd == 1003: disconnect_vpn()
                elif cmd == 1004: restore_win(h_w); disconnect_vpn(); os._exit(0)
                return 0
        return u32.DefWindowProcW(h_w, msg, wp, lp)
    cb = WNDPROC(wnd_proc)
    wc = WNDCLASSW(lpfnWndProc=cb, hInstance=hinst, lpszClassName=cls_name)
    u32.RegisterClassW(ctypes.byref(wc))
    global TRAY_HWND
    hwnd_msg = TRAY_HWND = u32.CreateWindowExW(0, cls_name, "NetPulseTray", 0, 0, 0, 0, 0, 0, 0, hinst, None)
    nid = NOTIFYICONDATAW(cbSize=ctypes.sizeof(NOTIFYICONDATAW), hWnd=hwnd_msg, uID=1, uFlags=7, uCallbackMessage=WM_TRAY, hIcon=u32.LoadIconW(0, 32516), szTip=f"NETPULSE V1.6.8 | {ACTIVE_NAME if ACTIVE_NAME else 'VPN: OFF'}"[:120])
    s32.Shell_NotifyIconW(0, ctypes.byref(nid))
    m_msg = wintypes.MSG()
    while u32.GetMessageW(ctypes.byref(m_msg), 0, 0, 0) != 0:
        u32.TranslateMessage(ctypes.byref(m_msg))
        u32.DispatchMessageW(ctypes.byref(m_msg))

def pipe_core_logs(proc):
    try:
        for raw_ln in iter(proc.stdout.readline, b""):
            if not raw_ln: break
            ln = raw_ln.decode("utf-8", errors="ignore").strip(); low = ln.lower()
            if "accepted " in ln: add_log(ln.split("accepted ", 1).pop()[:72])
            elif "connection to " in low: add_log(ln[low.find("connection to "):][:72])
            elif any(x in low for x in ("fatal", "failed", "error", "bind:", "panic")): add_log(f"Core: {ln[-68:]}")
    except Exception: pass

def set_win_proxy(enable, port=10809):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
        if enable:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"http=127.0.0.1:{port};https=127.0.0.1:{port}")
            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.*;10.*;172.16.*;192.168.*;*.ru;*.xn--p1ai;<local>")
        winreg.CloseKey(key)
    except Exception: pass

def disconnect_vpn():
    global ACTIVE_START, ACTIVE_IP, ACTIVE_CC
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    if ACTIVE_NAME: add_log(f"Отключено: {ACTIVE_NAME}")
    if ACTIVE_PROC:
        try: ACTIVE_PROC.kill()
        except Exception: pass
        ACTIVE_PROC = None
    if TUN_CFG_PATH and os.path.exists(TUN_CFG_PATH):
        try: os.remove(TUN_CFG_PATH)
        except Exception: pass
    TUN_CFG_PATH, ACTIVE_NAME, ACTIVE_URI, ACTIVE_START, ACTIVE_IP, ACTIVE_CC = "", "", "", 0.0, "", ""
    set_win_proxy(False)

def pick_bind_port(pref_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: s.bind(("127.0.0.1", pref_port)); return pref_port
    except Exception:
        alt = first(get_free_ports(1), pref_port + 1); add_log(f"Порт :{pref_port} занят (v2rayN?), взят :{alt}"); return alt

def connect_vpn(uri, label):
    global ACTIVE_START, ACTIVE_IP, ACTIVE_CC
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    disconnect_vpn()
    clean_uri = first(uri.split("#"), uri); sc, _, _ = get_hp(clean_uri); xray_bin, sb_bin = find_cores()
    if CFG.get("tun", False) or sc in ("hy2", "tuic"):
        if CFG.get("tun", False) and not is_admin(): add_log("Ошибка: для TUN нужны права Администратора"); return False
        if not sb_bin or not os.path.exists(sb_bin): add_log("Ошибка: не найден sing-box.exe"); return False
        sb_out = build_sb_out(clean_uri, "proxy")
        if not sb_out: add_log("Ошибка sing-box: невалидный формат ссылки"); return False
        port = pick_bind_port(CFG.get("px_port", 10809))
        inb = [{"type": "tun", "interface_name": "NetPulseTUN", "address": ["172.19.0.1/30"], "mtu": 1400, "auto_route": True, "strict_route": True, "stack": "system"}] if CFG.get("tun", False) else [{"type": "http", "listen": "127.0.0.1", "listen_port": port}]
        sb_cfg = {"log": {"level": "info", "timestamp": False}, "dns": {"servers": [{"tag": "remote", "type": "https", "server": "1.1.1.1", "detour": "proxy"}, {"tag": "local", "type": "local"}], "rules": [{"domain_suffix": RU_BYPASS_DOMAINS, "server": "local"}]}, "inbounds": inb, "outbounds": [sb_out, {"type": "direct", "tag": "direct"}], "route": {"rules": [{"action": "sniff"}, {"protocol": "dns", "action": "hijack-dns"}, {"domain_suffix": RU_BYPASS_DOMAINS, "outbound": "direct"}, {"ip_is_private": True, "outbound": "direct"}], "auto_detect_interface": True, "default_domain_resolver": "local"}}
        TUN_CFG_PATH = os.path.abspath("netpulse_sb_active.json")
        with open(TUN_CFG_PATH, "w", encoding="utf-8") as f: json.dump(sb_cfg, f, indent=2)
        try:
            ACTIVE_PROC = subprocess.Popen([sb_bin, "run", "-c", TUN_CFG_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            threading.Thread(target=pipe_core_logs, args=(ACTIVE_PROC,), daemon=True).start(); time.sleep(1.5)
            if ACTIVE_PROC.poll() is None:
                if not CFG.get("tun", False): set_win_proxy(True, port)
                ACTIVE_NAME, ACTIVE_URI, ACTIVE_START = f"{label} ({'TUN-Split' if CFG.get('tun', False) else f'SB:{port}'})", clean_uri, time.time()
                ACTIVE_CC, ACTIVE_IP, _ = fetch_trace_info(None if CFG.get("tun", False) else {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}, 3.0, True)
                add_log(f"Подключено: {ACTIVE_NAME} [{ACTIVE_CC} • {ACTIVE_IP}]"); return True
        except Exception as e: add_log(f"Сбой sing-box: {str(e)[:60]}")
        disconnect_vpn(); return False
    if not xray_bin or not os.path.exists(xray_bin): add_log("Ошибка Xray: не найден xray.exe"); return False
    out = build_out(clean_uri, "proxy")
    if not out: add_log("Ошибка Xray: невалидный формат ссылки"); return False
    port = pick_bind_port(CFG.get("px_port", 10809))
    cfg = {"log": {"loglevel": "info"}, "dns": {"servers": ["localhost"]}, "inbounds": [{"tag": "http", "port": port, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}], "outbounds": [out]}
    TUN_CFG_PATH = os.path.abspath("netpulse_xray_active.json")
    with open(TUN_CFG_PATH, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2)
    try:
        ACTIVE_PROC = subprocess.Popen([xray_bin, "run", "-c", TUN_CFG_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        threading.Thread(target=pipe_core_logs, args=(ACTIVE_PROC,), daemon=True).start()
        if wait_port(port, 100):
            set_win_proxy(True, port); ACTIVE_NAME, ACTIVE_URI, ACTIVE_START = f"{label} (Proxy:{port})", clean_uri, time.time()
            ACTIVE_CC, ACTIVE_IP, _ = fetch_trace_info({"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}, 3.0, True)
            add_log(f"Подключено: {ACTIVE_NAME} [{ACTIVE_CC} • {ACTIVE_IP}]"); return True
        add_log(f"Ошибка Xray: таймаут порта :{port}")
    except Exception as e: add_log(f"Сбой запуска Xray: {str(e)[:60]}")
    disconnect_vpn(); return False

def failover_loop():
    global NEXT_AUTO_SCAN
    fails = 0
    while True:
        time.sleep(10)
        iv = CFG.get("auto_scan_min", 0)
        if iv > 0 and NEXT_AUTO_SCAN > 0 and time.time() >= NEXT_AUTO_SCAN and not SCAN_BUSY:
            NEXT_AUTO_SCAN = time.time() + iv * 60
            add_log(f"Планировщик: запуск авто-проверки (интервал {iv} мин)")
            threading.Thread(target=run_scan, kwargs={"from_cache": False, "auto_bg": True}, daemon=True).start()
        if not ACTIVE_PROC or not ACTIVE_URI or not CFG.get("failover", True):
            fails = 0; continue
        ok = False
        try:
            if ACTIVE_PROC.poll() is None:
                sess = requests.Session(); sess.trust_env = False; px = None
                if "(Proxy:" in ACTIVE_NAME or "(SB:" in ACTIVE_NAME:
                    p_str = ACTIVE_NAME.split(":").pop().rstrip(")")
                    if p_str.isdigit(): px = {"http": f"http://127.0.0.1:{p_str}", "https": f"http://127.0.0.1:{p_str}"}
                ok = sess.get("https://icanhazip.com", proxies=px, timeout=4).status_code in (200, 204)
        except Exception: ok = False
        fails = 0 if ok else fails + 1
        if fails >= 2 and os.path.exists("best_configs.txt"):
            global FAILOVER_CNT
            fails = 0; FAILOVER_CNT += 1; dead_uri, old_lbl = ACTIVE_URI, ACTIVE_NAME
            add_log(f"Failover: узел {old_lbl} перестал отвечать, ищу замену...")
            try:
                with open("best_configs.txt", "r", encoding="utf-8") as f: rows = [ln.strip() for ln in f if ln.strip()]
                fav_bases = {first(x.split("#"), x) for x in load_favs()}
                if dead_uri not in fav_bases:
                    rows = [ln for ln in rows if first(ln.split("#"), ln) != dead_uri]
                    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
                    add_log("Failover: мёртвый узел удалён из списка")
                bases = [first(ln.split("#"), ln) for ln in rows]
                start = (bases.index(dead_uri) + 1) if dead_uri in bases else 0
                for step in range(len(rows)):
                    idx = (start + step) % len(rows)
                    b, sc, cc, _, _, _ = parse_row_info(rows[idx])
                    if b != dead_uri and connect_vpn(b, f"#{idx + 1} {sc}_{cc}"):
                        try: winsound.Beep(660, 120); winsound.Beep(880, 160)
                        except Exception: pass
                        break
            except Exception: pass

def parse_row_info(ln):
    parts = ln.strip().split("#", 1)
    base, tag = first(parts, ""), (parts.pop() if len(parts) > 1 else "")
    sc = first(base.split("://"), "UNK").upper()
    if sc == "HYSTERIA2": sc = "HY2"
    cc, ms, spd = "??", "-", "-"
    for tok in tag.split("_"):
        if len(tok) == 2 and tok.isalpha() and tok.isupper() and tok not in ("SS", "WL"): cc = tok
        elif tok in ("FAST", "UN", "IMP"): cc = tok
        elif tok.endswith("ms") and tok[:-2].isdigit(): ms = tok
        elif tok.endswith("Mbps"): spd = tok
    if "_WL" in tag: cc = f"{cc}+WL"
    return base, sc, cc, ms, spd, tag

def import_nodes_ui(rows):
    c = CFG["color"]
    print(f"\n{c}Импорт серверов (VLESS / Trojan / SS / HY2 / TUIC / Base64):{RST}")
    print("  1. Из буфера обмена (Clipboard)\n  2. Из текстового файла (путь к файлу)")
    src_t, raw_txt = input("> ").strip(), ""
    if src_t == "1":
        try: raw_txt = subprocess.check_output(["powershell", "-command", "Get-Clipboard"], text=True, encoding="utf-8", errors="ignore")
        except Exception: pass
    elif src_t == "2":
        fp = input("Путь к файлу > ").strip().strip('"')
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8", errors="ignore") as f: raw_txt = f.read()
    found = parse_text(raw_txt)
    if not found: print("\033[91m[!] Ссылки не найдены.\033[0m"); time.sleep(1.2); return rows
    existing, added = {first(r.split("#"), r) for r in rows}, 0
    for u in found:
        base = first(u.split("#"), u)
        if base in existing: continue
        sc, _, _ = get_hp(base)
        print(f"  Проверка {sc.upper()}...")
        ms = run_single_test(base, False, False)
        if ms is not None:
            cc = run_single_test(base, False, True) if CFG.get("geoip", True) else "IMP"
            if cc in BLOCKED_COUNTRIES: continue
            rows.insert(0, f"{base}#{sc.upper()}_{cc}_{ms}ms"); existing.add(base); added += 1
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
    add_log(f"Импортировано вручную: {added} серверов")
    print(f"{c}[+] Импортировано рабочих серверов: {added}{RST}"); time.sleep(1.4); return rows

def export_nodes_ui(rows):
    c = CFG["color"]
    if not rows: return
    print(f"\n{c}Экспорт списка ({len(rows)} серверов):{RST}")
    print("  1. Скопировать подписку Base64 в буфер обмена\n  2. Сохранить в файл export_nodes.txt (список ссылок)")
    ex_t = input("> ").strip()
    if ex_t == "1":
        b64 = base64.b64encode("\n".join(rows).encode("utf-8")).decode("utf-8")
        subprocess.run("clip", input=b64.encode("utf-8"), check=False)
        add_log(f"Экспорт Base64 в буфер ({len(rows)} узлов)")
        print(f"{c}[+] Base64-подписка скопирована в буфер обмена!{RST}"); time.sleep(1.2)
    elif ex_t == "2":
        with open("export_nodes.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
        add_log(f"Экспорт в export_nodes.txt ({len(rows)} узлов)")
        print(f"{c}[+] Сохранено в export_nodes.txt!{RST}"); time.sleep(1.2)
def manage_sources():
    c, page, per_page = CFG["color"], 0, 25
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        db = load_src_db()
        items = sorted(db.items(), key=lambda x: (x[1].get("working", 0), x[1].get("collected", 0)), reverse=True)
        tot_p = max(1, (len(items) + per_page - 1) // per_page)
        page = max(0, min(page, tot_p - 1))
        chunk = items[page * per_page:(page + 1) * per_page]
        prio_cnt = sum(1 for _, v in items if v.get("prio", False))
        rh = f"{style_txt('REPO LEADERBOARD & PRIORITY')}{RST}{c} │ Баз: [96m{len(items)}[0m{c} │ Приоритет ★: [93m{prio_cnt}[0m{c} │ Стр.{page + 1}/{tot_p}"
        print(f"{c}╔{'═' * 72}╗{RST}\n{box_row(rh, c)}\n{c}╚{'═' * 72}╝{RST}")
        if not items: print("  Статистика пока пуста. Запустите поиск (пункт 1)!")
        else:
            print(f"  {'#':<4} {'PRIO':<6} {'WORK':<7} {'TOTAL':<9} {'SOURCE (REPO / TG / WEB)'}\n  {'-' * 68}")
            for idx, (src, st) in enumerate(chunk, page * per_page + 1):
                star = f"{c}★ ДА{RST}" if st.get("prio", False) else "  -"
                disp = src[3:] if src.startswith("gh:") else (src.split("/").pop() if src.startswith("http") else src)
                print(f"  {c}{idx:<4}{RST} {star:<14} {st.get('working', 0):<7} {st.get('collected', 0):<9} {disp[:40]}")
        print(f"\n{c}Команды:{RST} [Номера] Вкл/Выкл ★ | [N] След. | [P] Пред. | [C] Сброс | [Enter] Меню")
        cmd = ru2en(input("\n> ").strip()).upper()
        if not cmd: break
        elif cmd == "N": page += 1
        elif cmd == "P": page -= 1
        elif cmd == "C": save_src_db({})
        else:
            nums = [int(x) for x in re.findall(r'\d+', cmd)]
            if nums:
                for n in nums:
                    if 1 <= n <= len(items): k = items[n - 1][0]; db[k]["prio"] = not db[k].get("prio", False)
                save_src_db(db)

def manage_servers():
    c, flt, page, per_page = CFG["color"], "", 0, 20
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        all_rows = [ln.strip() for ln in open("best_configs.txt", "r", encoding="utf-8") if ln.strip()] if os.path.exists("best_configs.txt") else list()
        favs = load_favs(); fav_bases = {first(x.split("#"), x) for x in favs}
        indexed = list(enumerate(all_rows, 1))
        if flt:
            if flt == "★": indexed = [(i, ln) for i, ln in indexed if first(ln.split("#"), ln) in fav_bases]
            else: indexed = [(i, ln) for i, ln in indexed if flt in ln.upper()]
        tot_p = max(1, (len(indexed) + per_page - 1) // per_page)
        page = max(0, min(page, tot_p - 1))
        chunk = indexed[page * per_page:(page + 1) * per_page]
        t_mode = f"TUN-Split (Admin: {'OK' if is_admin() else 'NO'})" if CFG.get("tun", False) else f"Proxy (:{CFG.get('px_port', 10809)})"
        flt_tag = f" | Фильтр: [{flt}]" if flt else ""
        vpn_c = "\033[92m" if ACTIVE_NAME else DIM
        fo_c = "\033[92m" if CFG.get("failover", True) else "\033[91m"
        r1 = f"{style_txt('SERVER MANAGER')}{RST}{c} │ {t_mode} │ Стр.{page + 1}/{tot_p} ([96m{len(indexed)}/{len(all_rows)}[0m{c}){flt_tag}"
        r2 = f"Failover: {fo_c}{tr('on') if CFG.get('failover', True) else tr('off')}[0m{c} │ Избр: [93m★{len(favs)}[0m{c} │ VPN: {vpn_c}{(ACTIVE_NAME if ACTIVE_NAME else 'OFF')[:30]}[0m"
        print(f"{c}╔{'═' * 72}╗{RST}\n{box_row(r1, c)}\n{c}╟{'─' * 72}╢{RST}\n{box_row(r2, c)}\n{c}╚{'═' * 72}╝{RST}")
        if not chunk: print("  Список пуст (или нет совпадений по фильтру — нажмите [C] для сброса).")
        else:
            print(f"  {c}{'#':<4} {'PROTO':<8} {'CC':<8} {'PING':<8} {'SPEED':<10} {'HOST'}{RST}\n  {DIM}{'─' * 68}{RST}")
            for i, ln in chunk:
                base, sc, cc, ms, spd, _ = parse_row_info(ln); _, h, _ = get_hp(base)
                sc_c = "\033[96m" if sc == "VLESS" else ("\033[95m" if sc == "HY2" else ("\033[93m" if sc == "TROJAN" else "\033[92m"))
                cc_c = "\033[92m" if "+WL" in cc else "\033[97m"
                print(f"  {c}{i:<4}{RST} {sc_c}{sc:<8}{RST} {cc_c}{cc:<8}{RST} {fmt_ping(ms)} {fmt_spd(spd)} {c}{'★ ' if base in fav_bases else ''}{RST}{str(h)[:24]}{c}{' *' if ACTIVE_NAME and f'#{i} ' in ACTIVE_NAME else ''}{RST}")
        print(f"\n{c}Журнал трафика и событий (последние 6):{RST}")
        with LOG_LOCK: snap = list(VPN_LOG[-6:])
        if not snap: print(f"  {DIM}(пока пусто — нажмите [R] для обновления){RST}")
        else:
            for lg in snap: print(f"  {DIM}{lg}{RST}")
        c1 = f"[97m[N/P][0m{c} Стр. │ [97m[Текст][0m{c} Фильтр (NL/HY2/WL/★) │ [97m[C][0m{c} Сброс"
        c2 = f"[97m[T][0m{c} Proxy/TUN │ [97m[F][0m{c} Failover │ [97m[I][0m{c} Импорт │ [97m[E][0m{c} Экспорт │ [92m[A][0m{c} Тест БД"
        c3 = f"[97m[R][0m{c} Обновить  │ [97m[W][0m{c} Трей     │ [97m[L][0m{c} Лог    │ [91m[D][0m{c} Откл.   │ [97m[Enter][0m{c} Меню"
        print(f"\n{c}╔{'═' * 72}╗{RST}\n{box_row(c1, c)}\n{box_row(c2, c)}\n{box_row(c3, c)}\n{c}╚{'═' * 72}╝{RST}")

        cmd = ru2en(input("\n> ").strip()).upper()
        if not cmd: break
        elif cmd == "R": continue
        elif cmd == "N": page += 1
        elif cmd == "P": page -= 1
        elif cmd == "C": flt, page = "", 0
        elif cmd == "W": minimize_to_tray()
        elif cmd == "F": CFG["failover"] = not CFG.get("failover", True); save_cfg(); add_log(f"Auto-Failover: {'ВКЛ' if CFG['failover'] else 'ВЫКЛ'}")
        elif cmd == "I": import_nodes_ui(all_rows)
        elif cmd == "E": export_nodes_ui(all_rows)
        elif cmd == "L":
            l_act = input(f"\n{c}1. Открыть {LOG_FILE}  2. Очистить > {RST}").strip()
            if l_act == "1" and os.path.exists(LOG_FILE):
                try: os.startfile(LOG_FILE)
                except Exception: pass
            elif l_act == "2":
                with LOG_LOCK: VPN_LOG.clear()
                try: open(LOG_FILE, "w", encoding="utf-8").close()
                except Exception: pass
        elif cmd == "T":
            CFG["tun"] = not CFG.get("tun", False); save_cfg(); add_log(f"Режим VPN: {'TUN-Split' if CFG['tun'] else 'Proxy'}")
            if CFG["tun"] and not is_admin() and ru2en(input(f"\n{c}[!] Нужны права Админа. Перезапустить? (Y/N) > {RST}").strip()).upper() == "Y":
                disconnect_vpn(); ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(f'"{a}"' for a in (sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv)), None, 1); sys.exit(0)
        elif cmd == "D": disconnect_vpn(); print("[*] VPN отключен."); time.sleep(0.8)
        elif cmd == "A":
            print(f"\n{c}[1/2] Бережная проверка отклика {len(all_rows)} серверов (4 потока, 2 попытки)...{RST}")
            t_a, done_a, dead_cnt = time.time(), 0, 0
            alive_tmp, kept_favs = list(), list()
            max_p, min_s = CFG.get("max_ping", 0), float(CFG.get("min_speed", 0.0))
            def ping_one(item):
                idx, ln = item
                base, sc, old_cc, _, _, _ = parse_row_info(ln)
                ms = run_single_test(base, False, False)
                if ms is None:
                    time.sleep(0.25)
                    ms = run_single_test(base, False, False)
                if ms is None or (max_p > 0 and ms > max_p):
                    return (idx, None, None, None, ln if base in fav_bases else None)
                cc = run_single_test(base, False, True) if CFG.get("geoip", True) else old_cc
                if cc in BLOCKED_COUNTRIES and base not in fav_bases:
                    return (idx, None, None, None, None)
                return (idx, base, sc, cc, ms)
            with ThreadPoolExecutor(max_workers=4) as ex:
                for idx, base, sc, cc, ms in ex.map(ping_one, enumerate(all_rows)):
                    done_a += 1; draw_bar(done_a, len(all_rows), "", t_a)
                    if base: alive_tmp.append((idx, base, sc, cc, ms))
                    elif ms: kept_favs.append((0.0, 99999, idx, ms))
                    else: dead_cnt += 1
            scored_rows = list(kept_favs)
            if CFG.get("speed", True) and alive_tmp:
                print(f"\n{c}[2/2] Замер скорости ({len(alive_tmp)} живых, 2 потока)...{RST}")
                t_s, done_s = time.time(), 0
                def spd_one(it):
                    idx, base, sc, cc, ms = it
                    mbps = run_single_test(base, True, False)
                    if min_s > 0 and mbps < min_s and base not in fav_bases: return None
                    return (mbps, ms, idx, f"{base}#{sc}_{cc}_{ms}ms_{mbps}Mbps")
                with ThreadPoolExecutor(max_workers=2) as ex:
                    for res in ex.map(spd_one, alive_tmp):
                        done_s += 1; draw_bar(done_s, len(alive_tmp), "", t_s)
                        if res: scored_rows.append(res)
                        else: dead_cnt += 1
            else:
                for idx, base, sc, cc, ms in alive_tmp:
                    scored_rows.append((0.0, ms, idx, f"{base}#{sc}_{cc}_{ms}ms"))
            scored_rows.sort(key=lambda t: (-t, t, t))
            new_rows = [res_ln for _, _, _, res_ln in scored_rows]
            with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(new_rows))
            add_log(f"Умная проверка: живых {len(new_rows)}, удалено {dead_cnt}")
            print(f"\n{c}[+] Готово! Живых: {len(new_rows)} | Удалено: {dead_cnt}{RST}"); time.sleep(1.5)
        elif cmd.isdigit() and 1 <= int(cmd) <= len(all_rows):
            idx = int(cmd) - 1; base, sc, cc, ms, spd, tag = parse_row_info(all_rows[idx]); is_fav = base in fav_bases
            print(f"\n{c}Сервер #{idx + 1}: {sc} | {cc} | {ms} | {spd}{RST}\n  1. Подключить VPN  2. Тест (Пинг+Страна+Скорость)  3. Копировать  4. Удалить  5. {'Убрать ★' if is_fav else 'В Избранное ★'}  6. Глубокий тест (3 пинга + YT + AI)  7. Тест 4K + Leak")
            act = input("> ").strip()
            if act == "1": print(f"{c}[+] Подключено!{RST}" if connect_vpn(base, f"#{idx + 1} {sc}_{cc}") else "\033[91m[!] Ошибка запуска.\033[0m"); time.sleep(1.3)
            elif act == "2":
                nms = run_single_test(base, False, False)
                if nms is not None:
                    ncc, nspd = run_single_test(base, False, True), run_single_test(base, True, False)
                    all_rows[idx] = f"{base}#{sc}_{ncc}_{nms}ms_{nspd}Mbps"
                    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(all_rows))
                    print(f"  {c}[+] {ncc} | {nms}ms | {nspd}Mbps{RST}")
                else: print("  \033[91m[!] Не отвечает.\033[0m")
                time.sleep(1.2)
            elif act == "3": subprocess.run("clip", input=all_rows[idx].encode("utf-8"), check=False); print("  [+] Скопировано!"); time.sleep(0.8)
            elif act == "4": all_rows.pop(idx); open("best_configs.txt", "w", encoding="utf-8").write("\n".join(all_rows))
        elif act == "5":
                favs = [x for x in favs if first(x.split("#"), x) != base] if is_fav else favs + [all_rows[idx]]
                save_favs(favs); print(f"  {c}[+] Избранное обновлено!{RST}"); time.sleep(0.8)
        elif act == "6":
                print("  Запуск глубокого теста (3 пинга, Jitter, YouTube, ChatGPT)...")
                dt = deep_test_node(base)
                if dt:
                    yt_s = f"{c}OK{RST}" if dt["yt"] else "\033[91mNO\033[0m"
                    ai_s = f"{c}OK{RST}" if dt["ai"] else "\033[91mNO\033[0m"
                    print(f"  {c}[+] Пакеты: {dt['ok']}/3 | Ср. пинг: {dt['avg']}ms | Jitter: {dt['jitter']}ms | YouTube: {yt_s} | ChatGPT: {ai_s}{RST}")
                else: print("  \033[91m[!] Узел не прошёл глубокий тест.\033[0m")
                input("  Enter...")
        elif act == "7":
            print("  Замер реального видеопотока (4K/1080p) и проверка утечки IP...")
            t_v = time.time()
            v_spd = run_single_test(base, True, False)
            cc_chk, ip_chk, _ = fetch_trace_info(None if CFG.get("tun", False) else {"http": f"http://127.0.0.1:{CFG.get('px_port', 10809)}", "https": f"http://127.0.0.1:{CFG.get('px_port', 10809)}"}, 3.0, True)
            q_verdict = "\033[96mYouTube 4K60 ULTRA\033[0m" if v_spd >= 35 else ("\033[92m1080p FullHD OK\033[0m" if v_spd >= 12 else "\033[93m720p / Базовый\033[0m")
            leak_s = "\033[91mУТЕЧКА RU IP!\033[0m" if (ip_chk and ip_chk == REAL_HOME_IP) else "\033[92mIP защищён (OK)\033[0m"
            print(f"  {c}[+] Поток: {v_spd} Mbps ({q_verdict}) | Защита: {leak_s} ({time.time() - t_v:.1f}с){RST}")
            input("  Enter...")
        else:
            flt, page = cmd, 0

def fetch_url(u_list):
    if isinstance(u_list, str): u_list = [u_list]
    for u in u_list:
        try:
            with requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, proxies=get_px(), stream=True, timeout=(4, 6)) as r:
                if r.status_code != 200: continue
                chunks, sz = list(), 0
                for ch in r.iter_content(65536, decode_unicode=True):
                    if ch:
                        chunks.append(ch); sz += len(ch)
                        if sz > 1500000: break
                res = parse_text("".join(chunks))
                if res: return res
        except Exception: continue
    return list()

class SubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = self.path.strip("/").lower() or "sub"
        if key in SUB_MAP and SUB_MAP[key]:
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8" if key.startswith(("clash", "sb")) else "text/plain; charset=utf-8"); self.end_headers()
            self.wfile.write(SUB_MAP[key].encode("utf-8"))
        else: self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

def make_shortcut():
    desk = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desk): desk = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    with open(os.path.join(desk, "NETPULSE.bat"), "w", encoding="utf-8") as f:
        f.write(f'@echo off\nchcp 65001 >nul\ncd /d "{os.path.dirname(os.path.abspath(first(sys.argv, "netpulse.py")))}"\n"{sys.executable}" "{os.path.basename(first(sys.argv, "netpulse.py"))}"\n')
    print(f"\n{CFG['color']}{tr('bat_ok')}{RST}")
def finalize_results(work, all_sources, bl, append_existing=False, run_collected=None, auto_bg=False):
    global SUB_MAP
    c_col, db = CFG["color"], load_src_db()
    if run_collected:
        for s, cnt in run_collected.items():
            ent = db.setdefault(s, {"collected": 0, "working": 0, "prio": False}); ent["collected"] = ent.get("collected", 0) + cnt
    for s, wk_cnt in SRC_STATS.items():
        if wk_cnt > 0:
            ent = db.setdefault(s, {"collected": 0, "working": 0, "prio": False}); ent["working"] = ent.get("working", 0) + wk_cnt
    save_src_db(db)
    strict_filter = bool(CFG["countries"]) or bool(parse_proto_set(CFG.get("proto", ""))) or CFG.get("wl_mode", 0) == 2
    if CFG.get("blacklist", True) and all_sources and not STOP_EVENT.is_set() and not strict_filter:
        dead_cnt = 0
        for s in all_sources:
            if SRC_STATS.get(s, -1) == 0 and db.get(s, {}).get("working", 0) == 0: bl[s] = time.time() + 86400; dead_cnt += 1
        save_bl(bl)
        if dead_cnt and not auto_bg: print(f"{DIM}{c_col}[*] Quarantine (24h): {dead_cnt} empty sources{RST}")
    by_cc = {}
    if CFG["speed"] and work:
        if not auto_bg: print(f"\n{c_col}{tr('s5')} ({len(work)})...{RST}")
        scored, t_sp = list(), time.time()
        try:
            min_s = float(CFG.get("min_speed", 0.0))
            for idx, (ms, cc, cfg) in enumerate(work, 1):
                mbps = run_single_test(cfg, True, False)
                if min_s > 0 and mbps < min_s:
                    if not auto_bg: draw_bar(idx, len(work), f"| Skip {mbps}Mbps", t_sp)
                    continue
                tag = f"{cfg}_{mbps}Mbps"
                scored.append((mbps, cc, tag))
                if not auto_bg: sys.stdout.write(f"\r\033[K  {c_col}-> {tag.split('#').pop()}{RST}\n"); draw_bar(idx, len(work), "", t_sp)
        except KeyboardInterrupt:
            for ms, cc, cfg in work[len(scored):]: scored.append((0.0, cc, cfg))
        scored.sort(key=lambda x: first(x, 0.0), reverse=True)
        fin = list((c for _, _, c in scored))
        for _, cc, c in scored:
            if cc != "FAST": by_cc.setdefault(cc.lower(), list()).append(c)
    else:
        work.sort(key=lambda x: first(x, 9999))
        fin = list((c for _, _, c in work))
        for _, cc, c in work:
            if cc != "FAST": by_cc.setdefault(cc.lower(), list()).append(c)
    if append_existing and os.path.exists("best_configs.txt"):
        try:
            old_rows = [ln.strip() for ln in open("best_configs.txt", "r", encoding="utf-8") if ln.strip()]
            new_bases = {first(x.split("#"), x) for x in fin}
            fin = fin + [x for x in old_rows if first(x.split("#"), x) not in new_bases]
        except Exception: pass
    favs = load_favs()
    if favs:
        fav_bases = {first(x.split("#"), x) for x in favs}
        fin = favs + [x for x in fin if first(x.split("#"), x) not in fav_bases]
    if fin:
        with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(fin))
        add_log(f"{'Авто-поиск' if auto_bg else 'Поиск'} завершён: {len(fin)} серверов")
    c_yaml, sb_json = build_clash_sub(fin), build_sb_sub(fin)
    open("sub_clash.yaml", "w", encoding="utf-8").write(c_yaml); open("sub_singbox.json", "w", encoding="utf-8").write(sb_json)
    SUB_MAP = {"sub": base64.b64encode("\n".join(fin).encode("utf-8")).decode("utf-8"), "clash": c_yaml, "sb": sb_json}
    if by_cc:
        os.makedirs("configs_by_country", exist_ok=True)
        for cc, items in by_cc.items():
            open(os.path.join("configs_by_country", f"best_{cc.upper()}.txt"), "w", encoding="utf-8").write("\n".join(items))
            SUB_MAP[cc], SUB_MAP[f"clash/{cc}"], SUB_MAP[f"sb/{cc}"] = base64.b64encode("\n".join(items).encode("utf-8")).decode("utf-8"), build_clash_sub(items), build_sb_sub(items)
    if auto_bg: return
    try: winsound.Beep(880, 180); winsound.Beep(1174, 240)
    except Exception: pass
    s_port = CFG.get("sub_port", 18080)
    top_spd = fin.split("_").pop() if fin and "Mbps" in fin else "-"
    top_ccs = ", ".join(k.upper() for k in list(by_cc.keys())[:4]) or "MIX"
    print(f"\n{c_col}╔{'═' * 72}╗\n║  \033[92m✔ {tr('done')} {len(fin):<6}\033[0m {c_col}│ Рекорд: \033[96m{top_spd:<10}\033[0m {c_col}│ Страны: \033[93m{top_ccs:<16}\033[0m{c_col}║\n║  {tr('url')} http://127.0.0.1:{s_port}/sub | /clash | /sb{' ' * 16}║\n╚{'═' * 72}╝{RST}")
    if by_cc: print(f"{c_col}By country: [{' | '.join(f'/{cc}' for cc in sorted(by_cc.keys()))}]{RST}")
    srv = HTTPServer(("127.0.0.1", s_port), SubHandler); threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("Enter -> Menu")
    try: input()
    except KeyboardInterrupt: pass
    srv.shutdown(); srv.server_close()

def execute_batch_pool(alive, b_workers, b_size, silent=False):
    global CHECKED, FOUND_COUNT
    work, xray_items, sb_items = list(), list(), list()
    for src, uri in alive:
        sc, _, _ = get_hp(uri)
        (sb_items if sc in ("hy2", "tuic") else xray_items).append((src, uri))
    batches = [(xray_items[i:i + b_size], False) for i in range(0, len(xray_items), b_size)] + [(sb_items[i:i + 20], True) for i in range(0, len(sb_items), 20)]
    t4_tm, c_col, unit_lbl = time.time(), CFG["color"], tr("unit")
    with ThreadPoolExecutor(max_workers=b_workers) as ex:
        futs = {ex.submit(run_batch_group, b, is_sb): len(b) for b, is_sb in batches}
        for f in as_completed(futs):
            b_len = futs[f]
            try:
                for src, ms, cc, clean in f.result():
                    with LOCK:
                        if FOUND_COUNT >= CFG["limit"]: STOP_EVENT.set(); break
                        FOUND_COUNT += 1; SRC_STATS[src] = SRC_STATS.get(src, 0) + 1
                        if not silent: sys.stdout.write(f"\r\033[K  {c_col}[+] {clean.split('#').pop()}{RST}\n")
                        work.append((ms, cc, clean))
            except Exception: pass
            with LOCK:
                CHECKED += b_len
                if not silent: draw_bar(len(alive) if STOP_EVENT.is_set() else min(CHECKED, len(alive)), len(alive), f"| {int(CHECKED / max(time.time() - t4_tm, 0.1))} {unit_lbl} | Found: {FOUND_COUNT}", t4_tm)
            if STOP_EVENT.is_set():
                for pending in futs: pending.cancel()
                break
    return work

def run_tcp_filter(filtered, t_tcp, silent=False):
    alive, done = list(), 0
    with ThreadPoolExecutor(max_workers=TCP_WORKERS) as ex:
        for f in as_completed([ex.submit(tcp_ok, item) for item in filtered]):
            done += 1; r = f.result()
            if r: alive.append(r)
            if not silent and (done % 300 == 0 or done == len(filtered)): draw_bar(done, len(filtered), f"| OK: {len(alive)}", t_tcp)
    return alive
def run_clipboard_scan():
    global CHECKED, FOUND_COUNT, PROC_FLAGS, SRC_STATS, REAL_HOME_IP, SCAN_BUSY
    if SCAN_BUSY: return
    xray_bin, sb_bin = find_cores()
    if not xray_bin and not sb_bin:
        if ru2en(input(f"\033[93m{tr('no_xray')}{RST}").strip()).upper() == "Y" and download_cores(False): pass
        else: return
    c_col, raw_txt = CFG["color"], ""
    try: raw_txt = subprocess.check_output(["powershell", "-command", "Get-Clipboard"], text=True, encoding="utf-8", errors="ignore")
    except Exception: pass
    found = parse_text(raw_txt)
    if not found: print(f"\033[91m[!] В буфере обмена не найдено ссылок.{RST}"); return
    SCAN_BUSY, CHECKED, FOUND_COUNT, SRC_STATS = True, 0, 0, {}; STOP_EVENT.clear(); work = list()
    try:
        if CFG.get("strict_ip", True): _, REAL_HOME_IP, _ = fetch_trace_info(None, 5.0, False)
        b_workers, b_size, PROC_FLAGS = (2, 20, 0x00004000) if CFG["mode"] == 1 else ((4, 25, 0) if CFG["mode"] == 2 else (6, 25, 0))
        filtered = smart_prefilter([("clip", u) for u in found])
        print(f"{c_col}[1/2] Буфер обмена: {len(found)} -> {len(filtered)}, TCP-отсев...{RST}")
        alive = run_tcp_filter(filtered, time.time())
        if not alive: print("\033[91m[!] Нет ответа по TCP.\033[0m"); return
        print(f"{c_col}[2/2] Турбо-проверка ({len(alive)})...{RST}")
        work = execute_batch_pool(alive, b_workers, b_size)
    except KeyboardInterrupt:
        STOP_EVENT.set(); time.sleep(0.2); print(f"\n{c_col}[!] Стоп. Найдено: {len(work)}{RST}")
        if not work: return
    finally: SCAN_BUSY = False
    finalize_results(work, set(), {}, append_existing=True)

def run_scan(from_cache=False, auto_bg=False):
    global CHECKED, FOUND_COUNT, PROC_FLAGS, SRC_STATS, REAL_HOME_IP, SCAN_BUSY
    if SCAN_BUSY: return
    xray_bin, sb_bin = find_cores()
    if not xray_bin and not sb_bin:
        if auto_bg: return
        if ru2en(input(f"\033[93m{tr('no_xray')}{RST}").strip()).upper() == "Y" and download_cores(False): pass
        else: return
    SCAN_BUSY, CHECKED, FOUND_COUNT, SRC_STATS = True, 0, 0, {}; STOP_EVENT.clear(); c_col = CFG["color"]
    if not auto_bg:
        print(f"{c_col}╔{'═' * 72}╗\n║  {style_txt('NETPULSE SCANNER ENGINE • TURBO DISCOVERY')}{RST}{c_col}{' ' * 27}║\n╚{'═' * 72}╝{RST}")
    work, all_sources, bl, by_src = list(), set(), load_bl(), {}
    try:
        if CFG.get("strict_ip", True): _, REAL_HOME_IP, _ = fetch_trace_info(None, 5.0, False)
        b_workers, b_size, PROC_FLAGS = (2, 20, 0x00004000) if CFG["mode"] == 1 else ((4, 25, 0) if CFG["mode"] == 2 else (6, 25, 0))
        cap = CFG.get("batch_cap", 3500)
        if from_cache:
            c_data = load_cache(); c_nodes, off = c_data.get("nodes", list()), c_data.get("offset", 0)
            if off >= len(c_nodes):
                if not auto_bg: print(f"\033[93m[!] Весь кэш ({len(c_nodes)}) проверен!{RST}")
                return
            alive = [tuple(x) for x in c_nodes[off:off + cap]]; save_cache(c_nodes, off + len(alive))
            if not auto_bg: print(f"\n{c_col}[КЭШ] Допроверка {off + 1}..{off + len(alive)} из {len(c_nodes)}...{RST}")
        else:
            if not auto_bg: print(f"\n{c_col}{tr('s1')}{RST}")
            urls, t1, db = list(), time.time(), load_src_db()
            prio_tags = {k for k, v in db.items() if v.get("prio", False)}
            if CFG.get("src", 0) in (0, 2, 3):
                tg_urls = get_tg_and_web(bl)
                for s, _ in tg_urls: all_sources.add(s)
                urls.extend(tg_urls)
            if CFG.get("src", 0) in (0, 1, 3):
                gl = CFG.get("gh_lang", 0)
                q_list = SEARCH_QUERIES_RU if gl == 1 else (SEARCH_QUERIES_EN if gl == 2 else (SEARCH_QUERIES_EN + SEARCH_QUERIES_RU))
                repos_dict, pinned = {}, [k[3:] for k in prio_tags if k.startswith("gh:")] + (PINNED_REPOS_RU if gl in (0, 1) else [])
                if os.path.exists(CUSTOM_FILE):
                    try:
                        for ln in open(CUSTOM_FILE, "r", encoding="utf-8"):
                            s = ln.strip()
                            if s and not s.startswith(("#", "http://", "https://", "@")) and "/" in s: pinned.append(s.strip("/"))
                    except Exception: pass
                for full_n in dict.fromkeys(pinned):
                    prio_tags.add(f"gh:{full_n}")
                    if full_n not in repos_dict and "/" in full_n:
                        o_n, r_n = full_n.split("/", 1)
                        repos_dict[full_n] = {"owner": {"login": o_n}, "name": r_n, "default_branch": "main", "full_name": full_n}
                target_cnt, per_q = CFG.get("repos", 40) + len(repos_dict), max(10, min(100, (CFG.get("repos", 40) // len(q_list)) + 5))
                for q_str in q_list:
                    if len(repos_dict) >= target_cnt: break
                    got_api = False
                    try:
                        r = requests.get(f"{GH}/search/repositories", params={"q": q_str, "sort": "updated", "order": "desc", "per_page": min(100, per_q)}, headers=get_hdr(), proxies=get_px(), timeout=3.5)
                        if r.status_code == 200:
                            for it in r.json().get("items", list()):
                                fn = it.get("full_name")
                                if fn and fn not in repos_dict and len(repos_dict) < target_cnt: repos_dict[fn] = it
                            got_api = True
                    except Exception: pass
                    if not got_api:
                        for pg in (1,):
                            if len(repos_dict) >= target_cnt: break
                            try:
                                wr = requests.get(f"{GH_HOST}/search", params={"q": q_str, "type": "repositories", "s": "updated", "o": "desc", "p": pg}, headers={"User-Agent": "Mozilla/5.0"}, proxies=get_px(), timeout=6)
                                found_pg = 0
                                for o_n, r_n in re.findall(r'"hl_name":"([^"/]+)/([^"]+)"', wr.text) + re.findall(r'href="/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"', wr.text):
                                    o_n, r_n = re.sub(r'<[^>]+>', '', o_n), re.sub(r'<[^>]+>', '', r_n)
                                    fn = f"{o_n}/{r_n}"
                                    if o_n.lower() not in ("search", "topics", "collections", "sponsors", "login", "signup", "features", "enterprise", "pricing", "about", "site", "settings") and fn not in repos_dict and len(repos_dict) < target_cnt:
                                        repos_dict[fn] = {"owner": {"login": o_n}, "name": r_n, "default_branch": "main", "full_name": fn}
                                        found_pg += 1
                                if found_pg == 0: break
                            except Exception: break
                repos = [r for r in repos_dict.values() if not CFG.get("blacklist", True) or f"gh:{r.get('full_name')}" not in bl]
                for r in repos: all_sources.add(f"gh:{r.get('full_name')}")
                with ThreadPoolExecutor(max_workers=16) as ex:
                    for idx, f_urls in enumerate(ex.map(get_files, repos), 1):
                        urls.extend(f_urls)
                        if not auto_bg: draw_bar(idx, len(repos), f"| URLs: {len(urls)}", t1)
            if not auto_bg: print(f"{c_col}{tr('s2')} ({len(urls)})...{RST}")
            raw, done, t2, by_cat = list(), 0, time.time(), {"GitHub": 0, "Web": 0, "TG": 0}
            with ThreadPoolExecutor(max_workers=50) as ex:
                futs = {ex.submit(fetch_url, u_list): s for s, u_list in urls}
                for f in as_completed(futs):
                    done += 1; s = futs[f]
                    try:
                        items = f.result()
                        for c in items: raw.append((s, c))
                        if items: by_src[s] = by_src.get(s, 0) + len(items); by_cat["GitHub" if s.startswith("gh:") else ("TG" if s.startswith("tg:") else "Web")] += len(items)
                    except Exception: pass
                    if not auto_bg and (done % 10 == 0 or done == len(urls)): draw_bar(done, len(urls), "", t2)
            if not auto_bg: print(f"  {c_col}-> Собрано: GitHub: {by_cat['GitHub']} | Web: {by_cat['Web']} | TG: {by_cat['TG']}{RST}")
            filtered = smart_prefilter(raw)
            for src, _ in filtered: SRC_STATS[src] = 0
            if not auto_bg: print(f"{c_col}{tr('s3')} ({len(raw)} -> {len(filtered)})...{RST}")
            alive_all = run_tcp_filter(filtered, time.time(), silent=auto_bg)
            prio, mid_rest, tail_rest, src_cap = list(), list(), list(), {}; random.shuffle(alive_all)
            for src, uri in alive_all:
                if src in prio_tags or (CFG.get("wl_mode", 0) == 1 and is_whitelist_sni(uri)): prio.append((src, uri))
                elif src_cap.get(src, 0) < 250: mid_rest.append((src, uri)); src_cap[src] = src_cap.get(src, 0) + 1
                else: tail_rest.append((src, uri))
            ordered_all = prio + mid_rest + tail_rest; alive = ordered_all[:cap]; save_cache([list(x) for x in ordered_all], len(alive))
        if not auto_bg: print(f"{c_col}{tr('s4')} ({len(alive)})...{RST}")
        work = execute_batch_pool(alive, b_workers, b_size, silent=auto_bg)
    except KeyboardInterrupt:
        STOP_EVENT.set(); time.sleep(0.2); print(f"\n{c_col}[!] Стоп. Найдено: {len(work)}{RST}")
        if not work: return
    finally: SCAN_BUSY = False
    finalize_results(work, all_sources, bl, append_existing=from_cache, run_collected=by_src, auto_bg=auto_bg)
class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.ULONG), ("nFont", wintypes.DWORD), ("dwFontSize", wintypes._COORD), ("FontFamily", wintypes.UINT), ("FontWeight", wintypes.UINT), ("FaceName", wintypes.WCHAR * 32)]

def apply_win_font(face="Consolas"):
    try:
        h_out = ctypes.windll.kernel32.GetStdHandle(-11)
        cfi = CONSOLE_FONT_INFOEX()
        cfi.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
        cfi.dwFontSize.X = 0
        cfi.dwFontSize.Y = 18
        cfi.FontFamily = 54
        cfi.FontWeight = 700 if CFG.get("tstyle", 1) == 2 else 400
        cfi.FaceName = face
        ctypes.windll.kernel32.SetCurrentConsoleFontEx(h_out, False, ctypes.byref(cfi))
    except Exception: pass

def style_txt(txt):
    st = CFG.get("tstyle", 1)
    if st == 2: return f"\033[1m{txt}"
    if st == 3: return f"\033[3m{txt}"
    if st == 4: return f"\033[1m» {txt}"
    if st == 5: return f"\033[1;3m» {txt}"
    if st == 6: return f"\033[4m{txt}"
    return txt

TSTYLE_NAMES = {1: "Normal", 2: "Bold", 3: "Italic", 4: "Cyber»", 5: "Glow", 6: "HUD-Line"}

def colorize_logo(b_lines, tick, c):
    gm = CFG.get("grad", 1)
    if gm == 0: return [f"{c}{ln}{RST}" for ln in b_lines]
    res = list()
    for r_i, ln in enumerate(b_lines):
        if gm == 1:
            t = r_i / max(1, len(b_lines) - 1)
            rv, gv, bv = int(138 * (1 - t)), int(79 + 150 * t), 255
            res.append(f"\033[38;2;{rv};{gv};{bv}m{ln}{RST}")
        else:
            out_ch = list()
            for c_i, ch in enumerate(ln):
                if ch == " ": out_ch.append(" ")
                else:
                    ph = (c_i + r_i * 3 + tick * 2) % 24
                    pal = [(138,79,255),(90,140,255),(0,229,255),(0,255,170),(120,255,120),(255,215,0),(255,105,180),(190,80,255)]
                    rv, gv, bv = pal[(ph // 3) % len(pal)]
                    out_ch.append(f"\033[38;2;{rv};{gv};{bv}m{ch}")
            res.append("".join(out_ch) + RST)
    return res

def fmt_ping(ms_str):
    v = int(ms_str[:-2]) if ms_str.endswith("ms") and ms_str[:-2].isdigit() else 9999
    col = "\033[92m" if v <= 250 else ("\033[93m" if v <= 650 else "\033[91m")
    return f"{col}{ms_str:<8}{RST}"

def fmt_spd(spd_str):
    try: v = float(spd_str.rstrip("Mbps"))
    except Exception: v = 0.0
    col = "\033[96m" if v >= 30 else ("\033[92m" if v >= 12 else ("\033[97m" if v > 0 else DIM))
    return f"{col}{spd_str:<10}{RST}"

def box_row(txt, c, w=72):
    vis = len(re.sub(r'\033\[[0-9;]*m', '', txt))
    return f"{c}║ {txt}{' ' * max(0, w - 1 - vis)}{c}║{RST}"

TRAY_HWND = None

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [("ReadOperationCount", ctypes.c_uint64), ("WriteOperationCount", ctypes.c_uint64), ("OtherOperationCount", ctypes.c_uint64), ("ReadTransferCount", ctypes.c_uint64), ("WriteTransferCount", ctypes.c_uint64), ("OtherTransferCount", ctypes.c_uint64)]

LAST_IO = [0.0, 0, 0, 0.0, 0.0, 0]

def get_vpn_traffic():
    global LAST_IO
    if not ACTIVE_PROC or ACTIVE_PROC.poll() is not None:
        LAST_IO = [0.0, 0, 0, 0.0, 0.0, 0]
        return "0.0 Mbps", "0.0 Mbps", "0 MB"
    try:
        ioc = IO_COUNTERS()
        if ctypes.windll.kernel32.GetProcessIoCounters(int(ACTIVE_PROC._handle), ctypes.byref(ioc)):
            now = time.time()
            rx, tx = ioc.ReadTransferCount, ioc.WriteTransferCount
            if LAST_IO > 0 and now - LAST_IO >= 0.4:
                dt = now - LAST_IO
                LAST_IO = max(0.0, ((rx - LAST_IO) * 8) / (dt * 1_000_000))
                LAST_IO = max(0.0, ((tx - LAST_IO) * 8) / (dt * 1_000_000))
                LAST_IO, LAST_IO, LAST_IO = now, rx, tx
            elif LAST_IO == 0:
                LAST_IO, LAST_IO, LAST_IO = now, rx, tx
            tot_mb = (rx + tx) / (1024 * 1024)
            return f"{LAST_IO:.1f}M", f"{LAST_IO:.1f}M", f"{tot_mb:.1f}MB"
    except Exception: pass
    return "0.0M", "0.0M", "0MB"

def notify_tray(title, msg):
    add_log(f"{title}: {msg}")
    if not TRAY_HWND: return
    try:
        nid = NOTIFYICONDATAW(cbSize=ctypes.sizeof(NOTIFYICONDATAW), hWnd=TRAY_HWND, uID=1, uFlags=0x10, szInfo=msg[:250], szInfoTitle=title[:60], dwInfoFlags=1)
        ctypes.windll.shell32.Shell_NotifyIconW(1, ctypes.byref(nid))
    except Exception: pass

def start_hud_overlay():
    def _run():
        import tkinter as tk
        u32 = ctypes.windll.user32
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.90)
        root.configure(bg="#111118", highlightthickness=1, highlightbackground="#8A4FFF")
        lbl = tk.Label(root, text="NETPULSE • VPN: OFF", font=("Consolas", 11, "bold"), fg="#8A4FFF", bg="#111118", padx=12, pady=4)
        lbl.pack()
        root.update_idletasks()
        hwnd = u32.GetParent(root.winfo_id()) or root.winfo_id()
        ex = u32.GetWindowLongW(hwnd, -20)
        u32.SetWindowLongW(hwnd, -20, ex | 0x80000 | 0x20 | 0x08000000)
        def tick_hud():
            if not CFG.get("overlay", True):
                root.withdraw()
            else:
                root.deiconify()
                hx = CFG.get("cname", "#8A4FFF")
                fg_c = hx if hx.startswith("#") else "#9D4EDD"
                root.configure(highlightbackground=fg_c)
                if ACTIVE_NAME:
                    rx_s, tx_s, _ = get_vpn_traffic()
                    up_m = int((time.time() - ACTIVE_START) // 60) if ACTIVE_START > 0 else 0
                    cc_t = ACTIVE_CC if ACTIVE_CC else "VPN"
                    txt = f"⚡ NETPULSE │ {cc_t} ON │ ↓{rx_s} ↑{tx_s} │ {up_m}m"
                else:
                    txt = "◈ NETPULSE │ VPN: OFF"
                lbl.config(text=txt, fg=fg_c)
                root.update_idletasks()
                sw = root.winfo_screenwidth()
                w = root.winfo_reqwidth()
                root.geometry(f"+{sw - w - 14}+44")
            root.after(1000, tick_hud)
        tick_hud()
        root.mainloop()
    threading.Thread(target=_run, daemon=True).start()

def auto_heal_loop():
    while True:
        time.sleep(1200)
        if SCAN_BUSY or not os.path.exists("best_configs.txt"): continue
        try:
            rows = [ln.strip() for ln in open("best_configs.txt", encoding="utf-8") if ln.strip()]
            if len(rows) < 3: continue
            top_n, rest = rows[:10], rows[10:]
            alive_top = [ln for ln in top_n if run_single_test(first(ln.split("#"), ln), False, False) is not None]
            if len(alive_top) < len(top_n):
                with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(alive_top + rest))
                notify_tray("NETPULSE Auto-Heal", f"Удалено мёртвых из Топ-10: {len(top_n) - len(alive_top)}")
        except Exception: pass

def render_pulse_bar(tick, width, c):
    bars = "▁▂▃▄▅▆▇█▇▆▅▄▃▂"
    step = 2 if (ACTIVE_NAME or SCAN_BUSY) else 1
    wave = "".join(bars[(i + tick * step) % len(bars)] for i in range(width))
    return f"{c}{wave}{RST}"

def render_bg(bg_type, tick, w=78, h=28):
    grid = list((list((" " * w)) for _ in range(h)))
    if bg_type == 1:
        for x in range(w): grid[h - 2][x] = "─────────╲╱╲──/\\──╲/─────────"[(x + tick) % 29]
    elif bg_type == 2:
        for col in range(2, w - 2, 4):
            y = (tick + col * 3) % h; grid[y][col], grid[(y - 1) % h][col] = "01011001"[(col + tick) % 8], "01011001"[(col + tick + 1) % 8]
    elif bg_type == 3:
        for row in range(1, h - 1, 3):
            x = (tick * 2 + row * 7) % (w - 4); grid[row][x], grid[row][x + 1], grid[row][x + 2] = "·", "•", "»"
    elif bg_type == 4:
        for i in range(18): grid[(i * 7) % (h - 2)][(i * 17 + (tick if i % 2 == 0 else 0)) % w] = "+" if (tick + i) % 3 == 0 else "."
    elif bg_type == 5:
        for r in range(1, 12):
            x, y = int(w // 2 + r * 2.2 * (1 if (tick % 4) in (0, 1) else -1)), int(h // 2 + (r // 2) * (1 if (tick % 4) in (1, 2) else -1))
            if 0 <= x < w and 0 <= y < h - 1: grid[y][x] = "o"
    elif bg_type == 6:
        for y in range(h - 1):
            p1 = (y + tick) % 12; off = p1 if p1 < 6 else 12 - p1; x1, x2 = 2 + off * 2, w - 4 - off * 2; grid[y][x1], grid[y][x2] = "●", "○"
            if off == 3:
                for mx in range(x1 + 1, x2, 3): grid[y][mx] = "·"
    elif bg_type == 7:
        for i in range(28): grid[(i * 5 + tick * 2) % (h - 1)][(i * 13 + tick) % (w - 2)] = "/"
    elif bg_type == 8:
        for x in range(w):
            y = (h // 2) + [0, 1, 2, 2, 1, 0, -1, -2, -2, -1][(x + tick) % 10] * 2
            if 0 <= y < h - 1: grid[y][x] = "~"
    elif bg_type == 9:
        for i in range(24): grid[(i * 13 + (tick // 3) * 7) % (h - 1)][(i * 29 + (tick // 2) * 11) % w] = "*✦·+°"[(i + tick) % 5]
    elif bg_type == 10:
        span = h - 2; pos = tick % (span * 2); y = pos if pos < span else (span * 2 - pos)
        for x in range(1, w - 1): grid[y][x] = "═" if x % 2 == 0 else "─"
    return grid

def apply_preset_ui():
    c = CFG["color"]
    keys = ("wl_mode", "proto", "max_ping", "min_speed", "limit", "src", "repos", "gh_lang", "speed", "mode", "target")
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        up = CFG.setdefault("user_presets", {})
        print(c + "╔" + "═" * 72 + "╗" + RST + "\n" + box_row(style_txt("HUNT PRESETS • БЫСТРЫЕ ПРОФИЛИ ОХОТЫ И СВОИ СЛОТЫ") + RST, c) + "\n" + c + "╚" + "═" * 72 + "╝" + RST)
        print("  1. Мобильный / Белые списки (Строго RU-SNI • VLESS+HY2 • Пинг < 800ms)")
        print("  2. Турбо-сбор (Максимум баз • Все протоколы • Лимит 300 • Без порогов)")
        print("  3. Гейминг / Стриминг 4K (Скорость > 20 Mbps • Пинг < 350ms • Без SS)")
        print("  4. Сбалансированный стандарт (АВТО CDN • Лимит 150 • Все протоколы)")
        print(f"\n{c}Свои сохранённые профили:{RST}")
        for slot in ("5", "6", "7"):
            if slot in up:
                d = up[slot]
                cc_lbl = ",".join(d.get("countries", list())) or "ALL"
                pr_lbl = d.get("proto", "").upper() or "ВСЕ"
                print(f"  {c}{slot}. {d.get('name', f'Слот #{slot}')}{RST} ({cc_lbl} • {pr_lbl} • L:{d.get('limit', 150)} • >{d.get('min_speed', 0)}M • <{d.get('max_ping', 0)}ms)")
            else:
                print(f"  {DIM}{slot}. [ Пустой слот — нажмите S{slot} чтобы сохранить текущие настройки ]{RST}")
        print(f"\n{c}Команды:{RST} [1-7] Загрузить | [S5 / S6 / S7] Сохранить текущие в слот | [D5 / D6 / D7] Удалить | [Enter] Меню")
        ps = input("\n> ").strip().upper()
        if not ps: break
        elif ps == "1": CFG.update({"wl_mode": 2, "proto": "hy2+vless", "max_ping": 800, "min_speed": 0.0, "limit": 100, "src": 0})
        elif ps == "2": CFG.update({"wl_mode": 0, "proto": "", "max_ping": 0, "min_speed": 0.0, "limit": 300, "src": 0, "repos": 60})
        elif ps == "3": CFG.update({"wl_mode": 0, "proto": "hy2+trojan+tuic+vless", "max_ping": 350, "min_speed": 20.0, "limit": 80})
        elif ps == "4": CFG.update({"wl_mode": 0, "proto": "", "max_ping": 0, "min_speed": 0.0, "limit": 150, "src": 0})
        elif ps in ("5", "6", "7") and ps in up:
            d = up[ps]
            for k in keys:
                if k in d: CFG[k] = d[k]
            CFG["countries"] = set(d.get("countries", list()))
        elif ps in ("S5", "S6", "S7"):
            slot = ps[1:]
            nm = input(f"Название для слота #{slot} (Enter = Мой профиль #{slot}) > ").strip() or f"Мой профиль #{slot}"
            snap = {k: CFG[k] for k in keys if k in CFG}
            snap["countries"] = sorted(list(CFG.get("countries", set())))
            snap["name"] = nm
            up[slot] = snap
            save_cfg(); print(f"{c}[+] Профиль «{nm}» сохранён в слот #{slot}!{RST}"); time.sleep(1.0); continue
        elif ps in ("D5", "D6", "D7") and ps[1:] in up:
            del up[ps[1:]]; save_cfg(); continue
        else: continue
        save_cfg(); print(f"{c}[+] Профиль применён!{RST}"); time.sleep(0.9); break

def customize_ui():
    c = CFG["color"]
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        f_name = first(BANNERS.get(CFG.get("font", 1), ("Block 3D", None)), "Block 3D")
        ts_n = TSTYLE_NAMES.get(CFG.get("tstyle", 1), "Normal")
        b_str = tr("bgs").get(CFG.get("bg", 6), "ДНК")
        g_lbl = ['Выкл', 'Неон-Градиент', 'Живая волна'][CFG.get('grad', 1)]
        for prev_ln in colorize_logo(list(BANNERS.get(CFG.get("font", 1), list(BANNERS.values())))[-1], 4, c): print(prev_ln)
        ch_row = f"{style_txt('CUSTOMIZATION STUDIO')}{RST}{c} │ Цвет: [97m{CFG['cname']}[0m{c} │ Фон: [96m{b_str}[0m{c} │ Град: [93m{g_lbl}[0m"
        print(f"{c}╔{'═' * 72}╗{RST}\n{box_row(ch_row, c)}\n{c}╚{'═' * 72}╝{RST}")
        print(f"  {c}1.{RST} {style_txt('Изменить ЦВЕТ интерфейса')}{RST}       {DIM}(Палитра + свой RGB / HEX){RST}")
        print(f"  {c}2.{RST} {style_txt('Изменить АНИМАЦИЮ ФОНА')}{RST}         {DIM}(10 режимов + Выкл){RST}")
        print(f"  {c}3.{RST} {style_txt('Изменить ШРИФТ ЛОГОТИПА')}{RST}        {DIM}({f_name}){RST}")
        print(f"  {c}4.{RST} {style_txt('Изменить СТИЛЬ ТЕКСТА')}{RST}           {DIM}({ts_n}){RST}")
        print(f"  {c}5.{RST} {style_txt('Готовые ТЕМЫ в 1 клик')}{RST}          {DIM}(4 авторских пресета){RST}")
        print(f"  {c}6.{RST} {style_txt('Режим ГРАДИЕНТА логотипа')}{RST}       \033[96m[{g_lbl}]\033[0m")
        print(f"  {c}0.{RST} {style_txt('Назад в главное меню')}{RST}")
        act = input("\n> ").strip()
        if not act or act == "0": break
        elif act == "1":
            for k, (col, nm) in COLORS.items(): print(f"  {k:<2}. {col}{nm}{RST}")
            sel = input(f"  15. {c}Свой RGB / HEX{RST}\n> ").strip()
            if sel in COLORS: CFG["color"], CFG["cname"] = COLORS[sel]
            elif sel == "15":
                raw_rgb = input("RGB (R G B) или #HEX > ").strip().lstrip("#")
                if len(raw_rgb) == 6 and re.fullmatch(r'[0-9a-fA-F]{6}', raw_rgb):
                    r_v, g_v, b_v = int(raw_rgb[0:2], 16), int(raw_rgb[2:4], 16), int(raw_rgb[4:6], 16)
                    CFG["color"], CFG["cname"] = f"\033[38;2;{r_v};{g_v};{b_v}m", f"#{raw_rgb.upper()}"
                else:
                    nums = [int(x) for x in re.findall(r'\d+', raw_rgb)]
                    if len(nums) >= 3 and all(0 <= v <= 255 for v in nums[:3]):
                        CFG["color"], CFG["cname"] = f"\033[38;2;{nums};{nums};{nums}m", f"RGB({nums},{nums},{nums})"
        elif act == "2":
            bsel = input("\nФон: 1.Пульс 2.Матрица 3.Поток 4.Звезды 5.Радар 6.ДНК 7.Дождь 8.Волны 9.Искры 10.Сканер 0.Выкл > ").strip()
            if bsel.isdigit() and 0 <= int(bsel) <= 10: CFG["bg"] = int(bsel)
        elif act == "3":
            fsel = input("\nШрифт лого: 1.Block 3D | 2.Cyber Slant | 3.Double Neon | 4.Cyber Blade | 5.Heavy Block > ").strip()
            if fsel.isdigit() and int(fsel) in BANNERS: CFG["font"] = int(fsel)
        elif act == "4":
            tsel = input("\nСтиль текста: 1.Normal | 2.Bold | 3.Italic | 4.Cyber» | 5.Glow | 6.HUD-Line > ").strip()
            if tsel.isdigit() and int(tsel) in TSTYLE_NAMES: CFG["tstyle"] = int(tsel)
        elif act == "6": CFG["grad"] = (CFG.get("grad", 1) + 1) % 3
        elif act == "5":
            print("\n  1. Cyber Violet (Неон #8A4FFF + Double Neon + Glow + ДНК)")
            print("  2. Matrix Hacker (Изумрудный + Cyber Slant + Cyber» + Матрица)")
            print("  3. Crimson Blade (Красный + Cyber Blade + Bold + Сканер)")
            print("  4. Arctic Ghost (Ледяной синий + Block 3D + Italic + Звезды)")
            th = input("> ").strip()
            if th == "1": CFG.update({"color": "\033[38;2;138;79;255m", "cname": "#8A4FFF", "font": 3, "tstyle": 5, "bg": 6})
            elif th == "2": CFG.update({"color": "\033[92m", "cname": "Green", "font": 2, "tstyle": 4, "bg": 2})
            elif th == "3": CFG.update({"color": "\033[91m", "cname": "Red", "font": 4, "tstyle": 2, "bg": 10})
            elif th == "4": CFG.update({"color": "\033[38;5;39m", "cname": "Ice Blue", "font": 1, "tstyle": 3, "bg": 4})
        save_cfg(); c = CFG["color"]

def build_right_panel(c, panel_w):
    if panel_w < 38: return list()
    inner = panel_w - 4
    rows = [ln.strip() for ln in open("best_configs.txt", "r", encoding="utf-8") if ln.strip()] if os.path.exists("best_configs.txt") else list()
    favs = load_favs()
    x_ok = bool(CFG.get("xray") and os.path.exists(CFG.get("xray", "")))
    s_ok = bool(CFG.get("singbox") and os.path.exists(CFG.get("singbox", "")))
    cores_s = f"Xray:{'OK' if x_ok else 'NO'} | SB:{'OK' if s_ok else 'NO'}"
    mode_s = "TUN-Split" if CFG.get("tun", False) else f"Proxy :{CFG.get('px_port', 10809)}"
    up_s = f"{int((time.time() - ACTIVE_START) // 60)}m" if ACTIVE_NAME and ACTIVE_START > 0 else "-"
    ip_s = f"{ACTIVE_CC} ({ACTIVE_IP})" if ACTIVE_IP else ("TUN Active" if ACTIVE_NAME else "Не подключен")
    rx_s, tx_s, tot_s = get_vpn_traffic()
    box = [
        f"{c}╔{'═' * (panel_w - 2)}╗{RST}",
        f"{c}║ {'LIVE DASHBOARD • TELEMETRY':<{inner}} {c}║{RST}",
        f"{c}╠{'═' * (panel_w - 2)}╣{RST}",
        f"{c}║ {RST}{f'Режим: {mode_s} | {cores_s}'[:inner]:<{inner}}{c} ║{RST}",
        f"{c}║ {RST}{f'Статус: {ip_s} | Аптайм: {up_s}'[:inner]:<{inner}}{c} ║{RST}",
        f"{c}║ {RST}{f'Сеть: ↓{rx_s} ↑{tx_s} ({tot_s}) | База:{len(rows)} | FO:{FAILOVER_CNT}'[:inner]:<{inner}}{c} ║{RST}",
        f"{c}╠{'═' * (panel_w - 2)}╣{RST}",
        f"{c}║ {'TOP-5 СЕРВЕРОВ [T1-T5 Пуск | D Стоп]':<{inner}} {c}║{RST}",
        f"{c}╟{'─' * (panel_w - 2)}╢{RST}"
    ]
    if not rows:
        box.append(f"{c}║ {DIM}{'Список пуст — запустите поиск':<{inner}}{RST}{c} ║{RST}")
    else:
        for i in range(5):
            if i < len(rows):
                _, sc, cc, ms, spd, _ = parse_row_info(rows[i])
                act_m = " *" if ACTIVE_NAME and f"#{i + 1} " in ACTIVE_NAME else ""
                sc_c = "\033[96m" if sc == "VLESS" else ("\033[95m" if sc == "HY2" else "\033[93m")
                p_v = int(ms[:-2]) if ms.endswith("ms") and ms[:-2].isdigit() else 9999
                ms_c = "\033[92m" if p_v <= 250 else ("\033[93m" if p_v <= 650 else "\033[91m")
                pad = " " * max(0, inner - len(f"T{i + 1} │ {sc:<6} │ {cc:<5} │ {ms:<7} │ {spd}{act_m}"))
                box.append(f"{c}║ \033[97mT{i + 1}{RST} │ {sc_c}{sc:<6}{RST} │ \033[92m{cc:<5}{RST} │ {ms_c}{ms:<7}{RST} │ \033[96m{spd}{RST}{c}{act_m}{RST}{pad}{c} ║{RST}")
            else:
                box.append(f"{c}║ {' ' * inner} ║{RST}")
    box.append(f"{c}╠{'═' * (panel_w - 2)}╣{RST}")
    box.append(f"{c}║ {'ЖУРНАЛ СОБЫТИЙ (LIVE LOG)':<{inner}} {c}║{RST}")
    box.append(f"{c}╟{'─' * (panel_w - 2)}╢{RST}")
    with LOG_LOCK: snap = list(VPN_LOG[-4:])
    for i in range(4):
        lg = snap[i] if i < len(snap) else ("(ожидание событий...)" if i == 0 else "")
        box.append(f"{c}║ {DIM}{lg[:inner]:<{inner}}{RST}{c} ║{RST}")
    box.append(f"{c}╚{'═' * (panel_w - 2)}╝{RST}")
    return box

def show_menu():
    apply_win_font(CFG.get("winfont", "Consolas"))
    global NEXT_AUTO_SCAN
    b_lines = list(BANNERS.get(CFG.get("font", 1), list(BANNERS.values())[0]))[-1]
    tick, buf, last_sz, r_panel_cache, last_draw, force_draw = 0, "", (0, 0), list(), 0.0, True
    if CFG.get("auto_scan_min", 0) > 0 and NEXT_AUTO_SCAN <= 0: NEXT_AUTO_SCAN = time.time() + CFG["auto_scan_min"] * 60
    os.system("cls" if os.name == "nt" else "clear"); sys.stdout.write("\033[?25l")
    try:
        while True:
            if TRAY_HIDDEN: time.sleep(0.2); continue
            now_t = time.time()
            if now_t - last_draw >= 0.05 or force_draw:
                force_draw, last_draw = False, now_t
                ts = shutil.get_terminal_size((120, 30))
                term_w, term_h = max(80, ts.columns), max(28, ts.lines)
                if (term_w, term_h) != last_sz:
                    os.system("cls" if os.name == "nt" else "clear")
                    last_sz = (term_w, term_h)
                c = CFG["color"]
                if tick % 40 == 0:
                    c_info, db = load_cache(), load_src_db()
                    rem_c = max(0, len(c_info.get("nodes", list())) - c_info.get("offset", 0))
                    cache_tag = f" [Кэш: {rem_c}]" if rem_c > 0 else ""
                    repo_tag = f" [★{sum(1 for v in db.values() if v.get('prio', False))} / {len(db)}]"
                    r_panel_cache = build_right_panel(c, min(56, term_w - 79)) if term_w >= 116 else list()
                c_str = ", ".join(sorted(CFG["countries"])) if CFG["countries"] else tr("all")
                p_set = parse_proto_set(CFG.get("proto", ""))
                p_str = "+".join(x.upper() for x in sorted(p_set)) if p_set else "ВСЕ"
                wl_str, s_src = tr("wl_m")[CFG.get("wl_mode", 0)], f"{tr('srcs')[CFG.get('src', 0)]} [{tr('gh_l')[CFG.get('gh_lang', 0)]}] | Ban:{len(load_bl())}"
                px_s = f"{tr('on')} (:{CFG.get('px_port', 10809)})" if CFG.get("use_px", False) else tr("off")
                g_str = f"Geo:{tr('on') if (CFG.get('geoip', True) or bool(CFG['countries'])) else tr('off')} | IP:{tr('on') if CFG.get('strict_ip', True) else tr('off')}"
                _, t_name = TARGETS.get(CFG.get("target", 1), ("", "Basic"))
                sp_cpu = f"Speed:{tr('on') if CFG['speed'] else tr('off')} | {tr('modes')[CFG['mode']]}"
                b_str, iv = tr("bgs")[CFG.get("bg", 6)], CFG.get("auto_scan_min", 0)
                tm_str = (f"{iv}m (след. ~{max(0, int((NEXT_AUTO_SCAN - time.time()) // 60))}m)" if not SCAN_BUSY else "ИДЁТ СКАН...") if iv > 0 else tr("off")
                if ACTIVE_NAME:
                    up_m = int((time.time() - ACTIVE_START) // 60) if ACTIVE_START > 0 else 0
                    ip_part = f" • {ACTIVE_CC}:{ACTIVE_IP}" if ACTIVE_IP else ""
                    vpn_tag = f" | VPN: {ACTIVE_NAME}{ip_part} • {up_m}m • FO:{FAILOVER_CNT}"
                else: vpn_tag = f" | VPN: OFF (FO:{FAILOVER_CNT})"
                b_lines = list(BANNERS.get(CFG.get("font", 1), list(BANNERS.values())))[-1]
                f_name = first(BANNERS.get(CFG.get("font", 1), ("Block 3D", None)), "Block 3D")
                ms_tag = f"{CFG.get('min_speed', 0.0)}M" if CFG.get("min_speed", 0.0) > 0 else "0"
                mp_tag = f"{CFG.get('max_ping', 0)}ms" if CFG.get("max_ping", 0) > 0 else "∞"
                ts_n = TSTYLE_NAMES.get(CFG.get("tstyle", 1), "Normal")
                lim_c = CFG["limit"]
                l0, l1, l2, l3, l4, l5 = colorize_logo(b_lines, tick, c)
                hdr_lines = [l0, l1, l2, l3, l4, l5, f"{c}{' ' * 14}:: {style_txt(tr('sub'))} ::{RST}", f"{c}{' ' * 12}[ {tr('auth')}{vpn_tag} ]{RST}", f"{c}{'=' * 74}{RST}"]
                if CFG.get("compact", False):
                    body_lines = [f"  {style_txt(tr('m1'))}{RST}{c}{cache_tag}{RST}", f"  {style_txt(tr('m2'))}{RST}", f"  {style_txt(tr('m3'))}{RST}", f"  {style_txt(tr('m4'))}{RST}{c}{repo_tag}{RST}", f"  {style_txt('5. Щит / Страны / Протоколы')}{RST}       {c}[{wl_str} | {c_str} | {p_str}]{RST}", f"  {style_txt('12. Пороги (Лимит / Скорость / Пинг)')}{RST} {c}[L:{lim_c} | >{ms_tag} | <{mp_tag}]{RST}", f"  {style_txt('13. Кастомизация (Цвет / Фон / Шрифт)')}{RST} {c}[{CFG['cname']} | {f_name} | {ts_n} | {b_str}]{RST}", f"  {style_txt('[P] Пресеты | [V] Вид | [O] Оверлей | [W] Трей | 0. Выход')}{RST}"]
                else:
                    body_lines = [f"  {style_txt(tr('m1'))}{RST}{c}{cache_tag}{RST}", f"  {style_txt(tr('m2'))}{RST}", f"  {style_txt(tr('m3'))}{RST}", f"  {style_txt(tr('m4'))}{RST}{c}{repo_tag}{RST}", f"  {style_txt(tr('m5')):<44} {c}[{wl_str}]{RST}", f"  {style_txt(tr('m6')):<44} {c}[{s_src}]{RST}", f"  {style_txt(tr('m7')):<44} {c}[{px_s}]{RST}", f"  {style_txt(tr('m8')):<44} {c}[{c_str} | {p_str}]{RST}", f"  {style_txt(tr('m9')):<44} {c}[{g_str}]{RST}", f"  {style_txt(tr('m10')):<44} {c}[{t_name}]{RST}", f"  {style_txt(tr('m11')):<44} {c}[{sp_cpu}]{RST}", f"  {style_txt(tr('m12')):<44} {c}[L:{lim_c} | >{ms_tag} | <{mp_tag}]{RST}", f"  {style_txt(tr('m13')):<44} {c}[{CFG['cname']} | {f_name} | {ts_n} | {b_str}]{RST}", f"  {style_txt(tr('m14')):<44} {c}[{CFG['lang']} | :{CFG.get('sub_port', 18080)}]{RST}", f"  {style_txt(tr('m15')):<44} {c}[{tm_str}]{RST}", f"  {style_txt('0. Выход  |  [P] Пресеты | [V] Вид | [O] Оверлей | [W] Трей')}{RST}"]
                grid = render_bg(CFG.get("bg", 6), tick, w=min(term_w - 1, 130), h=min(term_h - 1, 28))
                bg_on = CFG.get("bg", 6) != 0
                lines = hdr_lines + body_lines + [render_pulse_bar(tick, 74, c), f"{DIM}{c}{''.join(grid[-2])}{RST}" if bg_on else "", f"{style_txt(tr('ask'))}{RST}{c}{buf}{RST}   "]
                out = list()
                for idx, ln in enumerate(lines):
                    bg_s = f"{DIM}{c}{''.join(grid[idx % len(grid)])}{RST}\033[{idx + 1};1H" if (bg_on and idx < len(lines) - 2) else "\033[K"
                    rp_part = f"\033[{idx + 1};78H{r_panel_cache[idx]}" if idx < len(r_panel_cache) else ""
                    out.append(f"\033[{idx + 1};1H{bg_s}{ln}{rp_part}")
                sys.stdout.write("".join(out))
                sys.stdout.flush()
                tick += 1
            if msvcrt.kbhit():
                ch_in = msvcrt.getwch()
                if ch_in in ("\r", "\n"):
                    force_draw = True
                    ch, buf = ru2en(buf.strip()).upper(), ""; sys.stdout.write("\033[?25h"); os.system("cls" if os.name == "nt" else "clear")
                    if ch == "0": return
                    elif ch == "W": minimize_to_tray()
                    elif ch == "P": apply_preset_ui()
                    elif ch == "V": CFG["compact"] = not CFG.get("compact", False); save_cfg()
                    elif ch == "O":
                        CFG["overlay"] = not CFG.get("overlay", False); save_cfg()
                        if CFG["overlay"]: start_hud_overlay()
                    elif ch == "D": disconnect_vpn(); print("[*] VPN отключен."); time.sleep(0.8)
                    elif ch in ("T1", "T2", "T3", "T4", "T5"):
                        t_idx = int(ch[1:]) - 1
                        rows_q = [ln.strip() for ln in open("best_configs.txt", encoding="utf-8") if ln.strip()] if os.path.exists("best_configs.txt") else list()
                        if t_idx < len(rows_q):
                            b, sc, cc, _, _, _ = parse_row_info(rows_q[t_idx])
                            print(f"{c}[*] Подключение к #{t_idx + 1} {sc}_{cc}...{RST}")
                            print(f"{c}[+] Подключено!{RST}" if connect_vpn(b, f"#{t_idx + 1} {sc}_{cc}") else "\033[91m[!] Ошибка запуска.\033[0m")
                            time.sleep(1.1)
                    elif ch == "1":
                        rem_c = max(0, len(load_cache().get("nodes", list())) - load_cache().get("offset", 0))
                        if rem_c > 0:
                            sc_sel = input(f"  1. Новый полный поиск\n  2. Допроверить кэш ({rem_c})\n> ").strip()
                            if sc_sel in ("1", "2"): run_scan(from_cache=(sc_sel == "2"))
                        else: run_scan(from_cache=False)
                        input(f"\n{tr('back')}")
                    elif ch == "2": run_clipboard_scan(); input(f"\n{tr('back')}")
                    elif ch == "3": manage_servers()
                    elif ch == "4": manage_sources()
                    elif ch == "5": CFG["wl_mode"] = 0 if CFG.get("wl_mode", 0) == 2 else CFG.get("wl_mode", 0) + 1; save_cfg()
                    elif ch == "6":
                        s_sel = input(f"  1. Источники: {tr('srcs')[CFG.get('src', 0)]}\n  2. Язык GH: {tr('gh_l')[CFG.get('gh_lang', 0)]}\n  3. Карантин (24ч)\n  4. Очистить бан-лист\n> ").strip()
                        if s_sel == "1": CFG["src"] = 0 if CFG.get("src", 0) == 3 else CFG.get("src", 0) + 1; save_cfg(); print(f"{c}[*] Свои источники: {CUSTOM_FILE}{RST}"); time.sleep(1.2)
                        elif s_sel == "2": CFG["gh_lang"] = 0 if CFG.get("gh_lang", 0) == 2 else CFG.get("gh_lang", 0) + 1; save_cfg()
                        elif s_sel == "3": CFG["blacklist"] = not CFG.get("blacklist", True); save_cfg()
                        elif s_sel == "4": save_bl({})
                    elif ch == "7":
                        px_s_in = input("  1. Вкл/Выкл прокси v2rayN\n  2. Порт прокси (10809)\n> ").strip()
                        if px_s_in == "1": CFG["use_px"] = not CFG.get("use_px", False); save_cfg()
                        elif px_s_in == "2":
                            p_val = input("Port > ").strip()
                            if p_val.isdigit() and 1 <= int(p_val) <= 65535: CFG["px_port"] = int(p_val); save_cfg()
                    elif ch == "8":
                        cp_sel = input("  1. Фильтр стран (без RU)\n  2. Протокол (vless+trojan, trojan+hy2...)\n> ").strip()
                        if cp_sel == "1":
                            for code, name in COUNTRIES_INFO: print(f"  {c}{code}{RST} - {name}")
                            picked = {x for x in re.findall(r'[A-Z]{2}', ru2en(input("\nDE NL ES FI... (Enter = ALL кроме RU) > ")).upper()) if x not in BLOCKED_COUNTRIES}
                            CFG["countries"] = picked
                            if CFG["countries"]: CFG["geoip"] = True
                            save_cfg()
                        elif cp_sel == "2":
                            print(f"  Доступные: {c}vless{RST}, {c}trojan{RST}, {c}ss{RST}, {c}hy2{RST}, {c}tuic{RST} (напр.: vless+trojan | trojan+hy2, Enter = ВСЕ)")
                            p_parsed = parse_proto_set(ru2en(input("> ").strip()))
                            CFG["proto"] = "+".join(sorted(p_parsed)) if p_parsed else ""; save_cfg()
                    elif ch == "9":
                        g_sel = input("  1. GeoIP\n  2. Strict Anti-DPI (IP)\n> ").strip()
                        if g_sel == "1" and not CFG["countries"]: CFG["geoip"] = not CFG.get("geoip", True); save_cfg()
                        elif g_sel == "2": CFG["strict_ip"] = not CFG.get("strict_ip", True); save_cfg()
                    elif ch == "10": CFG["target"] = 1 if CFG.get("target", 1) == 3 else CFG.get("target", 1) + 1; save_cfg()
                    elif ch == "11":
                        sc_cpu = input("  1. Замер скорости\n  2. ЦП (2x20 -> 4x25 -> 6x25)\n> ").strip()
                        if sc_cpu == "1": CFG["speed"] = not CFG.get("speed", True); save_cfg()
                        elif sc_cpu == "2": CFG["mode"] = 1 if CFG.get("mode", 3) == 3 else CFG.get("mode", 3) + 1; save_cfg()
                    elif ch == "12":
                        r_val = input("Repos (1-250, Enter=skip) > ").strip()
                        c_val = input("Cap [4/5] (100-20000, Enter=skip) > ").strip()
                        l_val = input("Limit (5-1000, Enter=skip) > ").strip()
                        ms_val = input("Min Speed Mbps (напр. 5.0, 0=выкл) > ").strip().replace(",", ".")
                        mp_val = input("Max Ping ms (напр. 1200, 0=выкл) > ").strip()
                        if r_val.isdigit() and 1 <= int(r_val) <= 250: CFG["repos"] = int(r_val)
                        if c_val.isdigit() and 100 <= int(c_val) <= 20000: CFG["batch_cap"] = int(c_val)
                        if l_val.isdigit() and 1 <= int(l_val) <= 1000: CFG["limit"] = int(l_val)
                        try:
                            if ms_val != "" and float(ms_val) >= 0: CFG["min_speed"] = float(ms_val)
                        except Exception: pass
                        if mp_val.isdigit() and int(mp_val) >= 0: CFG["max_ping"] = int(mp_val)
                        save_cfg()
                    elif ch == "13": customize_ui()
                    elif ch == "14":
                        sub_s = input("  1. Язык (RU/EN)  2. Ярлык  3. GitHub Token  4. Порт подписки  5. Скачать ядра\n> ").strip()
                        if sub_s == "1": CFG["lang"] = "EN" if CFG["lang"] == "RU" else "RU"; save_cfg()
                        elif sub_s == "2": make_shortcut(); input(f"\n{tr('back')}")
                        elif sub_s == "3": CFG["token"] = input("Token > ").strip(); save_cfg()
                        elif sub_s == "4":
                            sp_val = input("Port (1024-65535) > ").strip()
                            if sp_val.isdigit() and 1024 <= int(sp_val) <= 65535: CFG["sub_port"] = int(sp_val); save_cfg()
                        elif sub_s == "5": download_cores(True); input(f"\n{tr('back')}")
                    elif ch == "15":
                        t_map = {"0": 0, "1": 30, "2": 60, "3": 180, "4": 360, "5": 720}
                        t_sel = input("  Авто-поиск: 0.Выкл | 1.30м | 2.1ч | 3.3ч | 4.6ч | 5.12ч > ").strip()
                        if t_sel in t_map: CFG["auto_scan_min"] = t_map[t_sel]; NEXT_AUTO_SCAN = (time.time() + CFG["auto_scan_min"] * 60) if CFG["auto_scan_min"] > 0 else 0.0; save_cfg()
                    os.system("cls" if os.name == "nt" else "clear"); sys.stdout.write("\033[?25l")
                elif ch_in == "\b": buf = buf[:-1]; sys.stdout.write(f"\033[{len(lines)};1H{style_txt(tr('ask'))}{RST}{c}{buf}{RST}   "); sys.stdout.flush()
                elif ch_in.isprintable(): buf += ch_in
                time.sleep(0.012)
    finally: disconnect_vpn(); sys.stdout.write("\033[?25h")

threading.Thread(target=failover_loop, daemon=True).start(); threading.Thread(target=auto_heal_loop, daemon=True).start()
try: show_menu()
except KeyboardInterrupt: disconnect_vpn(); sys.stdout.write("\033[?25h")
except Exception: disconnect_vpn(); traceback.print_exc(); input("\nEnter...")

