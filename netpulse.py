import base64, json, msvcrt, os, random, re, socket, subprocess, sys, threading, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import requests

os.system("")
XRAY_PATH = r"C:\vpns\v2rayN-windows-64\bin\xray\xray.exe"
SEARCH_QUERY = "vless reality subscription"
MAX_REPOS, TCP_WORKERS = 20, 300
TEST_URL = "http://msftconnecttest.com"
SPEED_URL = "http://tele2.net"
TIMEOUT, LOCAL_PORT = 3.0, 18080

GH = "https://" + "a" + "pi" + ".github.com"
RAW = "https://" + "raw" + ".githubusercontent.com"

CFG_FILE = "netpulse_config.json"
CFG = {"lang": "RU", "color": "\033[96m", "cname": "Cyan", "countries": set(), "speed": True, "mode": 3, "limit": 40, "token": "", "bg": 1}

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

def get_hdr():
    h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NetPulse/2.0"}
    if CFG.get("token"): h["Authorization"] = f"Bearer {CFG['token']}"
    return h

load_cfg()
COLORS = {"1": ("\033[92m", "Green / Изумрудный"), "2": ("\033[96m", "Cyan / Неоновый"), "3": ("\033[95m", "Purple / Киберпанк"), "4": ("\033[93m", "Amber / Янтарный"), "5": ("\033[97m", "White / Белый"), "6": ("\033[91m", "Red / Красный")}
COUNTRIES_INFO = [("DE", "Германия / Germany"), ("NL", "Нидерланды / Netherlands"), ("FI", "Финляндия / Finland"), ("SE", "Швеция / Sweden"), ("PL", "Польша / Poland"), ("GB", "Британия / UK"), ("US", "США / USA"), ("TR", "Турция / Turkey"), ("KZ", "Казахстан / Kazakhstan"), ("AE", "ОАЭ / UAE"), ("SG", "Сингапур / Singapore"), ("JP", "Япония / Japan")]
RST, DIM = "\033[0m", "\033[2m"

TXT = {
    "RU": {"sub": "Умный агрегатор и валидатор VLESS / Trojan", "auth": "Авторы: Gemini & Glitch", "m1": "1. Запустить поиск и проверку", "m2": "2. Страны фильтрации", "m3": "3. Замер скорости скачивания", "m4": "4. Режим нагрузки на ЦП", "m5": "5. Лимит рабочих серверов", "m6": "6. Справочник кодов стран", "m7": "7. Кастомизация (Цвет и Фон)", "m8": "8. Сменить язык (RU / EN)", "m9": "9. Создать ярлык на Рабочем столе", "m10": "10. GitHub API Токен", "m0": "0. Выход", "ask": "Выберите пункт меню > ", "all": "ВСЕ СТРАНЫ", "on": "ВКЛ", "off": "ВЫКЛ", "notok": "НЕТ (60 запр/ч)", "bgs": {1: "Пульс", 2: "Матрица", 3: "Поток", 0: "Выкл"}, "modes": {1: "Игровой (12 пот., низкий ЦП)", 2: "Средний (35 потоков)", 3: "Турбо (80 потоков)"}, "s1": "[1/5] Поиск репозиториев...", "s2": "[2/5] Скачивание файлов", "s3": "[3/5] Быстрый TCP-отсев", "s4": "[4/5] Проверка через Xray", "s5": "[5/5] Замер скорости скачивания", "done": "Готово! Найдено рабочих:", "url": "Локальная подписка:", "back": "Нажмите Enter для возврата в меню...", "bat_ok": "[+] Ярлык NETPULSE.bat создан на Рабочем столе!", "net_err": "[!] Ошибка сети при запросе к GitHub. Попробуйте еще раз."},
    "EN": {"sub": "Smart VLESS / Trojan Aggregator & Validator", "auth": "Authors: Gemini & Glitch", "m1": "1. Start Scan & Validation", "m2": "2. Target Countries", "m3": "3. Download Speed Test", "m4": "4. CPU Load Mode", "m5": "5. Max Working Servers Limit", "m6": "6. Supported Country Codes", "m7": "7. Customization (Color & BG)", "m8": "8. Switch Language (RU / EN)", "m9": "9. Create Desktop Shortcut (.bat)", "m10": "10. GitHub API Token", "m0": "0. Exit", "ask": "Select option > ", "all": "ALL COUNTRIES", "on": "ON", "off": "OFF", "notok": "NONE (60 req/h)", "bgs": {1: "Pulse", 2: "Matrix", 3: "Stream", 0: "Off"}, "modes": {1: "Gaming (12 thr., Low CPU)", 2: "Balanced (35 threads)", 3: "Turbo (80 threads)"}, "s1": "[1/5] Searching repositories...", "s2": "[2/5] Downloading files", "s3": "[3/5] Fast TCP filtering", "s4": "[4/5] Xray real validation", "s5": "[5/5] Measuring download speed", "done": "Done! Working servers:", "url": "Local subscription:", "back": "Press Enter to return to menu...", "bat_ok": "[+] Shortcut NETPULSE.bat created on Desktop!", "net_err": "[!] GitHub network timeout. Please try again."}
}

