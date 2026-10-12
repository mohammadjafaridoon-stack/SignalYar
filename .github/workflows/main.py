
name: SignalYar CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - name: دریافت کد پروژه
        uses: actions/checkout@v4

      - name: تنظیم پایتون
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: نصب وابستگی‌ها
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            pip install python-telegram-bot requests
          fi

      - name: بررسی صحت کد پایتون
        run: python -m compileall -q .
