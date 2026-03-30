---
title: "Quick Python environment with nix-shell"
date: 2024-09-22
tags: [nix, python, development]
---

You can quickly spin up a Python environment with specific packages using `nix-shell`:

```bash
nix-shell -p python3 python3Packages.requests python3Packages.numpy
```

This drops you into a shell with Python 3 and the specified packages available. Great for quick experiments without polluting your system Python or setting up a full virtual environment.

The `-p` flag lets you specify multiple packages, and you can find available Python packages by searching for `python3Packages.` followed by the package name.

For more complex setups, you can create a `shell.nix` file, but for one-offs, this command line approach is perfect.