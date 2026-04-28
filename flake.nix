		{
		  description = "Python project";

		  inputs = {
		    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
		  };

		  outputs = { self, nixpkgs }:
		    let
		      system = "x86_64-linux";
		      pkgs = nixpkgs.legacyPackages.x86_64-linux;
		    in
		    {
		      devShells.x86_64-linux.default = pkgs.mkShell {
		        buildInputs = with pkgs; [
		          python313
		          ruff
							ty
							uv
							ffmpeg
							python313Packages.opencv4						
							xorg.libxcb
							xorg.libX11
							libGL
							arduino-ide
              zlib
              stdenv.cc.cc.lib
              glib
              nixfmt-rfc-style
							gcc
							gnumake
							cmake
							clang-tools
							boost
              ninja
              socat
              jq
              esptool
		        ];
						shellHook = ''
              export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc.lib
                pkgs.zlib
                pkgs.glib
              ]}:$LD_LIBRARY_PATH"
            '';
		      };
		    };
		}
