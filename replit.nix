{pkgs}: {
  deps = [
    pkgs.geos
    pkgs.proj
    pkgs.gdal
    pkgs.postgis
    pkgs.postgresql
  ];
}
