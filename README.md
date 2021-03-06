eventbot-web-api
================

[![CircleCI](https://circleci.com/gh/duffj/eventbot-web-api.svg?style=svg)](https://circleci.com/gh/duffj/eventbot-web-api)

Eventbot web API.


Pipeline
--------

CircleCI is configured to auto-deploy to Heroku if the build passes.


Local development
-----------------

NB. Tested on a Mac, not on Windows.

### Pre-requisites

* Python 2.7 with pipenv
* Heroku CLI Toolbelt
* GNU Make

FYI I use [homebrew][1] for most of these things on my Mac. 

### Setup

Install pip requirements:

    pipenv install

### To run locally

    make local

### To run the tests

    make test

### To deploy

The app is deployed automatically to Heroku by CircleCI on
successful build of the `master` branch.


ngrok
-----

To run:

    ngrok http 50000

View the dashboard: [Dashboard](http://localhost:4040/inspect/http)

Technologies
------------

* Python (with pipenv) - see [Pipfile](Pipfile)
* Heroku
* CircleCI
* ngrok


Environment variables
---------------------

See:

* [.env.example](.env.example) for examples
* [settings.py](eventbot/settings.py) for default values
* variables configured into Heroku for live settings
* variables configured into CircleCI for test settings

Tips
----

### Adding a new 'slash command'

See [Slash Commands](https://api.slack.com/slash-commands) (official Slack docs).

1. Go to [https://api.slack.com](https://api.slack.com) / Your Apps / Eventbot / Slash commands.

Links
-----

* https://elements.heroku.com/addons/mongolab
* https://community.nitrous.io/tutorials/deploying-a-flask-application-to-heroku
* [Using ngrok to develop locally for Slack](https://api.slack.com/tutorials/tunneling-with-ngrok)

[1]: https://brew.sh/ "homebrew"
