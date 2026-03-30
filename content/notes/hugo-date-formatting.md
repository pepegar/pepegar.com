---
title: "Hugo date formatting gotcha"
date: 2024-09-21
tags: [hugo, templating, web-development]
---

Hugo uses Go's reference time for date formatting: `Mon Jan 2 15:04:05 MST 2006`.

Instead of typical format strings like `%Y-%m-%d`, you use the reference time:

```go
{{ .Date.Format "January 2, 2006" }}     // September 21, 2024
{{ .Date.Format "2006-01-02" }}          // 2024-09-21  
{{ .Date.Format "Jan 2" }}               // Sep 21
```

The trick is remembering the reference time represents `01/02 03:04:05PM '06 -0700`, so each component has a unique number that you use in your format string.

This initially confused me coming from other templating systems, but it's actually quite elegant once you get used to it.