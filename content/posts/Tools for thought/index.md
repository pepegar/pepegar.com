---
title: "Tools for thought"
date: "2021-02-27"
toc: true
---

For quite some time I’ve been searching for the best tool for supporting my studying. I’m a programmer, and am interested in quite a lot of different subjects, ranging from programming languages, distributed systems, compilers, machine learning, big data, etc.

Something I've noticed is that, propietary tools come and go, and having all your notes siloed on someone else's servers is not what you probably want. So, I've been looking at plain text implementations of knowledge management systems lately.

There is an awful number of concepts in all these fields that I’d like to retain if I want to keep studying and advancing on these fields, and I’ve tried a lot of different approaches:

## Notion

{{% sidenote %}}<https://notion.so>{{% /sidenote %}}Notion is an awesome tool. Its interface is easy to use, the app works on all possible devices, and it feels just nice. The big drawback I find to it is that it does too much for me. Maybe I haven’t learned it correctly, or I haven’t spent enough time working on my setup, but I’ve found that it’s just too big for me.

I think there's not much to say about Notion nowadays. Everybody seems to be using it, and there's a lot of content for it by better advocates than myself. Also, there's lots of companies migrating from more clunky documentation platforms such as Confluence to it, which is a great advantage!

## Roam research

I discovered the Zettelkasten method thanks to Roam research. I’m no expert in it, but people ensure they can supercharge their brain using it, by asking questions to your _zettelkasten_ and being able to discover links between ideas stored in it. It’s based on so called _heterarchies_ that form in the information organically through links and backlinks.

Roam research is a SAAS application that applies this method, and it’s a great tool

{{< youtube vxOffM_tVHI >}}

## Org roam

{{% sidenote %}}<https://www.orgroam.com/> Don't expect a old text-only interface for org-roam, it provides other fancy features. Here you can see other sub project of org-roam, org-roam-server, that allows the user to see the graph formed by their zettelkasten in a webapp ![](org-roam-server.gif){{% /sidenote %}}org-roam is the Emacs based alternative for Roam. It’s an awesome Emacs extension, opensource, and delightly crafted.

I used it a lot for some time and, once you get used to the flow, it's fantastic. On [my braindump](https://braindump.pepegar.com) I managed to publish a Hugo site generated from the org-roam zettels. The setup was mostly copied from Jethro Kuan's own setup though.

## Neuron

Neuron is a standalone Zettelkasten implementation. It features also a static site generator to convert all your markdown based notes into beautiful websites. Something else that makes it very appealing to me is that it's written by [Sridhar](https://www.srid.ca/), and keeps the project updated.

It is what I'm using nowadays, and I'm publishing updates to my zettelkasten to [https://neuron.pepegar.com/](https://neuron.pepegar.com).

## Muse

{{% sidenote %}}<https://museapp.com>{{% /sidenote %}} Muse is an app with a very unique UX. It claims to be a tool for thought, helping with research and deep thinking. The idea is that you have a n-dimensional canvas, and you can annotate at any point, crop images from a PDF, paste it somewhere else while the app knows where do they were cropped from... It's very interesting!

With a hefty $100 price tag per year, it came a bit short for me. I bought it and tried it for a few months, but don't use it anymore because you need to be in iOS devices to use it, and even on iPhone app doesn't work as good as the iPad app. Also, my daily driver is a beefy Linux server, and I couldn't access my data from there.

# Conclusion

As much as I love Emacs and the Org ecosystem, I'm nowadays using Neuron more and more. It's a much simpler implementation, you're not tied to org mode, but simple Markdown files, and the website generation is flawless.

Also, @srid has created this app, [cerveau.app](https://cerveau.app) to be able to update your neuron based zettelkasten from the web directly.

