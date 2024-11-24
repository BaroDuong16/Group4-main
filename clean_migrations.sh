#!/bin/bash

# Xóa các tệp .py trong thư mục migrations, trừ _init_.py, và bỏ qua thư mục .venv
find . -path "./.venv" -prune -o -path "/migrations/.py" -not -name "_init_.py" -exec rm -f {} +

# Xóa các tệp .pyc trong thư mục migrations và bỏ qua thư mục .venv
find . -path "./.venv" -prune -o -path "/migrations/.pyc" -exec rm -f {} +