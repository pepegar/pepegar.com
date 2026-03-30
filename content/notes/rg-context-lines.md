---
title: "Ripgrep context lines for better code search"
date: 2024-09-20
tags: [ripgrep, cli-tools, productivity]
---

When searching code with `rg`, the `-A`, `-B`, and `-C` flags are incredibly useful:

```bash
rg -A 3 -B 2 "function.*authenticate"  # 3 lines after, 2 before
rg -C 5 "TODO"                         # 5 lines before and after
```

This gives you much better context around matches, especially when you're trying to understand how a function is called or what surrounds a particular pattern.

The `-C` flag is particularly handy for finding TODO comments with enough surrounding code to understand what needs to be done.

I've been using plain `rg` for too long without these context flags - they make code archaeology so much more effective.