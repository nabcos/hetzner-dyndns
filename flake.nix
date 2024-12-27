{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: (import nixpkgs {
        inherit system;
        config = {
          # e.g. permittedInsecurePackages for the build
        };
      }));
    in
    {
      packages = forAllSystems (system: {
        hetzner-dyndns = pkgs.${system}.callPackage ./default.nix { };
      });
    };
}
