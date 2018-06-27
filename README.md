# Dash APM Workshop (2018)

This repo contains microservices written in Python and Docker for an APM Workshop I'm running at [DASH](https://www.dashcon.io/) in 2018. 

This repo builds upon the excellent work of [vlad-mh's PyCon UK talk](https://github.com/vlad-mh/pyconuk-2017) about APM, and the [dd-py-tracing-workshop](https://github.com/DataDog/dd-py-tracing-workshop) from [mstbbs](https://github.com/mstbbs).

This repo is meant to be used alongside the Jupyter notebooks in this repo. 

You'll check out this repo, run `jupyter notebook`, and run the docker containers here from within the Jupyter notebook.

# Pre APM Event Prep

Because Wifi tends to be spotty at events, it would help if you downloaded the Docker images ahead of time.

If you don't already have [Docker](https://www.docker.com/) installed locally, you'll need to do that too. 

Once you've got that running, you can then clone this repo, and from within the top level directory run a `STEP=1 docker-compose up`. 

Docker will download all the images necessary for you to run through the event. All of the Docker images are pinned, so they won't change.

You'll be making for a better experience for everyone else. Thanks!
# Running the Examples

You'll need to first create a Datadog account, and then get your API key from the prompt. 

You'll then be able to start the example project with a:

```bash
DD_API_KEY=<YOUR_API_KEY> STEP=1 docker-compose up
```
