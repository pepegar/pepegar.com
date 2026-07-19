---
title: "The Good Things About the Apocalypse"
date: 2026-07-19T16:30:00+01:00
draft: true
---

You know that feeling when the industry you've called home becomes a
mess, and all hope is lost?

What nobody tells you about that is that you'll be able to finally
create the development environment you've been longing for for five
years.  I have a background of FP with Scala and Haskell, mostly, and
I loved the simplicity of just having a coding editor and a compiler
in a CLI.  No IDEs, no _indexing_, no nothing.  But then I started
working on Kotlin and experienced what a good IDE is like with
IntelliJ.

After that, all my efforts to come back to the frugal editor + cli
were bain, I was always missing my find references, goto definition,
and the rest of the code intelligence that I was used to from the IDE.

In parallel, the language server protocol has been developing, and
it's more and more mature.  Working on a Go or Typescript project in
Visual Studio Code is amazing nowadays, I don't miss a thing about an
IDE.

So that was what the Apocalypse brought me, the industry I love is
probably going to hell, but I'm gonna craft the best dev environment I
can.

## The plan

I wanted to build [ktlsp][], a compiler free, treesitter based,
language server for Kotlin and Java.  I distributed the work on a
bunch of different Codex and Kimi sessions, and it went roughly like
this: In the first days, I made the agent learn as much as possible
about treesitter, LSIF indices, and the language server protocol.  In
parallel, I tried to lift the hood of the marvelous tools from
[astral][] and see how are they so fast and amazing to use.

[ktlsp]: https://github.com/pepegar/ktlsp
[astral]: http://astral.sh
