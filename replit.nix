
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.chromium
    pkgs.xvfb-run
    pkgs.dbus
    pkgs.fontconfig
    pkgs.freetype
    pkgs.glib
    pkgs.gtk3
    pkgs.libdrm
    pkgs.libxkbcommon
    pkgs.mesa
    pkgs.nspr
    pkgs.nss
    pkgs.pango
    pkgs.xorg.libX11
    pkgs.xorg.libXcomposite
    pkgs.xorg.libXdamage
    pkgs.xorg.libXext
    pkgs.xorg.libXfixes
    pkgs.xorg.libXrandr
    pkgs.xorg.libxcb
    pkgs.xorg.libxshmfence
    pkgs.at-spi2-atk
    pkgs.at-spi2-core
    pkgs.atk
    pkgs.cairo
    pkgs.cups
    pkgs.expat
    pkgs.gdk-pixbuf
    pkgs.libxslt
    pkgs.libuuid
    pkgs.libappindicator-gtk3
  ];

  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.chromium}/bin";
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "1";
    DISPLAY = ":99";
  };
}
