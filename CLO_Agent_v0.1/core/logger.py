# -*- coding: utf-8 -*-
"""Readable logger. Output is meant to be pasteable into ChatGPT/Claude for debugging."""
import os, time

class Logger:
    def __init__(self, log_dir, echo=True):
        os.makedirs(log_dir, exist_ok=True)
        self.path = os.path.join(log_dir, time.strftime("run_%Y%m%d_%H%M%S.log"))
        self.echo = echo
        self.lines = []

    def _w(self, s):
        self.lines.append(s)
        if self.echo:
            print(s)
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(s + "\n")
        except Exception:
            pass

    def header(self, s):
        self._w("")
        self._w(s)
        self._w("-" * max(8, len(s)))

    def ok(self, s):     self._w(f"[PASS] {s}")
    def fail(self, s):   self._w(f"[FAIL] {s}")
    def warn(self, s):   self._w(f"[WARN] {s}")
    def info(self, s):   self._w(f"       {s}")
    def stop(self, s):   self._w(f"[STOP] {s}")
    def raw(self, s):    self._w(s)
