import base64, ctypes, io, json, msvcrt, os, random, re, socket, subprocess, sys, threading, time, traceback, uuid, winreg, winsound, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import requests

os.system("")
SEARCH_QUERIES_EN = [
    "vless reality subscription",
    "vless trojan free",
    "hysteria2 tuic vless free",
    "shadowsocks vless nodes",
    "xray singbox config"
]
SEARCH_QUERIES_RU = [
    "vless ru",
    "vless reality ru",
    "whitelist vless",
    "vless обход рф",
    "бесплатный впн vless"
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
TCP_WORKERS = 300
SPEED_URL = "https://cloudflare.com"
IPIFY_URL = "https://icanhazip.com"
TIMEOUT = 4.0

GH = "https://" + "a" + "pi" + ".github.com"
RAW = "https://" + "raw" + ".githubusercontent.com"
JSDELIVR = "https://" + "cdn" + ".jsdelivr.net/gh"
STATICALLY = "https://" + "cdn" + ".statically.io/gh"
TG_WEB = "https://" + "t" + ".me/s/"

DEFAULT_TG = ["vless_free", "v2ray_configs_pool", "FreeV2rayVPN", "v2rayng_vpn_free", "Outline_Vpn_Free", "v2ray_free_conf", "PrivateVPNs", "vless_vmess"]
DEFAULT_WEB = [
    f"{JSDELIVR}/kort0881/vpn-vless-configs-russia@main/subscribed/vless.txt",
    f"{JSDELIVR}/FLAT447/v2ray-lists@main/vless.txt",
    f"{JSDELIVR}/jsxta/whitelist-russia@main/whitelist.txt",
    f"{RAW}/rtwo2/FastNodes/main/All_Configs_Sub.txt",
    f"{RAW}/AmirrezaFarnamTaheri/HUNTX/main/All_Configs_Sub.txt",
    f"{RAW}/peasoft/NoMoreWalls/master/list_raw.txt",
    f"{RAW}/Pawdroid/Free-servers/main/sub",
    f"{RAW}/mfuu/v2ray/master/v2ray",
    f"{RAW}/aiboboxx/v2rayfree/main/v2",
    f"{RAW}/freefq/free/master/v2",
    f"{RAW}/Mahdi0024/ProxyCollector/master/sub/proxies.txt",
    f"{RAW}/ermaozi/get_subscribe/main/subscribe/v2ray.txt"
]
RU_BYPASS_DOMAINS = [".ru", ".xn--p1ai", ".su", "yandex.ru", "ya.ru", "vk.com", "vk.ru", "mail.ru", "gosuslugi.ru", "sberbank.ru", "tbank.ru", "ozon.ru", "wildberries.ru", "avito.ru", "kinopoisk.ru"]
CUSTOM_FILE = "custom_sources.txt"
BL_FILE = "netpulse_blacklist.json"
CFG_FILE = "netpulse_config.json"
FAV_FILE = "favorites.txt"
CACHE_FILE = "alive_cache.json"
STATS_FILE = "sources_stats.json"
LOG_FILE = "netpulse_vpn.log"

CFG = {"lang": "RU", "color": "\033[96m", "cname": "Cyan", "countries": set(), "proto": 0, "src": 0, "gh_lang": 0, "wl_mode": 0, "use_px": False, "px_port": 10809, "sub_port": 18080, "tun": False, "failover": True, "blacklist": True, "geoip": True, "strict_ip": True, "ip_provider": 0, "speed": True, "mode": 3, "repos": 40, "batch_cap": 3500, "limit": 40, "token": "", "bg": 1, "target": 1, "xray": r"C:\vpns\v2rayN-windows-64\bin\xray\xray.exe", "singbox": ""}

TARGETS = {
    1: ("https://icanhazip.com", "Basic HTTPS / Базовый IP"),
    2: ("https://youtube.com", "YouTube / Google"),
    3: ("https://discord.com", "Discord / OpenAI")
}

def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f: data = json.load(f)
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
    except Exception:
        return None

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
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("nodes"): return data
        except Exception: pass
    return {"nodes": list(), "offset": 0, "ts": 0}

def save_cache(nodes, offset=0):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"nodes": nodes, "offset": offset, "ts": time.time()}, f)
    except Exception: pass

def load_src_db():
    db = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception: db = {}
    for r in PINNED_REPOS_RU:
        k = f"gh:{r}"
        if k not in db:
            db[k] = {"collected": 0, "working": 0, "prio": True}
    return db

def save_src_db(db):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception: pass

def find_cores():
    x_ok = os.path.exists(CFG.get("xray", ""))
    s_ok = os.path.exists(CFG.get("singbox", ""))
    if x_ok and s_ok: return CFG["xray"], CFG["singbox"]
    roots = [os.getcwd(), os.path.join(os.getcwd(), "cores"), r"C:\vpns", r"C:\Program Files", os.path.expanduser("~")]
    for root in roots:
        if not os.path.exists(root): continue
        for dp, _, fn in os.walk(root):
            if not x_ok and "xray.exe" in fn:
                CFG["xray"] = os.path.join(dp, "xray.exe"); x_ok = True
            if not s_ok and "sing-box.exe" in fn:
                CFG["singbox"] = os.path.join(dp, "sing-box.exe"); s_ok = True
            if x_ok and s_ok: break
            if dp.count(os.sep) - root.count(os.sep) > 3: del _[:]
    save_cfg()
    return CFG.get("xray", ""), CFG.get("singbox", "")

def get_hdr():
    h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NetPulse/5.4"}
    if CFG.get("token"): h["Authorization"] = f"Bearer {CFG['token']}"
    return h

def download_cores(force=False):
    c = CFG["color"]
    core_dir = os.path.abspath("cores")
    os.makedirs(core_dir, exist_ok=True)
    x_bin, s_bin = find_cores()
    tasks = list()
    if force or not x_bin or not os.path.exists(x_bin):
        tasks.append(("Xray-core", "XTLS/Xray-core", "xray-windows-64.zip", "xray.exe", "xray"))
    if force or not s_bin or not os.path.exists(s_bin):
        tasks.append(("sing-box", "SagerNet/sing-box", "windows-amd64.zip", "sing-box.exe", "singbox"))
    if not tasks:
        print(f"{c}[+] Оба ядра (Xray + sing-box) уже установлены!{RST}")
        return True
    for title, repo, kw, exe_name, cfg_key in tasks:
        print(f"\n{c}[*] Загрузка {title} с GitHub ({repo})...{RST}")
        try:
            r = requests.get(f"{GH}/repos/{repo}/releases/latest", headers=get_hdr(), proxies=get_px(), timeout=15)
            r.raise_for_status()
            dl_url = ""
            for a in r.json().get("assets", list()):
                nm = a.get("name", "").lower()
                if kw in nm and nm.endswith(".zip"):
                    dl_url = a.get("browser_download_url", ""); break
            if not dl_url:
                print(f"\033[91m[!] Архив {title} не найден в релизе.\033[0m"); continue
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
                        with zf.open(member) as src_f, open(dst, "wb") as out_f:
                            out_f.write(src_f.read())
                        CFG[cfg_key] = dst; save_cfg()
                        print(f"{c}[+] {title} успешно установлен: {dst}{RST}")
                        break
        except Exception as e:
            print(f"\033[91m[!] Ошибка скачивания {title}: {e}{RST}")
    x_ok, s_ok = find_cores()
    return bool(x_ok and os.path.exists(x_ok))
load_cfg()
find_cores()
COLORS = {
    "1": ("\033[92m", "Green / Изумрудный"), "2": ("\033[96m", "Cyan / Неоновый"),
    "3": ("\033[95m", "Purple / Киберпанк"), "4": ("\033[93m", "Amber / Янтарный"),
    "5": ("\033[97m", "White / Белый"), "6": ("\033[91m", "Red / Красный"),
    "7": ("\033[38;5;39m", "Ice Blue / Ледяной синий"), "8": ("\033[38;5;48m", "Mint / Мятный"),
    "9": ("\033[38;5;208m", "Orange / Оранжевый"), "10": ("\033[38;5;198m", "Hot Pink / Неоновый розовый")
}
COUNTRIES_INFO = [("DE", "Германия / Germany"), ("NL", "Нидерланды / Netherlands"), ("FI", "Финляндия / Finland"), ("SE", "Швеция / Sweden"), ("PL", "Польша / Poland"), ("GB", "Британия / UK"), ("US", "США / USA"), ("TR", "Турция / Turkey"), ("KZ", "Казахстан / Kazakhstan"), ("AE", "ОАЭ / UAE"), ("SG", "Сингапур / Singapore"), ("JP", "Япония / Japan")]
RST, DIM = "\033[0m", "\033[2m"

