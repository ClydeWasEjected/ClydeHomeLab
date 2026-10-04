"""Type a pasted string as keystrokes, for consoles that do not accept paste.

Run on the laptop (needs a screen): pip install pyautogui
Usage: python type_paste.py
Paste the text at the hidden prompt, press Enter, then click into the VM
console during the countdown.
"""
import getpass
import sys
import time

import pyautogui

COUNTDOWN = 5
KEY_INTERVAL = 0.05

pyautogui.FAILSAFE = True


def main():
    text = getpass.getpass("Text to type (hidden): ")
    if not text:
        print("Nothing to type.")
        return
    print(f"{len(text)} characters. Click into the target window.")
    for n in range(COUNTDOWN, 0, -1):
        print(f"  typing in {n}...", end="\r", flush=True)
        time.sleep(1)
    print(" " * 30, end="\r")
    pyautogui.write(text, interval=KEY_INTERVAL)
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nAborted.")
