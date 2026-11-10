"""What the window tests open instead of a Tk root: the desks a test opened, pumped by update() and closed by destroy().

The window is a web page now (fpfa/web); its rules live in fpfa.desk.Desk, which needs no display.
A test opens a desk through a Loop, calls the desk's actions as the page's POSTs would, runs what the
workers left on the queue with update(), and reads the state the page draws (Desk.snapshot,
Desk.thread_text). The page's own behaviour is pinned by frontend/tests and tests/test_web.py.
"""

from __future__ import annotations


class Loop:
    def __init__(self):
        self.desks = []

    def open_desk(self, **options):
        from fpfa.desk import Desk

        desk = Desk(**options)
        self.desks.append(desk)
        return desk

    def update(self):
        for desk in self.desks:
            desk.pump()

    update_idletasks = update

    def destroy(self):
        for desk in self.desks:
            desk.close()
        self.desks = []
