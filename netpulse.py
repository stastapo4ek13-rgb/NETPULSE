import base64, json, msvcrt, os, random, re, socket, subprocess, sys, threading, time, traceback, winsound
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import requests

os.system("")
SEARCH_QUERY = "vless trojan ss subscription"
TCP_WORKERS = 300
SPEED_URL = "http://tele2.net"
TIMEOUT, LOCAL_PORT = 3.5, 18080

GH = "https://" + "a" + "pi" + ".github.com"
RAW = "https://" + "raw" + ".githubusercontent.com"

CFG_FILE = "netpulse_config.json"
CFG = {"lang": "RU", "color": "\033[96m", "cname": "Cyan", "countries": set(), "proto": 0, "geoip": False, "speed": True, "mode": 3, "repos": 20, "limit": 40, "token": "", "bg": 1, "target": 1, "xray": r"C:\vpns\v2rayN-windows-64\bin\xray\xray.exe"}

TARGETS = {
    1: ("http://msftconnecttest.com", "Basic Internet / Базовый"),
    2: ("https://youtube.com", "YouTube / Google"),
    3: ("https://discord.com", "Discord / OpenAI")
}

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            CFG.update(data)
            CFG["countries"] = set(data.get("countries", list()))
        except Exception: pass

def save_cfg():
    try:
        out = dict(CFG)
        out["countries"] = list(CFG["countries"])
        with open(CFG_FILE, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
    except Exception: pass

def find_xray():
    if os.path.exists(CFG.get("xray", "")): return CFG["xray"]
    roots = [os.getcwd(), r"C:\vpns", r"C:\Program Files", os.path.expanduser("~")]
    for root in roots:
        if not os.path.exists(root): continue
        for dp, _, fn in os.walk(root):
            if "xray.exe" in fn:
                CFG["xray"] = os.path.join(dp, "xray.exe")
                save_cfg()
                return CFG["xray"]
            if dp.count(os.sep) - root.count(os.sep) > 3: del _[:]
    return ""

def get_hdr():
    h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NetPulse/2.4"}
    if CFG.get("token"): h["Authorization"] = f"Bearer {CFG['token']}"
    return h

load_cfg()
find_xray()
COLORS = {"1": ("\033[92m", "Green / Изумрудный"), "2": ("\033[96m", "Cyan / Неоновый"), "3": ("\033[95m", "Purple / Киберпанк"), "4": ("\033[93m", "Amber / Янтарный"), "5": ("\033[97m", "White / Белый"), "6": ("\033[91m", "Red / Красный")}
COUNTRIES_INFO = [("DE", "Германия / Germany"), ("NL", "Нидерланды / Netherlands"), ("FI", "Финляндия / Finland"), ("SE", "Швеция / Sweden"), ("PL", "Польша / Poland"), ("GB", "Британия / UK"), ("US", "США / USA"), ("TR", "Турция / Turkey"), ("KZ", "Казахстан / Kazakhstan"), ("AE", "ОАЭ / UAE"), ("SG", "Сингапур / Singapore"), ("JP", "Япония / Japan")]
RST, DIM = "\033[0m", "\033[2m"

TXT = {
    "RU": {"sub": "Умный агрегатор VLESS / Trojan / Shadowsocks v2.4", "auth": "Авторы: Gemini & Glitch", "m1": "1. Запустить поиск с GitHub", "m2": "2. Перепроверить best_configs.txt", "m3": "3. Страны фильтрации", "m4": "4. Протокол поиска", "m5": "5. GeoIP проверка стран", "m6": "6. Цель проверки (Сайт)", "m7": "7. Замер скорости скачивания", "m8": "8. Режим нагрузки на ЦП", "m9": "9. Репозиториев для поиска", "m10": "10. Лимит рабочих серверов", "m11": "11. Справочник кодов стран", "m12": "12. Кастомизация (Цвет и Фон)", "m13": "13. Сменить язык (RU / EN)", "m14": "14. Создать ярлык на Рабочем столе", "m15": "15. GitHub API Токен", "m0": "0. Выход", "ask": "Выберите пункт меню > ", "all": "ВСЕ СТРАНЫ", "on": "ВКЛ", "off": "ВЫКЛ", "notok": "НЕТ (60 запр/ч)", "protos": {0: "ВСЕ (VLESS+Trojan+SS)", 1: "Только VLESS", 2: "Только Trojan", 3: "Только Shadowsocks"}, "bgs": {1: "Пульс", 2: "Матрица", 3: "Поток", 0: "Выкл"}, "modes": {1: "Игровой (12 пот., низкий ЦП)", 2: "Средний (35 потоков)", 3: "Турбо (80 потоков)"}, "s1": "[1/5] Поиск репозиториев и веток...", "s2": "[2/5] Скачивание файлов", "s3": "[3/5] Быстрый TCP-отсев", "s4": "[4/5] Проверка через Xray", "s5": "[5/5] Замер скорости скачивания", "done": "Готово! Найдено рабочих:", "url": "Общая подписка:", "back": "Нажмите Enter для возврата в меню...", "bat_ok": "[+] Ярлык NETPULSE.bat создан на Рабочем столе!", "net_err": "[!] Ошибка сети при запросе к GitHub.", "no_xray": "[!] xray.exe не найден! Укажите путь в netpulse_config.json"},
    "EN": {"sub": "Smart VLESS / Trojan / Shadowsocks Validator v2.4", "auth": "Authors: Gemini & Glitch", "m1": "1. Start GitHub Scan", "m2": "2. Re-check best_configs.txt", "m3": "3. Target Countries", "m4": "4. Target Protocol", "m5": "5. GeoIP Country Lookup", "m6": "6. Validation Target Site", "m7": "7. Download Speed Test", "m8": "8. CPU Load Mode", "m9": "9. Repositories to Scan", "m10": "10. Max Working Servers Limit", "m11": "11. Supported Country Codes", "m12": "12. Customization (Color & BG)", "m13": "13. Switch Language (RU / EN)", "m14": "14. Create Desktop Shortcut (.bat)", "m15": "15. GitHub API Token", "m0": "0. Exit", "ask": "Select option > ", "all": "ALL COUNTRIES", "on": "ON", "off": "OFF", "notok": "NONE (60 req/h)", "protos": {0: "ALL (VLESS+Trojan+SS)", 1: "VLESS Only", 2: "Trojan Only", 3: "Shadowsocks Only"}, "bgs": {1: "Pulse", 2: "Matrix", 3: "Stream", 0: "Off"}, "modes": {1: "Gaming (12 thr., Low CPU)", 2: "Balanced (35 threads)", 3: "Turbo (80 threads)"}, "s1": "[1/5] Scanning repositories & trees...", "s2": "[2/5] Downloading files", "s3": "[3/5] Fast TCP filtering", "s4": "[4/5] Xray real validation", "s5": "[5/5] Measuring download speed", "done": "Done! Working servers:", "url": "Main subscription:", "back": "Press Enter to return to menu...", "bat_ok": "[+] Shortcut NETPULSE.bat created on Desktop!", "net_err": "[!] GitHub network timeout.", "no_xray": "[!] xray.exe not found! Set path in netpulse_config.json"}
}

SUB_MAP, CHECKED, FOUND_COUNT, STOP_EVENT, LOCK, PROC_FLAGS = {}, 0, 0, threading.Event(), threading.Lock(), 0
first = lambda s, d="": next(iter(s), d) if s else d
tr = lambda k: TXT[CFG["lang"]][k]

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
    urls = list()
    for _ in range(2):
        try:
            r = requests.get(f"{GH}/repos/{o}/{n}/git/trees/{b}", params={"recursive": "1"}, headers=get_hdr(), timeout=15)
            if r.status_code == 200:
                for i in r.json().get("tree", list()):
                    p = i.get("path", "")
                    if i.get("type") == "blob" and (p.endswith((".txt", ".list")) or "." not in p.split("/")[-1]):
                        if not any(x in p.lower() for x in ("readme", "license", ".git")):
                            urls.append(f"{RAW}/{o}/{n}/{b}/{p}")
                break
        except Exception: time.sleep(1)
    return urls

def parse_text(txt):
    pat = re.compile(r'(?:vless|trojan|ss)://[^\s"\'<>]+')
    m = pat.findall(txt)
    if not m:
        try: m = pat.findall(b64_dec(txt))
        except Exception: pass
    return m

def get_hp(uri):
    sc = first(uri.split("://"), "").lower()
    if sc == "ss":
        res = parse_ss(uri)
        return (sc, res[0], res[1]) if res else (sc, None, None)
    p = urlparse(uri)
    return sc, p.hostname, int(p.port) if p.port else None

def tcp_ok(uri):
    try:
        sc, h, pt = get_hp(uri)
        pr = CFG.get("proto", 0)
        if pr == 1 and sc != "vless": return None
        if pr == 2 and sc != "trojan": return None
        if pr == 3 and sc != "ss": return None
        if not h or not pt or h in ("127.0.0.1", "0.0.0.0", "localhost"): return None
        if sc == "vless" and "security=none" in uri.lower(): return None
        with socket.create_connection((h, pt), timeout=0.9): return uri
    except Exception: return None

def get_cc_one(host):
    try: ip = socket.gethostbyname(host)
    except Exception: ip = host
    for url, key in ((f"https://country.is{ip}", "country"), (f"http://ip-api.com{ip}?fields=countryCode", "countryCode")):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                cc = r.json().get(key)
                if cc: return host, cc.upper()
        except Exception: pass
    return host, "UN"

def build_out(uri):
    sc = first(uri.split("://"), "").lower()
    if sc == "ss":
        res = parse_ss(uri)
        if not res: return None
        h, pt, m, pwd = res
        return {"protocol": "shadowsocks", "settings": {"servers": list(({"address": h, "port": pt, "method": m, "password": pwd},))}}
    p, q = urlparse(uri), parse_qs(urlparse(uri).query)
    net = first(q.get("type"), "tcp")
    if sc == "vless":
        sec = first(q.get("security"), "none")
        if sec == "none": return None
        out = {"protocol": "vless", "settings": {"vnext": list(({"address": p.hostname, "port": int(p.port), "users": list(({"id": p.username, "encryption": first(q.get("encryption"), "none"), "flow": first(q.get("flow"), "")},))},))}, "streamSettings": {"network": net, "security": sec}}
    elif sc == "trojan":
        sec = first(q.get("security"), "tls")
        out = {"protocol": "trojan", "settings": {"servers": list(({"address": p.hostname, "port": int(p.port), "password": unquote(p.username or "")},))}, "streamSettings": {"network": net, "security": sec}}
    else: return None
    if sec == "reality":
        out["streamSettings"]["realitySettings"] = {"serverName": first(q.get("sni"), ""), "fingerprint": first(q.get("fp"), "chrome"), "publicKey": first(q.get("pbk"), ""), "shortId": first(q.get("sid"), ""), "spiderX": unquote(first(q.get("spx"), "/"))}
    elif sec == "tls":
        out["streamSettings"]["tlsSettings"] = {"serverName": first(q.get("sni"), p.hostname), "allowInsecure": first(q.get("allowInsecure"), "0") in ("1", "true")}
    if net == "ws": out["streamSettings"]["wsSettings"] = {"path": unquote(first(q.get("path"), "/")), "headers": {"Host": first(q.get("host"), p.hostname)}}
    elif net == "grpc": out["streamSettings"]["grpcSettings"] = {"serviceName": first(q.get("serviceName"), "")}
    return out

def wait_port(port):
    for _ in range(25):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.05): return True
        except Exception: time.sleep(0.015)
    return False

