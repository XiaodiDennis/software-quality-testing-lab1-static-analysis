#!/bin/zsh
set -e
cd "$(dirname "$0")"
mkdir -p reports/original reports/fixed
{
  echo "Student: Xiaodi Wang"
  echo "Group: KP-44i"
  echo "Date: $(date)"
  echo "Python: $(python3 --version 2>&1)"
  echo "OS: $(sw_vers 2>/dev/null | tr '\n' ' ' || uname -a)"
  echo
  echo "Pylint:"
  pylint --version 2>&1 || true
  echo
  echo "Flake8:"
  flake8 --version 2>&1 || true
  echo
  echo "Bandit:"
  bandit --version 2>&1 || true
} > reports/environment_and_versions.txt

python3 static_analyzer.py sample_code.py --output reports/original
python3 static_analyzer.py fixed_sample_code.py --output reports/fixed

printf '\nAnalysis complete.\nOriginal code report: %s/reports/original/static_analysis_report.html\nFixed code report: %s/reports/fixed/static_analysis_report.html\n' "$PWD" "$PWD"
