# Hollow Soil Column — Streamlit

Interactive incremental elastic simulation of an annular soil specimen with a stiff outer hoop membrane, softer inner hoop membrane, and pressurized air cavity.

## Upload and deploy without using Git commands

1. Extract `soil-column-streamlit.zip` on your computer.
2. Create a new GitHub repository, for example `soil-column-streamlit`.
3. In the repository, select **Add file → Upload files** (a new empty repository also shows an upload-existing-file link).
4. Upload the **contents** of the extracted project folder, not the ZIP itself. `streamlit_app.py`, `model.py`, and `requirements.txt` must appear at the repository root. Upload README.md, MODEL.md, tests/, and example_parameters.json too. Hidden `.streamlit/`, `.github/`, and `.gitignore` are optional for deployment; if your file chooser hides them, the app still runs without them.
5. Commit the files.
6. Open https://share.streamlit.io/ and connect your GitHub account.
7. Create a new app, choose the repository and branch (usually `main`), and set the entrypoint to **streamlit_app.py**.
8. In advanced settings, select **Python 3.12**, then deploy. No secrets, API keys, datasets, or external system packages are required.

If you uploaded the project as a nested folder, either move its contents to the root or select `soil-column-streamlit/streamlit_app.py` as the entrypoint. Keep model.py and requirements.txt alongside it.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
Dependency placement: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization

## Run locally

Use Python 3.12 (recommended). In a terminal inside the project directory:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Features

- Inputs in mm, MPa, kPa, and N; internal calculations in SI units.
- Live specimen cross section with undeformed outlines and adjustable displacement exaggeration.
- Radial displacement profile through the soil annulus.
- Load–shortening, radial displacement, and cavity-pressure curves.
- Comparison of sealed isothermal air with regulated constant pressure.
- CSV sweep and parameter JSON downloads.
- Input validation and small-deformation screening messages.
- GitHub Actions workflow for mechanics and app checks.

The loading slider is a quasi-static load progression, not a time-dependent simulation. The parameter JSON is an export for reproducibility, not an in-app import. Illustrative defaults are supplied in example_parameters.json.

## Validate

```bash
python -m unittest discover -s tests -v
```

Tests check the analytical free-uniaxial elastic limit, energy stiffness symmetry and positivity, equilibrium, gas coupling, radial boundaries, linearity, invalid input, and Streamlit startup/control interaction.

## Model scope

This is a small-strain incremental model about an already pressurized equilibrium. It assumes a shared rigid top plate spanning both soil and air, frictionless radial movement at the plates, maintained membrane contact, and hoop-only membrane stiffness. It omits initial inflation, prestress geometric stiffness, soil yielding, drainage, buckling, wrinkling, and heightwise bulging. Read MODEL.md before interpreting results. Parameters and results are illustrative until calibrated.

For loading applied to the annular soil alone with a mechanically independent cavity end cap, revise the boundary conditions rather than using this shared-plate model unchanged.

## Project files

- streamlit_app.py: user interface and visualization
- model.py: mechanics, parameter validation, and load sweep
- MODEL.md: derivation and interpretation
- requirements.txt: dependencies
- example_parameters.json: SI-unit defaults
- tests/: numerical and app tests
- .streamlit/config.toml: optional theme
- .github/workflows/tests.yml: optional automated checks
