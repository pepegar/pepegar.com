let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    buildInputs = [
      pkgs.hugo
      pkgs.ruff
      pkgs.alejandra
      pkgs.python3Packages.colorama
    ];
  }
