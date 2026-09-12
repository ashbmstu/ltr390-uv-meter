# Security

This firmware has no network stack, no Bluetooth, no stored credentials and no
user data. The radio on the ESP32-C3 is never switched on. There is no remote
attack surface to report against.

## What is worth reporting

**A measurement bug.** The one way this project can hurt somebody is by telling
them the UV index is low when it is high. A wrong conversion, a misread register,
a silent saturation that pins the display at a small number in strong sun — any of
those could put a person in the sun believing they are safe. Treat that class of
bug as a safety issue and report it, even though nothing about it is a security
vulnerability in the usual sense.

The meter is not a medical or occupational instrument and must not be used as one.
See [docs/measurement.md](docs/measurement.md) for what the number actually is.

**Battery handling.** The cell is charged by the XIAO's own circuitry, not by
anything in this repository. If you find an instruction in these docs that would
lead somebody to wire a cell dangerously, that is worth reporting too.

## How to report

Use [GitHub's private vulnerability
reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository. For an ordinary measurement bug a normal issue is fine and
easier to discuss in the open.

## What to expect

There is no support commitment and no CVE process. Reports are read in good faith;
fixes depend on maintainer time and on how badly the bug misleads.
