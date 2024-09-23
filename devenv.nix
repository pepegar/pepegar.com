{pkgs, ...}: {
  packages = [
    pkgs.git
    pkgs.hugo
    pkgs.ruff
    pkgs.alejandra
    pkgs.python3
    pkgs.python3Packages.colorama
  ];

  pre-commit.hooks = {
    markdown-preprocessor = {
      enable = true;
      name = "Markdown Preprocessor";
      entry = "${pkgs.python3}/bin/python ./scripts/preprocess.py --check";
      files = "\.md\.in$";
      pass_filenames = false;
    };
  };
}