SUB_DATA, CHECKED, FOUND_COUNT, STOP_EVENT, LOCK, PROC_FLAGS = "", 0, 0, threading.Event(), threading.Lock(), 0
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
    pat = re.compile(r'(?:vless|trojan)://[^\s"\'<>]+')
    m = pat.findall(txt)
    if not m:
        try: m = pat.findall(base64.b64decode(txt.strip() + "=" * (-len(txt.strip()) % 4)).decode("utf-8", errors="ignore"))
        except Exception: pass
    return m

def tcp_ok(uri):
    try:
        p = urlparse(uri)
        if p.hostname in ("127.0.0.1", "0.0.0.0", "localhost"): return None
        if p.scheme.lower() == "vless" and "security=none" in uri.lower(): return None
        with socket.create_connection((p.hostname, int(p.port)), timeout=0.9): return uri
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
    p, q, sc = urlparse(uri), parse_qs(urlparse(uri).query), urlparse(uri).scheme.lower()
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
        proc = subprocess.Popen(list((XRAY_PATH, "run", "-c", "stdin:")), stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=PROC_FLAGS)
        proc.stdin.write(json.dumps(cfg).encode("utf-8")); proc.stdin.close()
        if not wait_port(port): return 0.0 if speed_mode else None
        px = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
        sess = requests.Session(); sess.trust_env = False
        t0 = time.time()
        if not speed_mode:
            res = sess.get(TEST_URL, proxies=px, timeout=TIMEOUT)
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
        _, cc = get_cc_one(urlparse(uri).hostname)
        if not CFG["countries"] or cc in CFG["countries"]:
            clean = f"{first(uri.split('#'), uri)}#{urlparse(uri).scheme.upper()}_{cc}_{ms}ms"
            with LOCK:
                FOUND_COUNT += 1
                with open("best_configs.txt", "a", encoding="utf-8") as f: f.write(clean + "\n")
                if FOUND_COUNT >= CFG["limit"]: STOP_EVENT.set()
                sys.stdout.write(f"\r  {CFG['color']}[+] {clean.split('#')[-1]}{RST}" + " " * 45 + "\n")
            res_item = (ms, clean)
    with LOCK:
        CHECKED += 1
        if CHECKED % 15 == 0 or CHECKED == tot or STOP_EVENT.is_set():
            draw_bar(tot if STOP_EVENT.is_set() else CHECKED, tot, f"| Found: {FOUND_COUNT}")
    return res_item

class SubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/sub":
            self.send_response(200); self.send_header("Content-type", "text/plain; charset=utf-8"); self.end_headers()
            self.wfile.write(SUB_DATA.encode("utf-8"))
        else: self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

def make_shortcut():
    desk = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desk): desk = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    bat_path = os.path.join(desk, "NETPULSE.bat")
    work_dir = os.path.dirname(os.path.abspath(first(sys.argv, "parcer.py")))
    script_name = os.path.basename(first(sys.argv, "parcer.py"))
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(f'@echo off\nchcp 65001 >nul\ncd /d "{work_dir}"\n"{sys.executable}" "{script_name}"\n')
    print(f"\n{CFG['color']}{tr('bat_ok')}{RST}")