def run_xray_test(uri, speed_mode=False):
    proc = None
    try:
        out = build_out(uri)
        if not out: return None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            _, port = s.getsockname()
        cfg = {"log": {"loglevel": "none"}, "inbounds": list(({"port": port, "listen": "127.0.0.1", "protocol": "http"},)), "outbounds": list((out,))}
        proc = subprocess.Popen(list((CFG["xray"], "run", "-c", "stdin:")), stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        proc.stdin.write(json.dumps(cfg).encode("utf-8")); proc.stdin.close()
        if not wait_port(port): return 0.0 if speed_mode else None
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        sess = requests.Session(); sess.trust_env = False
        t0 = time.time()
        if not speed_mode:
            pair = TARGETS.get(CFG.get("target", 1), ("http://msftconnecttest.com", ""))
            t_url = first(pair, "http://msftconnecttest.com")
            res = sess.get(t_url, proxies=px, timeout=TIMEOUT)
            return int((time.time() - t0) * 1000) if res.status_code in (200, 204) else None
        dl = 0
        with sess.get(SPEED_URL, proxies=px, stream=True, timeout=8) as r:
            for ch in r.iter_content(65536):
                dl += len(ch)
                if dl >= 5242880 or (time.time() - t0) > 6: break
        return round((dl * 8) / (max(time.time() - t0, 0.01) * 1000000), 1)
    except Exception: return 0.0 if speed_mode else None
    finally:
        if proc:
            try: proc.kill()
            except Exception: pass
def check_worker(uri, tot):
    global CHECKED, FOUND_COUNT
    if STOP_EVENT.is_set(): return None
    ms = run_xray_test(uri, False)
    res_item = None
    if ms is not None:
        sc, h, _ = get_hp(uri)
        need_geo = bool(CFG["countries"]) or CFG.get("geoip", False)
        _, cc = get_cc_one(h) if need_geo else ("", "FAST")
        if not CFG["countries"] or cc in CFG["countries"]:
            clean = f"{first(uri.split('#'), uri)}#{sc.upper()}_{cc}_{ms}ms"
            with LOCK:
                FOUND_COUNT += 1
                with open("best_configs.txt", "a", encoding="utf-8") as f: f.write(clean + "\n")
                if FOUND_COUNT >= CFG["limit"]: STOP_EVENT.set()
                sys.stdout.write(f"\r  {CFG['color']}[+] {clean.split('#')[-1]}{RST}" + " " * 45 + "\n")
            res_item = (ms, cc, clean)
    with LOCK:
        CHECKED += 1
        if CHECKED % 15 == 0 or CHECKED == tot or STOP_EVENT.is_set():
            draw_bar(tot if STOP_EVENT.is_set() else CHECKED, tot, f"| Found: {FOUND_COUNT}")
    return res_item

class SubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = self.path.strip("/").lower() or "sub"
        if key in SUB_MAP:
            self.send_response(200); self.send_header("Content-type", "text/plain; charset=utf-8"); self.end_headers()
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

def finalize_results(work):
    global SUB_MAP
    by_cc = {}
    if CFG["speed"] and work:
        print(f"\n{CFG['color']}{tr('s5')} ({len(work)})...{RST}")
        scored = list()
        for idx, (ms, cc, cfg) in enumerate(work, 1):
            mbps = run_xray_test(cfg, True)
            tag = f"{cfg}_{mbps}Mbps"
            scored.append((mbps, cc, tag))
            sys.stdout.write(f"\r  {CFG['color']}-> {tag.split('#')[-1]}{RST}" + " " * 45 + "\n")
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
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(fin))
    SUB_MAP = {"sub": base64.b64encode("\n".join(fin).encode("utf-8")).decode("utf-8")}
    if by_cc:
        os.makedirs("configs_by_country", exist_ok=True)
        for cc, items in by_cc.items():
            with open(os.path.join("configs_by_country", f"best_{cc.upper()}.txt"), "w", encoding="utf-8") as f: f.write("\n".join(items))
            SUB_MAP[cc] = base64.b64encode("\n".join(items).encode("utf-8")).decode("utf-8")
    try: winsound.Beep(880, 180); winsound.Beep(1174, 240)
    except Exception: pass
    print(f"\n{CFG['color']}{tr('done')} {len(fin)}\n{tr('url')} http://127.0.0.1:{LOCAL_PORT}/sub{RST}")
    if by_cc:
        extra_urls = " | ".join(f"/{cc}" for cc in sorted(by_cc.keys()))
        print(f"{CFG['color']}By country: http://127.0.0.1:{LOCAL_PORT} [{extra_urls}]{RST}")
    print("Ctrl+C -> Menu")
    try: HTTPServer(("127.0.0.1", LOCAL_PORT), SubHandler).serve_forever()
    except KeyboardInterrupt: pass

