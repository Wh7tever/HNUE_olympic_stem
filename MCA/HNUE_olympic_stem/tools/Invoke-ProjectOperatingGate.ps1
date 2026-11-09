param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [ValidateSet('start', 'checkpoint', 'final')]
    [string]$Mode = 'checkpoint',

    [ValidateSet('auto', 'custom', 'tiny', 'small', 'standard', 'enterprise')]
    [string]$ProjectSize = 'auto',

    [switch]$SkipLint,
    [switch]$SkipTypecheck,
    [switch]$SkipTest,
    [switch]$SkipBuild,

    [switch]$NoAutoSync,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-ProjectRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Project root does not exist: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Get-StatusRank {
    param(
        [string]$Status
    )

    switch (($Status + '').ToLowerInvariant()) {
        'pass' { return 0 }
        'ready' { return 0 }
        'warn' { return 1 }
        'needs_attention' { return 1 }
        'fail' { return 2 }
        default { return 1 }
    }
}

function Join-Recommendations {
    param(
        $Readiness,
        $Delivery
    )

    $items = @()
    if ($Readiness -and $Readiness.PSObject.Properties.Name -contains 'recommendations') {
        $items += @($Readiness.recommendations)
    }

    if ($Delivery -and $Delivery.PSObject.Properties.Name -contains 'recommendations') {
        $items += @($Delivery.recommendations)
    }

    return @($items | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$readinessTool = Join-Path $PSScriptRoot 'Test-ProjectAgentReadiness.ps1'
$deliveryTool = Join-Path $PSScriptRoot 'Test-ProjectDeliveryState.ps1'

$readiness = $null
$delivery = $null
$gateNotes = @()

if (-not (Test-Path -LiteralPath $readinessTool)) {
    throw "Required tool does not exist: $readinessTool"
}

if (-not (Test-Path -LiteralPath $deliveryTool)) {
    throw "Required tool does not exist: $deliveryTool"
}

$readiness = & $readinessTool -ProjectRoot $resolvedRoot -ProjectSize $ProjectSize -Json | ConvertFrom-Json

if ($NoAutoSync) {
    $delivery = & $deliveryTool -ProjectRoot $resolvedRoot -Json | ConvertFrom-Json
} else {
    $delivery = & $deliveryTool -ProjectRoot $resolvedRoot -AutoSync -Json | ConvertFrom-Json
}

$readinessStatus = ($readiness.status + '')
$deliveryStatus = ($delivery.overall_status + '')
$readinessRank = Get-StatusRank -Status $readinessStatus
$deliveryRank = Get-StatusRank -Status $deliveryStatus

$overallRank = [Math]::Max($readinessRank, $deliveryRank)

if ($Mode -eq 'start') {
    if ($readinessRank -ge 2) {
        $overallRank = 2
        $gateNotes += 'Start gate failed because project readiness has blocking failures.'
    } elseif ($deliveryRank -ge 2) {
        $overallRank = [Math]::Max($overallRank, 1)
        $gateNotes += 'Start gate found delivery-state issues; fix before claiming completion.'
    }
}

if ($Mode -eq 'checkpoint') {
    if ($readinessRank -ge 2 -or $deliveryRank -ge 2) {
        $overallRank = 2
        $gateNotes += 'Checkpoint gate failed because readiness or delivery state has blocking failures.'
    }
}

if ($Mode -eq 'final') {
    if ($readinessRank -ge 2 -or $deliveryRank -ge 2) {
        $overallRank = 2
        $gateNotes += 'Final gate failed because readiness or delivery state has blocking failures.'
    }

    if (($delivery.score -as [int]) -lt 100) {
        $overallRank = 2
        $gateNotes += 'Final gate requires delivery score 100.'
    }

    # Static Analysis Checks
    $packageJsonPath = Join-Path $resolvedRoot 'package.json'
    if ((-not $SkipLint) -and (Test-Path -LiteralPath $packageJsonPath)) {
        try {
            $pkg = Get-Content -Raw -LiteralPath $packageJsonPath | ConvertFrom-Json
            if ($pkg.scripts -and $pkg.scripts.lint) {
                Write-Output "Running npm run lint in $resolvedRoot..."
                $oldWd = Get-Location
                Set-Location $resolvedRoot
                $lintOutput = & npm.cmd run lint 2>&1
                $lintExitCode = $LASTEXITCODE
                Set-Location $oldWd
                if ($lintExitCode -ne 0) {
                    $overallRank = 2
                    $gateNotes += "Static Analysis FAIL: 'npm run lint' failed (ExitCode: $lintExitCode)."
                    $flatOutput = @($lintOutput) -join "`n"
                    if ($flatOutput.Length -gt 200) {
                        $flatOutput = $flatOutput.Substring(0, 200) + "..."
                    }
                    $gateNotes += "Linter output: $flatOutput"
                } else {
                    Write-Output "Static Analysis: 'npm run lint' passed."
                }
            }
        } catch {
            Write-Warning "Failed to run npm run lint: $_"
        }
    }

    if (-not $SkipLint) {
        try {
            $psFiles = Get-ChildItem -Path $resolvedRoot -Filter *.ps1 -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
                $_.FullName -notmatch '\\(node_modules|\.git|\.venv|\.antigravity|\.aok-runtime)\\?'
            }
            if ($psFiles) {
                if (Get-Command Invoke-ScriptAnalyzer -ErrorAction SilentlyContinue) {
                    Write-Output "Running PSScriptAnalyzer on PowerShell files..."
                    $analyzerErrors = @()
                    foreach ($file in $psFiles) {
                        $issues = Invoke-ScriptAnalyzer -Path $file.FullName -Severity @('Error', 'Warning') -ErrorAction SilentlyContinue
                        if ($issues) {
                            foreach ($issue in $issues) {
                                $analyzerErrors += "$($file.Name): Line $($issue.Line) - [$($issue.Severity)] $($issue.Message)"
                            }
                        }
                    }
                    if ($analyzerErrors.Count -gt 0) {
                        $overallRank = 2
                        $gateNotes += "Static Analysis FAIL: PSScriptAnalyzer found $($analyzerErrors.Count) issues."
                        foreach ($err in ($analyzerErrors | Select-Object -First 5)) {
                            $gateNotes += "  $err"
                        }
                    } else {
                        Write-Output "Static Analysis: PSScriptAnalyzer passed."
                    }
                }
            }
        } catch {
            Write-Warning "Failed to run PSScriptAnalyzer: $_"
        }
    }
}

$overallStatus = switch ($overallRank) {
    0 { 'PASS' }
    1 { 'WARN' }
    default { 'FAIL' }
}

$modelRecommendation = switch ($Mode) {
    'start' { 'GPT-5.5 extra high for initial planning if project is new/ambiguous; otherwise GPT-5.5 medium.' }
    'checkpoint' { 'GPT-5.5 medium for normal execution; switch to GPT-5.5 extra high only if the gate reports failures or ambiguity.' }
    'final' { 'GPT-5.5 extra high for final audit/closeout.' }
}

$recommendations = @(Join-Recommendations -Readiness $readiness -Delivery $delivery)

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    mode = $Mode
    overall_status = $overallStatus
    model_recommendation = $modelRecommendation
    readiness = [PSCustomObject]@{
        status = $readinessStatus
        score = $readiness.score
        fail_count = @($readiness.checks | Where-Object { $_.status -eq 'FAIL' }).Count
        warn_count = @($readiness.checks | Where-Object { $_.status -eq 'WARN' }).Count
    }
    delivery = [PSCustomObject]@{
        status = $deliveryStatus
        score = $delivery.score
        total_tasks = $delivery.counts.total
        doing = $delivery.counts.doing
        blocked = $delivery.counts.blocked
        review = $delivery.counts.review
        done = $delivery.counts.done
        fail_count = @($delivery.checks | Where-Object { $_.status -eq 'FAIL' }).Count
        warn_count = @($delivery.checks | Where-Object { $_.status -eq 'WARN' }).Count
    }
    notes = $gateNotes
    recommendations = $recommendations
}