def run_scan():
    global SUB_DATA, CHECKED, FOUND_COUNT, PROC_FLAGS
    if not os.path.exists(XRAY_PATH): return print(f"[!] Not found: {XRAY_PATH}")
    CHECKED, FOUND_COUNT = 0, 0
    STOP_EVENT.clear()
    workers, PROC_FLAGS = (12, 0x00004000) if CFG["mode"] == 1 else ((35, 0) if CFG["mode"] == 2 else (80, 0))
    open("best_configs.txt", "w", encoding="utf-8").close()
    print(f"\n{CFG['color']}{tr('s1')}{RST}")
    repos = None
    for attempt in range(3):
        try:
            r = requests.get(f"{GH}/search/repositories", params={"q": SEARCH_QUERY, "sort": "updated", "order": "desc", "per_page": MAX_REPOS}, headers=get_hdr(), timeout=20)
            r.raise_for_status()
            repos = r.json().get("items", list())
            break
        except Exception:
            if attempt < 2: time.sleep(2)
    if repos is None: return print(f"\033[91m{tr('net_err')}{RST}")
    urls = list()
    for r in repos: urls.extend(get_files(r))
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
            p = urlparse(c)
            if p.hostname and p.port and f"{p.scheme}:{p.hostname}:{p.port}" not in uniq: uniq[f"{p.scheme}:{p.hostname}:{p.port}"] = c
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
    if CFG["speed"] and work:
        print(f"\n{CFG['color']}{tr('s5')} ({len(work)})...{RST}")
        scored = list()
        for idx, (ms, cfg) in enumerate(work, 1):
            mbps = run_xray_test(cfg, True)
            tag = f"{cfg}_{mbps}Mbps"
            scored.append((mbps, tag))
            sys.stdout.write(f"\r  {CFG['color']}-> {tag.split('#')[-1]}{RST}" + " " * 45 + "\n")
            draw_bar(idx, len(work))
        scored.sort(key=lambda x: first(x, 0.0), reverse=True)
        fin = list((c for _, c in scored))
    else:
        work.sort(key=lambda x: first(x, 9999))
        fin = list((c for _, c in work))
    with open("best_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(fin))
    SUB_DATA = base64.b64encode("\n".join(fin).encode("utf-8")).decode("utf-8")
    print(f"\n{CFG['color']}{tr('done')} {len(fin)}\n{tr('url')} http://127.0.0.1:{LOCAL_PORT}/sub{RST}")
    print("Ctrl+C -> Menu")
    try: HTTPServer(("127.0.0.1", LOCAL_PORT), SubHandler).serve_forever()
    except KeyboardInterrupt: pass
def render_bg(bg_type, tick, w=78, h=23):
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
    logo = ("  ███╗   ██╗███████╗████████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗",
            "  ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝",
            "  ██╔██╗ ██║█████╗     ██║   ██████╔╝██║   ██║██║     ███████╗█████╗  ",
            "  ██║╚██╗██║██╔══╝     ██║   ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  ",
            "  ██║ ╚████║███████╗   ██║   ██║     ╚██████╔╝███████╗███████║███████╗",
            "  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝")
    tick, buf = 0, ""
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    try:
        while True:
            c = CFG["color"]
            c_str = ", ".join(sorted(CFG["countries"])) if CFG["countries"] else tr("all")
            s_str = tr("on") if CFG["speed"] else tr("off")
            m_str = tr("modes")[CFG["mode"]]
            tk = CFG.get("token", "")
            t_str = f"{tk[:8]}..." if len(tk) > 8 else (tk if tk else tr("notok"))
            b_str = tr("bgs")[CFG.get("bg", 1)]
            grid = render_bg(CFG.get("bg", 1), tick)
            lines = [
                f"{c}{logo[0]}{RST}", f"{c}{logo[1]}{RST}", f"{c}{logo[2]}{RST}",
                f"{c}{logo[3]}{RST}", f"{c}{logo[4]}{RST}", f"{c}{logo[5]}{RST}",
                f"{c}{' ' * 16}:: {tr('sub')} ::{RST}",
                f"{c}{' ' * 24}[ {tr('auth')} ]{RST}",
                f"{c}{'=' * 74}{RST}",
                f"  {tr('m1')}",
                f"  {tr('m2'):<36} {c}[{c_str}]{RST}",
                f"  {tr('m3'):<36} {c}[{s_str}]{RST}",
                f"  {tr('m4'):<36} {c}[{m_str}]{RST}",
                f"  {tr('m5'):<36} {c}[{CFG['limit']}]{RST}",
                f"  {tr('m6')}",
                f"  {tr('m7'):<36} {c}[{CFG['cname']} | {b_str}]{RST}",
                f"  {tr('m8'):<36} {c}[{CFG['lang']}]{RST}",
                f"  {tr('m9')}",
                f"  {tr('m10'):<36} {c}[{t_str}]{RST}",
                f"  {tr('m0')}",
                f"{c}{'=' * 74}{RST}",
                f"{DIM}{''.join(grid[21])}{RST}",
                f"{tr('ask')}{c}{buf}{RST}   "
            ]
            out = list(("\033[H",))
            for idx, ln in enumerate(lines):
                if idx < 21 and CFG.get("bg", 1) != 0:
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
                        elif ch == "2":
                            raw_c = input("DE NL FI... (Enter = ALL) > ").upper()
                            CFG["countries"] = set(re.findall(r'[A-Z]{2}', raw_c)); save_cfg()
                        elif ch == "3": CFG["speed"] = not CFG["speed"]; save_cfg()
                        elif ch == "4": CFG["mode"] = 1 if CFG["mode"] == 3 else CFG["mode"] + 1; save_cfg()
                        elif ch == "5":
                            val = input("10 - 200 > ").strip()
                            if val.isdigit() and int(val) > 0: CFG["limit"] = int(val); save_cfg()
                        elif ch == "6":
                            print(f"\n{c}--- ISO 3166-1 Alpha-2 ---{RST}")
                            for code, name in COUNTRIES_INFO: print(f"  {c}{code}{RST} - {name}")
                            input(f"\n{tr('back')}")
                        elif ch == "7":
                            print(f"\n{c}--- Цвет / Color ---{RST}")
                            for k, (col, nm) in COLORS.items(): print(f"  {k}. {col}{nm}{RST}")
                            sel = input("> ").strip()
                            if sel in COLORS: CFG["color"], CFG["cname"] = COLORS[sel]
                            print(f"\n{c}--- Задний фон / Background ---{RST}")
                            print("  1. Пульс / Pulse\n  2. Падающие цифры / Matrix\n  3. Сетевой поток / Stream\n  0. Выключить / Off")
                            bsel = input("> ").strip()
                            if bsel in ("0", "1", "2", "3"): CFG["bg"] = int(bsel)
                            save_cfg()
                        elif ch == "8": CFG["lang"] = "EN" if CFG["lang"] == "RU" else "RU"; save_cfg()
                        elif ch == "9": make_shortcut(); input(f"\n{tr('back')}")
                        elif ch == "10":
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
