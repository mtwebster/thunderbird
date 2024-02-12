#!/usr/bin/python3

import os, sys
import json

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

if archi == "amd64":
    archi="linux-x86_64"
else:
    archi="linux-i686"

US_URL = "http://download-origin.cdn.mozilla.net/pub/firefox/releases/%s/%s/en-US/firefox-%s.tar.bz2" % (release, archi, release)
XPI_URL = "http://download-origin.cdn.mozilla.net/pub/firefox/releases/%s/%s/xpi" % (release, archi)

os.system("rm -rf %s/debian/firefox" % curdir)
os.system("rm -rf %s/debian/firefox-*" % curdir)
os.system("mkdir -p %s/debian/firefox/usr/lib" % curdir)
os.chdir("%s/debian/firefox/usr/lib" % curdir)
if not abort:

    os.system("wget %s" % US_URL)
    if (not os.path.exists("firefox-%s.tar.bz2" % release)):
        print("FAILED: Could not download %s" % (US_URL))
        sys.exit(1)

    os.system("bzip2 -d firefox-%s.tar.bz2" % release)
    os.system("tar xvf firefox-%s.tar" % release)
    os.system("rm firefox-%s.tar" % release)

    os.system("mkdir -p %s/debian/firefox/usr/lib/firefox/distribution" % curdir)
    os.system("cp %s/pref/policies.json %s/debian/firefox/usr/lib/firefox/distribution" % (curdir, curdir))
    os.system("cp %s/pref/distribution.ini %s/debian/firefox/usr/lib/firefox/distribution" % (curdir, curdir))

    os.system("mkdir -p %s/debian/firefox/usr/share/icons/hicolor" % curdir)
    os.chdir("%s/debian/firefox/usr/share/icons/hicolor" % curdir)
    os.system("mkdir -p 16x16/apps 32x32/apps 48x48/apps 128x128/apps")
    os.system("ln -s /usr/lib/firefox/browser/chrome/icons/default/default16.png 16x16/apps/firefox.png")
    os.system("ln -s /usr/lib/firefox/browser/chrome/icons/default/default32.png 32x32/apps/firefox.png")
    os.system("ln -s /usr/lib/firefox/browser/chrome/icons/default/default48.png 48x48/apps/firefox.png")
    os.system("ln -s /usr/lib/firefox/browser/icons/mozicon128.png 128x128/apps/firefox.png")

if lmde:
    locale_prefix = "firefox-l10n"
else:
    locale_prefix = "firefox-locale"

codes = {}

with open(os.path.join(curdir, "locales.shipped")) as f:
    for line in f:
        if line.startswith("#"):
            continue

        xpi_name, pkg_name = line.split(":")
        pkg_name = pkg_name.replace("\n", "")

        if "-mac" in xpi_name:
            continue

        codes[xpi_name] = pkg_name

for xpi in codes.keys():
    package_code = codes[xpi]
    os.system("mkdir -p %s/debian/%s-%s/usr/lib/firefox/distribution/extensions" % (curdir, locale_prefix, package_code))
    os.chdir("%s/debian/%s-%s/usr/lib/firefox/distribution/extensions" % (curdir, locale_prefix, package_code))

    if not abort:
        os.system("wget %s/%s.xpi" % (XPI_URL, xpi))
        if (not os.path.exists("%s.xpi" % xpi)):
            print("FAILED: Could not download %s/%s.xpi" % (XPI_URL, xpi))
            sys.exit(1)
        os.system("mv %s.xpi langpack-%s@firefox.mozilla.org.xpi" % (xpi, xpi))

os.chdir(curdir)
