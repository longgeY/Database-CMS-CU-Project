# run_all.ps1
# 一键批量跑 CMS 基准：多 ε、多工作负载、CU on/off
# 使用：
#   powershell -ExecutionPolicy Bypass -File .\run_all.ps1

$ErrorActionPreference = "Stop"

# ---- 参数区：按需修改 ----
$python    = "python"         # 或填写完整路径，比如 "C:\Users\...\python.exe"
$bench     = ".\benchmark.py" # benchmark.py 路径
$N         = 200000           # updates 数
$U         = 100000           # key 空间
$delta     = 1e-3
$trials    = 3
$Q         = 2000
$alpha     = 1.0              # Zipf 参数
$epsList   = @(0.002, 0.001, 0.0005)   # 扫描的 ε
$resultsDir= ".\results"
$stamp     = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir    = Join-Path $resultsDir "run_$stamp"

# ---- 准备输出目录 ----
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$logFile = Join-Path $runDir "run.log"

function Run-Job {
    param(
        [string]$workload, [double]$eps, [int]$use_cu, [double]$alpha
    )
    $cuTag = $(if ($use_cu -eq 1) {"cu"} else {"nocu"})
    $epsTag = ("{0:g}" -f $eps).Replace(".", "p")
    $outName = "{0}_{1}_eps{2}.csv" -f $workload, $cuTag, $epsTag
    if ($workload -eq "zipf") {
        $outName = "{0}_{1}_a{2}_eps{3}.csv" -f $workload, $cuTag, ("{0:g}" -f $alpha).Replace(".", "p"), $epsTag
    }
    $outPath = Join-Path $runDir $outName

    $args = @("--eps", $eps, "--delta", $delta, "--N", $N, "--U", $U,
              "--workload", $workload, "--Q", $Q, "--trials", $trials,
              "--seed", 7, "--out", $outPath)

    if ($workload -eq "zipf") {
        $args += @("--alpha", $alpha)
    }
    if ($use_cu -eq 1) {
        $args += @("--use_cu")
    }

    $cmd = "$python $bench " + ($args -join " ")
    Write-Host ">>> $cmd"
    Add-Content -Path $logFile -Value ">>> $cmd"
    & $python $bench @args 2>&1 | Tee-Object -FilePath $logFile
}

# ---- 批量执行 ----
Write-Host "=== CMS Benchmark batch start: $stamp ==="
Add-Content -Path $logFile -Value "=== CMS Benchmark batch start: $stamp ==="

foreach ($eps in $epsList) {
    # uniform: CU on/off
    Run-Job -workload "uniform" -eps $eps -use_cu 0 -alpha $alpha
    Run-Job -workload "uniform" -eps $eps -use_cu 1 -alpha $alpha

    # zipf(a=1.0): CU on
    Run-Job -workload "zipf" -eps $eps -use_cu 1 -alpha $alpha
}

Write-Host "=== All runs finished. Merging CSVs... ==="
Add-Content -Path $logFile -Value "=== All runs finished. Merging CSVs... ==="

# ---- 合并所有本次 CSV ----
$merged = Join-Path $runDir "all_results_merged.csv"
$csvs = Get-ChildItem -Path $runDir -Filter *.csv | Where-Object { $_.Name -ne "all_results_merged.csv" }

if ($csvs.Count -gt 0) {
    $first = $true
    Remove-Item -ErrorAction Ignore $merged
    foreach ($f in $csvs) {
        if ($first) {
            Get-Content $f.FullName | Out-File -FilePath $merged -Encoding UTF8
            $first = $false
        } else {
            (Get-Content $f.FullName | Select-Object -Skip 1) | Out-File -Append -FilePath $merged -Encoding UTF8
        }
    }
    Write-Host "Merged to: $merged"
    Add-Content -Path $logFile -Value "Merged to: $merged"
} else {
    Write-Host "No CSVs found to merge."
    Add-Content -Path $logFile -Value "No CSVs found to merge."
}

Write-Host "=== Done. Results in $runDir ==="
Add-Content -Path $logFile -Value "=== Done. Results in $runDir ==="
