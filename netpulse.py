import base64, ctypes, io, json, msvcrt, os, random, re, socket, subprocess, sys, threading, time, traceback, winreg, winsound, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import requests

os.system("")
SEARCH_QUERIES = [
    "vless reality subscription",
    "vless trojan free",
    "hysteria2 tuic vless free",
    "shadowsocks vless nodes",
    "xray singbox config"
]
TCP_WORKERS = 300
SPEED_URL = "https://cloudflare.com"
TRACE_URL = "https://cloudflare.com"
TIMEOUT = 3.5

GH = "https://" + "a" + "pi" + ".github.com"
RAW = "https://" + "raw" + ".githubusercontent.com"
TG_WEB = "https://" + "t" + ".me/s/"

DEFAULT_TG = ["vless_free", "v2ray_configs_pool", "FreeV2rayVPN", "v2rayng_vpn_free", "Outline_Vpn_Free", "v2ray_free_conf", "PrivateVPNs", "vless_vmess"]
CUSTOM_FILE = "custom_sources.txt"
BL_FILE = "netpulse_blacklist.json"
CFG_FILE = "netpulse_config.json"
FAV_FILE = "favorites.txt"

CFG = {"lang": "RU", "color": "\033[96m", "cname": "Cyan", "countries": set(), "proto": 0, "src": 0, "use_px": False, "px_port": 10809, "sub_port": 18080, "tun": False, "failover": True, "blacklist": True, "geoip": False, "speed": True, "mode": 3, "repos": 40, "limit": 40, "token": "", "bg": 1, "target": 1, "xray": r"C:\vpns\v2rayN-windows-64\bin\xray\xray.exe", "singbox": ""}

TARGETS = {
    1: ("http://msftconnecttest.com", "Basic Internet / Базовый"),
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
                f.write("# Добавьте сюда свои Telegram-каналы (без @) или прямые ссылки http/https\n# Add your Telegram channels (without @) or direct URLs below\n")
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
    return {"http": f"http://127.0.0.1:{p}", "https": f"http://127.0.0.1:{p}"}

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
    h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NetPulse/3.9"}
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
            with requests.get(dl_url, proxies=get_px(), stream=True, timeout=(10, 60)) as z_res:
                z_res.raise_for_status()
                tot = int(z_res.headers.get("content-length", 0))
                buf, cur = io.BytesIO(), 0
                for ch in z_res.iter_content(65536):
                    if ch:
                        buf.write(ch); cur += len(ch)
                        if tot > 0: draw_bar(cur, tot, f"| {cur // 1048576} MB")
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
    "RU": {"sub": "Умный агрегатор и VPN-менеджер v3.9", "auth": "Авторы: Gemini & Glitch", "m1": "1. Запустить поиск", "m2": "2. Менеджер серверов (VPN / TUN / Очистка)", "m3": "3. Источники поиска", "m4": "4. Карантин пустых баз (24ч)", "m5": "5. Прокси v2rayN для парсинга", "m6": "6. Страны фильтрации", "m7": "7. Протокол поиска", "m8": "8. GeoIP проверка стран", "m9": "9. Цель проверки (Сайт)", "m10": "10. Замер скорости скачивания", "m11": "11. Режим нагрузки на ЦП", "m12": "12. Репозиториев / Лимит", "m13": "13. Кастомизация (Цвет и Фон)", "m14": "14. Язык / Ярлык / Ядра / Токен / Порт", "m0": "0. Выход", "ask": "Выберите пункт меню > ", "all": "ВСЕ СТРАНЫ", "on": "ВКЛ", "off": "ВЫКЛ", "srcs": {0: "ВСЕ (GitHub + TG + Web)", 1: "Только GitHub", 2: "Только Telegram + Web", 3: "GitHub + Web (без TG)"}, "protos": {0: "ВСЕ (VLESS+Trojan+SS+HY2+TUIC)", 1: "Только VLESS", 2: "Только Trojan", 3: "Только Shadowsocks", 4: "Только Hysteria2 / TUIC"}, "bgs": {1: "Пульс", 2: "Матрица", 3: "Поток", 4: "Звезды", 5: "Радар", 0: "Выкл"}, "modes": {1: "Игровой (12 пот., низкий ЦП)", 2: "Средний (35 потоков)", 3: "Турбо (80 потоков)"}, "s1": "[1/5] Сбор источников (GitHub / TG / Web)...", "s2": "[2/5] Скачивание и парсинг", "s3": "[3/5] Умный фильтр и TCP-отсев", "s4": "[4/5] Batch-проверка (Xray / Sing-box)", "s5": "[5/5] Замер скорости скачивания", "done": "Готово! Найдено рабочих:", "url": "Подписки:", "back": "Нажмите Enter для возврата в меню...", "bat_ok": "[+] Ярлык NETPULSE.bat создан на Рабочем столе!", "no_xray": "[!] Ядра не найдены! Скачать автоматически с GitHub? (Y/N) > "},
    "EN": {"sub": "Smart Aggregator & VPN Manager v3.9", "auth": "Authors: Gemini & Glitch", "m1": "1. Start Scan", "m2": "2. Server Manager (VPN / TUN / Auto-Clean)", "m3": "3. Search Sources", "m4": "4. Dead Source Quarantine (24h)", "m5": "5. v2rayN Proxy for Scraping", "m6": "6. Target Countries", "m7": "7. Target Protocol", "m8": "8. GeoIP Country Lookup", "m9": "9. Validation Target Site", "m10": "10. Download Speed Test", "m11": "11. CPU Load Mode", "m12": "12. Repos / Limit", "m13": "13. Customization (Color & BG)", "m14": "14. Lang / Shortcut / Cores / Token / Port", "m0": "0. Exit", "ask": "Select option > ", "all": "ALL COUNTRIES", "on": "ON", "off": "OFF", "srcs": {0: "ALL (GitHub + TG + Web)", 1: "GitHub Only", 2: "Telegram + Web Only", 3: "GitHub + Web (No TG)"}, "protos": {0: "ALL (VLESS+Trojan+SS+HY2+TUIC)", 1: "VLESS Only", 2: "Trojan Only", 3: "Shadowsocks Only", 4: "Hysteria2 / TUIC Only"}, "bgs": {1: "Pulse", 2: "Matrix", 3: "Stream", 4: "Stars", 5: "Radar", 0: "Off"}, "modes": {1: "Gaming (12 thr., Low CPU)", 2: "Balanced (35 threads)", 3: "Turbo (80 threads)"}, "s1": "[1/5] Collecting sources (GitHub / TG / Web)...", "s2": "[2/5] Downloading & parsing", "s3": "[3/5] Smart filter & TCP check", "s4": "[4/5] Batch check (Xray / Sing-box)", "s5": "[5/5] Measuring download speed", "done": "Done! Working servers:", "url": "Subscriptions:", "back": "Press Enter to return to menu...", "bat_ok": "[+] Shortcut NETPULSE.bat created on Desktop!", "no_xray": "[!] Cores not found! Download automatically from GitHub? (Y/N) > "}
}
SUB_MAP, SRC_STATS, CHECKED, FOUND_COUNT, STOP_EVENT, LOCK, PROC_FLAGS = {}, {}, 0, 0, threading.Event(), threading.Lock(), 0
ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH = None, "", "", ""
first = lambda s, d="": next(iter(s), d) if s else d
tr = lambda k: TXT[CFG["lang"]][k]

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