TXT = {
    "RU": {"sub": "Умный агрегатор и VPN-менеджер v5.4", "auth": "Авторы: Gemini & Glitch", "m1": "1. Запустить поиск / Допроверить кэш", "m2": "2. Проверить буфер обмена (Clipboard Scan)", "m3": "3. Менеджер серверов (VPN / TUN / Трафик-лог)", "m4": "4. Рейтинг репозиториев и Приоритет скана", "m5": "5. Защита от белых списков (CDN + RU-SNI)", "m6": "6. Источники / Язык баз / Карантин", "m7": "7. Прокси v2rayN для парсинга", "m8": "8. Страны и Протокол поиска", "m9": "9. GeoIP / Strict Anti-DPI (Смена IP)", "m10": "10. Цель проверки (Сайт)", "m11": "11. Замер скорости / Нагрузка на ЦП", "m12": "12. Репы / Допуск в [4/5] / Лимит", "m13": "13. Кастомизация (Цвет и Фон)", "m14": "14. Язык / Ярлык / Ядра / Токен / Порт", "m0": "0. Выход", "ask": "Выберите пункт меню > ", "all": "ВСЕ СТРАНЫ", "on": "ВКЛ", "off": "ВЫКЛ", "unit": "узл/с", "wl_m": {0: "АВТО (CDN)", 1: "Приоритет RU-SNI", 2: "Строго RU-SNI"}, "srcs": {0: "ВСЕ (GH+TG+Web)", 1: "Только GH", 2: "Только TG+Web", 3: "GH+Web"}, "gh_l": {0: "RU+EN", 1: "Только RU", 2: "Только EN"}, "protos": {0: "ВСЕ", 1: "VLESS", 2: "Trojan", 3: "SS", 4: "HY2/TUIC"}, "bgs": {1: "Пульс", 2: "Матрица", 3: "Поток", 4: "Звезды", 5: "Радар", 0: "Выкл"}, "modes": {1: "2x20", 2: "4x25", 3: "6x25"}, "s1": "[1/5] Сбор источников (GitHub / CDN / TG / Web)...", "s2": "[2/5] Скачивание и парсинг", "s3": "[3/5] Умный фильтр и TCP-отсев", "s4": "[4/5] Турбо-проверка (Ctrl+C = Стоп)", "s5": "[5/5] Замер скорости скачивания", "done": "Готово! Рабочих серверов:", "url": "Подписки:", "back": "Нажмите Enter для возврата в меню...", "bat_ok": "[+] Ярлык NETPULSE.bat создан на Рабочем столе!", "no_xray": "[!] Ядра не найдены! Скачать автоматически с GitHub? (Y/N) > "},
    "EN": {"sub": "Smart Aggregator & VPN Manager v5.4", "auth": "Authors: Gemini & Glitch", "m1": "1. Start Scan / Resume TCP Cache", "m2": "2. Clipboard Scan (Paste & Test)", "m3": "3. Server Manager (VPN / TUN / Traffic Log)", "m4": "4. Repo Leaderboard & Scan Priority", "m5": "5. Whitelist Shield (CDN + RU-SNI)", "m6": "6. Sources / Repo Lang / Quarantine", "m7": "7. v2rayN Proxy for Scraping", "m8": "8. Countries & Target Protocol", "m9": "9. GeoIP / Strict Anti-DPI (IP Check)", "m10": "10. Validation Target Site", "m11": "11. Speed Test / CPU Load Mode", "m12": "12. Repos / [4/5] Cap / Limit", "m13": "13. Customization (Color & BG)", "m14": "14. Lang / Shortcut / Cores / Token / Port", "m0": "0. Exit", "ask": "Select option > ", "all": "ALL", "on": "ON", "off": "OFF", "unit": "nodes/s", "wl_m": {0: "AUTO (CDN)", 1: "Priority RU-SNI", 2: "Strict RU-SNI"}, "srcs": {0: "ALL (GH+TG+Web)", 1: "GH Only", 2: "TG+Web Only", 3: "GH+Web"}, "gh_l": {0: "RU+EN", 1: "RU Only", 2: "EN Only"}, "protos": {0: "ALL", 1: "VLESS", 2: "Trojan", 3: "SS", 4: "HY2/TUIC"}, "bgs": {1: "Pulse", 2: "Matrix", 3: "Stream", 4: "Stars", 5: "Radar", 0: "Off"}, "modes": {1: "2x20", 2: "4x25", 3: "6x25"}, "s1": "[1/5] Collecting sources (GitHub / CDN / TG / Web)...", "s2": "[2/5] Downloading & parsing", "s3": "[3/5] Smart filter & TCP check", "s4": "[4/5] Turbo batch check (Ctrl+C = Stop)", "s5": "[5/5] Measuring download speed", "done": "Done! Working servers:", "url": "Subscriptions:", "back": "Press Enter to return to menu...", "bat_ok": "[+] Shortcut NETPULSE.bat created on Desktop!", "no_xray": "[!] Cores not found! Download automatically from GitHub? (Y/N) > "}
}
SUB_MAP, SRC_STATS, CHECKED, FOUND_COUNT, STOP_EVENT, LOCK, PROC_FLAGS = {}, {}, 0, 0, threading.Event(), threading.Lock(), 0
ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH, REAL_HOME_IP = None, "", "", "", ""
VPN_LOG, LOG_LOCK = list(), threading.Lock()
first = lambda s, d="": next(iter(s), d) if s else d
tr = lambda k: TXT[CFG["lang"]][k]

def add_log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_LOCK:
        VPN_LOG.append(line)
        if len(VPN_LOG) > 60:
            VPN_LOG.pop(0)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

def load_favs():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return [ln.strip() for ln in f if ln.strip()]
        except Exception: pass
    return list()

def save_favs(favs):
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(favs))
    except Exception: pass

def draw_bar(cur, tot, extra="", t0=None):
    if tot <= 0: return
    ratio = min(1.0, max(0.0, cur / tot))
    pct = ratio * 100.0
    width = 28
    blocks = " ▏▎▍▌▋▊▉█"
    exact = ratio * width
    full = int(exact)
    rem = int((exact - full) * 8)
    if full >= width:
        bar = "█" * width
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
    raw_u = f"{RAW}/{o}/{n}/{b}/{p}"
    jsd_u = f"{JSDELIVR}/{o}/{n}@{b}/{p}"
    stc_u = f"{STATICALLY}/{o}/{n}/{b}/{p}"
    if CFG.get("wl_mode", 0) in (1, 2):
        return [jsd_u, stc_u, raw_u]
    return [raw_u, jsd_u, stc_u]

def get_files(repo):
    o, n, b = repo.get("owner", {}).get("login"), repo.get("name"), repo.get("default_branch")
    tag = f"gh:{o}/{n}"
    urls = list()
    for _ in range(2):
        try:
            r = requests.get(f"{GH}/repos/{o}/{n}/git/trees/{b}", params={"recursive": "1"}, headers=get_hdr(), proxies=get_px(), timeout=15)
            if r.status_code == 200:
                for i in r.json().get("tree", list()):
                    p = i.get("path", "")
                    if i.get("type") == "blob" and (p.endswith((".txt", ".list", ".sub", ".conf", ".yaml", ".yml")) or "." not in p.split("/").pop()):
                        if not any(x in p.lower() for x in ("readme", "license", ".git")):
                            urls.append((tag, make_gh_mirrors(o, n, b, p)))
                break
        except Exception: time.sleep(1)
    return urls

def get_tg_and_web(bl):
    items = list()
    src_mode = CFG.get("src", 0)
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
                    elif "/" in s and not s.startswith("@"):
                        pass
                    elif src_mode in (0, 2): channels.append(s.lstrip("@"))
        except Exception: pass
    for u in dict.fromkeys(web_urls):
        if not CFG.get("blacklist", True) or u not in bl:
            items.append((u, [u]))
    for ch in dict.fromkeys(channels):
        tag = f"tg:{ch}"
        if not CFG.get("blacklist", True) or tag not in bl:
            items.append((tag, [f"{TG_WEB}{ch}"]))
    return items

def parse_text(txt):
    clean = re.sub(r'<[^>]+>', '\n', txt)
    pat = re.compile(r'(?:vless|trojan|ss|hy2|hysteria2|tuic)://[^\s"\'<>]+')
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
        sni = first(q.get("sni"), "").lower().strip()
        host = first(q.get("host"), "").lower().strip()
        for target in (sni, host):
            if target and any(target == d or target.endswith("." + d) for d in WHITELIST_SNI):
                return True
    except Exception: pass
    return False

def smart_prefilter(raw_list):
    uniq, subnets = {}, {}
    bad_hosts = ("127.0.0.1", "0.0.0.0", "localhost", "example.com", "://cloudflare.com")
    pr = CFG.get("proto", 0)
    wl_mode = CFG.get("wl_mode", 0)
    for src, uri in raw_list:
        try:
            sc, h, pt = get_hp(uri)
            if not h or not pt or not (1 <= pt <= 65535) or h.lower() in bad_hosts: continue
            if pr == 1 and sc != "vless": continue
            if pr == 2 and sc != "trojan": continue
            if pr == 3 and sc != "ss": continue
            if pr == 4 and sc not in ("hy2", "tuic"): continue
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
        if sc in ("hy2", "tuic"):
            return (src, uri) if CFG.get("singbox") and os.path.exists(CFG.get("singbox", "")) else None
        with socket.create_connection((h, pt), timeout=0.9): return (src, uri)
    except Exception: return None
VALID_SS_METHODS = {"aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305", "chacha20-poly1305", "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm", "2022-blake3-chacha20-poly1305", "none", "plain"}

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val).strip())
        return True
    except Exception:
        return False

