{ lib, pkgs, ... }:
pkgs.python3.pkgs.buildPythonPackage rec {
  name = "hddns-${version}";
  version = "0.4.2";

  src = ./.;

  format = "pyproject";
  buildInputs = with pkgs.python3.pkgs; [ setuptools ];
  propagatedBuildInputs = with pkgs.python3.pkgs; [ requests loguru ];

  meta = with lib; {
    homepage = "https://git.nabcos.de/nabcos/hetzner-dyndns";
    description = "Use hetzner DNS as dyndns provider";
    license = licenses.isc;
    platforms = platforms.linux;
    maintainers = [
      {
        name = "Benjamin Hanzelmann";
        email = "benjamin@hanzelmann.de";
        github = "nabcos";
      }
    ];
  };
}
