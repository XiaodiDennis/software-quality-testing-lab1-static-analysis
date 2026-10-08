# Laboratory Work #1 - Software Inspection and Analysis (Part 2)

**Student:** Xiaodi Wang  
**Group:** KP-44i  
**Program:** Bachelor in Software Engineering  
**Faculty:** Faculty of Program Systems and Applied Mathematics  
**University:** NTUU KPI  
**OS:** macOS  
**GitHub:** https://github.com/XiaodiDennis

## Topic
Using Software Tools to Implement a Module for Static Software Analysis.

## Included files

- `sample_code.py` - intentionally imperfect Python code for inspection.
- `fixed_sample_code.py` - corrected version after interpreting findings.
- `static_analyzer.py` - analysis module. Runs Pylint, Flake8 and Bandit and creates summary reports.
- `requirements.txt` - required third-party static-analysis tools.
- `run_analysis.sh` - one-command macOS runner.
- `reports/` - raw and summarized analysis outputs.
- `docs/Lab_Report_Xiaodi_Wang.docx` - formal laboratory report.
- `docs/Lab_Report_Xiaodi_Wang.pdf` - PDF copy of the report.

## Exact macOS steps

Open Terminal and run:

```bash
cd /Users/hsiao/Downloads
unzip KP44i_SQT_Lab1_Xiaodi_Wang.zip
cd KP44i_SQT_Lab1_Xiaodi_Wang

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

./run_analysis.sh
open reports/static_analysis_report.html
```

You can also run the tools separately:

```bash
pylint sample_code.py | tee reports/pylint_report.txt
flake8 sample_code.py | tee reports/flake8_report.txt
bandit -r sample_code.py | tee reports/bandit_report.txt
```

Then rerun:

```bash
python3 static_analyzer.py sample_code.py --output reports
```

This refreshes the summary and HTML report while preserving the real third-party tool output.

## Typical findings to explain during defence

1. Unused imports increase noise and can indicate unfinished code.
2. Non-standard function/class names reduce readability and violate Python naming conventions.
3. Missing docstrings reduce maintainability and API clarity.
4. Long lines are style violations and make review harder.
5. A hard-coded password-like value is a security smell.
6. `subprocess.run(..., shell=True)` with concatenated input can create command-injection risk.
7. `random` is not appropriate for security-sensitive tokens; use `secrets`.
8. The corrected version removes or mitigates these issues.

## Suggested GitHub repository

Repository name:

`software-quality-testing-lab1-static-analysis`

If GitHub CLI is installed and authenticated:

```bash
cd /Users/hsiao/Downloads/KP44i_SQT_Lab1_Xiaodi_Wang
git init
git add .
git commit -m "Complete Laboratory Work 1 static analysis"
git branch -M main
gh repo create software-quality-testing-lab1-static-analysis --public --source=. --remote=origin --push
```
