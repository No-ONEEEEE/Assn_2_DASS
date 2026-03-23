# DASS Assignment 2 Submission

This repository is organized in submission format with three sections:

- `blackbox/`
- `integration/`
- `whitebox/`

It contains test artifacts, reports, and test suites for the assignment tasks.

## Repository Link

- GitHub: https://github.com/No-ONEEEEE/Assn_2_DASS

## Folder Structure

```text
Testing_DASS_A2/
  blackbox/
    test_quickcart_api.py
    bug_report.md
    bug_report.tex

  integration/
    code/
    tests/
    diagrams/
    report.pdf

  whitebox/
    tests/
    diagrams/
    report.tex
```

## Prerequisites

1. Python 3.10+ and pip
2. `pytest`
3. For blackbox API testing: Docker Desktop (or Docker Engine) running
4. QuickCart API image available locally (for example from `quickcart_image.tar`)

Recommended install command:

```powershell
python -m pip install -U pytest requests
```

## How To Run The Code And Tests

## 1) Blackbox

### Start the QuickCart API

If you have a tar image file:

```powershell
Set-Location "<repo-root>"
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" load -i quickcart_image.tar
```

Run container:

```powershell
docker rm -f quickcart-test 2>$null
docker run --name quickcart-test -p 8080:8080 quickcart
```

The API should be available at:

- `http://localhost:8080/api/v1`

### Run blackbox tests

Open a second terminal:

```powershell
Set-Location "<repo-root>"
python -m pytest blackbox/test_quickcart_api.py -q
```

## 2) Integration

### Run integration test suite

```powershell
Set-Location "<repo-root>"
python -m pytest integration/tests/test_integration_scenarios.py -q
```

### Run integration demo script

```powershell
Set-Location "<repo-root>"
python integration/code/run_integration_demo.py
```

## 3) Whitebox

### Run whitebox test suite

```powershell
Set-Location "<repo-root>"
python -m pytest whitebox/tests/test_white_box_q1_3.py -q
```

## Reports Included

- Blackbox report: `blackbox/bug_report.md`, `blackbox/bug_report.tex`
- Integration report artifact: `integration/report.pdf`
- Whitebox report artifact: `whitebox/report.tex`

## Notes

- Use a virtual environment if required by your setup.
- Replace `<repo-root>` with your local absolute path to this repository.
- If imports fail after folder restructuring, run from repository root and ensure your Python path points to the required package locations used by your local setup.