def is_valid_reality(pbk, sid):
    if not pbk or not (42 <= len(pbk) <= 44): return False
    try:
        raw_k = base64.urlsafe_b64decode(pbk + "=" * (-len(pbk) % 4))
        if len(raw_k) != 32: return False
    except Exception:
        return False
    if sid and (len(sid) > 16 or len(sid) % 2 != 0 or not re.fullmatch(r'[0-9a-fA-F]+', sid)):
        return False
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
            pbk, sid = first(q.get("pbk"), "").strip(), first(q.get("sid"), "").strip()
            sni = first(q.get("sni"), "").strip()
            if not sni or not is_valid_reality(pbk, sid): return None
            out["streamSettings"]["realitySettings"] = {"serverName": sni, "fingerprint": first(q.get("fp"), "chrome") or "chrome", "publicKey": pbk, "password": pbk, "shortId": sid, "spiderX": unquote(first(q.get("spx"), "/"))}
        elif sec == "tls":
            out["streamSettings"]["tlsSettings"] = {"serverName": first(q.get("sni"), p.hostname), "allowInsecure": first(q.get("allowInsecure"), "0") in ("1", "true")}
        if net == "ws": out["streamSettings"]["wsSettings"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
        elif net == "grpc": out["streamSettings"]["grpcSettings"] = {"serviceName": first(q.get("serviceName"), "")}
        return out
    except Exception:
        return None

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
                pbk, sid = first(q.get("pbk"), "").strip(), first(q.get("sid"), "").strip()
                sni = first(q.get("sni"), "").strip()
                if not sni or not is_valid_reality(pbk, sid): return None
                tls["utls"] = {"enabled": True, "fingerprint": first(q.get("fp"), "chrome") or "chrome"}
                tls["reality"] = {"enabled": True, "public_key": pbk, "short_id": sid}
            out["tls"] = tls
        if net == "ws": out["transport"] = {"type": "ws", "path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
        elif net == "grpc": out["transport"] = {"type": "grpc", "service_name": first(q.get("serviceName"), "")}
        return out
    except Exception:
        return None
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
        if sec == "reality":
            px["client-fingerprint"] = first(q.get("fp"), "chrome")
            px["reality-opts"] = {"public-key": first(q.get("pbk"), ""), "short-id": first(q.get("sid"), "")}
    elif sc == "trojan":
        px = {"name": name, "type": "trojan", "server": p.hostname, "port": int(p.port), "password": unquote(p.username or ""), "network": net, "udp": True, "sni": first(q.get("sni"), p.hostname)}
    else: return None
    if net == "ws": px["ws-opts"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
    elif net == "grpc": px["grpc-opts"] = {"grpc-service-name": first(q.get("serviceName"), "")}
    return px

def build_clash_sub(uris):
    proxies, names = list(), list()
    for i, u in enumerate(uris, 1):
        tag = u.split("#").pop() if "#" in u else "NODE"
        nm = f"{i:02d}_{tag}"
        px = build_clash_proxy(u, nm)
        if px: proxies.append(px); names.append(nm)
    if not proxies: return ""
    cfg = {
        "mixed-port": 7890, "allow-lan": False, "mode": "rule", "log-level": "info",
        "proxies": proxies,
        "proxy-groups": [
            {"name": "NETPULSE-SELECT", "type": "select", "proxies": ["AUTO-BEST"] + names},
            {"name": "AUTO-BEST", "type": "url-test", "proxies": names, "url": "http://gstatic.com", "interval": 300}
        ],
        "rules": [
            "DOMAIN-SUFFIX,ru,DIRECT", "DOMAIN-SUFFIX,xn--p1ai,DIRECT",
            "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve", "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
            "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve", "MATCH,NETPULSE-SELECT"
        ]
    }
    return json.dumps(cfg, ensure_ascii=False, indent=2)

def build_sb_sub(uris):
    outs, tags = list(), list()
    for i, u in enumerate(uris, 1):
        tg = f"{i:02d}_{u.split('#').pop() if '#' in u else 'NODE'}"
        o = build_sb_out(u, tg)
        if o: outs.append(o); tags.append(tg)
    if not outs: return ""
    cfg = {
        "log": {"level": "info"},
        "dns": {
            "servers": [
                {"tag": "remote", "type": "https", "server": "1.1.1.1", "detour": "proxy"},
                {"tag": "local", "type": "local"}
            ],
            "rules": [{"domain_suffix": RU_BYPASS_DOMAINS, "server": "local"}]
        },
        "inbounds": [{"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 2080}],
        "outbounds": [{"type": "selector", "tag": "proxy", "outbounds": ["auto"] + tags}, {"type": "urltest", "tag": "auto", "outbounds": tags, "url": "http://gstatic.com", "interval": "5m"}] + outs + [{"type": "direct", "tag": "direct"}],
        "route": {
            "rules": [
                {"action": "sniff"},
                {"protocol": "dns", "action": "hijack-dns"},
                {"domain_suffix": RU_BYPASS_DOMAINS, "outbound": "direct"},
                {"ip_is_private": True, "outbound": "direct"}
            ],
            "auto_detect_interface": True,
            "default_domain_resolver": "local"
        }
    }
    return json.dumps(cfg, ensure_ascii=False, indent=2)
def wait_port(port, tries=35):
    for _ in range(tries):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.05): return True
        except Exception: time.sleep(0.02)
    return False

def get_free_ports(n):
    socks, ports = list(), list()
    for _ in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        _, pt = s.getsockname()
        ports.append(pt)
        socks.append(s)
    for s in socks: s.close()
    return ports

def lookup_ip_cc(ip, px=None):
    if not ip: return "UN"
    sess = requests.Session(); sess.trust_env = False
    checks = [
        (f"http://ip-api.com{ip}?fields=countryCode", None),
        (f"https://country.is{ip}", "country"),
        (f"https://ipwho.is{ip}", "country_code")
    ]
    for url, key in checks:
        try:
            r = sess.get(url, proxies=px, timeout=3.0)
            if r.status_code == 200:
                code = (r.json().get(key, "") if key else r.text).strip().upper()
                if len(code) == 2 and code.isalpha(): return code
        except Exception: pass
    return "UN"

def fetch_trace_info(px=None, tout=TIMEOUT, need_cc=True):
    try:
        sess = requests.Session(); sess.trust_env = False
        t0 = time.time()
        res = sess.get(IPIFY_URL, proxies=px, timeout=tout)
        ms = int((time.time() - t0) * 1000)
        ip = res.text.strip()
        if res.status_code == 200 and 7 <= len(ip) <= 45 and "<" not in ip and ("." in ip or ":" in ip):
            cc = lookup_ip_cc(ip, px) if need_cc else "OK"
            return cc, ip, ms
        return "UN", "", None
    except Exception: return "UN", "", None

def probe_local_port(port, speed_mode=False, cc_mode=False):
    try:
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        if cc_mode:
            cc, _, _ = fetch_trace_info(px, TIMEOUT, True)
            return cc
        sess = requests.Session(); sess.trust_env = False
        t0 = time.time()
        if not speed_mode:
            pair = TARGETS.get(CFG.get("target", 1), ("https://icanhazip.com", ""))
            t_url = first(pair, "https://icanhazip.com")
            res = sess.get(t_url, proxies=px, timeout=TIMEOUT)
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
        clean_uri = first(uri.split("#"), uri)
        sc, _, _ = get_hp(clean_uri)
        port = first(get_free_ports(1), 0)
        if sc in ("hy2", "tuic"):
            sb_bin = CFG.get("singbox", "")
            out = build_sb_out(clean_uri, "proxy")
            if not sb_bin or not os.path.exists(sb_bin) or not out: return "UN" if cc_mode else None
            cfg = {"log": {"level": "panic"}, "inbounds": [{"type": "http", "listen": "127.0.0.1", "listen_port": port}], "outbounds": [out]}
            tmp_cfg = os.path.abspath(f"tmp_sb_{port}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump(cfg, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            out = build_out(clean_uri, "proxy")
            if not out: return "UN" if cc_mode else None
            cfg = {"log": {"loglevel": "none"}, "dns": {"servers": ["localhost"]}, "inbounds": [{"port": port, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}], "outbounds": [out]}
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps(cfg).encode("utf-8")); proc.stdin.close()
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
def run_batch_group(items, is_sb=False):
    if not items: return list()
    ports = get_free_ports(len(items))
    inbs, outs, rules, valid_map = list(), list(), list(), list()
    for idx, ((src, uri), pt) in enumerate(zip(items, ports)):
        tg = f"p_{idx}"
        out = build_sb_out(uri, tg) if is_sb else build_out(uri, tg)
        if not out: continue
        if is_sb:
            inbs.append({"type": "http", "tag": f"in_{idx}", "listen": "127.0.0.1", "listen_port": pt})
            rules.append({"inbound": [f"in_{idx}"], "outbound": tg})
        else:
            inbs.append({"tag": f"in_{idx}", "port": pt, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}})
            rules.append({"type": "field", "inboundTag": [f"in_{idx}"], "outboundTag": tg})
        outs.append(out)
        valid_map.append((src, uri, pt))
    if not valid_map: return list()
    proc, tmp_cfg = None, ""
    found_batch = list()
    try:
        _, _, first_pt = first(valid_map)
        _, _, last_pt = valid_map[-1]
        if is_sb:
            sb_bin = CFG.get("singbox", "")
            if not sb_bin or not os.path.exists(sb_bin): return list()
            cfg = {"log": {"level": "panic"}, "inbounds": inbs, "outbounds": outs, "route": {"rules": rules}}
            tmp_cfg = os.path.abspath(f"tmp_batch_{first_pt}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump(cfg, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            cfg = {"log": {"loglevel": "none"}, "dns": {"servers": ["localhost"]}, "inbounds": inbs, "outbounds": outs, "routing": {"domainStrategy": "AsIs", "rules": rules}}
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps(cfg).encode("utf-8")); proc.stdin.close()
        if not wait_port(last_pt, 50): return list()
        def test_slot(slot):
            if STOP_EVENT.is_set(): return None
            src, uri, pt = slot
            strict = CFG.get("strict_ip", True) and bool(REAL_HOME_IP)
            need_geo = bool(CFG["countries"]) or CFG.get("geoip", True)
            need_trace = need_geo or strict
            cc = "FAST"
            if need_trace and CFG.get("target", 1) == 1:
                px = {"http": f"http://127.0.0.1:{pt}", "https": f"http://127.0.0.1:{pt}"}
                tr_cc, tr_ip, ms = fetch_trace_info(px, TIMEOUT, need_geo)
                if ms is None: return None
                if strict and (not tr_ip or tr_ip == REAL_HOME_IP): return None
                if CFG["countries"] and tr_cc not in CFG["countries"]: return None
                if need_geo: cc = tr_cc
            else:
                ms = probe_local_port(pt, False, False)
                if ms is None: return None
                if need_trace:
                    px = {"http": f"http://127.0.0.1:{pt}", "https": f"http://127.0.0.1:{pt}"}
                    tr_cc, tr_ip, _ = fetch_trace_info(px, TIMEOUT, need_geo)
                    if strict and (not tr_ip or tr_ip == REAL_HOME_IP): return None
                    if CFG["countries"] and tr_cc not in CFG["countries"]: return None
                    if need_geo: cc = tr_cc
            sc, _, _ = get_hp(uri)
            wl_tag = "_WL" if is_whitelist_sni(uri) else ""
            clean = f"{first(uri.split('#'), uri)}#{sc.upper()}_{cc}{wl_tag}_{ms}ms"
            return (src, ms, cc, clean)
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
def pipe_core_logs(proc):
    try:
        for raw_ln in iter(proc.stdout.readline, b""):
            if not raw_ln: break
            ln = raw_ln.decode("utf-8", errors="ignore").strip()
            low = ln.lower()
            if "accepted " in ln:
                part = ln.split("accepted ", 1).pop()
                add_log(part[:72])
            elif "connection to " in low:
                idx = low.find("connection to ")
                add_log(ln[idx:][:72])
            elif any(x in low for x in ("fatal", "failed", "error", "bind:", "panic")):
                add_log(f"Core: {ln[-68:]}")
    except Exception:
        pass

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
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    if ACTIVE_NAME:
        add_log(f"Отключено: {ACTIVE_NAME}")
    if ACTIVE_PROC:
        try: ACTIVE_PROC.kill()
        except Exception: pass
        ACTIVE_PROC = None
    if TUN_CFG_PATH and os.path.exists(TUN_CFG_PATH):
        try: os.remove(TUN_CFG_PATH)
        except Exception: pass
    TUN_CFG_PATH, ACTIVE_NAME, ACTIVE_URI = "", "", ""
    set_win_proxy(False)

def pick_bind_port(pref_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", pref_port))
            return pref_port
    except Exception:
        alt = first(get_free_ports(1), pref_port + 1)
        add_log(f"Порт :{pref_port} занят (v2rayN?), взят :{alt}")
        return alt

def connect_vpn(uri, label):
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    disconnect_vpn()
    clean_uri = first(uri.split("#"), uri)
    sc, _, _ = get_hp(clean_uri)
    xray_bin, sb_bin = find_cores()
    use_sb = CFG.get("tun", False) or sc in ("hy2", "tuic")
    if use_sb:
        if CFG.get("tun", False) and not is_admin():
            add_log("Ошибка: для TUN нужны права Администратора")
            return False
        if not sb_bin or not os.path.exists(sb_bin):
            add_log("Ошибка: не найден sing-box.exe")
            return False
        sb_out = build_sb_out(clean_uri, "proxy")
        if not sb_out:
            add_log("Ошибка sing-box: невалидный формат ссылки")
            return False
        port = pick_bind_port(CFG.get("px_port", 10809))
        inb = [{"type": "tun", "interface_name": "NetPulseTUN", "address": ["172.19.0.1/30"], "mtu": 1400, "auto_route": True, "strict_route": True, "stack": "system"}] if CFG.get("tun", False) else [{"type": "http", "listen": "127.0.0.1", "listen_port": port}]
        sb_cfg = {
            "log": {"level": "info", "timestamp": False},
            "dns": {
                "servers": [
                    {"tag": "remote", "type": "https", "server": "1.1.1.1", "detour": "proxy"},
                    {"tag": "local", "type": "local"}
                ],
                "rules": [{"domain_suffix": RU_BYPASS_DOMAINS, "server": "local"}]
            },
            "inbounds": inb,
            "outbounds": [sb_out, {"type": "direct", "tag": "direct"}],
            "route": {
                "rules": [
                    {"action": "sniff"},
                    {"protocol": "dns", "action": "hijack-dns"},
                    {"domain_suffix": RU_BYPASS_DOMAINS, "outbound": "direct"},
                    {"ip_is_private": True, "outbound": "direct"}
                ],
                "auto_detect_interface": True,
                "default_domain_resolver": "local"
            }
        }
        TUN_CFG_PATH = os.path.abspath("netpulse_sb_active.json")
        with open(TUN_CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(sb_cfg, f, indent=2)
        try:
            ACTIVE_PROC = subprocess.Popen([sb_bin, "run", "-c", TUN_CFG_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            threading.Thread(target=pipe_core_logs, args=(ACTIVE_PROC,), daemon=True).start()
            time.sleep(1.5)
            if ACTIVE_PROC.poll() is None:
                if not CFG.get("tun", False):
                    set_win_proxy(True, port)
                ACTIVE_NAME = f"{label} ({'TUN-Split' if CFG.get('tun', False) else f'SB:{port}'})"
                ACTIVE_URI = clean_uri
                add_log(f"Подключено: {ACTIVE_NAME}")
                return True
        except Exception as e:
            add_log(f"Сбой sing-box: {str(e)[:60]}")
        disconnect_vpn()
        return False
    if not xray_bin or not os.path.exists(xray_bin):
        add_log("Ошибка Xray: не найден xray.exe")
        return False
    out = build_out(clean_uri, "proxy")
    if not out:
        add_log("Ошибка Xray: невалидный формат ссылки")
        return False
    port = pick_bind_port(CFG.get("px_port", 10809))
    cfg = {"log": {"loglevel": "info"}, "dns": {"servers": ["localhost"]}, "inbounds": [{"tag": "http", "port": port, "listen": "127.0.0.1", "protocol": "http", "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}], "outbounds": [out]}
    TUN_CFG_PATH = os.path.abspath("netpulse_xray_active.json")
    with open(TUN_CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    try:
        ACTIVE_PROC = subprocess.Popen([xray_bin, "run", "-c", TUN_CFG_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        threading.Thread(target=pipe_core_logs, args=(ACTIVE_PROC,), daemon=True).start()
        if wait_port(port, 100):
            set_win_proxy(True, port)
            ACTIVE_NAME, ACTIVE_URI = f"{label} (Proxy:{port})", clean_uri
            add_log(f"Подключено: {ACTIVE_NAME}")
            return True
        add_log(f"Ошибка Xray: таймаут порта :{port}")
    except Exception as e:
        add_log(f"Сбой запуска Xray: {str(e)[:60]}")
    disconnect_vpn()
    return False
def failover_loop():
    fails = 0
    while True:
        time.sleep(15)
        if not ACTIVE_PROC or not ACTIVE_URI or not CFG.get("failover", True):
            fails = 0; continue
        ok = False
        try:
            if ACTIVE_PROC.poll() is None:
                sess = requests.Session(); sess.trust_env = False
                px = None
                if "(Proxy:" in ACTIVE_NAME or "(SB:" in ACTIVE_NAME:
                    p_str = ACTIVE_NAME.split(":").pop().rstrip(")")
                    if p_str.isdigit():
                        px = {"http": f"http://127.0.0.1:{p_str}", "https": f"http://127.0.0.1:{p_str}"}
                r = sess.get("https://icanhazip.com", proxies=px, timeout=4)
                ok = r.status_code in (200, 204)
        except Exception: ok = False
        fails = 0 if ok else fails + 1
        if fails >= 2 and os.path.exists("best_configs.txt"):
            fails = 0
            dead_uri = ACTIVE_URI
            old_lbl = ACTIVE_NAME
            add_log(f"Failover: узел {old_lbl} перестал отвечать, ищу замену...")
            try:
                with open("best_configs.txt", "r", encoding="utf-8") as f:
                    rows = [ln.strip() for ln in f if ln.strip()]
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
    base = first(parts, "")
    tag = parts.pop() if len(parts) > 1 else ""
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
    src_t = input("> ").strip()
    raw_txt = ""
    if src_t == "1":
        try: raw_txt = subprocess.check_output(["powershell", "-command", "Get-Clipboard"], text=True, encoding="utf-8", errors="ignore")
        except Exception: pass
    elif src_t == "2":
        fp = input("Путь к файлу > ").strip().strip('"')
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8", errors="ignore") as f: raw_txt = f.read()
    found = parse_text(raw_txt)
    if not found:
        print("\033[91m[!] Ссылки не найдены.\033[0m"); time.sleep(1.2); return rows
    existing = {first(r.split("#"), r) for r in rows}
    added = 0
    for u in found:
        base = first(u.split("#"), u)
        if base in existing: continue
        sc, _, _ = get_hp(base)
        print(f"  Проверка {sc.upper()}...")
        ms = run_single_test(base, False, False)
        if ms is not None:
            cc = run_single_test(base, False, True) if CFG.get("geoip", True) else "IMP"
            rows.insert(0, f"{base}#{sc.upper()}_{cc}_{ms}ms")
            existing.add(base); added += 1
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
    add_log(f"Импортировано вручную: {added} серверов")
    print(f"{c}[+] Импортировано рабочих серверов: {added}{RST}"); time.sleep(1.4)
    return rows

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
    c = CFG["color"]
    page = 0
    per_page = 25
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        db = load_src_db()
        items = sorted(db.items(), key=lambda x: (x.get("working", 0), x.get("collected", 0)), reverse=True)
        tot_p = max(1, (len(items) + per_page - 1) // per_page)
        page = max(0, min(page, tot_p - 1))
        chunk = items[page * per_page:(page + 1) * per_page]
        prio_cnt = sum(1 for _, v in items if v.get("prio", False))
        print(f"{c}{'=' * 74}")
        print(f"  REPO LEADERBOARD & PRIORITY | Всего баз: {len(items)} | Приоритетных ★: {prio_cnt} | Стр. {page + 1}/{tot_p}")
        print(f"{'=' * 74}{RST}")
        if not items:
            print("  Статистика пока пуста. Запустите поиск (пункт 1)!")
        else:
            print(f"  {'#':<4} {'PRIO':<6} {'WORK':<7} {'TOTAL':<9} {'SOURCE (REPO / TG / WEB)'}")
            print(f"  {'-' * 68}")
            for idx, (src, st) in enumerate(chunk, page * per_page + 1):
                star = f"{c}★ ДА{RST}" if st.get("prio", False) else "  -"
                wk = st.get("working", 0)
                col = st.get("collected", 0)
                disp = src[3:] if src.startswith("gh:") else (src.split("/").pop() if src.startswith("http") else src)
                print(f"  {c}{idx:<4}{RST} {star:<14} {wk:<7} {col:<9} {disp[:40]}")
        print(f"\n{c}Команды / Commands:{RST}")
        print("  [Номера через пробел] - Вкл/Выкл ★ ПРИОРИТЕТ (напр.: 1 2 5)")
        print("  [N] - След. страница  [P] - Пред. страница  [C] - Сбросить статистику  [Enter] - Меню")
        cmd = input("\n> ").strip().upper()
        if not cmd: break
        elif cmd == "N": page += 1
        elif cmd == "P": page -= 1
        elif cmd == "C":
            save_src_db({})
        else:
            nums = [int(x) for x in re.findall(r'\d+', cmd)]
            if nums:
                for n in nums:
                    if 1 <= n <= len(items):
                        k = items[n - 1]
                        db[k]["prio"] = not db[k].get("prio", False)
                save_src_db(db)

def manage_servers():
    c = CFG["color"]
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        rows = list()
        if os.path.exists("best_configs.txt"):
            with open("best_configs.txt", "r", encoding="utf-8") as f:
                rows = [ln.strip() for ln in f if ln.strip()]
        favs = load_favs()
        fav_bases = {first(x.split("#"), x) for x in favs}
        t_mode = f"TUN-Split (Admin: {'OK' if is_admin() else 'NO'})" if CFG.get("tun", False) else f"Proxy (:{CFG.get('px_port', 10809)})"
        fo_st = tr("on") if CFG.get("failover", True) else tr("off")
        print(f"{c}{'=' * 74}")
        print(f"  SERVER MANAGER | {t_mode} | Failover: {fo_st} | Favs: {len(favs)} | VPN: {ACTIVE_NAME if ACTIVE_NAME else 'OFF'}")
        print(f"{'=' * 74}{RST}")
        if not rows:
            print("  Список пуст / List is empty. Запустите поиск (пункт 1) или буфер обмена (пункт 2).")
        else:
            print(f"  {'#':<4} {'PROTO':<8} {'CC':<8} {'PING':<9} {'SPEED':<11} {'HOST'}")
            print(f"  {'-' * 68}")
            for i, ln in enumerate(rows, 1):
                base, sc, cc, ms, spd, _ = parse_row_info(ln)
                _, h, _ = get_hp(base)
                star = "★ " if base in fav_bases else ""
                mark = " *" if ACTIVE_NAME and f"#{i} " in ACTIVE_NAME else ""
                print(f"  {c}{i:<4}{RST} {sc:<8} {cc:<8} {ms:<9} {spd:<11} {c}{star}{RST}{str(h)[:24]}{c}{mark}{RST}")
        print(f"\n{c}Журнал трафика и событий / Live Traffic Log (последние 8):{RST}")
        with LOG_LOCK:
            snap = list(VPN_LOG[-8:])
        if not snap:
            print(f"  {DIM}(пока пусто / empty — нажмите [R] для обновления){RST}")
        else:
            for lg in snap:
                print(f"  {DIM}{lg}{RST}")
        print(f"\n{c}Команды / Commands:{RST}")
        print("  [Номер] - Выбрать сервер (VPN / Тест / Избранное ★ / Копировать / Удалить)")
        print("  [T]     - Режим VPN: Proxy <-> TUN-Split  [F] - Вкл/Выкл Auto-Failover")
        print("  [I]     - Импорт ссылок / Base64          [E] - Экспорт списка / Base64")
        print("  [A]     - Перепроверить и очистить        [R] - Обновить лог трафика")
        print("  [L]     - Полный лог / Очистить           [D] - Отключить VPN   [Enter] - Меню")
        cmd = input("\n> ").strip().upper()
        if not cmd: break
        elif cmd == "R": continue
        elif cmd == "F":
            CFG["failover"] = not CFG.get("failover", True); save_cfg()
            add_log(f"Auto-Failover: {'ВКЛ' if CFG['failover'] else 'ВЫКЛ'}")
        elif cmd == "I": rows = import_nodes_ui(rows)
        elif cmd == "E": export_nodes_ui(rows)
        elif cmd == "L":
            print(f"\n{c}Журнал ({LOG_FILE}):{RST}\n  1. Открыть полный лог в Блокноте\n  2. Очистить журнал")
            l_act = input("> ").strip()
            if l_act == "1" and os.path.exists(LOG_FILE):
                try: os.startfile(LOG_FILE)
                except Exception: pass
            elif l_act == "2":
                with LOG_LOCK: VPN_LOG.clear()
                try:
                    with open(LOG_FILE, "w", encoding="utf-8") as f: f.write("")
                except Exception: pass
        elif cmd == "T":
            CFG["tun"] = not CFG.get("tun", False); save_cfg()
            add_log(f"Режим VPN изменён на {'TUN-Split' if CFG['tun'] else 'Proxy'}")
            if CFG["tun"] and not is_admin():
                print(f"\n{c}[!] Для TUN-режима нужны права Администратора. Перезапустить от Админа? (Y/N){RST}")
                if input("> ").strip().upper() == "Y":
                    disconnect_vpn()
                    args = " ".join(f'"{a}"' for a in (sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv))
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
                    sys.exit(0)
        elif cmd == "D":
            disconnect_vpn(); print("[*] VPN отключен."); time.sleep(0.8)
        elif cmd == "A" and rows:
            new_rows, dead_cnt = list(), 0
            for idx, ln in enumerate(rows, 1):
                base, sc, _, _, _, _ = parse_row_info(ln)
                print(f"  [{idx}/{len(rows)}] Проверка {sc}...")
                ms = run_single_test(base, False, False)
                if ms is not None:
                    cc = run_single_test(base, False, True)
                    spd = run_single_test(base, True, False)
                    new_rows.append(f"{base}#{sc}_{cc}_{ms}ms_{spd}Mbps")
                elif base in fav_bases:
                    new_rows.append(ln)
                else:
                    dead_cnt += 1
            with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(new_rows))
            add_log(f"Массовая проверка: живых {len(new_rows)}, удалено мёртвых {dead_cnt}")
            print(f"\n{c}[+] Очистка завершена! Живых: {len(new_rows)} | Удалено мёртвых: {dead_cnt}{RST}")
            time.sleep(1.5)
        elif cmd.isdigit() and 1 <= int(cmd) <= len(rows):
            idx = int(cmd) - 1
            base, sc, cc, ms, spd, tag = parse_row_info(rows[idx])
            is_fav = base in fav_bases
            print(f"\n{c}Сервер #{idx + 1}: {sc} | {cc} | {ms} | {spd}{RST}")
            print(f"  1. Подключиться (Включить VPN)\n  2. Пропинговать и замерить скорость + страну\n  3. Скопировать ссылку в буфер обмена\n  4. Удалить из списка\n  5. {'Убрать из Избранного' if is_fav else 'Добавить в Избранное ★'}")
            act = input("> ").strip()
            if act == "1":
                ok = connect_vpn(base, f"#{idx + 1} {sc}_{cc}")
                if ok: print(f"{c}[+] Подключено! Режим: {ACTIVE_NAME}{RST}")
                else: print("\033[91m[!] Ошибка запуска (см. причину в Журнале трафика выше).\033[0m")
                time.sleep(1.4)
            elif act == "2":
                print("  Тестирую пинг, страну и скорость...")
                nms = run_single_test(base, False, False)
                if nms is not None:
                    ncc = run_single_test(base, False, True)
                    nspd = run_single_test(base, True, False)
                    rows[idx] = f"{base}#{sc}_{ncc}_{nms}ms_{nspd}Mbps"
                    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
                    add_log(f"Тест #{idx + 1}: {ncc} | {nms}ms | {nspd}Mbps")
                    print(f"  {c}[+] Результат: {ncc} | {nms}ms | {nspd}Mbps{RST}")
                else: print("  \033[91m[!] Сервер не отвечает.\033[0m")
                time.sleep(1.3)
            elif act == "3":
                subprocess.run("clip", input=rows[idx].encode("utf-8"), check=False)
                print("  [+] Скопировано в буфер обмена!"); time.sleep(0.8)
            elif act == "4":
                rows.pop(idx)
                with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
                add_log(f"Удалён узел #{idx + 1} ({sc}_{cc})")
            elif act == "5":
                if is_fav: favs = [x for x in favs if first(x.split("#"), x) != base]
                else: favs.append(rows[idx])
                save_favs(favs)
                add_log(f"Избранное: {'убран' if is_fav else 'добавлен'} #{idx + 1}")
                print(f"  {c}[+] Избранное обновлено!{RST}"); time.sleep(0.8)
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
            ct = "application/json; charset=utf-8" if key.startswith(("clash", "sb")) else "text/plain; charset=utf-8"
            self.send_header("Content-type", ct); self.end_headers()
            self.wfile.write(SUB_MAP[key].encode("utf-8"))
        else: self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

def make_shortcut():
    desk = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desk): desk = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    bat_path = os.path.join(desk, "NETPULSE.bat")
    work_dir = os.path.dirname(os.path.abspath(first(sys.argv, "netpulse.py")))
    script_name = os.path.basename(first(sys.argv, "netpulse.py"))
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(f'@echo off\nchcp 65001 >nul\ncd /d "{work_dir}"\n"{sys.executable}" "{script_name}"\n')
    c_col, ok_txt = CFG["color"], tr("bat_ok")
    print(f"\n{c_col}{ok_txt}{RST}")

def finalize_results(work, all_sources, bl, append_existing=False, run_collected=None):
    global SUB_MAP
    c_col = CFG["color"]
    db = load_src_db()
    if run_collected:
        for s, cnt in run_collected.items():
            ent = db.setdefault(s, {"collected": 0, "working": 0, "prio": False})
            ent["collected"] = ent.get("collected", 0) + cnt
    for s, wk_cnt in SRC_STATS.items():
        if wk_cnt > 0:
            ent = db.setdefault(s, {"collected": 0, "working": 0, "prio": False})
            ent["working"] = ent.get("working", 0) + wk_cnt
    save_src_db(db)
    strict_filter = bool(CFG["countries"]) or CFG.get("proto", 0) != 0 or CFG.get("wl_mode", 0) == 2
    if CFG.get("blacklist", True) and all_sources and not STOP_EVENT.is_set() and not strict_filter:
        dead_cnt = 0
        for s in all_sources:
            if SRC_STATS.get(s, -1) == 0 and db.get(s, {}).get("working", 0) == 0:
                bl[s] = time.time() + 86400; dead_cnt += 1
        save_bl(bl)
        if dead_cnt: print(f"{DIM}{c_col}[*] Quarantine (24h): {dead_cnt} empty sources{RST}")
    by_cc = {}
    if CFG["speed"] and work:
        s5_lbl = tr("s5")
        print(f"\n{c_col}{s5_lbl} ({len(work)})...{RST}")
        scored, t_sp = list(), time.time()
        try:
            for idx, (ms, cc, cfg) in enumerate(work, 1):
                mbps = run_single_test(cfg, True, False)
                tag = f"{cfg}_{mbps}Mbps"
                scored.append((mbps, cc, tag))
                nm_part = tag.split("#").pop()
                sys.stdout.write(f"\r\033[K  {c_col}-> {nm_part}{RST}\n")
                draw_bar(idx, len(work), "", t_sp)
        except KeyboardInterrupt:
            print(f"\n{c_col}[!] Замер скорости прерван, сохраняю уже проверенные...{RST}")
            for ms, cc, cfg in work[len(scored):]:
                scored.append((0.0, cc, cfg))
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
            with open("best_configs.txt", "r", encoding="utf-8") as f:
                old_rows = [ln.strip() for ln in f if ln.strip()]
            new_bases = {first(x.split("#"), x) for x in fin}
            fin = fin + [x for x in old_rows if first(x.split("#"), x) not in new_bases]
        except Exception: pass
    favs = load_favs()
    if favs:
        fav_bases = {first(x.split("#"), x) for x in favs}
        fin = favs + [x for x in fin if first(x.split("#"), x) not in fav_bases]
    if fin:
        with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(fin))
        add_log(f"Поиск завершён: в списке {len(fin)} рабочих серверов")
    c_yaml, sb_json = build_clash_sub(fin), build_sb_sub(fin)
    with open("sub_clash.yaml", "w", encoding="utf-8") as f: f.write(c_yaml)
    with open("sub_singbox.json", "w", encoding="utf-8") as f: f.write(sb_json)
    SUB_MAP = {"sub": base64.b64encode("\n".join(fin).encode("utf-8")).decode("utf-8"), "clash": c_yaml, "sb": sb_json}
    if by_cc:
        os.makedirs("configs_by_country", exist_ok=True)
        for cc, items in by_cc.items():
            with open(os.path.join("configs_by_country", f"best_{cc.upper()}.txt"), "w", encoding="utf-8") as f: f.write("\n".join(items))
            SUB_MAP[cc] = base64.b64encode("\n".join(items).encode("utf-8")).decode("utf-8")
            SUB_MAP[f"clash/{cc}"] = build_clash_sub(items)
            SUB_MAP[f"sb/{cc}"] = build_sb_sub(items)
    try: winsound.Beep(880, 180); winsound.Beep(1174, 240)
    except Exception: pass
    s_port = CFG.get("sub_port", 18080)
    done_lbl, url_lbl = tr("done"), tr("url")
    print(f"\n{c_col}{done_lbl} {len(fin)}\n{url_lbl} http://127.0.0.1:{s_port}/sub | /clash | /sb{RST}")
    if by_cc:
        extra_urls = " | ".join(f"/{cc}" for cc in sorted(by_cc.keys()))
        print(f"{c_col}By country: [{extra_urls}] (also /clash/cc, /sb/cc){RST}")
    srv = HTTPServer(("127.0.0.1", s_port), SubHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("Enter -> Menu")
    try: input()
    except KeyboardInterrupt: pass
    srv.shutdown(); srv.server_close()
def execute_batch_pool(alive, b_workers, b_size):
    global CHECKED, FOUND_COUNT
    work = list()
    xray_items, sb_items = list(), list()
    for src, uri in alive:
        sc, _, _ = get_hp(uri)
        if sc in ("hy2", "tuic"): sb_items.append((src, uri))
        else: xray_items.append((src, uri))
    batches = [(xray_items[i:i + b_size], False) for i in range(0, len(xray_items), b_size)] + [(sb_items[i:i + 20], True) for i in range(0, len(sb_items), 20)]
    t4_tm = time.time()
    c_col, unit_lbl = CFG["color"], tr("unit")
    with ThreadPoolExecutor(max_workers=b_workers) as ex:
        futs = {ex.submit(run_batch_group, b, is_sb): len(b) for b, is_sb in batches}
        for f in as_completed(futs):
            b_len = futs[f]
            try:
                res_list = f.result()
                with LOCK:
                    for src, ms, cc, clean in res_list:
                        if FOUND_COUNT >= CFG["limit"]: STOP_EVENT.set(); break
                        FOUND_COUNT += 1
                        SRC_STATS[src] = SRC_STATS.get(src, 0) + 1
                        tag_txt = clean.split("#").pop()
                        sys.stdout.write(f"\r\033[K  {c_col}[+] {tag_txt}{RST}\n")
                        work.append((ms, cc, clean))
            except Exception: pass
            with LOCK:
                CHECKED += b_len
                spd_n = int(CHECKED / max(time.time() - t4_tm, 0.1))
                cur_n = len(alive) if STOP_EVENT.is_set() else min(CHECKED, len(alive))
                draw_bar(cur_n, len(alive), f"| {spd_n} {unit_lbl} | Found: {FOUND_COUNT}", t4_tm)
            if STOP_EVENT.is_set():
                for pending in futs: pending.cancel()
                break
    return work

def run_tcp_filter(filtered, t_tcp):
    alive, done = list(), 0
    with ThreadPoolExecutor(max_workers=TCP_WORKERS) as ex:
        futs = list((ex.submit(tcp_ok, item) for item in filtered))
        for f in as_completed(futs):
            done += 1; r = f.result()
            if r: alive.append(r)
            if done % 300 == 0 or done == len(filtered):
                draw_bar(done, len(filtered), f"| OK: {len(alive)}", t_tcp)
    return alive

def run_clipboard_scan():
    global CHECKED, FOUND_COUNT, PROC_FLAGS, SRC_STATS, REAL_HOME_IP
    xray_bin, sb_bin = find_cores()
    if not xray_bin and not sb_bin:
        no_x = tr("no_xray")
        ans = input(f"\033[93m{no_x}{RST}").strip().upper()
        if ans == "Y":
            if not download_cores(False): return
        else: return
    c_col = CFG["color"]
    raw_txt = ""
    try: raw_txt = subprocess.check_output(["powershell", "-command", "Get-Clipboard"], text=True, encoding="utf-8", errors="ignore")
    except Exception: pass
    found = parse_text(raw_txt)
    if not found:
        print(f"\033[91m[!] В буфере обмена не найдено ссылок или Base64-подписки.{RST}")
        return
    CHECKED, FOUND_COUNT, SRC_STATS = 0, 0, {}
    STOP_EVENT.clear()
    work = list()
    try:
        if CFG.get("strict_ip", True):
            _, REAL_HOME_IP, _ = fetch_trace_info(None, 5.0, False)
        b_workers, b_size, PROC_FLAGS = (2, 20, 0x00004000) if CFG["mode"] == 1 else ((4, 25, 0) if CFG["mode"] == 2 else (6, 25, 0))
        raw = [("clip", u) for u in found]
        filtered = smart_prefilter(raw)
        print(f"{c_col}[1/2] Буфер обмена: найдено {len(raw)} -> уникальных {len(filtered)}, TCP-отсев...{RST}")
        alive = run_tcp_filter(filtered, time.time())
        if not alive:
            print("\033[91m[!] Ни один сервер из буфера обмена не ответил по TCP.\033[0m"); return
        print(f"{c_col}[2/2] Турбо-проверка ({len(alive)})...{RST}")
        work = execute_batch_pool(alive, b_workers, b_size)
    except KeyboardInterrupt:
        STOP_EVENT.set()
        try: time.sleep(0.2)
        except KeyboardInterrupt: pass
        print(f"\n\n{c_col}[!] Остановлено пользователем. Найдено: {len(work)}{RST}")
        if not work: return
    finalize_results(work, set(), {}, append_existing=True)
def run_scan(from_cache=False):
    global CHECKED, FOUND_COUNT, PROC_FLAGS, SRC_STATS, REAL_HOME_IP
    xray_bin, sb_bin = find_cores()
    if not xray_bin and not sb_bin:
        no_x = tr("no_xray")
        ans = input(f"\033[93m{no_x}{RST}").strip().upper()
        if ans == "Y":
            if not download_cores(False): return
        else: return
    CHECKED, FOUND_COUNT, SRC_STATS = 0, 0, {}
    STOP_EVENT.clear()
    c_col = CFG["color"]
    work, all_sources, bl, by_src = list(), set(), load_bl(), {}
    try:
        if CFG.get("strict_ip", True):
            _, REAL_HOME_IP, _ = fetch_trace_info(None, 5.0, False)
        b_workers, b_size, PROC_FLAGS = (2, 20, 0x00004000) if CFG["mode"] == 1 else ((4, 25, 0) if CFG["mode"] == 2 else (6, 25, 0))
        cap = CFG.get("batch_cap", 3500)
        if from_cache:
            c_data = load_cache()
            c_nodes, off = c_data.get("nodes", list()), c_data.get("offset", 0)
            if off >= len(c_nodes):
                print(f"\033[93m[!] Весь кэш ({len(c_nodes)} узлов) уже проверен! Запустите полный поиск.{RST}")
                return
            alive = [tuple(x) for x in c_nodes[off:off + cap]]
            save_cache(c_nodes, off + len(alive))
            print(f"\n{c_col}[КЭШ] Допроверка порции {off + 1}..{off + len(alive)} из {len(c_nodes)}...{RST}")
        else:
            s1_lbl = tr("s1")
            print(f"\n{c_col}{s1_lbl}{RST}")
            urls, t1 = list(), time.time()
            db = load_src_db()
            prio_tags = {k for k, v in db.items() if v.get("prio", False)}
            if CFG.get("src", 0) in (0, 2, 3):
                tg_urls = get_tg_and_web(bl)
                for s, _ in tg_urls: all_sources.add(s)
                urls.extend(tg_urls)
            if CFG.get("src", 0) in (0, 1, 3):
                gl = CFG.get("gh_lang", 0)
                q_list = SEARCH_QUERIES_RU if gl == 1 else (SEARCH_QUERIES_EN if gl == 2 else (SEARCH_QUERIES_EN + SEARCH_QUERIES_RU))
                repos_dict = {}
                pinned = [k[3:] for k in prio_tags if k.startswith("gh:")]
                if gl in (0, 1): pinned.extend(PINNED_REPOS_RU)
                if os.path.exists(CUSTOM_FILE):
                    try:
                        with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
                            for ln in f:
                                s = ln.strip()
                                if s and not s.startswith(("#", "http://", "https://", "@")) and "/" in s:
                                    pinned.append(s.strip("/"))
                    except Exception: pass
                for full_n in dict.fromkeys(pinned):
                    prio_tags.add(f"gh:{full_n}")
                    if full_n not in repos_dict:
                        try:
                            rr = requests.get(f"{GH}/repos/{full_n}", headers=get_hdr(), proxies=get_px(), timeout=15)
                            if rr.status_code == 200: repos_dict[full_n] = rr.json()
                        except Exception: pass
                target_cnt = CFG.get("repos", 40) + len(repos_dict)
                per_q = max(10, min(100, (CFG.get("repos", 40) // len(q_list)) + 5))
                for q_str in q_list:
                    if len(repos_dict) >= target_cnt: break
                    for attempt in range(2):
                        try:
                            r = requests.get(f"{GH}/search/repositories", params={"q": q_str, "sort": "updated", "order": "desc", "per_page": per_q}, headers=get_hdr(), proxies=get_px(), timeout=20)
                            r.raise_for_status()
                            for it in r.json().get("items", list()):
                                full_n = it.get("full_name")
                                if full_n and full_n not in repos_dict and len(repos_dict) < target_cnt:
                                    repos_dict[full_n] = it
                            break
                        except Exception:
                            if attempt < 1: time.sleep(1.5)
                repos = list(repos_dict.values())
                for idx, r in enumerate(repos, 1):
                    r_name = r.get("full_name")
                    tag = f"gh:{r_name}"
                    if not CFG.get("blacklist", True) or tag not in bl:
                        all_sources.add(tag)
                        urls.extend(get_files(r))
                    draw_bar(idx, len(repos), f"| URLs: {len(urls)}", t1)
            s2_lbl = tr("s2")
            print(f"{c_col}{s2_lbl} ({len(urls)})...{RST}")
            raw, done, t2 = list(), 0, time.time()
            by_cat = {"GitHub": 0, "Web": 0, "TG": 0}
            with ThreadPoolExecutor(max_workers=50) as ex:
                futs = {ex.submit(fetch_url, u_list): s for s, u_list in urls}
                for f in as_completed(futs):
                    done += 1; s = futs[f]
                    try:
                        items = f.result()
                        for c in items: raw.append((s, c))
                        if items:
                            by_src[s] = by_src.get(s, 0) + len(items)
                            cat = "GitHub" if s.startswith("gh:") else ("TG" if s.startswith("tg:") else "Web")
                            by_cat[cat] += len(items)
                    except Exception: pass
                    if done % 10 == 0 or done == len(urls): draw_bar(done, len(urls), "", t2)
            gh_c, wb_c, tg_c = by_cat["GitHub"], by_cat["Web"], by_cat["TG"]
            print(f"  {c_col}-> Собрано / Collected: GitHub: {gh_c} | Web: {wb_c} | TG: {tg_c}{RST}")
            filtered = smart_prefilter(raw)
            for src, _ in filtered: SRC_STATS[src] = 0
            s3_lbl = tr("s3")
            print(f"{c_col}{s3_lbl} ({len(raw)} -> {len(filtered)})...{RST}")
            alive_all = run_tcp_filter(filtered, time.time())
            prio, mid_rest, tail_rest, src_cap = list(), list(), list(), {}
            random.shuffle(alive_all)
            for src, uri in alive_all:
                if src in prio_tags or (CFG.get("wl_mode", 0) == 1 and is_whitelist_sni(uri)):
                    prio.append((src, uri))
                elif src_cap.get(src, 0) < 250:
                    mid_rest.append((src, uri))
                    src_cap[src] = src_cap.get(src, 0) + 1
                else:
                    tail_rest.append((src, uri))
            ordered_all = prio + mid_rest + tail_rest
            alive = ordered_all[:cap]
            save_cache([list(x) for x in ordered_all], len(alive))
        s4_lbl = tr("s4")
        print(f"{c_col}{s4_lbl} ({len(alive)})...{RST}")
        work = execute_batch_pool(alive, b_workers, b_size)
    except KeyboardInterrupt:
        STOP_EVENT.set()
        try: time.sleep(0.2)
        except KeyboardInterrupt: pass
        print(f"\n\n{c_col}[!] Поиск остановлен пользователем (Ctrl+C). Найдено: {len(work)}{RST}")
        if not work: return
    finalize_results(work, all_sources, bl, append_existing=from_cache, run_collected=by_src)
def render_bg(bg_type, tick, w=78, h=27):
    grid = list((list((" " * w)) for _ in range(h)))
    if bg_type == 1:
        wave = "─────────╲╱╲──/\\──╲/─────────"
        row = h - 2
        for x in range(w): grid[row][x] = wave[(x + tick) % len(wave)]
    elif bg_type == 2:
        chars = "01011001"
        for col in range(2, w - 2, 4):
            y = (tick + col * 3) % h
            grid[y][col] = chars[(col + tick) % 8]
            grid[(y - 1) % h][col] = chars[(col + tick + 1) % 8]
    elif bg_type == 3:
        for row in range(1, h - 1, 3):
            x = (tick * 2 + row * 7) % (w - 4)
            grid[row][x] = "·"; grid[row][x + 1] = "•"; grid[row][x + 2] = "»"
    elif bg_type == 4:
        for i in range(18):
            x = (i * 17 + (tick if i % 2 == 0 else 0)) % w
            y = (i * 7) % (h - 2)
            grid[y][x] = "+" if (tick + i) % 3 == 0 else "."
    elif bg_type == 5:
        cx, cy = w // 2, h // 2
        for r in range(1, 12):
            x = int(cx + r * 2.2 * (1 if (tick % 4) in (0, 1) else -1))
            y = int(cy + (r // 2) * (1 if (tick % 4) in (1, 2) else -1))
            if 0 <= x < w and 0 <= y < h - 1: grid[y][x] = "o"
    return grid

def show_menu():
    l0 = "  ███╗   ██╗███████╗████████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗"
    l1 = "  ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝"
    l2 = "  ██╔██╗ ██║█████╗     ██║   ██████╔╝██║   ██║██║     ███████╗█████╗  "
    l3 = "  ██║╚██╗██║██╔══╝     ██║   ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  "
    l4 = "  ██║ ╚████║███████╗   ██║   ██║     ╚██████╔╝███████╗███████║███████╗"
    l5 = "  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝"
    tick, buf = 0, ""
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    try:
        while True:
            c = CFG["color"]
            c_info = load_cache()
            rem_c = max(0, len(c_info.get("nodes", list())) - c_info.get("offset", 0))
            cache_tag = f" [Кэш: {rem_c}]" if rem_c > 0 else ""
            db = load_src_db()
            prio_cnt = sum(1 for v in db.values() if v.get("prio", False))
            repo_tag = f" [★{prio_cnt} / {len(db)}]"
            bl_cnt = len(load_bl())
            c_str = ", ".join(sorted(CFG["countries"])) if CFG["countries"] else tr("all")
            p_str = tr("protos")[CFG.get("proto", 0)]
            wl_str = tr("wl_m")[CFG.get("wl_mode", 0)]
            s_src = f"{tr('srcs')[CFG.get('src', 0)]} [{tr('gh_l')[CFG.get('gh_lang', 0)]}] | Ban:{bl_cnt}"
            px_s = f"{tr('on')} (:{CFG.get('px_port', 10809)})" if CFG.get("use_px", False) else tr("off")
            g_on = CFG.get("geoip", True) or bool(CFG["countries"])
            st_on = CFG.get("strict_ip", True)
            g_str = f"Geo:{tr('on') if g_on else tr('off')} | IP:{tr('on') if st_on else tr('off')}"
            _, t_name = TARGETS.get(CFG.get("target", 1), ("", "Basic"))
            sp_cpu = f"Speed:{tr('on') if CFG['speed'] else tr('off')} | {tr('modes')[CFG['mode']]}"
            b_str = tr("bgs")[CFG.get("bg", 1)]
            vpn_tag = f" | VPN: {ACTIVE_NAME}" if ACTIVE_NAME else ""
            grid = render_bg(CFG.get("bg", 1), tick)
            bot_row = "".join(grid[-2])
            r_cnt, b_cap, lim_c = CFG.get("repos", 40), CFG.get("batch_cap", 3500), CFG["limit"]
            lines = [
                f"{c}{l0}{RST}", f"{c}{l1}{RST}", f"{c}{l2}{RST}",
                f"{c}{l3}{RST}", f"{c}{l4}{RST}", f"{c}{l5}{RST}",
                f"{c}{' ' * 14}:: {tr('sub')} ::{RST}",
                f"{c}{' ' * 22}[ {tr('auth')}{vpn_tag} ]{RST}",
                f"{c}{'=' * 74}{RST}",
                f"  {tr('m1')}{c}{cache_tag}{RST}",
                f"  {tr('m2')}",
                f"  {tr('m3')}",
                f"  {tr('m4')}{c}{repo_tag}{RST}",
                f"  {tr('m5'):<42} {c}[{wl_str}]{RST}",
                f"  {tr('m6'):<42} {c}[{s_src}]{RST}",
                f"  {tr('m7'):<42} {c}[{px_s}]{RST}",
                f"  {tr('m8'):<42} {c}[{c_str} | {p_str}]{RST}",
                f"  {tr('m9'):<42} {c}[{g_str}]{RST}",
                f"  {tr('m10'):<42} {c}[{t_name}]{RST}",
                f"  {tr('m11'):<42} {c}[{sp_cpu}]{RST}",
                f"  {tr('m12'):<42} {c}[{r_cnt} / {b_cap} / {lim_c}]{RST}",
                f"  {tr('m13'):<42} {c}[{CFG['cname']} | {b_str}]{RST}",
                f"  {tr('m14'):<42} {c}[{CFG['lang']} | :{CFG.get('sub_port', 18080)}]{RST}",
                f"  {tr('m0')}", f"{c}{'=' * 74}{RST}",
                f"{DIM}{c}{bot_row}{RST}", f"{tr('ask')}{c}{buf}{RST}   "
            ]
            out = list(("\033[H",))
            for idx, ln in enumerate(lines):
                if idx < 25 and CFG.get("bg", 1) != 0:
                    bg_line = f"{DIM}{c}{''.join(grid[idx])}{RST}"
                    out.append(f"\033[{idx + 1};1H{bg_line}\033[{idx + 1};1H{ln}")
                else:
                    out.append(f"\033[{idx + 1};1H{ln}")
            sys.stdout.write("".join(out))
            sys.stdout.flush()
            tick += 1
            for _ in range(8):
                if msvcrt.kbhit():
                    ch_in = msvcrt.getwch()
                    if ch_in in ("\r", "\n"):
                        ch, buf = buf.strip(), ""
                        sys.stdout.write("\033[?25h")
                        os.system("cls" if os.name == "nt" else "clear")
                        if ch == "1":
                            c_info = load_cache()
                            rem_c = max(0, len(c_info.get("nodes", list())) - c_info.get("offset", 0))
                            if rem_c > 0:
                                print(f"  1. Новый полный поиск (с нуля)\n  2. Допроверить остаток из кэша ({rem_c} живых TCP-узлов)")
                                sc_sel = input("> ").strip()
                                if sc_sel == "2": run_scan(from_cache=True)
                                elif sc_sel == "1": run_scan(from_cache=False)
                            else: run_scan(from_cache=False)
                            back_lbl = tr("back")
                            input(f"\n{back_lbl}")
                        elif ch == "2":
                            run_clipboard_scan()
                            back_lbl = tr("back")
                            input(f"\n{back_lbl}")
                        elif ch == "3": manage_servers()
                        elif ch == "4": manage_sources()
                        elif ch == "5": CFG["wl_mode"] = 0 if CFG.get("wl_mode", 0) == 2 else CFG.get("wl_mode", 0) + 1; save_cfg()
                        elif ch == "6":
                            print(f"  1. Источники: {tr('srcs')[CFG.get('src', 0)]}")
                            print(f"  2. Язык репозиториев GitHub: {tr('gh_l')[CFG.get('gh_lang', 0)]}")
                            print("  3. Вкл/Выкл карантин (24ч)\n  4. Очистить черный список (Clear Blacklist)")
                            s_sel = input("> ").strip()
                            if s_sel == "1":
                                CFG["src"] = 0 if CFG.get("src", 0) == 3 else CFG.get("src", 0) + 1; save_cfg()
                                print(f"{c}[*] Свои каналы, репы и сайты можно вписать в: {CUSTOM_FILE}{RST}"); time.sleep(1.2)
                            elif s_sel == "2":
                                CFG["gh_lang"] = 0 if CFG.get("gh_lang", 0) == 2 else CFG.get("gh_lang", 0) + 1; save_cfg()
                            elif s_sel == "3": CFG["blacklist"] = not CFG.get("blacklist", True); save_cfg()
                            elif s_sel == "4": save_bl({})
                        elif ch == "7":
                            print("  1. Вкл/Выкл прокси v2rayN (Toggle)\n  2. Изменить HTTP-порт прокси (по умолч. 10809)")
                            px_s_in = input("> ").strip()
                            if px_s_in == "1": CFG["use_px"] = not CFG.get("use_px", False); save_cfg()
                            elif px_s_in == "2":
                                p_val = input("Port (e.g. 10809) > ").strip()
                                if p_val.isdigit() and 1 <= int(p_val) <= 65535: CFG["px_port"] = int(p_val); save_cfg()
                        elif ch == "8":
                            print("  1. Фильтр стран (DE, NL, FI...)\n  2. Протокол поиска (ВСЕ / VLESS / Trojan / SS / HY2)")
                            cp_sel = input("> ").strip()
                            if cp_sel == "1":
                                for code, name in COUNTRIES_INFO: print(f"  {c}{code}{RST} - {name}")
                                raw_c = input("\nDE NL FI... (Enter = ALL) > ").upper()
                                CFG["countries"] = set(re.findall(r'[A-Z]{2}', raw_c))
                                if CFG["countries"]: CFG["geoip"] = True
                                save_cfg()
                            elif cp_sel == "2":
                                CFG["proto"] = 0 if CFG.get("proto", 0) == 4 else CFG.get("proto", 0) + 1; save_cfg()
                        elif ch == "9":
                            print("  1. Вкл/Выкл определение страны (GeoIP)\n  2. Вкл/Выкл Strict Anti-DPI (проверка смены IP)")
                            g_sel = input("> ").strip()
                            if g_sel == "1" and not CFG["countries"]: CFG["geoip"] = not CFG.get("geoip", True); save_cfg()
                            elif g_sel == "2": CFG["strict_ip"] = not CFG.get("strict_ip", True); save_cfg()
                        elif ch == "10": CFG["target"] = 1 if CFG.get("target", 1) == 3 else CFG.get("target", 1) + 1; save_cfg()
                        elif ch == "11":
                            print("  1. Вкл/Выкл замер скорости скачивания\n  2. Режим нагрузки на ЦП (2x20 -> 4x25 -> 6x25)")
                            sc_cpu = input("> ").strip()
                            if sc_cpu == "1": CFG["speed"] = not CFG.get("speed", True); save_cfg()
                            elif sc_cpu == "2": CFG["mode"] = 1 if CFG.get("mode", 3) == 3 else CFG.get("mode", 3) + 1; save_cfg()
                        elif ch == "12":
                            r_val = input("Repos (1 - 250, Enter = skip) > ").strip()
                            if r_val.isdigit() and 1 <= int(r_val) <= 250: CFG["repos"] = int(r_val)
                            c_val = input("Max nodes in [4/5] (100 - 20000, Enter = skip) > ").strip()
                            if c_val.isdigit() and 100 <= int(c_val) <= 20000: CFG["batch_cap"] = int(c_val)
                            l_val = input("Target working limit (5 - 200, Enter = skip) > ").strip()
                            if l_val.isdigit() and int(l_val) > 0: CFG["limit"] = int(l_val)
                            save_cfg()
                        elif ch == "13":
                            for k, (col, nm) in COLORS.items(): print(f"  {k}. {col}{nm}{RST}")
                            sel = input("> ").strip()
                            if sel in COLORS: CFG["color"], CFG["cname"] = COLORS[sel]
                            print("\n  1. Пульс | 2. Матрица | 3. Поток | 4. Звезды | 5. Радар | 0. Выкл")
                            bsel = input("> ").strip()
                            if bsel in ("0", "1", "2", "3", "4", "5"): CFG["bg"] = int(bsel)
                            save_cfg()
                        elif ch == "14":
                            print("  1. Сменить язык (RU/EN)\n  2. Создать ярлык на Рабочем столе\n  3. Ввести GitHub Token\n  4. Изменить локальный порт подписки (по умолч. 18080)\n  5. Скачать / Обновить ядра (Xray + sing-box)")
                            sub_s = input("> ").strip()
                            if sub_s == "1": CFG["lang"] = "EN" if CFG["lang"] == "RU" else "RU"; save_cfg()
                            elif sub_s == "2":
                                make_shortcut()
                                back_lbl = tr("back")
                                input(f"\n{back_lbl}")
                            elif sub_s == "3": CFG["token"] = input("Token > ").strip(); save_cfg()
                            elif sub_s == "4":
                                sp_val = input("Local sub port (1024 - 65535) > ").strip()
                                if sp_val.isdigit() and 1024 <= int(sp_val) <= 65535: CFG["sub_port"] = int(sp_val); save_cfg()
                            elif sub_s == "5":
                                download_cores(True)
                                back_lbl = tr("back")
                                input(f"\n{back_lbl}")
                        elif ch == "0": return
                        os.system("cls" if os.name == "nt" else "clear")
                        sys.stdout.write("\033[?25l")
                        break
                    elif ch_in == "\b": buf = buf[:-1]
                    elif ch_in.isprintable(): buf += ch_in
                time.sleep(0.015)
    finally:
        disconnect_vpn()
        sys.stdout.write("\033[?25h")

threading.Thread(target=failover_loop, daemon=True).start()
try: show_menu()
except KeyboardInterrupt: disconnect_vpn(); sys.stdout.write("\033[?25h")
except Exception: disconnect_vpn(); traceback.print_exc(); input("\nEnter...")