def draw_bar(cur, tot, extra=""):
    if tot <= 0: return
    pct = min(100.0, (cur / tot) * 100)
    fill = int(24 * cur // tot)
    bar = "█" * fill + "░" * (24 - fill)
    sys.stdout.write(f"\r  {CFG['color']}[{bar}] {pct:5.1f}% ({cur}/{tot}) {extra}{RST}   ")
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
                    if i.get("type") == "blob" and (p.endswith((".txt", ".list")) or "." not in p.split("/").pop()):
                        if not any(x in p.lower() for x in ("readme", "license", ".git")):
                            urls.append((tag, f"{RAW}/{o}/{n}/{b}/{p}"))
                break
        except Exception: time.sleep(1)
    return urls

def get_tg_and_web(bl):
    items = list()
    channels = list(DEFAULT_TG) if CFG.get("src", 0) != 3 else list()
    if os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
                for ln in f:
                    s = ln.strip()
                    if not s or s.startswith("#"): continue
                    if s.startswith(("http://", "https://")):
                        if not CFG.get("blacklist", True) or s not in bl: items.append((s, s))
                    elif CFG.get("src", 0) != 3: channels.append(s.lstrip("@"))
        except Exception: pass
    for ch in dict.fromkeys(channels):
        tag = f"tg:{ch}"
        if not CFG.get("blacklist", True) or tag not in bl:
            items.append((tag, f"{TG_WEB}{ch}"))
    return items

def parse_text(txt):
    clean = re.sub(r'<[^>]+>', '\n', txt)
    pat = re.compile(r'(?:vless|trojan|ss|hy2|hysteria2|tuic)://[^\s"\'<>]+')
    m = pat.findall(clean)
    if not m and len(clean) < 500000:
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

def smart_prefilter(raw_list):
    uniq, subnets = {}, {}
    bad_hosts = ("127.0.0.1", "0.0.0.0", "localhost", "example.com", "://cloudflare.com")
    pr = CFG.get("proto", 0)
    for src, uri in raw_list:
        try:
            sc, h, pt = get_hp(uri)
            if not h or not pt or h.lower() in bad_hosts: continue
            if pr == 1 and sc != "vless": continue
            if pr == 2 and sc != "trojan": continue
            if pr == 3 and sc != "ss": continue
            if pr == 4 and sc not in ("hy2", "tuic"): continue
            if sc == "vless" and "security=none" in uri.lower(): continue
            key = f"{sc}:{h}:{pt}"
            if key in uniq: continue
            parts = h.split(".")
            if len(parts) == 4 and all(x.isdigit() for x in parts):
                sub24 = ".".join(parts[:3])
                if subnets.get(sub24, 0) >= 2: continue
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
def build_out(uri, tag="proxy"):
    uri = first(uri.split("#"), uri)
    sc = first(uri.split("://"), "").lower()
    if sc == "ss":
        res = parse_ss(uri)
        if not res: return None
        h, pt, m, pwd = res
        return {"tag": tag, "protocol": "shadowsocks", "settings": {"servers": list(({"address": h, "port": pt, "method": m, "password": pwd},))}}
    p, q = urlparse(uri), parse_qs(urlparse(uri).query)
    net = first(q.get("type"), "tcp")
    if sc == "vless":
        sec = first(q.get("security"), "none")
        if sec == "none": return None
        out = {"tag": tag, "protocol": "vless", "settings": {"vnext": list(({"address": p.hostname, "port": int(p.port), "users": list(({"id": p.username, "encryption": first(q.get("encryption"), "none"), "flow": first(q.get("flow"), "")},))},))}, "streamSettings": {"network": net, "security": sec}}
    elif sc == "trojan":
        sec = first(q.get("security"), "tls")
        out = {"tag": tag, "protocol": "trojan", "settings": {"servers": list(({"address": p.hostname, "port": int(p.port), "password": unquote(p.username or "")},))}, "streamSettings": {"network": net, "security": sec}}
    else: return None
    if sec == "reality":
        out["streamSettings"]["realitySettings"] = {"serverName": first(q.get("sni"), ""), "fingerprint": first(q.get("fp"), "chrome"), "publicKey": first(q.get("pbk"), ""), "shortId": first(q.get("sid"), ""), "spiderX": unquote(first(q.get("spx"), "/"))}
    elif sec == "tls":
        out["streamSettings"]["tlsSettings"] = {"serverName": first(q.get("sni"), p.hostname), "allowInsecure": first(q.get("allowInsecure"), "0") in ("1", "true")}
    if net == "ws": out["streamSettings"]["wsSettings"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
    elif net == "grpc": out["streamSettings"]["grpcSettings"] = {"serviceName": first(q.get("serviceName"), "")}
    return out

def build_sb_out(uri, tag="proxy"):
    uri = first(uri.split("#"), uri)
    sc = first(uri.split("://"), "").lower()
    if sc == "hysteria2": sc = "hy2"
    if sc == "ss":
        res = parse_ss(uri)
        if not res: return None
        h, pt, m, pwd = res
        return {"type": "shadowsocks", "tag": tag, "server": h, "server_port": pt, "method": m, "password": pwd}
    p, q = urlparse(uri), parse_qs(urlparse(uri).query)
    if sc == "hy2":
        tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname), "insecure": first(q.get("insecure"), "0") in ("1", "true")}
        out = {"type": "hysteria2", "tag": tag, "server": p.hostname, "server_port": int(p.port), "password": unquote(p.username or ""), "tls": tls}
        if q.get("obfs"): out["obfs"] = {"type": first(q.get("obfs"), ""), "password": first(q.get("obfs-password"), "")}
        return out
    if sc == "tuic":
        tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname), "insecure": first(q.get("allow_insecure"), "0") in ("1", "true"), "alpn": ["h3"]}
        return {"type": "tuic", "tag": tag, "server": p.hostname, "server_port": int(p.port), "uuid": p.username, "password": unquote(p.password or ""), "congestion_control": first(q.get("congestion_control"), "bbr"), "tls": tls}
    net = first(q.get("type"), "tcp")
    if sc == "vless":
        sec = first(q.get("security"), "none")
        if sec == "none": return None
        out = {"type": "vless", "tag": tag, "server": p.hostname, "server_port": int(p.port), "uuid": p.username, "flow": first(q.get("flow"), "")}
    elif sc == "trojan":
        sec = first(q.get("security"), "tls")
        out = {"type": "trojan", "tag": tag, "server": p.hostname, "server_port": int(p.port), "password": unquote(p.username or "")}
    else: return None
    if sec in ("tls", "reality"):
        tls = {"enabled": True, "server_name": first(q.get("sni"), p.hostname)}
        if sec == "reality":
            tls["utls"] = {"enabled": True, "fingerprint": first(q.get("fp"), "chrome")}
            tls["reality"] = {"enabled": True, "public_key": first(q.get("pbk"), ""), "short_id": first(q.get("sid"), "")}
        out["tls"] = tls
    if net == "ws": out["transport"] = {"type": "ws", "path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
    elif net == "grpc": out["transport"] = {"type": "grpc", "service_name": first(q.get("serviceName"), "")}
    return out
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
        "dns": {"servers": [{"tag": "remote", "address": "1.1.1.1", "detour": "proxy"}, {"tag": "local", "address": "local", "detour": "direct"}], "rules": [{"domain_suffix": [".ru", ".xn--p1ai"], "server": "local"}]},
        "inbounds": [{"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 2080}],
        "outbounds": [{"type": "selector", "tag": "proxy", "outbounds": ["auto"] + tags}, {"type": "urltest", "tag": "auto", "outbounds": tags, "url": "http://gstatic.com", "interval": "5m"}] + outs + [{"type": "direct", "tag": "direct"}, {"type": "dns", "tag": "dns-out"}],
        "route": {"rules": [{"protocol": "dns", "outbound": "dns-out"}, {"domain_suffix": [".ru", ".xn--p1ai"], "outbound": "direct"}, {"ip_is_private": True, "outbound": "direct"}], "auto_detect_interface": True}
    }
    return json.dumps(cfg, ensure_ascii=False, indent=2)
def wait_port(port, tries=25):
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
        ports.append(s.getsockname().pop())
        socks.append(s)
    for s in socks: s.close()
    return ports

def probe_local_port(port, speed_mode=False, cc_mode=False):
    try:
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        sess = requests.Session(); sess.trust_env = False
        if cc_mode:
            res = sess.get(TRACE_URL, proxies=px, timeout=4)
            for ln in res.text.splitlines():
                if ln.startswith("loc="): return ln.split("=", 1).pop().strip().upper()
            return "UN"
        t0 = time.time()
        if not speed_mode:
            pair = TARGETS.get(CFG.get("target", 1), ("http://msftconnecttest.com", ""))
            t_url = first(pair, "http://msftconnecttest.com")
            res = sess.get(t_url, proxies=px, timeout=TIMEOUT)
            return int((time.time() - t0) * 1000) if res.status_code in (200, 204) else None
        dl = 0
        with sess.get(SPEED_URL, proxies=px, stream=True, timeout=(4, 10)) as r:
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
            cfg = {"log": {"loglevel": "none"}, "inbounds": [{"port": port, "listen": "127.0.0.1", "protocol": "http"}], "outbounds": [out]}
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
            inbs.append({"tag": f"in_{idx}", "port": pt, "listen": "127.0.0.1", "protocol": "http"})
            rules.append({"type": "field", "inboundTag": [f"in_{idx}"], "outboundTag": tg})
        outs.append(out)
        valid_map.append((src, uri, pt))
    if not valid_map: return list()
    proc, tmp_cfg = None, ""
    found_batch = list()
    try:
        _, _, first_pt = first(valid_map)
        if is_sb:
            sb_bin = CFG.get("singbox", "")
            if not sb_bin or not os.path.exists(sb_bin): return list()
            cfg = {"log": {"level": "panic"}, "inbounds": inbs, "outbounds": outs, "route": {"rules": rules}}
            tmp_cfg = os.path.abspath(f"tmp_batch_{first_pt}.json")
            with open(tmp_cfg, "w", encoding="utf-8") as f: json.dump(cfg, f)
            proc = subprocess.Popen([sb_bin, "run", "-c", tmp_cfg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        else:
            cfg = {"log": {"loglevel": "none"}, "inbounds": inbs, "outbounds": outs, "routing": {"rules": rules}}
            proc = subprocess.Popen([CFG.get("xray", ""), "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
            proc.stdin.write(json.dumps(cfg).encode("utf-8")); proc.stdin.close()
        if not wait_port(first_pt, 45): return list()
        def test_slot(slot):
            if STOP_EVENT.is_set(): return None
            src, uri, pt = slot
            ms = probe_local_port(pt, False, False)
            if ms is None: return None
            need_geo = bool(CFG["countries"]) or CFG.get("geoip", False)
            cc = probe_local_port(pt, False, True) if need_geo else "FAST"
            if CFG["countries"] and cc not in CFG["countries"]: return None
            sc, _, _ = get_hp(uri)
            clean = f"{first(uri.split('#'), uri)}#{sc.upper()}_{cc}_{ms}ms"
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

def purge_dead_rows(rows):
    if not rows: return list(), 0
    xray_items, sb_items = list(), list()
    for ln in rows:
        base = first(ln.split("#"), ln)
        sc, _, _ = get_hp(base)
        if sc in ("hy2", "tuic"): sb_items.append(("clean", ln))
        else: xray_items.append(("clean", ln))
    alive_map = {}
    for batch, is_sb in [(xray_items[i:i + 50], False) for i in range(0, len(xray_items), 50)] + [(sb_items[i:i + 25], True) for i in range(0, len(sb_items), 25)]:
        for _, ms, cc, clean in run_batch_group(batch, is_sb):
            alive_map[first(clean.split("#"), clean)] = (ms, clean)
    new_rows = list()
    for ln in rows:
        base = first(ln.split("#"), ln)
        if base in alive_map:
            _, updated = alive_map[base]
            new_rows.append(updated)
    removed = len(rows) - len(new_rows)
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(new_rows))
    return new_rows, removed
def set_win_proxy(enable, port=10809):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
        if enable: winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"127.0.0.1:{port}")
        winreg.CloseKey(key)
    except Exception: pass

def disconnect_vpn():
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    if ACTIVE_PROC:
        try: ACTIVE_PROC.kill()
        except Exception: pass
        ACTIVE_PROC = None
    if TUN_CFG_PATH and os.path.exists(TUN_CFG_PATH):
        try: os.remove(TUN_CFG_PATH)
        except Exception: pass
    TUN_CFG_PATH, ACTIVE_NAME, ACTIVE_URI = "", "", ""
    set_win_proxy(False)

def connect_vpn(uri, label):
    global ACTIVE_PROC, ACTIVE_NAME, ACTIVE_URI, TUN_CFG_PATH
    disconnect_vpn()
    clean_uri = first(uri.split("#"), uri)
    sc, _, _ = get_hp(clean_uri)
    xray_bin, sb_bin = find_cores()
    use_sb = CFG.get("tun", False) or sc in ("hy2", "tuic")
    if use_sb:
        if CFG.get("tun", False) and not is_admin(): return False
        if not sb_bin or not os.path.exists(sb_bin): return False
        sb_out = build_sb_out(clean_uri, "proxy")
        if not sb_out: return False
        port = CFG.get("px_port", 10809)
        inb = [{"type": "tun", "interface_name": "NetPulseTUN", "inet4_address": "172.19.0.1/30", "auto_route": True, "strict_route": True, "stack": "system", "sniff": True}] if CFG.get("tun", False) else [{"type": "http", "listen": "127.0.0.1", "listen_port": port}]
        sb_cfg = {
            "log": {"level": "error"},
            "dns": {"servers": [{"tag": "remote", "address": "1.1.1.1", "detour": "proxy"}, {"tag": "local", "address": "local", "detour": "direct"}], "rules": [{"outbound": "any", "server": "local"}]},
            "inbounds": inb, "outbounds": [sb_out, {"type": "direct", "tag": "direct"}, {"type": "dns", "tag": "dns-out"}],
            "route": {"rules": [{"protocol": "dns", "outbound": "dns-out"}, {"ip_is_private": True, "outbound": "direct"}], "auto_detect_interface": True}
        }
        TUN_CFG_PATH = os.path.abspath("netpulse_sb_active.json")
        with open(TUN_CFG_PATH, "w", encoding="utf-8") as f: json.dump(sb_cfg, f, indent=2)
        try:
            ACTIVE_PROC = subprocess.Popen([sb_bin, "run", "-c", TUN_CFG_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.2)
            if ACTIVE_PROC.poll() is None:
                if not CFG.get("tun", False): set_win_proxy(True, port)
                ACTIVE_NAME = f"{label} ({'TUN' if CFG.get('tun', False) else 'SB-Proxy'})"
                ACTIVE_URI = clean_uri
                return True
        except Exception: pass
        disconnect_vpn()
        return False
    if not xray_bin: return False
    out = build_out(clean_uri, "proxy")
    if not out: return False
    port = CFG.get("px_port", 10809)
    cfg = {"log": {"loglevel": "none"}, "inbounds": [{"port": port, "listen": "127.0.0.1", "protocol": "http"}], "outbounds": [out]}
    try:
        ACTIVE_PROC = subprocess.Popen([xray_bin, "run", "-c", "stdin:"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ACTIVE_PROC.stdin.write(json.dumps(cfg).encode("utf-8")); ACTIVE_PROC.stdin.close()
        if wait_port(port):
            set_win_proxy(True, port)
            ACTIVE_NAME, ACTIVE_URI = f"{label} (Proxy)", clean_uri
            return True
    except Exception: pass
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
                px = None if "(TUN)" in ACTIVE_NAME else {"http": f"http://127.0.0.1:{CFG.get('px_port', 10809)}", "https": f"http://127.0.0.1:{CFG.get('px_port', 10809)}"}
                r = sess.get("http://msftconnecttest.com", proxies=px, timeout=4)
                ok = r.status_code in (200, 204)
        except Exception: ok = False
        fails = 0 if ok else fails + 1
        if fails >= 2 and os.path.exists("best_configs.txt"):
            fails = 0
            dead_uri = ACTIVE_URI
            try:
                with open("best_configs.txt", "r", encoding="utf-8") as f:
                    rows = [ln.strip() for ln in f if ln.strip()]
                fav_bases = {first(x.split("#"), x) for x in load_favs()}
                if dead_uri not in fav_bases:
                    rows = [ln for ln in rows if first(ln.split("#"), ln) != dead_uri]
                    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
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
        if len(tok) == 2 and tok.isalpha() and tok.isupper() and tok != "SS": cc = tok
        elif tok in ("FAST", "UN", "IMP"): cc = tok
        elif tok.endswith("ms") and tok[:-2].isdigit(): ms = tok
        elif tok.endswith("Mbps"): spd = tok
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
            cc = run_single_test(base, False, True) if CFG.get("geoip", False) else "IMP"
            rows.insert(0, f"{base}#{sc.upper()}_{cc}_{ms}ms")
            existing.add(base); added += 1
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
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
        print(f"{c}[+] Base64-подписка скопирована в буфер обмена!{RST}"); time.sleep(1.2)
    elif ex_t == "2":
        with open("export_nodes.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
        print(f"{c}[+] Сохранено в export_nodes.txt!{RST}"); time.sleep(1.2)
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
        t_mode = f"TUN (Admin: {'OK' if is_admin() else 'NO'})" if CFG.get("tun", False) else f"Proxy (:{CFG.get('px_port', 10809)})"
        fo_st = tr("on") if CFG.get("failover", True) else tr("off")
        print(f"{c}{'=' * 74}")
        print(f"  SERVER MANAGER | {t_mode} | Failover: {fo_st} | Favs: {len(favs)} | VPN: {ACTIVE_NAME if ACTIVE_NAME else 'OFF'}")
        print(f"{'=' * 74}{RST}")
        if not rows:
            print("  Список пуст / List is empty. Запустите поиск (пункт 1) или нажмите [I] для импорта.")
        else:
            print(f"  {'#':<4} {'PROTO':<8} {'CC':<6} {'PING':<9} {'SPEED':<11} {'HOST'}")
            print(f"  {'-' * 68}")
            for i, ln in enumerate(rows, 1):
                base, sc, cc, ms, spd, _ = parse_row_info(ln)
                _, h, _ = get_hp(base)
                star = "★ " if base in fav_bases else ""
                mark = " *" if ACTIVE_NAME and f"#{i} " in ACTIVE_NAME else ""
                print(f"  {c}{i:<4}{RST} {sc:<8} {cc:<6} {ms:<9} {spd:<11} {c}{star}{RST}{str(h)[:26]}{c}{mark}{RST}")
        print(f"\n{c}Команды / Commands:{RST}")
        print("  [Номер] - Выбрать сервер (VPN / Тест / Избранное ★ / Копировать / Удалить)")
        print("  [T]     - Режим VPN: Proxy <-> TUN     [F] - Вкл/Выкл Auto-Failover")
        print("  [I]     - Импорт ссылок / Base64       [E] - Экспорт списка / Base64")
        print("  [A]     - Перепроверить и очистить     [D] - Отключить VPN   [Enter] - Меню")
        cmd = input("\n> ").strip().upper()
        if not cmd: break
        elif cmd == "F": CFG["failover"] = not CFG.get("failover", True); save_cfg()
        elif cmd == "I": rows = import_nodes_ui(rows)
        elif cmd == "E": export_nodes_ui(rows)
        elif cmd == "T":
            CFG["tun"] = not CFG.get("tun", False); save_cfg()
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
                else: print("\033[91m[!] Ошибка запуска (проверьте права Админа и наличие ядра).\033[0m")
                time.sleep(1.4)
            elif act == "2":
                print("  Тестирую пинг, страну и скорость...")
                nms = run_single_test(base, False, False)
                if nms is not None:
                    ncc = run_single_test(base, False, True)
                    nspd = run_single_test(base, True, False)
                    rows[idx] = f"{base}#{sc}_{ncc}_{nms}ms_{nspd}Mbps"
                    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
                    print(f"  {c}[+] Результат: {ncc} | {nms}ms | {nspd}Mbps{RST}")
                else: print("  \033[91m[!] Сервер не отвечает.\033[0m")
                time.sleep(1.3)
            elif act == "3":
                subprocess.run("clip", input=rows[idx].encode("utf-8"), check=False)
                print("  [+] Скопировано в буфер обмена!"); time.sleep(0.8)
            elif act == "4":
                rows.pop(idx)
                with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(rows))
            elif act == "5":
                if is_fav: favs = [x for x in favs if first(x.split("#"), x) != base]
                else: favs.append(rows[idx])
                save_favs(favs)
                print(f"  {c}[+] Избранное обновлено!{RST}"); time.sleep(0.8)
def fetch_url(u):
    try:
        with requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, proxies=get_px(), stream=True, timeout=(4, 6)) as r:
            if r.status_code != 200: return list()
            chunks, sz = list(), 0
            for ch in r.iter_content(65536, decode_unicode=True):
                if ch:
                    chunks.append(ch); sz += len(ch)
                    if sz > 1500000: break
            return parse_text("".join(chunks))
    except Exception: return list()

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
    print(f"\n{CFG['color']}{tr('bat_ok')}{RST}")

def finalize_results(work, all_sources, bl):
    global SUB_MAP
    if CFG.get("blacklist", True) and all_sources:
        dead_cnt = 0
        for s in all_sources:
            if SRC_STATS.get(s, 0) == 0:
                bl[s] = time.time() + 86400; dead_cnt += 1
        save_bl(bl)
        if dead_cnt: print(f"{DIM}{CFG['color']}[*] Quarantine (24h): {dead_cnt} empty sources{RST}")
    by_cc = {}
    if CFG["speed"] and work:
        print(f"\n{CFG['color']}{tr('s5')} ({len(work)})...{RST}")
        scored = list()
        for idx, (ms, cc, cfg) in enumerate(work, 1):
            mbps = run_single_test(cfg, True, False)
            tag = f"{cfg}_{mbps}Mbps"
            scored.append((mbps, cc, tag))
            sys.stdout.write(f"\r  {CFG['color']}-> {tag.split('#').pop()}{RST}" + " " * 45 + "\n")
            draw_bar(idx, len(work))
        scored.sort(key=lambda x: first(x, 0.0), reverse=True)
        fin = list((c for _, _, c in scored))
        for _, cc, c in scored:
            if cc != "FAST": by_cc.setdefault(cc.lower(), list()).append(c)
    else:
        work.sort(key=lambda x: first(x, 9999))
        fin = list((c for _, _, c in work))
        for _, cc, c in work:
            if cc != "FAST": by_cc.setdefault(cc.lower(), list()).append(c)
    favs = load_favs()
    if favs:
        fav_bases = {first(x.split("#"), x) for x in favs}
        fin = favs + [x for x in fin if first(x.split("#"), x) not in fav_bases]
    if fin:
        with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(fin))
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
    print(f"\n{CFG['color']}{tr('done')} {len(fin)}\n{tr('url')} http://127.0.0.1:{s_port}/sub | /clash | /sb{RST}")
    if by_cc:
        extra_urls = " | ".join(f"/{cc}" for cc in sorted(by_cc.keys()))
        print(f"{CFG['color']}By country: [{extra_urls}] (also /clash/cc, /sb/cc){RST}")
    print("Ctrl+C -> Menu")
    try: HTTPServer(("127.0.0.1", s_port), SubHandler).serve_forever()
    except KeyboardInterrupt: pass

def run_scan():
    global CHECKED, FOUND_COUNT, PROC_FLAGS, SRC_STATS
    xray_bin, sb_bin = find_cores()
    if not xray_bin and not sb_bin:
        ans = input(f"\033[93m{tr('no_xray')}{RST}").strip().upper()
        if ans == "Y":
            if not download_cores(False): return
        else: return
    CHECKED, FOUND_COUNT, SRC_STATS = 0, 0, {}
    STOP_EVENT.clear()
    bl = load_bl()
    all_sources = set()
    b_size, PROC_FLAGS = (25, 0x00004000) if CFG["mode"] == 1 else ((45, 0) if CFG["mode"] == 2 else (65, 0))
    print(f"\n{CFG['color']}{tr('s1')}{RST}")
    urls = list()
    if CFG.get("src", 0) in (0, 2, 3):
        tg_urls = get_tg_and_web(bl)
        for s, _ in tg_urls: all_sources.add(s)
        urls.extend(tg_urls)
    if CFG.get("src", 0) in (0, 1, 3):
        repos_dict = {}
        target_cnt = CFG.get("repos", 40)
        per_q = max(10, min(100, (target_cnt // len(SEARCH_QUERIES)) + 5))
        for q_str in SEARCH_QUERIES:
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
            tag = f"gh:{r.get('full_name')}"
            if not CFG.get("blacklist", True) or tag not in bl:
                all_sources.add(tag)
                urls.extend(get_files(r))
            draw_bar(idx, len(repos), f"| URLs: {len(urls)}")
    print(f"{CFG['color']}{tr('s2')} ({len(urls)})...{RST}")
    raw, done = list(), 0
    with ThreadPoolExecutor(max_workers=50) as ex:
        futs = {ex.submit(fetch_url, u): s for s, u in urls}
        for f in as_completed(futs):
            done += 1; s = futs[f]
            try:
                for c in f.result(): raw.append((s, c))
            except Exception: pass
            if done % 10 == 0 or done == len(urls): draw_bar(done, len(urls))
    filtered = smart_prefilter(raw)
    print(f"{CFG['color']}{tr('s3')} ({len(raw)} -> {len(filtered)})...{RST}")
    alive, done = list(), 0
    with ThreadPoolExecutor(max_workers=TCP_WORKERS) as ex:
        for f in as_completed([ex.submit(tcp_ok, item) for item in filtered]):
            done += 1; r = f.result()
            if r: alive.append(r)
            if done % 300 == 0 or done == len(filtered): draw_bar(done, len(filtered), f"| OK: {len(alive)}")
    random.shuffle(alive)
    print(f"{CFG['color']}{tr('s4')} ({len(alive)})...{RST}")
    xray_items, sb_items = list(), list()
    for src, uri in alive:
        sc, _, _ = get_hp(uri)
        if sc in ("hy2", "tuic"): sb_items.append((src, uri))
        else: xray_items.append((src, uri))
    batches = [(xray_items[i:i + b_size], False) for i in range(0, len(xray_items), b_size)] + [(sb_items[i:i + 25], True) for i in range(0, len(sb_items), 25)]
    work = list()
    for batch, is_sb in batches:
        if STOP_EVENT.is_set(): break
        res_list = run_batch_group(batch, is_sb)
        for src, ms, cc, clean in res_list:
            if FOUND_COUNT >= CFG["limit"]: STOP_EVENT.set(); break
            FOUND_COUNT += 1
            SRC_STATS[src] = SRC_STATS.get(src, 0) + 1
            sys.stdout.write(f"\r  {CFG['color']}[+] {clean.split('#').pop()}{RST}" + " " * 45 + "\n")
            work.append((ms, cc, clean))
        CHECKED += len(batch)
        draw_bar(len(alive) if STOP_EVENT.is_set() else min(CHECKED, len(alive)), len(alive), f"| Found: {FOUND_COUNT}")
    finalize_results(work, all_sources, bl)
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
            bl_cnt = len(load_bl())
            c_str = ", ".join(sorted(CFG["countries"])) if CFG["countries"] else tr("all")
            s_src = tr("srcs")[CFG.get("src", 0)]
            b_q = f"{tr('on')} ({bl_cnt})" if CFG.get("blacklist", True) else tr("off")
            px_s = f"{tr('on')} (:{CFG.get('px_port', 10809)})" if CFG.get("use_px", False) else tr("off")
            p_str = tr("protos")[CFG.get("proto", 0)]
            g_str = tr("on") if (CFG.get("geoip", False) or CFG["countries"]) else tr("off")
            s_str = tr("on") if CFG["speed"] else tr("off")
            m_str = tr("modes")[CFG["mode"]]
            _, t_name = TARGETS.get(CFG.get("target", 1), ("", "Basic"))
            b_str = tr("bgs")[CFG.get("bg", 1)]
            vpn_tag = f" | VPN: {ACTIVE_NAME}" if ACTIVE_NAME else ""
            grid = render_bg(CFG.get("bg", 1), tick)
            bot_row = "".join(grid[-2])
            lines = [
                f"{c}{l0}{RST}", f"{c}{l1}{RST}", f"{c}{l2}{RST}",
                f"{c}{l3}{RST}", f"{c}{l4}{RST}", f"{c}{l5}{RST}",
                f"{c}{' ' * 14}:: {tr('sub')} ::{RST}",
                f"{c}{' ' * 22}[ {tr('auth')}{vpn_tag} ]{RST}",
                f"{c}{'=' * 74}{RST}",
                f"  {tr('m1')}", f"  {tr('m2')}",
                f"  {tr('m3'):<40} {c}[{s_src}]{RST}",
                f"  {tr('m4'):<40} {c}[{b_q}]{RST}",
                f"  {tr('m5'):<40} {c}[{px_s}]{RST}",
                f"  {tr('m6'):<40} {c}[{c_str}]{RST}",
                f"  {tr('m7'):<40} {c}[{p_str}]{RST}",
                f"  {tr('m8'):<40} {c}[{g_str}]{RST}",
                f"  {tr('m9'):<40} {c}[{t_name}]{RST}",
                f"  {tr('m10'):<40} {c}[{s_str}]{RST}",
                f"  {tr('m11'):<40} {c}[{m_str}]{RST}",
                f"  {tr('m12'):<40} {c}[{CFG.get('repos', 40)} / {CFG['limit']}]{RST}",
                f"  {tr('m13'):<40} {c}[{CFG['cname']} | {b_str}]{RST}",
                f"  {tr('m14'):<40} {c}[{CFG['lang']} | :{CFG.get('sub_port', 18080)}]{RST}",
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
                        if ch == "1": run_scan(); input(f"\n{tr('back')}")
                        elif ch == "2": manage_servers()
                        elif ch == "3":
                            CFG["src"] = 0 if CFG.get("src", 0) == 3 else CFG.get("src", 0) + 1; save_cfg()
                            print(f"{c}[*] Свои каналы и сайты можно вписать в файл: {CUSTOM_FILE}{RST}"); time.sleep(1.2)
                        elif ch == "4":
                            print("  1. Вкл/Выкл карантин (Toggle)\n  2. Очистить черный список (Clear Blacklist)")
                            q_sel = input("> ").strip()
                            if q_sel == "1": CFG["blacklist"] = not CFG.get("blacklist", True); save_cfg()
                            elif q_sel == "2": save_bl({})
                        elif ch == "5":
                            print("  1. Вкл/Выкл прокси v2rayN (Toggle)\n  2. Изменить HTTP-порт прокси (по умолч. 10809)")
                            px_s_in = input("> ").strip()
                            if px_s_in == "1": CFG["use_px"] = not CFG.get("use_px", False); save_cfg()
                            elif px_s_in == "2":
                                p_val = input("Port (e.g. 10809) > ").strip()
                                if p_val.isdigit() and 1 <= int(p_val) <= 65535: CFG["px_port"] = int(p_val); save_cfg()
                        elif ch == "6":
                            for code, name in COUNTRIES_INFO: print(f"  {c}{code}{RST} - {name}")
                            raw_c = input("\nDE NL FI... (Enter = ALL) > ").upper()
                            CFG["countries"] = set(re.findall(r'[A-Z]{2}', raw_c))
                            if CFG["countries"]: CFG["geoip"] = True
                            save_cfg()
                        elif ch == "7": CFG["proto"] = 0 if CFG.get("proto", 0) == 4 else CFG.get("proto", 0) + 1; save_cfg()
                        elif ch == "8":
                            if not CFG["countries"]: CFG["geoip"] = not CFG.get("geoip", False); save_cfg()
                        elif ch == "9": CFG["target"] = 1 if CFG.get("target", 1) == 3 else CFG.get("target", 1) + 1; save_cfg()
                        elif ch == "10": CFG["speed"] = not CFG.get("speed", True); save_cfg()
                        elif ch == "11": CFG["mode"] = 1 if CFG.get("mode", 3) == 3 else CFG.get("mode", 3) + 1; save_cfg()
                        elif ch == "12":
                            r_val = input("Repos (1 - 250, Enter = skip) > ").strip()
                            if r_val.isdigit() and 1 <= int(r_val) <= 250: CFG["repos"] = int(r_val)
                            l_val = input("Limit (10 - 200, Enter = skip) > ").strip()
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
                            elif sub_s == "2": make_shortcut(); input(f"\n{tr('back')}")
                            elif sub_s == "3": CFG["token"] = input("Token > ").strip(); save_cfg()
                            elif sub_s == "4":
                                sp_val = input("Local sub port (1024 - 65535) > ").strip()
                                if sp_val.isdigit() and 1024 <= int(sp_val) <= 65535: CFG["sub_port"] = int(sp_val); save_cfg()
                            elif sub_s == "5": download_cores(True); input(f"\n{tr('back')}")
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
except Exception: disconnect_vpn(); traceback.print_exc(); input("\nEnter...")
