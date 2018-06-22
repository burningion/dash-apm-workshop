# Dash APM Workshop (2018)

This repo contains microservices written in Python and Docker for an APM Workshop I'm running at [DASH](https://www.dashcon.io/) in 2018. 

This repo builds upon the excellent work of [vlad-mh's PyCon UK talk](https://github.com/vlad-mh/pyconuk-2017) about APM, and the [dd-py-tracing-workshop](https://github.com/DataDog/dd-py-tracing-workshop) from [mstbbs](https://github.com/mstbbs).

This repo is meant to be used alongside some Jupyter notebooks found [here](https://github.com/burningion/opentracing-notebook). You'll check out this repo, and run the docker containers here from within the Jupyter notebook.

# Running the Examples

You'll need to first create a Datadog account, and then get your API key from the prompt. 

You'll then be able to start the example project with a:

```bash
DD_API_KEY=<YOUR_API_KEY> STEP=1 docker-compose up
```