if ($Json) {
    $report | ConvertTo-Json -Depth 8
    return
}

Write-Output '========================================='
Write-Output '[ANTIGRAVITY CORE] FINAL OPERATING GATE'
Write-Output '========================================='
Write-Output ("Project operating gate: " + $overallStatus)
Write-Output ("Mode: " + $Mode)
Write-Output ("Readiness: " + $readinessStatus + " score=" + $readiness.score)
Write-Output ("Delivery: " + $deliveryStatus + " score=" + $delivery.score)
Write-Output ("Model: " + $modelRecommendation)
if (@($gateNotes).Count -gt 0) {
    Write-Output 'Notes:'
    foreach ($note in $gateNotes) {
        Write-Output ('- ' + $note)
    }
}

if (@($recommendations).Count -gt 0) {
    Write-Output 'Recommendations:'
    foreach ($recommendation in $recommendations) {
        Write-Output ('- ' + $recommendation)
    }
}

if ($Mode -eq 'final' -and $overallStatus -eq 'PASS') {
    Write-Output ''
    Write-Output '*** ANTIGRAVITY OPERATOR PLEDGE REQUIRED ***'
    Write-Output 'To claim completion in your final message, you MUST state:'
    Write-Output '"Với tư cách Người vận hành, tôi xác nhận vật liệu này đã được xử lý xong bằng Cỗ máy Antigravity."'
    Write-Output 'Do not claim completion without reciting this pledge.'
}
