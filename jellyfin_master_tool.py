import os
import shutil
import hashlib
import threading
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


class JellyfinMasterTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Jellyfin Master Tool v3.0")
        self.root.geometry("800x750")
        self.root.configure(bg="#1a1a1a")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1a1a1a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#333", foreground="white", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#00A4DC")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs erstellen
        self.tab_music = self.create_tab("🎵 Musik", "#1DB954")
        self.tab_series = self.create_tab("📺 Serien", "#00A4DC")
        self.tab_movies = self.create_tab("🎬 Filme", "#E5A00D")

    def create_tab(self, name, color):
        frame = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(frame, text=name)

        # UI Komponenten pro Tab
        tk.Label(frame, text=f"{name} Cleanup & Merge", font=("Segoe UI", 16, "bold"), fg=color, bg="#1a1a1a").pack(
            pady=15)

        p_frame = tk.Frame(frame, bg="#1a1a1a")
        p_frame.pack(fill=tk.X, padx=20)

        path_ent = tk.Entry(p_frame, bg="#333", fg="white", font=("Segoe UI", 10), borderwidth=0)
        path_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 10))

        tk.Button(p_frame, text="Pfad wählen", bg="#555", fg="white", command=lambda: self.browse(path_ent)).pack(
            side=tk.RIGHT)

        log_area = scrolledtext.ScrolledText(frame, height=15, bg="black", fg=color, font=("Consolas", 9))

        # Start Buttons mit spezifischer Logik
        if "Musik" in name:
            btn = tk.Button(frame, text="MUSIC CLEANUP STARTEN", bg=color, font=("Segoe UI", 11, "bold"),
                            command=lambda: self.start_thread(self.run_music, path_ent, log_area))
        elif "Serien" in name:
            btn = tk.Button(frame, text="SERIEN MERGE & CLEANUP", bg=color, font=("Segoe UI", 11, "bold"),
                            command=lambda: self.start_thread(self.run_series, path_ent, log_area))
        else:
            btn = tk.Button(frame, text="FILM PRO-RENAME & CLEANUP", bg=color, font=("Segoe UI", 11, "bold"),
                            command=lambda: self.start_thread(self.run_movies, path_ent, log_area))

        btn.pack(fill=tk.X, padx=20, pady=15)
        log_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        return {"path": path_ent, "log": log_area}

    # --- CORE UTILS ---
    def browse(self, entry):
        p = filedialog.askdirectory()
        if p: entry.delete(0, tk.END); entry.insert(0, p)

    def log(self, area, msg):
        area.insert(tk.END, msg + "\n");
        area.see(tk.END)

    def get_hash(self, path):
        hasher = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                hasher.update(f.read(1024 * 1024))
            return hasher.hexdigest()
        except:
            return None

    def start_thread(self, target, path_ent, log_area):
        path = path_ent.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", "Pfad ungültig!");
            return
        threading.Thread(target=target, args=(path, log_area), daemon=True).start()

    # --- LOGIKEN ---
    def run_music(self, path, area):
        self.log(area, "--- 🎵 Musik Cleanup gestartet ---")
        self.cleanup_engine(path, area, keep=('.mp3', '.flac', '.m4a', '.wav', '.jpg', '.lrc'),
                            junk=('.url', '.lnk', '.txt', '.exe'))
        self.log(area, "--- ✅ Musik fertig! ---")

    def run_series(self, path, area):
        self.log(area, "--- 📺 Serien Merge & Cleanup gestartet ---")
        # Zuerst Müll raus
        self.cleanup_engine(path, area, keep=('.mp4', '.mkv', '.vtt', '.nfo'), junk=('.url', '.lnk', '.txt'))
        # Dann Mergen
        all_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for folder in all_dirs:
            clean = re.split(r' \(| \[', folder)[0].strip()
            if clean != folder:
                src, tgt = os.path.join(path, folder), os.path.join(path, clean)
                if os.path.exists(tgt):
                    for item in os.listdir(src):
                        try:
                            shutil.move(os.path.join(src, item), os.path.join(tgt, item))
                        except:
                            pass
                    try:
                        os.rmdir(src); self.log(area, f"📦 Merged: {folder}")
                    except:
                        pass
                else:
                    os.rename(src, tgt);
                    self.log(area, f"✅ Umbenannt: {folder}")
        self.log(area, "--- ✅ Serien fertig! ---")

    def run_movies(self, path, area):
        self.log(area, "--- 🎬 Filme Pro-Rename gestartet ---")
        all_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for folder in all_dirs:
            name = folder.replace('.', ' ').replace('_', ' ')
            year_m = re.search(r'(19|20)\d{2}', name)
            if year_m:
                year = year_m.group()
                title = name.split(year)[0].strip()
                clean = f"{title} ({year})"
                src, tgt = os.path.join(path, folder), os.path.join(path, clean)

                # Ordner Rename/Merge
                work_path = src
                if clean.lower() != folder.lower():
                    if os.path.exists(tgt):
                        for i in os.listdir(src): shutil.move(os.path.join(src, i), os.path.join(tgt, i))
                        os.rmdir(src);
                        work_path = tgt
                    else:
                        os.rename(src, tgt);
                        work_path = tgt

                # Datei Rename (Größte Datei)
                vids = [f for f in os.listdir(work_path) if f.lower().endswith(('.mkv', '.mp4'))]
                if vids:
                    main = max(vids, key=lambda x: os.path.getsize(os.path.join(work_path, x)))
                    ext = os.path.splitext(main)[1]
                    try:
                        os.rename(os.path.join(work_path, main), os.path.join(work_path, f"{clean}{ext}"))
                    except:
                        pass
        self.log(area, "--- ✅ Filme fertig! ---")

    def cleanup_engine(self, path, area, keep, junk):
        bin = os.path.join(path, "_ISOLATED_JUNK")
        if not os.path.exists(bin): os.makedirs(bin)
        hashes = {}
        for root, dirs, files in os.walk(path, topdown=False):
            if "_ISOLATED_JUNK" in root: continue
            for f in files:
                f_p = os.path.join(root, f)
                ext = os.path.splitext(f.lower())[1]
                # Junk & Duplikate
                if ext in junk:
                    shutil.move(f_p, os.path.join(bin, f"JUNK_{f}"));
                    self.log(area, f"🗑️ Junk: {f}")
                elif ext in keep:
                    h = self.get_hash(f_p)
                    if h in hashes:
                        shutil.move(f_p, os.path.join(bin, f"DUP_{f}"));
                        self.log(area, f"👯 Dublette: {f}")
                    else:
                        hashes[h] = f_p
            # Leere Ordner
            for d in dirs:
                d_p = os.path.join(root, d)
                if not os.listdir(d_p): os.rmdir(d_p); self.log(area, f"🧹 Leer entfernt: {d}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JellyfinMasterTool(root)
    root.mainloop()