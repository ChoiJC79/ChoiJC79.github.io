# 나를 정리하는 프로젝트 — GitHub 자동 발행 스크립트 (PowerShell)
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ── 설정 ──────────────────────────────────────
$TOKEN  = $env:GITHUB_TOKEN
$REPO   = "choijc79/choijc79.github.io"
$BRANCH = ""  # 자동 감지
$DIR    = Split-Path -Parent $MyInvocation.MyCommand.Path
# ─────────────────────────────────────────────

if (-not $TOKEN) {
    Write-Host "오류: GITHUB_TOKEN 환경변수가 설정되어 있지 않습니다." -ForegroundColor Red
    Write-Host '  setx GITHUB_TOKEN "본인의 GitHub Personal Access Token"' -ForegroundColor Yellow
    exit 1
}

$HEADERS = @{
    "Authorization" = "token $TOKEN"
    "Accept"        = "application/vnd.github.v3+json"
    "User-Agent"    = "NaeguJeongri/1.0"
}

function Set-HttpHeaders($req) {
    $req.Headers["Authorization"] = $HEADERS["Authorization"]
    $req.Accept                   = $HEADERS["Accept"]
    $req.UserAgent                = $HEADERS["User-Agent"]
}


function Get-FileSha($path) {
    try {
        $uri = "https://api.github.com/repos/$REPO/contents/$($path)?ref=$BRANCH"
        $req = [System.Net.HttpWebRequest]::Create($uri)
        $req.Method = "GET"
        Set-HttpHeaders $req
        $res = $req.GetResponse()
        $reader = New-Object System.IO.StreamReader($res.GetResponseStream())
        $body = $reader.ReadToEnd()
        $res.Close()
        $r = $body | ConvertFrom-Json
        $decoded = [System.Text.Encoding]::UTF8.GetString(
            [Convert]::FromBase64String(($r.content -replace "`n","")))
        return $r.sha, $decoded
    } catch {
        return $null, $null
    }
}

function Push-File($path, $content, $message) {
    $b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
    $sha, $_ = Get-FileSha $path

    $bodyObj = [ordered]@{ message = $message; content = $b64; branch = $BRANCH }
    if ($sha) { $bodyObj.sha = $sha }
    # ConvertTo-Json의 유니코드 이스케이프 문제 해결: -EscapeHandling 없이 수동 직렬화
    $json = $bodyObj | ConvertTo-Json -Compress -Depth 5
    # PowerShell 5.x에서 \uXXXX 이스케이프된 한글을 원래대로 복원
    $json = [System.Text.RegularExpressions.Regex]::Replace($json,
        '\\u([0-9a-fA-F]{4})',
        { param($m) [char][Convert]::ToInt32($m.Groups[1].Value, 16) })

    $uri = "https://api.github.com/repos/$REPO/contents/$path"
    Write-Host "      PUT $uri"

    try {
        $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $req = [System.Net.HttpWebRequest]::Create($uri)
        $req.Method = "PUT"
        $req.ContentType = "application/json; charset=utf-8"
        $req.ContentLength = $bodyBytes.Length
        Set-HttpHeaders $req
        $stream = $req.GetRequestStream()
        $stream.Write($bodyBytes, 0, $bodyBytes.Length)
        $stream.Close()
        $res = $req.GetResponse()
        $statusCode = [int]$res.StatusCode
        $res.Close()
        Write-Host "      HTTP $statusCode"
        return ($statusCode -in 200,201)
    } catch [System.Net.WebException] {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $errStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errStream)
        $errBody = $reader.ReadToEnd()
        Write-Host "      HTTP $statusCode : $errBody"
        # 토큰 스코프 확인
        try {
            $chk = [System.Net.HttpWebRequest]::Create("https://api.github.com/user")
            $chk.Method = "GET"
            Set-HttpHeaders $chk
            $chkRes = $chk.GetResponse()
            Write-Host "      Token scopes: $($chkRes.Headers['X-OAuth-Scopes'])"
            $chkRes.Close()
        } catch {}
        return $false
    }
}

function Read-Md($filename) {
    $fp = Join-Path $DIR $filename
    if (Test-Path $fp) { return Get-Content $fp -Raw -Encoding UTF8 } else { return "" }
}

