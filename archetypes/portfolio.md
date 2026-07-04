---
# One file in content/portfolio/. Appears as a homepage Activities card
# (layouts/partials/portfolio.html) and, if `layout:` is set, renders a hub page.
# Scaffold: "$HOME/Library/Application Support/Hugo/0.89.4/hugo" new portfolio/<slug>.md
title: "{{ replace .Name "-" " " | title }}"
type: portfolio                   # REQUIRED
date: "{{ dateFormat "2006-01-02" .Date }}"
description: ""
caption: "Find out more"          # small line under the card title
image: "images/portfolio/<slug>.jpg"   # REQUIRED for the card, relative to static/
category: []
# layout: explainer               # optional: explainer | projects | publications | resources
#                                 # must match a layouts/portfolio/<layout>.html
# dataKey: <key>                  # REQUIRED iff layout: explainer — must match data/<key>.yml
# _build: { render: always, list: never }   # keep the page but hide its Activities card
---
