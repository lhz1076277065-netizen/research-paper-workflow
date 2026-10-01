#!/bin/bash
cd "$(dirname "$0")" || exit 1
python3 install.py "$@"
result=$?
if [[ -t 0 ]]; then
  printf '\n按回车键关闭窗口。'
  read -r answer
fi
exit "$result"
