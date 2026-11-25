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
