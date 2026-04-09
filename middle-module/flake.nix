{
  description = "Standard Dev Shell for Arduino and ESP32";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              arduino-ide
              python313
              python3Packages.pyserial
              zlib
              uv
              ruff
              ty
              stdenv.cc.cc.lib
              glib
              nixfmt-rfc-style
							gcc
							gnumake
							cmake
							clang-tools
							boost
              ninja
            ];

            shellHook = ''
              export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc.lib
                pkgs.zlib
                pkgs.glib
              ]}:$LD_LIBRARY_PATH"
            '';
          };
        }
      );
    };
}
