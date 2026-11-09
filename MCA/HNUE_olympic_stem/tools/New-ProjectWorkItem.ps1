param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [string]$TaskId = '',
    [string]$SliceId = 'VS-001',

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [string]$Goal = 'TO_BE_FILLED',
    [string]$Scope = 'TO_BE_FILLED',
    [string]$FilesModules = 'TO_BE_FILLED',
    [string]$Verification = 'TO_BE_FILLED',
    [string[]]$Dependencies = @(),
    [string[]]$BlockedBy = @(),

    [ValidateSet('AFK', 'HITL', 'unknown')]
    [string]$InteractionMode = 'unknown',

    [ValidateSet('info_only', 'small_change', 'medium_change', 'large_change', 'sensitive_change', 'incident')]
    [string]$TaskClass = 'medium_change',

    [ValidateSet('todo', 'doing', 'blocked', 'review', 'done')]
    [string]$Status = 'todo',

    [ValidateSet('low', 'medium', 'high', 'unknown')]
    [string]$Risk = 'unknown',

    [string]$OwnerAgent = 'unassigned',
    [string]$Blocker = 'none',
    [string]$Evidence = 'TO_BE_FILLED',

    [switch]$NoSync,
    [switch]$Force,
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

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [string[]]$Lines
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    $content = ($Lines -join [Environment]::NewLine) + [Environment]::NewLine
    [System.IO.File]::WriteAllText($Path, $content, (New-Object System.Text.UTF8Encoding($false)))
}

function ConvertTo-MarkdownCell {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return 'TO_BE_FILLED'
    }

    return (($Value -replace '\|', '\|') -replace "(`r`n|`n|`r)", '<br>').Trim()
}

function Get-NextTaskId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $numbers = @()
    $tasksDir = Join-Path $Root 'TASKS'
    if (Test-Path -LiteralPath $tasksDir) {
        $taskFiles = @(Get-ChildItem -LiteralPath $tasksDir -File -Filter 'T-*.md' -ErrorAction SilentlyContinue)
        foreach ($file in $taskFiles) {
            $match = [regex]::Match($file.BaseName, '^T-(?<num>\d+)$')
            if ($match.Success) {
                $numbers += [int]$match.Groups['num'].Value
            }
        }
    }

    $ledgerPath = Join-Path $Root 'TASK_LEDGER.md'
    if (Test-Path -LiteralPath $ledgerPath) {
        $ledgerText = Get-Content -LiteralPath $ledgerPath -Raw -Encoding UTF8
        foreach ($line in ($ledgerText -split "`r`n|`n|`r")) {
            if ($line -match '^\|\s*T-0001\s*\|\s*VS-001\s*\|\s*todo\s*\|\s*unassigned\s*\|\s*TO_BE_FILLED\s*\|\s*TO_BE_FILLED\s*\|\s*TO_BE_FILLED\s*\|\s*none\s*\|\s*TO_BE_FILLED\s*\|\s*$') {
                continue
            }

            foreach ($match in [regex]::Matches($line, 'T-(?<num>\d{4,})')) {
                $numbers += [int]$match.Groups['num'].Value
            }
        }
    }

    $next = if ($numbers.Count -gt 0) { ([int]($numbers | Measure-Object -Maximum).Maximum) + 1 } else { 1 }
    return ('T-{0:D4}' -f $next)
}

function New-TasksReadmeLines {
    return @(
        '# TASKS',
        '',
        'This folder stores one file per project task or work item.',
        '',
        '## Rules',
        '',
        '- Keep each task bounded to one vertical slice or one clear technical outcome.',
        '- Link each task back to `DELIVERY_PLAN.md` and `TASK_LEDGER.md`.',
        '- Do not mark a task done without verification evidence.',
        '- If blocked, record the blocker and next recommended move.',
        '- Mark interaction_mode as AFK when the agent can proceed alone; use HITL when user input, private access, external action, or product judgment is needed.',
        '',
        '## Naming',
        '',
        '- `T-0001.md`',
        '- `T-0002.md`'
    )
}

