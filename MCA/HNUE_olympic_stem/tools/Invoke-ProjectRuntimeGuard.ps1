param(
    [string]$ProjectRoot,
    [string]$RuntimeSessionRoot,

    [ValidateSet('private_read', 'read', 'write', 'file_write', 'retry', 'command', 'dangerous_command')]
    [string]$ActionKind = 'command',

    [string]$CommandText,
    [string]$RequestedPath,
    [switch]$SameSurfaceRetry,
    [switch]$NewEvidenceAvailable,
    [string]$OutputPath,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RuntimeSessionRoot {
    param(
        [string]$ProjectRoot,
        [string]$RuntimeSessionRoot
    )

    if ($RuntimeSessionRoot) {
        if (-not (Test-Path -LiteralPath $RuntimeSessionRoot)) {
            throw "Runtime session root not found: $RuntimeSessionRoot"
        }
        return (Resolve-Path -LiteralPath $RuntimeSessionRoot).Path
    }

    if (-not $ProjectRoot) {
        throw 'Provide either -ProjectRoot or -RuntimeSessionRoot.'
    }

    if (-not (Test-Path -LiteralPath $ProjectRoot)) {
        throw "Project root not found: $ProjectRoot"
    }

    $resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
    $pointerPath = Join-Path $resolvedProjectRoot '.aok-runtime\CURRENT_RUNTIME_SESSION.txt'
    if (Test-Path -LiteralPath $pointerPath) {
        $pointer = (Get-Content -LiteralPath $pointerPath -Raw -Encoding UTF8).Trim()
        if ($pointer -and (Test-Path -LiteralPath $pointer)) {
            return (Resolve-Path -LiteralPath $pointer).Path
        }
    }

    $sessionsRoot = Join-Path $resolvedProjectRoot '.aok-runtime\sessions'
    if (-not (Test-Path -LiteralPath $sessionsRoot)) {
        throw "No runtime sessions found under project: $resolvedProjectRoot"
    }

    $latest = Get-ChildItem -LiteralPath $sessionsRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latest) {
        throw "No runtime sessions found under: $sessionsRoot"
    }

    return $latest.FullName
}

$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeGuardTool = Join-Path $toolDir 'Invoke-RuntimeGuard.ps1'
if (-not (Test-Path -LiteralPath $runtimeGuardTool)) {
    throw "Runtime guard bridge not found: $runtimeGuardTool"
}

$powerShellExe = (Get-Process -Id $PID).Path
if (-not $powerShellExe) {
    $powerShellExe = (Get-Command powershell -ErrorAction Stop).Source
}

$sessionRoot = Resolve-RuntimeSessionRoot -ProjectRoot $ProjectRoot -RuntimeSessionRoot $RuntimeSessionRoot
$requiredFiles = @{
    SessionStatePath = Join-Path $sessionRoot 'session.json'
    ApprovalStatePath = Join-Path $sessionRoot 'approval.json'
    VerificationStatePath = Join-Path $sessionRoot 'verification.json'
    CompiledContextPath = Join-Path $sessionRoot 'compiled-context.json'
    VaultAccessPath = Join-Path $sessionRoot 'vault-access.json'
    RetryStatusPath = Join-Path $sessionRoot 'retry-status.json'
}

foreach ($path in $requiredFiles.Values) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Runtime state file missing: $path"
    }
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $sessionRoot ('guard-decision-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [System.Guid]::NewGuid().ToString('N').Substring(0, 8) + '.json')
}

$guardArgs = @(
    '-ExecutionPolicy', 'Bypass',
    '-File', $runtimeGuardTool,
    '-SessionStatePath', $requiredFiles.SessionStatePath,
    '-ApprovalStatePath', $requiredFiles.ApprovalStatePath,
    '-VerificationStatePath', $requiredFiles.VerificationStatePath,
    '-CompiledContextPath', $requiredFiles.CompiledContextPath,
    '-VaultAccessPath', $requiredFiles.VaultAccessPath,
    '-RetryStatusPath', $requiredFiles.RetryStatusPath,
    '-ActionKind', $ActionKind,
    '-OutputPath', $OutputPath,
    '-Json'
)

if ($CommandText) { $guardArgs += @('-CommandText', $CommandText) }
if ($RequestedPath) { $guardArgs += @('-RequestedPath', $RequestedPath) }
if ($SameSurfaceRetry) { $guardArgs += '-SameSurfaceRetry' }
if ($NewEvidenceAvailable) { $guardArgs += '-NewEvidenceAvailable' }

$decision = & $powerShellExe @guardArgs | ConvertFrom-Json

$result = [PSCustomObject]@{
    runtime_session_root = $sessionRoot
    output_path = $OutputPath
    decision = $decision
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
    return
}

Write-Output ('Project runtime guard: ' + [string]$decision.decision)
Write-Output ('- session: ' + $sessionRoot)
Write-Output ('- action: ' + [string]$decision.action_kind)
Write-Output ('- output: ' + $OutputPath)
if ($decision.reasons) {
    Write-Output ('- reasons: ' + (($decision.reasons) -join ' | '))
}
if ($decision.required_next_steps) {
    Write-Output ('- next: ' + (($decision.required_next_steps) -join ' | '))
}
