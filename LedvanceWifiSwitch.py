#!/etc/openhab/scripts/tuya/venv/bin/python3
import argparse, sys, time, datetime as dt
import tinytuya
VERSION = "0.1"

"""
LedvanceWifiSwitch.py — CLI utility for Tuya smart switches
(Tuya protocol 3.3/3.5).

INSTALL REQUIREMENTS:
    Smartlife APP (https://play.google.com/store/apps/details?id=com.tuya.smartlife&pcampaignid=web_share)
    $pip install tinytuya
    follow guide: https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys
    $python3 -m tinytuya wizzard
    When you have the keys from the wizzard, you can use this utility it will work local.

USAGE (first 3 arguments are mandatory):
    LedvanceWifiSwitch.py DEV_ID IP LOCAL_KEY [options]
    Example: python SwitchControl.py bxxdd0xxdd2698529gse2 1.1.1.2 'your_local_key' --on

Options (can be combined):
  --status                       print DPS once and exit
  --tail [SEC]                   continuously print DPS every SEC (default 1)
  --on / --off                   turn on / off (DPS 1)
  --debug                        verbose tinytuya log
  --version                      print utility version


CREDIT: https://github.com/adm1nsys/Ledvence-Smart-WiFi-E27-A60-Local-Control
"""



# ---------------- helpers -----------------

def timestamp() -> str:
    return dt.datetime.now().strftime("%H:%M:%S")

# -------------- argparser -----------------

def get_parser() -> argparse.ArgumentParser:
    description = (
        "CLI utility for Tuya smart switches (Tuya protocol 3.3/3.5).\n\n"
        "USAGE (first 3 arguments are mandatory):\n"
        "  SwitchControl.py DEV_ID IP LOCAL_KEY [options]\n"
        "  Example: python SwitchControl.py bfcdd0dddd2698529gse2 1.1.1.2 'your_local_key' --on\n\n"
        f"Version: {VERSION}"
    )

    p = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    p.add_argument("dev_id", help="Device ID")
    p.add_argument("ip", help="Local IP Address")
    p.add_argument("local_key", help="Local Key")
    p.add_argument("--version", type=float, default=3.3, help="Tuya protocol version (default: 3.3)")

    pow_grp = p.add_mutually_exclusive_group()
    pow_grp.add_argument("--on", action="store_true", help="Turn on the switch (DPS 1)")
    pow_grp.add_argument("--off", action="store_true", help="Turn off the switch (DPS 1)")

    p.add_argument("--status", action="store_true", help="Print current device status")
    p.add_argument("--tail", nargs="?", const="1", metavar="SEC", help="Continuously print status every SEC (default: 1)")
    p.add_argument("--debug", action="store_true", help="Enable verbose tinytuya logs")
    return p

# --------------- main ---------------------

def main():
    # Grab argv commands & Normalize --on/--off to lowercase for case-insensitive input
    for i in range(len(sys.argv)):
        if sys.argv[i].lower() in ['--on', '--off']:
            sys.argv[i] = sys.argv[i].lower()

    args = get_parser().parse_args()

    if args.debug:
        tinytuya.set_debug()

    switch = tinytuya.Device(args.dev_id, args.ip, args.local_key)
    switch.set_version(args.version)
    switch.set_socketPersistent(True)

    # ---- tail mode --------------------------------------------------------
    if args.tail is not None:
        interval = max(0.2, float(args.tail))
        try:
            while True:
                print(timestamp(), switch.status().get("dps", {}))
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped.")
        sys.exit()

    # ---- single status ----------------------------------------------------
    if args.status and not any([args.on, args.off]):
        print(switch.status())
        sys.exit()

    # ---- power ------------------------------------------------------------
    if args.on:
        switch.set_value("1", True)
    if args.off:
        switch.set_value("1", False)

    # ---- final status -----------------------------------------------------
    time.sleep(0.3)
    #print(switch.status()) # print all state
    status = switch.status()  # returns the dict

    # Use dps['1'] boolean
    if status['dps'].get('1', False):
        print("ON")
    else:
        print("OFF")

if __name__ == "__main__":
    main()
