{ pkgs ? import <nixpkgs> {} }:

with pkgs;
pkgs.mkShell {
  buildInputs = [
    gnumake python3 curlFull nodejs
    # keep this line if you use bash
    bashInteractive
  ];
}