function New-TaskLedgerLines {
    return @(
        '# TASK_LEDGER.md',
        '',
        'Use this file as the project task ledger across humans, agents, and sessions.',
        '',
        '| Task ID | Slice | Status | Owner/Agent | Scope | Files/Modules | Verification | Blocker | Evidence | Interaction Mode | Blocked By |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
        '',
        '## Status Values',
        '',
        '- todo',
        '- doing',
        '- blocked',
        '- review',
        '- done',
        '',
        '## Interaction Mode',
        '',
        '- AFK: agent can continue without user input.',
        '- HITL: human decision, private access, external action, or product judgment is required.',
        '- unknown: not classified yet.'
    )
}

function Set-LedgerRow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Id,
        [Parameter(Mandatory = $true)]
        [string]$Row
    )

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in ($Text -split "`r`n|`n|`r")) {
        if ($line -ne '') {
            [void]$lines.Add($line)
        }
    }

    $taskPattern = '^\|\s*' + [regex]::Escape($Id) + '\s*\|'
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $taskPattern) {
            $lines[$i] = $Row
            return ($lines -join [Environment]::NewLine) + [Environment]::NewLine
        }
    }

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\|\s*---\s*\|') {
            $lines.Insert($i + 1, $Row)
            return ($lines -join [Environment]::NewLine) + [Environment]::NewLine
        }
    }

    [void]$lines.Add($Row)
    return ($lines -join [Environment]::NewLine) + [Environment]::NewLine
}

function Invoke-ProjectStatusSync {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $syncTool = Join-Path $PSScriptRoot 'Sync-ProjectStatus.ps1'
    if (Test-Path -LiteralPath $syncTool) {
        & $syncTool -ProjectRoot $Root -Json | Out-Null
        return $true
    }

    return $false
}

function New-TaskFileLines {
    param(
        [string]$Id,
        [string]$TaskTitle
    )

    $dependencyLines = if ($Dependencies.Count -gt 0) {
        @($Dependencies | ForEach-Object { '- ' + $_ })
    } else {
        @('- none')
    }

    $blockedByLines = if ($BlockedBy.Count -gt 0) {
        @($BlockedBy | ForEach-Object { '- ' + $_ })
    } else {
        @('- none')
    }

    return @(
        "# $Id`: $TaskTitle",
        '',
        '## Metadata',
        '',
        "- task_id: $Id",
        "- slice_id: $SliceId",
        "- task_class: $TaskClass",
        "- status: $Status",
        "- risk: $Risk",
        "- owner_agent: $OwnerAgent",
        "- interaction_mode: $InteractionMode",
        '',
        '## Goal',
        '',
        $Goal,
        '',
        '## Scope',
        '',
        $Scope,
        '',
        '## Files / Modules',
        '',
        $FilesModules,
        '',
        '## Dependencies',
        ''
    ) + $dependencyLines + @(
        '',
        '## Blocked By',
        ''
    ) + $blockedByLines + @(
        '',
        '## Verification',
        '',
        $Verification,
        '',
        '## Blocker',
        '',
        $Blocker,
        '',
        '## Evidence',
        '',
        $Evidence,
        '',
        '## Execution Log',
        '',
        '| Time | Actor | Event | Evidence |',
        '| --- | --- | --- | --- |',
        '| TO_BE_FILLED | TO_BE_FILLED | task created | TO_BE_FILLED |',
        '',
        '## Handoff Notes',
        '',
        '- TO_BE_FILLED'
    )
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$created = @()
$skipped = @()
$syncedStatus = $false

if ([string]::IsNullOrWhiteSpace($TaskId)) {
    $TaskId = Get-NextTaskId -Root $resolvedRoot
}

if ($TaskId -notmatch '^T-\d{4,}$') {
    throw 'TaskId must use format T-0001, T-0002, ...'
}

$tasksDir = Join-Path $resolvedRoot 'TASKS'
$tasksReadmePath = Join-Path $tasksDir 'README.md'
$taskPath = Join-Path $tasksDir ($TaskId + '.md')
$ledgerPath = Join-Path $resolvedRoot 'TASK_LEDGER.md'
$taskFileAlreadyExisted = Test-Path -LiteralPath $taskPath

if (-not (Test-Path -LiteralPath $tasksReadmePath)) {
    Write-Utf8NoBom -Path $tasksReadmePath -Lines (New-TasksReadmeLines)
    $created += 'TASKS\README.md'
}

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    Write-Utf8NoBom -Path $ledgerPath -Lines (New-TaskLedgerLines)
    $created += 'TASK_LEDGER.md'
}

