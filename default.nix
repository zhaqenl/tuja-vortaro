{ system ? builtins.currentSystem, pkgs ? import <nixpkgs> {} }:

with pkgs;

stdenv.mkDerivation {
  name = "shell";

  buildInputs = [
    rlwrap
    gnumake
    readline
    python3
    python3Packages.lxml
  ];

  shellHook = ''
    export PS1="\[\033[1;32m\][\u \h \w]\n>\[\033[0m\] "
    function rl () { rlwrap -s 1000000 -c -b "(){}[].,=&^%0\;|" $@; }
  '';
}
