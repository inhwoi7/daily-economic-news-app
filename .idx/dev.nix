# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # or "unstable"
  
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.nodejs_20
    pkgs.python3
    pkgs.docker
  ];

  # Enable Docker service
  services.docker.enable = true;

  # Sets environment variables in the workspace
  env = {};

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
    ];

    # Enable previews and customize configuration
    previews = {
      enable = true;
      previews = {
        web = {
          # 뉴스 앱(FastAPI)을 8000번 포트에서 실행합니다.
          command = ["./daily-economic-news-app/venv/bin/python" "daily-economic-news-app/main.py"];
          manager = "web";
          env = {
            PORT = "8000";
          };
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      onCreate = {
        # Open editors for the following files by default:
        default.openFiles = [ "daily-economic-news-app/main.py" "daily-economic-news-app/static/index.html" ];
      };
      onStart = {
        # 앱이 시작될 때마다 실행하고 싶다면 여기에 추가 가능합니다.
      };
    };
  };
}
