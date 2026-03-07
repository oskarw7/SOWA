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
		          uv
		          ruff
		          ty
		          
		          stdenv.cc.cc.lib
		          zlib
		          glib
		        ];

		        shellHook = ''
		          export LD_LIBRARY_PATH="/nix/store/0p8b2lqk47fvxm9hc6c8mnln5l8x51q1-gcc-14.3.0-lib/lib:/nix/store/xdxxfabbd8w0dadijsd8rkgvnhpn3rkf-zlib-1.3.1/lib:/nix/store/wy4c9khmxwp1vd2p6nbf1lpg0rpnk61v-glib-2.86.3/lib:$LD_LIBRARY_PATH"
		        '';
		      };
		    };
		}
