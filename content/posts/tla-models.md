---
title: "TLA+"
date: 2023-03-12
tags: [TLA+, distributed]
draft: true
---

# Specifying systems with TLA+

{{% sidenote %}} centralized as opposed to distributed{{% /sidenote %}}Last weeks at work I had to work on a bug in our backend systems.  In a centralized fashion, this wouldn't have been a bug, however distributed systems are difficult.

{{% tweet mathiasverraes 632260618599403520 %}}

## How I ended up thinking about TLA+

In our system we N producers and M consumers for a messaging queue, and upon receiving messages, the consumer would start a process that usually was _kinda_ short (in the order of seconds), but sometimes it would be _really_ long (up to **5m in some cases**).

Initially we started adding different timeouts on the producer and consumer side, however, it made it very difficult for me to reason about the system.

{{% sidenote %}}Here's the video, a great introduction to distributed system modelling with TLA+ {{< youtube qubS_wGgwO0 >}}{{% /sidenote %}}

I initially draw the system, and tried to specify it in text, but it was still hard to reason about it... and then I remembered a talk by [Hillel Wayne][hillel] I saw some time ago.

> Over a long enough talk, a system will do everything.
>
> Hillel Wayne

## TLA+ vs Pluscal

## Conclusion

[hillel]:https://www.hillelwayne.com/