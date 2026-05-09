#!/usr/bin/env python3
"""
central-mc — Terminal media player with audio visualiser
Usage: central-mc
"""

import curses
import os
import sys
import time
import math
import threading
import subprocess
import struct
import glob
import random
from collections import deque

# ── Audio capture via pacat ──────────────────────────────────────────────────

SAMPLE_RATE = 44100
CHUNK = 1024
CHANNELS = 1

class AudioCapture:
    def __init__(self):
        self.buffer = deque(maxlen=8)
        self.samples = [0.0] * CHUNK
        self.running = False
        self._proc = None
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._capture, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._proc:
            try:
                self._proc.terminate()
            except:
                pass

    def _capture(self):
        try:
            self._proc = subprocess.Popen(
                ["pacat", "--record", "--channels=1",
                 "--format=s16le", f"--rate={SAMPLE_RATE}",
                 "--latency-msec=20"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            bytes_per_chunk = CHUNK * 2
            while self.running:
                data = self._proc.stdout.read(bytes_per_chunk)
                if not data:
                    break
                if len(data) == bytes_per_chunk:
                    samples = struct.unpack(f"{CHUNK}h", data)
                    self.samples = [s / 32768.0 for s in samples]
        except Exception:
            pass

# ── FFT helpers ──────────────────────────────────────────────────────────────

def compute_fft(samples, n_bars):
    n = len(samples)
    if n == 0:
        return [0.0] * n_bars
    # Simple DFT magnitude for n_bars frequency bins
    fft = []
    half = n // 2
    spectrum = []
    # Use numpy-free FFT approximation via Cooley-Tukey would be complex;
    # instead use pacat + manual DFT on downsampled data
    try:
        import numpy as np
        data = np.array(samples)
        freq = np.abs(np.fft.rfft(data, n=n))[:half]
        # Map to n_bars using log scale
        bars = []
        log_min = math.log(1)
        log_max = math.log(max(half, 2))
        for i in range(n_bars):
            lo = int(math.exp(log_min + (log_max - log_min) * i / n_bars))
            hi = int(math.exp(log_min + (log_max - log_min) * (i + 1) / n_bars))
            hi = max(hi, lo + 1)
            hi = min(hi, half)
            chunk = freq[lo:hi]
            val = float(np.mean(chunk)) if len(chunk) > 0 else 0.0
            bars.append(val)
        # Normalize
        mx = max(bars) if max(bars) > 0 else 1
        return [min(b / mx, 1.0) for b in bars]
    except ImportError:
        return [0.0] * n_bars

def compute_waveform(samples, n_points):
    if not samples:
        return [0.0] * n_points
    step = max(1, len(samples) // n_points)
    wave = []
    for i in range(n_points):
        idx = i * step
        if idx < len(samples):
            wave.append(samples[idx])
        else:
            wave.append(0.0)
    return wave

# ── Media player subprocess ──────────────────────────────────────────────────

class MediaPlayer:
    def __init__(self):
        self._proc = None
        self.current_file = None
        self.playing = False

    def play(self, path):
        self.stop()
        self.current_file = path
        self.playing = True
        ext = os.path.splitext(path)[1].lower()
        # Use mpv if available, fallback to ffplay
        player = "mpv" if self._has("mpv") else "ffplay"
        if player == "mpv":
            cmd = ["mpv", "--no-video" if ext in (".mp3",".flac",".ogg",".wav",".m4a") else "--", path]
            if ext in (".mp3",".flac",".ogg",".wav",".m4a"):
                cmd = ["mpv", "--no-video", path]
            else:
                cmd = ["mpv", path]
        else:
            cmd = ["ffplay", "-nodisp", "-autoexit", path]
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            self.playing = False

    def stop(self):
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2)
            except:
                pass
            self._proc = None
        self.playing = False
        self.current_file = None

    def is_running(self):
        if self._proc:
            return self._proc.poll() is None
        return False

    def _has(self, cmd):
        try:
            subprocess.run(["which", cmd], capture_output=True, check=True)
            return True
        except:
            return False

# ── Visualiser modes ─────────────────────────────────────────────────────────

VIS_MODES = ["bars", "waveform", "spectrum", "circle"]

def draw_bars(win, samples, h, w, color_pair):
    n = max(4, w - 2)
    bars = compute_fft(samples, n)
    for i, val in enumerate(bars):
        x = i + 1
        if x >= w - 1:
            break
        bar_h = int(val * (h - 2))
        for row in range(h - 2, h - 2 - bar_h, -1):
            if 0 < row < h - 1:
                try:
                    win.addch(row, x, '█', color_pair)
                except curses.error:
                    pass

def draw_waveform(win, samples, h, w, color_pair):
    n = w - 2
    wave = compute_waveform(samples, n)
    mid = (h - 2) // 2 + 1
    prev_y = mid
    for i, val in enumerate(wave):
        x = i + 1
        if x >= w - 1:
            break
        y = int(mid - val * (mid - 1))
        y = max(1, min(h - 2, y))
        try:
            win.addch(y, x, '●', color_pair)
            # Draw line between prev and current
            if abs(y - prev_y) > 1:
                step = 1 if y > prev_y else -1
                for ly in range(prev_y + step, y, step):
                    if 1 <= ly <= h - 2:
                        win.addch(ly, x, '│', color_pair)
        except curses.error:
            pass
        prev_y = y
    # Draw zero line
    for x in range(1, w - 1):
        try:
            ch = win.inch(mid, x) & 0xFF
            if ch == ord(' '):
                win.addch(mid, x, '─', curses.color_pair(3))
        except curses.error:
            pass

def draw_spectrum(win, samples, h, w, color_pair):
    """Mirror bars top and bottom"""
    n = max(4, w - 2)
    bars = compute_fft(samples, n)
    mid = (h - 2) // 2 + 1
    for i, val in enumerate(bars):
        x = i + 1
        if x >= w - 1:
            break
        bar_h = int(val * (mid - 1))
        for offset in range(bar_h):
            try:
                win.addch(mid - 1 - offset, x, '▓', color_pair)
                win.addch(mid + 1 + offset, x, '▓', color_pair)
            except curses.error:
                pass
        try:
            win.addch(mid, x, '█', color_pair)
        except curses.error:
            pass

def draw_circle(win, samples, h, w, color_pair):
    """Radial visualiser"""
    bars = compute_fft(samples, 64)
    cx = w // 2
    cy = (h - 2) // 2 + 1
    r_base = min(cx, cy) // 2
    chars = '·∘○◯'
    for i, val in enumerate(bars):
        angle = (2 * math.pi * i) / len(bars)
        r = r_base + int(val * r_base * 0.8)
        for dr in range(r_base, r + 1):
            px = int(cx + dr * math.cos(angle) * 2)  # *2 for terminal aspect
            py = int(cy + dr * math.sin(angle) * 0.5)
            if 1 <= py <= h - 2 and 1 <= px <= w - 2:
                try:
                    win.addch(py, px, '█', color_pair)
                except curses.error:
                    pass

# ── File browser ─────────────────────────────────────────────────────────────

MEDIA_EXTS = {'.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac',
              '.mp4', '.mkv', '.avi', '.mov', '.webm', '.wmv'}

def get_media_files(path):
    files = []
    try:
        for f in sorted(os.listdir(path)):
            full = os.path.join(path, f)
            if os.path.isdir(full):
                files.append(('dir', f, full))
            elif os.path.splitext(f)[1].lower() in MEDIA_EXTS:
                files.append(('file', f, full))
    except PermissionError:
        pass
    return files

# ── Main TUI ─────────────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()

    # Colour pairs
    curses.init_pair(1, curses.COLOR_RED, -1)       # bars / accent
    curses.init_pair(2, curses.COLOR_WHITE, -1)     # text
    curses.init_pair(3, curses.COLOR_BLACK, -1)     # dim
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # selected
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)    # header
    curses.init_pair(6, curses.COLOR_CYAN, -1)      # waveform
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)   # spectrum

    audio = AudioCapture()
    audio.start()

    player = MediaPlayer()

    # State
    vis_mode_idx = 0
    view = "browser"   # "browser" | "visualiser"
    browser_path = os.path.expanduser("~")
    browser_files = get_media_files(browser_path)
    browser_sel = 0
    browser_scroll = 0
    now_playing = None
    smooth_bars = None
    SMOOTH = 0.3

    def refresh_browser():
        nonlocal browser_files, browser_sel, browser_scroll
        browser_files = get_media_files(browser_path)
        browser_sel = 0
        browser_scroll = 0

    refresh_browser()

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.erase()

        # ── Header ──────────────────────────────────────────────────────────
        title = " ▶ central-mc "
        mode_label = f" [{VIS_MODES[vis_mode_idx].upper()}] "
        np_label = f" ♪ {os.path.basename(now_playing)}" if now_playing else " ♪ nothing playing"
        if len(np_label) > w - len(title) - len(mode_label) - 4:
            np_label = np_label[:w - len(title) - len(mode_label) - 7] + "..."
        header = title + np_label + " " * (w - len(title) - len(np_label) - len(mode_label)) + mode_label
        header = header[:w]
        try:
            stdscr.addstr(0, 0, header, curses.color_pair(5) | curses.A_BOLD)
        except curses.error:
            pass

        # ── Footer ──────────────────────────────────────────────────────────
        keys = " [TAB] Switch view  [V] Cycle visualiser  [S] Stop  [Q] Quit  [ENTER] Play "
        keys = keys[:w]
        try:
            stdscr.addstr(h - 1, 0, keys.ljust(w), curses.color_pair(5))
        except curses.error:
            pass

        body_h = h - 2
        body_top = 1

        if view == "visualiser":
            # ── Visualiser view ─────────────────────────────────────────────
            vis_win = stdscr.subwin(body_h, w, body_top, 0)
            try:
                vis_win.border()
            except curses.error:
                pass

            samples = audio.samples
            mode = VIS_MODES[vis_mode_idx]

            vis_color = {
                "bars": curses.color_pair(1),
                "waveform": curses.color_pair(6),
                "spectrum": curses.color_pair(7),
                "circle": curses.color_pair(1),
            }.get(mode, curses.color_pair(1))

            if mode == "bars":
                draw_bars(vis_win, samples, body_h, w, vis_color)
            elif mode == "waveform":
                draw_waveform(vis_win, samples, body_h, w, vis_color)
            elif mode == "spectrum":
                draw_spectrum(vis_win, samples, body_h, w, vis_color)
            elif mode == "circle":
                draw_circle(vis_win, samples, body_h, w, vis_color)

            # Now playing overlay
            if now_playing:
                label = f" ♪ {os.path.basename(now_playing)} "
                tx = max(1, (w - len(label)) // 2)
                try:
                    vis_win.addstr(1, tx, label, curses.color_pair(5) | curses.A_BOLD)
                except curses.error:
                    pass

        else:
            # ── Browser view ────────────────────────────────────────────────
            # Split: left = file list, right = mini vis
            list_w = max(20, w * 2 // 3)
            vis_w = w - list_w

            # File list
            list_win = stdscr.subwin(body_h, list_w, body_top, 0)
            try:
                list_win.border()
                path_label = f" 📁 {browser_path} "[:list_w - 2]
                list_win.addstr(0, 2, path_label, curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

            visible = body_h - 2
            # Auto-scroll
            if browser_sel < browser_scroll:
                browser_scroll = browser_sel
            if browser_sel >= browser_scroll + visible:
                browser_scroll = browser_sel - visible + 1

            for i in range(visible):
                idx = i + browser_scroll
                if idx >= len(browser_files):
                    break
                kind, name, full = browser_files[idx]
                icon = "📂 " if kind == "dir" else "🎵 "
                line = f" {icon}{name}"[:list_w - 3]
                row = i + 1
                attr = curses.color_pair(4) | curses.A_BOLD if idx == browser_sel else curses.color_pair(2)
                if full == now_playing:
                    attr = curses.color_pair(1) | curses.A_BOLD
                try:
                    list_win.addstr(row, 1, line.ljust(list_w - 2), attr)
                except curses.error:
                    pass

            # Mini visualiser on right
            if vis_w > 4:
                vis_win = stdscr.subwin(body_h, vis_w, body_top, list_w)
                try:
                    vis_win.border()
                    vis_win.addstr(0, 2, " VIS ", curses.color_pair(5))
                except curses.error:
                    pass
                samples = audio.samples
                draw_bars(vis_win, samples, body_h, vis_w, curses.color_pair(1))

        stdscr.refresh()

        # ── Input ────────────────────────────────────────────────────────────
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('\t'):
            view = "visualiser" if view == "browser" else "browser"
        elif key == ord('v') or key == ord('V'):
            vis_mode_idx = (vis_mode_idx + 1) % len(VIS_MODES)
        elif key == ord('s') or key == ord('S'):
            player.stop()
            now_playing = None
        elif key == curses.KEY_UP:
            browser_sel = max(0, browser_sel - 1)
        elif key == curses.KEY_DOWN:
            browser_sel = min(len(browser_files) - 1, browser_sel + 1)
        elif key == curses.KEY_BACKSPACE or key == 127:
            parent = os.path.dirname(browser_path)
            if parent != browser_path:
                browser_path = parent
                refresh_browser()
        elif key in (curses.KEY_ENTER, 10, 13):
            if browser_files and 0 <= browser_sel < len(browser_files):
                kind, name, full = browser_files[browser_sel]
                if kind == "dir":
                    browser_path = full
                    refresh_browser()
                else:
                    player.play(full)
                    now_playing = full
                    view = "visualiser"

        # Check if player finished
        if now_playing and not player.is_running():
            now_playing = None

        time.sleep(0.04)  # ~25fps

    player.stop()
    audio.stop()

def run():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
