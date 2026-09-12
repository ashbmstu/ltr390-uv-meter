# Flashing

Getting MicroPython onto the XIAO ESP32-C3 and the three firmware files onto the
board. You do the MicroPython part once; after that, updating the meter is just
copying files.

You need the XIAO board, a USB-C cable that carries **data** (many charging
cables do not), and a computer. Nothing has to be soldered yet — it is easier to
get the software working on a bare board first.

## 1. Install Thonny

[Thonny](https://thonny.org) is a small Python editor that can install
MicroPython and copy files to the board. It runs on Windows, macOS and Linux and
needs no configuration.

## 2. Install MicroPython on the board

1. Plug the XIAO into the computer.
2. In Thonny, open **Tools → Options → Interpreter**.
3. Set the interpreter to **MicroPython (ESP32)**.
4. Pick the board's port from the list. On Windows it is a `COM` port; on macOS
   and Linux it is something like `/dev/tty.usbmodem…`.
5. Click **Install or update MicroPython** at the bottom of the dialog.
6. Choose the **ESP32-C3** family and the generic ESP32-C3 variant, then
   **Install**. It takes a minute or so.

If no port appears, put the board into bootloader mode: hold the **B** button
down, press and release **R**, then release **B**. The port appears, and you can
go back to step 4.

This project was written against **MicroPython 1.26.1**. Later versions should be
fine; anything much older may not have `SoftI2C`.

Close the dialog. The bottom panel in Thonny should now show a `>>>` prompt
coming from the board.

## 3. Copy the three files

1. In Thonny, open **View → Files**. You get two panes: your computer on top, the
   board underneath.
2. In the top pane, navigate to this repository's `src` folder.
3. Select `main.py`, `ltr390.py` and `ssd1306.py`, right-click, and choose
   **Upload to /**.

All three must end up at the **top level** of the board, not inside a folder. The
board's pane should list exactly:

```
ltr390.py
main.py
ssd1306.py
```

## 4. Run it

Press the **R** button on the XIAO, or unplug and replug it. MicroPython runs
`main.py` automatically at every power-up, which is why the meter needs no button
to start.

With nothing wired up yet you will see `Init: FAIL` in the Thonny console — the
sensor is not there. That is the correct answer at this stage. Wire the board up
following [hardware.md](hardware.md) and it will start reading.

## Changing the firmware later

Edit the file in Thonny and upload it again; there is no build step. If the board
is busy running `main.py` and will not respond, click into the console and press
**Ctrl+C** to stop it, then upload.

## Related

- [hardware.md](hardware.md) — what to solder where
- [troubleshooting.md](troubleshooting.md) — when the screen stays dark