function ConvertTo-HtmlItems($md) {
    $marker = "<!-- 새 항목은 아래에 추가됩니다 -->"
    if ($md -match [regex]::Escape($marker)) {
        $content = ($md -split [regex]::Escape($marker), 2)[1].Trim()
    } else { $content = $md.Trim() }

    if (-not $content) { return "<p class='empty'>아직 기록이 없습니다.</p>" }

    $items = @()
    $lines = $content -split "`n"
    $curDate = ""; $curText = @()

    foreach ($line in $lines) {
        $line = $line.Trim()
        if (-not $line) {
            if ($curText.Count -gt 0) { $items += ,@($curDate, ($curText -join " ")); $curText = @() }
            continue
        }
        if ($line -match '^#{1,4}\s*(\d{4}[\.\-/]\d{2}[\.\-/]\d{2})') {
            if ($curText.Count -gt 0) { $items += ,@($curDate, ($curText -join " ")); $curText = @() }
            $curDate = $Matches[1]
        } elseif ($line -match '^[-*]\s+(.+)') {
            if ($curText.Count -gt 0) { $items += ,@($curDate, ($curText -join " ")); $curText = @() }
            $curText = @($Matches[1])
        } else {
            $curText += $line -replace '^#+\s*', ''
        }
    }
    if ($curText.Count -gt 0) { $items += ,@($curDate, ($curText -join " ")) }

    if ($items.Count -eq 0) { return "<p class='empty'>아직 기록이 없습니다.</p>" }

    $recent = if ($items.Count -gt 30) { $items[($items.Count-30)..($items.Count-1)] } else { $items }
    $recent = [array]::Reverse($recent); $html = ""
    foreach ($item in $recent) {
        $date = $item[0]; $text = $item[1] -replace '\*\*(.+?)\*\*', '<strong>$1</strong>'
        $dateHtml = if ($date) { "<span class='date'>$date</span>" } else { "" }
        $html += "<div class='memo-item'>$dateHtml<span class='text'>$text</span></div>`n"
    }
    return $html
}

function Build-Html {
    $now    = (Get-Date).ToString("yyyy년 MM월 dd일 HH:mm")
    $ideas  = ConvertTo-HtmlItems (Read-Md "💡 아이디어·기획.md")
    $goals  = ConvertTo-HtmlItems (Read-Md "🎯 목표·계획·다짐.md")
    $diary  = ConvertTo-HtmlItems (Read-Md "📖 일상·감정·회고.md")
    $work   = ConvertTo-HtmlItems (Read-Md "📚 업무·논문·공부.md")

    return @"
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>정리노트 | 최승환</title>
<style>
  :root{--bg:#0d1117;--surface:#161b22;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--orange:#d29922;--purple:#bc8cff;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;line-height:1.7;padding:2rem 1rem;}
  .container{max-width:900px;margin:0 auto;}
  header{text-align:center;margin-bottom:3rem;padding-bottom:2rem;border-bottom:1px solid var(--border);}
  header h1{font-size:1.8rem;font-weight:700;margin-bottom:0.4rem;}
  header p{color:var(--muted);font-size:0.9rem;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;}
  @media(max-width:640px){.grid{grid-template-columns:1fr;}}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.5rem;}
  .card-title{font-size:1.1rem;font-weight:700;margin-bottom:1rem;}
  .card.ideas .card-title{color:var(--orange);}
  .card.goals .card-title{color:var(--green);}
  .card.diary .card-title{color:var(--purple);}
  .card.work  .card-title{color:var(--accent);}
  .memo-item{padding:0.6rem 0;border-bottom:1px solid var(--border);}
  .memo-item:last-child{border-bottom:none;}
  .date{display:inline-block;font-size:0.75rem;color:var(--muted);background:rgba(139,148,158,0.1);padding:0.1rem 0.5rem;border-radius:20px;margin-right:0.5rem;}
  .text{font-size:0.92rem;}
  .empty{color:var(--muted);font-size:0.9rem;font-style:italic;}
  footer{text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border);color:var(--muted);font-size:0.82rem;}
  a{color:var(--accent);text-decoration:none;}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📋 나를 정리하는 프로젝트</h1>
    <p>최승환 · 지방행정 연구자 · 제천시청 팀장 &nbsp;|&nbsp; 마지막 업데이트: $now</p>
    <p style="margin-top:0.5rem"><a href="/">← 홈으로</a></p>
  </header>
  <div class="grid">
    <div class="card ideas"><div class="card-title">💡 아이디어 · 기획</div>$ideas</div>
    <div class="card goals"><div class="card-title">🎯 목표 · 계획 · 다짐</div>$goals</div>
    <div class="card diary"><div class="card-title">📖 일상 · 감정 · 회고</div>$diary</div>
    <div class="card work"><div class="card-title">📚 업무 · 논문 · 공부</div>$work</div>
  </div>
  <footer><p>Claude와 함께 정리하는 나의 기록 &nbsp;·&nbsp; <a href="https://choijc79.github.io">choijc79.github.io</a></p></footer>
