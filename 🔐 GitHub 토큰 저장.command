#!/bin/zsh
# GitHub 발행 토큰을 macOS 키체인에 안전하게 저장하는 실행 파일
set -e

printf 'GitHub Personal Access Token을 붙여넣으세요. 입력 내용은 화면에 보이지 않습니다.\n'
read -rs github_token
printf '\n'

if [[ -z "$github_token" ]]; then
  printf '토큰이 입력되지 않아 저장하지 않았습니다.\n'
  exit 1
fi

security add-generic-password -U -a "$USER" -s "choijc79.github.io/GITHUB_TOKEN" -w "$github_token"
unset github_token
printf 'GitHub 토큰을 macOS 키체인에 저장했습니다. 이제 사이트 발행 파일을 실행하세요.\n'
