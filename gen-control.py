#!/usr/bin/python3

import os, sys

archi = sys.argv[1]
curdir = sys.argv[2]
version = sys.argv[3]
abort = False

lmde = False

release = version
if "+" in version:
    release = version.split("+")[0]

if "~" in version:
    release = version.split("~")[0]
    lmde = True

if lmde:
    locale_prefix = "firefox-l10n"
else:
    locale_prefix = "firefox-locale"

shipped_template = """
Package: %s-%s
Architecture: any
Depends: ${misc:Depends}
Description: %s language packs for Firefox
 %s language packs for the Mozilla Firefox Web Browser.
"""

unavailable_template = """
Package: %s-%s
Architecture: any
Depends: ${misc:Depends}
Description: Transitional package for unavailable language
 This language is unavailable for the current version of Firefox
 .
 This is an empty transitional package to ensure a clean upgrade
 process. You can safely remove this package after installation.
"""

# Load code:Name list to popular control descriptions
locale_name_dict = {}
with open(os.path.join(curdir, "locales.all")) as f:
    for line in f:
        if line.startswith("#"):
            continue
        code, lang = line.split(":")
        locale_name_dict[code] = lang.replace("\n", "")

xpi_locale_map = {}
shipped_packages = []

with open(os.path.join(curdir, "locales.shipped")) as f:
    for line in f:
        if line.startswith("#"):
            continue

        xpi_name, pkg_name = line.split(":")
        pkg_name = pkg_name.replace("\n", "")
        xpi_locale_map[xpi_name] = pkg_name

        if pkg_name not in shipped_packages:
            shipped_packages.append(pkg_name)

control_locales = ""
used_codes = []

print("\nGenerating %s entries for control file...\n")

for locale in locale_name_dict.keys():
    if locale in shipped_packages:
        print(locale, locale_name_dict[locale])
        control_locales += (shipped_template % (locale_prefix, locale, locale_name_dict[locale], locale_name_dict[locale]))
    else:
        print(locale, locale_name_dict[locale], ".......transitional package")
        control_locales += (unavailable_template % (locale_prefix, locale))

with open(os.path.join(curdir, "debian", "control"), "w") as f:
    control = ""
    with open(os.path.join(curdir, "debian", "control.in"), "r") as ini:
        control += ini.read()

    control += control_locales

    f.write(control)

print("\nDone generating control file...\n")

os.chdir(curdir)