</div>
</body>
</html>
"@
}

function Update-IndexNav {
    $sha, $indexHtml = Get-FileSha "index.html"
    if (-not $indexHtml) { Write-Host "      index.html 가져오기 실패 (건너뜀)"; return }

    if ($indexHtml -match 'memo\.html') { Write-Host "      nav 링크 이미 존재 (건너뜀)"; return }

    # 실제 nav 구조: <button onclick="showPage('travel')">여행</button>
    $newBtn = "<button onclick=`"location.href='/memo.html'`">정리노트</button>"

    if ($indexHtml -match "showPage\('travel'\)") {
        # travel 버튼 전체 찾아서 뒤에 삽입
        $updated = $indexHtml -replace "(onclick=`"showPage\('travel'\)`"[^<]*</button>)", "`$1`n    $newBtn"
    } elseif ($indexHtml -match '</nav>') {
        $updated = $indexHtml -replace '</nav>', "    $newBtn`n</nav>"
    } else {
        Write-Host "      nav 패턴 못 찾음 (건너뜀)"
        return
    }

    $ok = Push-File "index.html" $updated "nav: 정리노트 버튼 추가"
    if ($ok) { Write-Host "      홈페이지 nav 업데이트 완료!" }
}

# ── 실행 ──
Write-Host "=================================================="
Write-Host "  나를 정리하는 프로젝트 - GitHub 발행 시작"
Write-Host "=================================================="
Write-Host ""

# 브랜치 자동 감지
Write-Host "[0/3] 브랜치 확인 중..."
try {
    $req0 = [System.Net.HttpWebRequest]::Create("https://api.github.com/repos/$REPO")
    $req0.Method = "GET"
    Set-HttpHeaders $req0
    $res0 = $req0.GetResponse()
    $reader0 = New-Object System.IO.StreamReader($res0.GetResponseStream())
    $repoInfo = $reader0.ReadToEnd() | ConvertFrom-Json
    $res0.Close()
    $BRANCH = $repoInfo.default_branch
    Write-Host "      브랜치: $BRANCH"
} catch {
    Write-Host "      저장소 접근 실패: $_"
    Read-Host "엔터를 누르면 창이 닫힙니다"
    exit
}

Write-Host "[1/4] 메모 페이지 생성 중..."
$html = Build-Html

Write-Host "[2/4] memo.html 업로드 중..."
$now2 = (Get-Date).ToString("yyyy-MM-dd HH:mm")
$ok1 = Push-File "memo.html" $html "memo update ($now2)"

Write-Host "[3/4] vietnam_moto_guide.html 업로드 중..."
$vietPath = Join-Path $DIR "vietnam_moto_guide.html"
$ok2 = $false
if (Test-Path $vietPath) {
    $vietContent = Get-Content $vietPath -Raw -Encoding UTF8
    $ok2 = Push-File "vietnam_moto_guide.html" $vietContent "add: 베트남 오토바이 루트 가이드"
    if ($ok2) { Write-Host "      베트남 가이드 업로드 완료!" }
    else       { Write-Host "      베트남 가이드 업로드 실패 (이미 있거나 오류)" }
} else {
    Write-Host "      vietnam_moto_guide.html 파일 없음 (건너뜀)"
    $ok2 = $true
}

Write-Host "[4/4] 홈페이지 nav 링크 확인 중..."
Update-IndexNav

Write-Host ""
if ($ok1) {
    Write-Host "완료!" -ForegroundColor Green
    Write-Host "   정리노트: https://choijc79.github.io/memo.html"
    if ($ok2) { Write-Host "   베트남 가이드: https://choijc79.github.io/vietnam_moto_guide.html" }
    Write-Host "   (반영까지 1~2분 소요)"
} else {
    Write-Host "업로드 실패." -ForegroundColor Red
}
Write-Host ""
Read-Host "엔터를 누르면 창이 닫힙니다"