def run_scan(recheck_mode=False):
    global CHECKED, FOUND_COUNT, PROC_FLAGS
    if not find_xray(): return print(f"\033[91m{tr('no_xray')}{RST}")
    CHECKED, FOUND_COUNT = 0, 0
    STOP_EVENT.clear()
    workers, PROC_FLAGS = (12, 0x00004000) if CFG["mode"] == 1 else ((35, 0) if CFG["mode"] == 2 else (80, 0))
    if recheck_mode:
        if not os.path.exists("best_configs.txt"): return print("[!] best_configs.txt not found!")
        with open("best_configs.txt", "r", encoding="utf-8") as f:
            alive = list((first(ln.strip().split("#"), ln.strip()) for ln in f if ln.strip()))
        open("best_configs.txt", "w", encoding="utf-8").close()
    else:
        open("best_configs.txt", "w", encoding="utf-8").close()
        print(f"\n{CFG['color']}{tr('s1')}{RST}")
        repos = None
        for attempt in range(3):
            try:
                r = requests.get(f"{GH}/search/repositories", params={"q": SEARCH_QUERY, "sort": "updated", "order": "desc", "per_page": CFG.get("repos", 20)}, headers=get_hdr(), timeout=20)
                r.raise_for_status(); repos = r.json().get("items", list()); break
            except Exception:
                if attempt < 2: time.sleep(2)
        if repos is None: return print(f"\033[91m{tr('net_err')}{RST}")
        urls = list()
        for idx, r in enumerate(repos, 1):
            urls.extend(get_files(r))
            draw_bar(idx, len(repos), f"| Files: {len(urls)}")
        print(f"{CFG['color']}{tr('s2')} ({len(urls)})...{RST}")
        raw, done = set(), 0
        with ThreadPoolExecutor(max_workers=50) as ex:
            for f in as_completed(list((ex.submit(lambda u: parse_text(requests.get(u, timeout=8).text), u) for u in urls))):
                done += 1
                try: raw.update(f.result())
                except Exception: pass
                if done % 10 == 0 or done == len(urls): draw_bar(done, len(urls))
        uniq = {}
        for c in raw:
            try:
                sc, h, pt = get_hp(c)
                if h and pt and f"{sc}:{h}:{pt}" not in uniq: uniq[f"{sc}:{h}:{pt}"] = c
            except Exception: continue
        print(f"{CFG['color']}{tr('s3')} ({len(uniq)})...{RST}")
        alive, done = list(), 0
        with ThreadPoolExecutor(max_workers=TCP_WORKERS) as ex:
            for f in as_completed(list((ex.submit(tcp_ok, c) for c in uniq.values()))):
                done += 1
                r = f.result()
                if r: alive.append(r)
                if done % 300 == 0 or done == len(uniq): draw_bar(done, len(uniq), f"| TCP OK: {len(alive)}")
        random.shuffle(alive)
    print(f"{CFG['color']}{tr('s4')} ({len(alive)})...{RST}")
    work = list()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed(list((ex.submit(check_worker, u, len(alive)) for u in alive))):
            r = f.result()
            if r: work.append(r)
    finalize_results(work)
