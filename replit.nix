{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.gitFull
    pkgs.geos
    pkgs.proj
    pkgs.gdal
    pkgs.postgis
    pkgs.postgresql
  ];
}
