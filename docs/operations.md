# Operating and deployment guide

## Local execution

Follow the README installation commands. Use `portfolio build --source demo` for
a synthetic offline run or `--source full` for original UCI sources. Set a custom build
destination with `--output /path/to/results`. The dashboard reads the repository's
standard `artifacts/full` and `artifacts/demo` locations.

## Dashboard deployment

### Docker

```bash
docker build -t mohit-analytics-portfolio .
docker run --rm -p 8501:8501 mohit-analytics-portfolio
```

The image includes precomputed aggregate results. A non-root user runs the app.
The Dockerfile is supplied as a deployment option. It requires a working local
Docker engine. Validate the image in your deployment environment before use.

### Streamlit Community Cloud

After publishing the repository, create an app using `streamlit_app.py` and Python
3.12. The pinned `requirements.txt` is the runtime environment. The application
imports local code through the `src` path initialisation in its entrypoint.
No API keys, dataset credentials or secrets are needed. Do not upload real
customer data to this demonstration. No live deployment is claimed until a
provider returns and verifies an app URL.

### GitHub Pages

The static landing page in `docs/` presents computed evidence and links to exported
case studies. GitHub Pages cannot run the Python dashboard. Select GitHub Actions
as the Pages source in repository settings, then run the optional 'Publish showcase'
workflow. The workflow is manual so repository creation does not automatically
change publication settings.

## Expected outputs

The full and demo builds each produce retail CSV marts, JSON summaries,
retention model comparison/threshold/split/test outputs, logistics shipments/plan/
scenario outputs, a PNG overview and three Markdown memos. Local rebuilds also
create a DuckDB warehouse, line-level Parquet and trusted model pickle, which Git
ignores. Precomputed public-source results remain available in a fresh clone.

## Common failures

| Symptom | Action |
| --- | --- |
| Source checksum mismatch | Review upstream changes. Do not disable validation |
| Source download unavailable | Run the generated synthetic offline demo |
| Missing model for batch scoring | Rebuild the corresponding source mode |
| No feasible logistics scenario | Relax the chosen service/budget assumptions |
| Port 8501 in use | Add `--server.port 8502` to the Streamlit command |
| Test dependency unavailable | Use Python 3.12 and the supplied dependency lock |

## Verification boundaries

Local tests and notebook execution are recorded in `VERIFICATION.md`. GitHub CI,
Docker runtime and provider deployment need separate confirmation in their actual
environments. There is no fake green badge, fabricated commit history or assumed
deployment status.

The notebook runner defaults to in-process execution of ordinary Python cells,
with captured text and rich outputs. Use `--engine jupyter` for a separate kernel
on a machine that permits local sockets. The in-process path does not support
IPython magics or shell cells, and none of the supplied notebooks require them.