def render_bg(bg_type, tick, w=78, h=28):
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
            c_str = ", ".join(sorted(CFG["countries"])) if CFG["countries"] else tr("all")
            p_str = tr("protos")[CFG.get("proto", 0)]
            g_str = tr("on") if (CFG.get("geoip", False) or CFG["countries"]) else tr("off")
            s_str = tr("on") if CFG["speed"] else tr("off")
            m_str = tr("modes")[CFG["mode"]]
            _, t_name = TARGETS.get(CFG.get("target", 1), ("", "Basic"))
            tk = CFG.get("token", "")
            tk_str = f"{tk[:8]}..." if len(tk) > 8 else (tk if tk else tr("notok"))
            b_str = tr("bgs")[CFG.get("bg", 1)]
            grid = render_bg(CFG.get("bg", 1), tick)
            bot_row = "".join(grid[-2])
            lines = [
                f"{c}{l0}{RST}", f"{c}{l1}{RST}", f"{c}{l2}{RST}",
                f"{c}{l3}{RST}", f"{c}{l4}{RST}", f"{c}{l5}{RST}",
                f"{c}{' ' * 12}:: {tr('sub')} ::{RST}",
                f"{c}{' ' * 24}[ {tr('auth')} ]{RST}",
                f"{c}{'=' * 74}{RST}",
                f"  {tr('m1')}",
                f"  {tr('m2')}",
                f"  {tr('m3'):<36} {c}[{c_str}]{RST}",
                f"  {tr('m4'):<36} {c}[{p_str}]{RST}",
                f"  {tr('m5'):<36} {c}[{g_str}]{RST}",
                f"  {tr('m6'):<36} {c}[{t_name}]{RST}",
                f"  {tr('m7'):<36} {c}[{s_str}]{RST}",
                f"  {tr('m8'):<36} {c}[{m_str}]{RST}",
                f"  {tr('m9'):<36} {c}[{CFG.get('repos', 20)}]{RST}",
                f"  {tr('m10'):<36} {c}[{CFG['limit']}]{RST}",
                f"  {tr('m11')}",
                f"  {tr('m12'):<36} {c}[{CFG['cname']} | {b_str}]{RST}",
                f"  {tr('m13'):<36} {c}[{CFG['lang']}]{RST}",
                f"  {tr('m14')}",
                f"  {tr('m15'):<36} {c}[{tk_str}]{RST}",
                f"  {tr('m0')}",
                f"{c}{'=' * 74}{RST}",
                f"{DIM}{c}{bot_row}{RST}",
                f"{tr('ask')}{c}{buf}{RST}   "
            ]
            out = list(("\033[H",))
            for idx, ln in enumerate(lines):
                if idx < 26 and CFG.get("bg", 1) != 0:
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
                        if ch == "1": run_scan(False); input(f"\n{tr('back')}")
                        elif ch == "2": run_scan(True); input(f"\n{tr('back')}")
                        elif ch == "3":
                            raw_c = input("DE NL FI... (Enter = ALL) > ").upper()
                            CFG["countries"] = set(re.findall(r'[A-Z]{2}', raw_c))
                            if CFG["countries"]: CFG["geoip"] = True
                            save_cfg()
                        elif ch == "4": CFG["proto"] = 0 if CFG.get("proto", 0) == 3 else CFG.get("proto", 0) + 1; save_cfg()
                        elif ch == "5":
                            if not CFG["countries"]: CFG["geoip"] = not CFG.get("geoip", False); save_cfg()
                        elif ch == "6": CFG["target"] = 1 if CFG.get("target", 1) == 3 else CFG.get("target", 1) + 1; save_cfg()
                        elif ch == "7": CFG["speed"] = not CFG["speed"]; save_cfg()
                        elif ch == "8": CFG["mode"] = 1 if CFG["mode"] == 3 else CFG["mode"] + 1; save_cfg()
                        elif ch == "9":
                            val = input("1 - 100 > ").strip()
                            if val.isdigit() and 1 <= int(val) <= 100: CFG["repos"] = int(val); save_cfg()
                        elif ch == "10":
                            val = input("10 - 200 > ").strip()
                            if val.isdigit() and int(val) > 0: CFG["limit"] = int(val); save_cfg()
                        elif ch == "11":
                            print(f"\n{c}--- ISO 3166-1 Alpha-2 ---{RST}")
                            for code, name in COUNTRIES_INFO: print(f"  {c}{code}{RST} - {name}")
                            input(f"\n{tr('back')}")
                        elif ch == "12":
                            print(f"\n{c}--- Цвет / Color ---{RST}")
                            for k, (col, nm) in COLORS.items(): print(f"  {k}. {col}{nm}{RST}")
                            sel = input("> ").strip()
                            if sel in COLORS: CFG["color"], CFG["cname"] = COLORS[sel]
                            print(f"\n{c}--- Задний фон / Background ---{RST}")
                            print("  1. Пульс / Pulse\n  2. Падающие цифры / Matrix\n  3. Сетевой поток / Stream\n  0. Выключить / Off")
                            bsel = input("> ").strip()
                            if bsel in ("0", "1", "2", "3"): CFG["bg"] = int(bsel)
                            save_cfg()
                        elif ch == "13": CFG["lang"] = "EN" if CFG["lang"] == "RU" else "RU"; save_cfg()
                        elif ch == "14": make_shortcut(); input(f"\n{tr('back')}")
                        elif ch == "15":
                            CFG["token"] = input("Token (Enter = Clear) > ").strip(); save_cfg()
                        elif ch == "0": return
                        os.system("cls" if os.name == "nt" else "clear")
                        sys.stdout.write("\033[?25l")
                        break
                    elif ch_in == "\b": buf = buf[:-1]
                    elif ch_in.isprintable(): buf += ch_in
                time.sleep(0.015)
    finally:
        sys.stdout.write("\033[?25h")

try: show_menu()
except Exception: traceback.print_exc(); input("\nEnter...")
