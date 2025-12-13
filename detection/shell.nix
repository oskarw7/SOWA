{ pkgs ? import <nixpkgs> {
    config = {
      allowUnfree = true;
    };
  }
}:
let
  myPython = pkgs.python313.override
    {
      packageOverrides = self: super: {
        opencv4 = super.opencv4.override {
          enableGtk2 = true;
          gtk2 = pkgs.gtk2;
        };
        ultralytics-thop = super.ultralytics-thop.override {
          torch = super.torch-bin.override {
            triton = super.triton-bin;
          };
        };
        torch = super.torch-bin.override {
          triton = super.triton-bin;
        };
        torchvision = super.torchvision-bin;
      };
    };
in
pkgs.mkShell {
  name = "SOWA-env";
  packages = [
    (myPython.withPackages (ps: with ps; [
      opencv4
      numpy
      pandas
      requests
      faker
      sqlalchemy
      pyodbc
      ultralytics
    ]))
  ];

  shellHook = ''
    echo ""
  '';
}