if ($taskFileAlreadyExisted -and (-not $Force)) {
    $skipped += ('TASKS\' + $TaskId + '.md')
} else {
    Write-Utf8NoBom -Path $taskPath -Lines (New-TaskFileLines -Id $TaskId -TaskTitle $Title)
    $created += ('TASKS\' + $TaskId + '.md')
}

$ledgerText = Get-Content -LiteralPath $ledgerPath -Raw -Encoding UTF8
$row = '| ' + (ConvertTo-MarkdownCell $TaskId) +
        ' | ' + (ConvertTo-MarkdownCell $SliceId) +
        ' | ' + (ConvertTo-MarkdownCell $Status) +
        ' | ' + (ConvertTo-MarkdownCell $OwnerAgent) +
        ' | ' + (ConvertTo-MarkdownCell $Scope) +
        ' | ' + (ConvertTo-MarkdownCell $FilesModules) +
        ' | ' + (ConvertTo-MarkdownCell $Verification) +
        ' | ' + (ConvertTo-MarkdownCell $Blocker) +
        ' | ' + (ConvertTo-MarkdownCell $Evidence) +
        ' | ' + (ConvertTo-MarkdownCell $InteractionMode) +
        ' | ' + (ConvertTo-MarkdownCell ($BlockedBy -join '<br>')) + ' |'

$legacyPlaceholderPattern = '(?m)^\|\s*T-0001\s*\|\s*VS-001\s*\|\s*todo\s*\|\s*unassigned\s*\|\s*TO_BE_FILLED\s*\|\s*TO_BE_FILLED\s*\|\s*TO_BE_FILLED\s*\|\s*none\s*\|\s*TO_BE_FILLED\s*(\|\s*(unknown|TO_BE_FILLED)\s*\|\s*(none|TO_BE_FILLED)\s*)?\|\s*$'
$hasLedgerEntry = $ledgerText -match [regex]::Escape($TaskId)

if (($TaskId -eq 'T-0001') -and (-not $taskFileAlreadyExisted) -and ($ledgerText -match $legacyPlaceholderPattern)) {
    $updatedLedger = [regex]::Replace($ledgerText, $legacyPlaceholderPattern, $row, 1)
    [System.IO.File]::WriteAllText($ledgerPath, $updatedLedger, (New-Object System.Text.UTF8Encoding($false)))
    $created += 'TASK_LEDGER.md entry'
} elseif (-not $hasLedgerEntry) {
    $updatedLedger = Set-LedgerRow -Text $ledgerText -Id $TaskId -Row $row
    [System.IO.File]::WriteAllText($ledgerPath, $updatedLedger, (New-Object System.Text.UTF8Encoding($false)))
    $created += 'TASK_LEDGER.md entry'
} else {
    $skipped += 'TASK_LEDGER.md entry'
}

if (-not $NoSync) {
    $syncedStatus = Invoke-ProjectStatusSync -Root $resolvedRoot
}

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    task_id = $TaskId
    task_path = $taskPath
    ledger_path = $ledgerPath
    interaction_mode = $InteractionMode
    blocked_by = $BlockedBy
    created = $created
    skipped = $skipped
    synced_project_status = $syncedStatus
}

if ($Json) {
    $report | ConvertTo-Json -Depth 5
    return
}

Write-Output "Project work item: $TaskId"
Write-Output "Task file: $taskPath"
Write-Output "Ledger: $ledgerPath"
Write-Output ("Created: " + ($(if ($created.Count -gt 0) { $created -join ', ' } else { 'none' })))
Write-Output ("Skipped: " + ($(if ($skipped.Count -gt 0) { $skipped -join ', ' } else { 'none' })))
