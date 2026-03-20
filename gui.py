import tkinter as tk
from tkinter import ttk, messagebox
import threading
from bot import launch_browser, login, reserve


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zalando Lounge Reservator")
        self.root.configure(bg="#f5f6fa")
        self.root.resizable(False, False)
        self.driver = None
        self.running = False
        self.password_visible = False
        self._build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_gui(self):
        BG = "#f5f6fa"
        CARD_BG = "#ffffff"
        ACCENT = "#2563eb"
        ACCENT_HOVER = "#1d4ed8"
        TEXT = "#1e293b"
        TEXT_LIGHT = "#64748b"
        BORDER = "#e2e8f0"
        SUCCESS = "#16a34a"
        INPUT_BG = "#f8fafc"

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Main.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Title.TLabel", background=BG, foreground=ACCENT,
                         font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=TEXT_LIGHT,
                         font=("Segoe UI", 9))
        style.configure("Field.TLabel", background=CARD_BG, foreground=TEXT,
                         font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=BG, foreground=SUCCESS,
                         font=("Segoe UI", 10))

        main = ttk.Frame(self.root, style="Main.TFrame", padding=30)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="🛒 Zalando Lounge Reservator",
                  style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(main, text="Automatic product reservation",
                  style="Subtitle.TLabel").pack(pady=(0, 20))

        card = ttk.Frame(main, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        fields = [
            ("Product URL:", "url"),
            ("Email:", "email"),
            ("Password:", "password"),
            ("Sizes (e.g. M,L,XL):", "sizes"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(card, text=label, style="Field.TLabel").grid(
                row=i, column=0, sticky="w", pady=6, padx=(0, 12)
            )

            if key == "password":
                pw_frame = tk.Frame(card, bg=CARD_BG)
                pw_frame.grid(row=i, column=1, pady=6, sticky="ew")

                entry = tk.Entry(
                    pw_frame, width=38, font=("Segoe UI", 10),
                    show="•", bg=INPUT_BG, fg=TEXT,
                    relief="solid", bd=1,
                    highlightthickness=2, highlightcolor=ACCENT,
                    highlightbackground=BORDER
                )
                entry.pack(side="left", fill="x", expand=True)

                self.btn_toggle_pw = tk.Button(
                    pw_frame, text="👁", font=("Segoe UI", 10),
                    bg=CARD_BG, fg=TEXT_LIGHT, relief="flat", bd=0,
                    cursor="hand2", command=self._toggle_password,
                    activebackground=CARD_BG
                )
                self.btn_toggle_pw.pack(side="right", padx=(4, 0))

                self.entries[key] = entry
            else:
                entry = tk.Entry(
                    card, width=45, font=("Segoe UI", 10),
                    bg=INPUT_BG, fg=TEXT,
                    relief="solid", bd=1,
                    highlightthickness=2, highlightcolor=ACCENT,
                    highlightbackground=BORDER
                )
                entry.grid(row=i, column=1, pady=6, sticky="ew")
                self.entries[key] = entry

        card.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(main, bg=BG)
        btn_frame.pack(fill="x", pady=(5, 10))

        self.btn_start = tk.Button(
            btn_frame, text="▶  START",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT_HOVER,
            activeforeground="white", relief="flat", bd=0,
            cursor="hand2", padx=30, pady=10,
            command=self._on_start
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=2)

        self.btn_stop = tk.Button(
            btn_frame, text="■  STOP",
            font=("Segoe UI", 10, "bold"),
            bg="#94a3b8", fg="white", activebackground="#dc2626",
            activeforeground="white", relief="flat", bd=0,
            cursor="hand2", padx=20, pady=8,
            state="disabled", command=self._on_stop
        )
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=(5, 0), ipady=2)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var,
                  style="Status.TLabel").pack(anchor="w", pady=(0, 5))

        log_frame = tk.Frame(main, bg=BG)
        log_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.log_text = tk.Text(
            log_frame, height=10, bg="#f1f5f9", fg=TEXT,
            font=("Consolas", 9), relief="solid", bd=1,
            insertbackground=ACCENT, state="disabled", wrap="word"
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.geometry("580x560")

        self._accent = ACCENT

    def _toggle_password(self):
        self.password_visible = not self.password_visible
        entry = self.entries["password"]
        if self.password_visible:
            entry.configure(show="")
            self.btn_toggle_pw.configure(text="🔒")
        else:
            entry.configure(show="•")
            self.btn_toggle_pw.configure(text="👁")

    def _log(self, msg):
        def _update():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(0, _update)

    def _set_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def _on_start(self):
        url = self.entries["url"].get().strip()
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        sizes_raw = self.entries["sizes"].get().strip()

        if not all([url, email, password, sizes_raw]):
            messagebox.showwarning("Missing data", "Please fill in all fields.")
            return

        sizes = [s.strip() for s in sizes_raw.split(",")]

        self.running = True
        self.btn_start.configure(state="disabled", bg="#94a3b8")
        self.btn_stop.configure(state="normal", bg="#ef4444")
        for e in self.entries.values():
            e.configure(state="disabled")

        thread = threading.Thread(
            target=self._run, args=(url, email, password, sizes), daemon=True
        )
        thread.start()

    def _on_stop(self):
        self.running = False
        self._set_status("Stopping...")
        self._log("Stopping...")

    def _on_close(self):
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.root.destroy()

    def _reset_ui(self):
        def _r():
            self.btn_start.configure(state="normal", bg=self._accent)
            self.btn_stop.configure(state="disabled", bg="#94a3b8")
            for e in self.entries.values():
                e.configure(state="normal")
        self.root.after(0, _r)

    def _run(self, url, email, password, sizes):
        try:
            self._set_status("Launching browser...")
            self._log("Launching browser...")

            self.driver = launch_browser()

            self._set_status("Logging in...")
            login(self.driver, url, email, password, log=self._log)

            if not self.running:
                return

            self._set_status(f"Looking for: {', '.join(sizes)}")
            self._log(f"Looking for sizes: {', '.join(sizes)}")

            success = reserve(
                self.driver, sizes,
                log=self._log,
                is_running=lambda: self.running
            )

            if success:
                self._set_status("✅ Success! Product added to cart.")
            elif not self.running:
                self._set_status("Stopped.")

        except Exception as e:
            self._log(f"Error: {e}")
            self._set_status("Error")
        finally:
            self._reset_ui()
