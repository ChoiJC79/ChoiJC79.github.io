#!/bin/zsh
# macOS에서 칼럼 동기화를 확인한 뒤 사이트를 발행하는 실행 파일
set -e

cd "$(dirname "$0")"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  GITHUB_TOKEN="$(security find-generic-password -a "$USER" -s "choijc79.github.io/GITHUB_TOKEN" -w 2>/dev/null || true)"
fi

if [[ -z "$GITHUB_TOKEN" ]]; then
  printf 'GitHub 토큰이 macOS 키체인에 없습니다. 먼저 🔐 GitHub 토큰 저장.command를 실행하세요.\n'
  exit 1
fi

export GITHUB_TOKEN
python3 -X utf8 scripts/check_columns_sync.py
python3 -X utf8 publish.py
