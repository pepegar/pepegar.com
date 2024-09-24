---
title: "Repeatable Python environments"
date: 2023-03-12
tags: [Python, teaching, cookiecutter]
toc: true
draft: true
---

# Repeatable Python environments

As part of my work as an Assistant Professor at IE School of Science and
Technology, one of the most difficult things is to have my students have the
same environment to work on regardless of their computer.  Most of them use
MacOS, but there are some that use Windows machines.

In the past, I would have them install Anaconda and use that as the baseline for
all our work.  However, given it runs in the host OS, there would be small
differences between every installation and it would be hard to manage.

Next year, I'm going to try something new, I'm gonna create Github repositories
backed by a [devcontainer][devcontainers].  This repositories will provide:

- A base `Pipfile` for pipenv, providing some baseline libraries
- A set of recommended plugins
- A .devcontainer configured for Python development

## Initial setup

The only requirements for them will be:

1. Install Docker desktop and have it running
2. Install VSCode

## Dev containers

[Dev containers][devcontainers] are a great way to have a repeatable environment

## Automating the setup

I'll be creating **a lot** of repos, one per session and I'll have around 60
session next year.  In order to make it easy for me, I'll reuse
https://simonwillison.net/2021/Aug/28/dynamic-github-repository-templates/

[devcontainers]: https://code.visualstudio.com/docs/devcontainers/create-dev-container
