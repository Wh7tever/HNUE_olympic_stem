param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [string]$CurrentMilestone = '',
    [string]$ActiveSlice = '',

    [ValidateSet('', 'green', 'yellow', 'red', 'unknown')]
    [string]$OverallStatus = '',

    [string[]]$NextAction = @(),
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

function ConvertFrom-MarkdownCell {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }

    return (($Value.Trim() -replace '\\\|', '|') -replace '<br>', ' / ')
}

function ConvertTo-MarkdownCell {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return 'none'
    }

    return (($Value.Trim() -replace '\|', '\|') -replace "(`r`n|`n|`r)", '<br>')
}

function Test-Filled {
    param(
        [string]$Value
    )

    return (-not [string]::IsNullOrWhiteSpace($Value)) -and ($Value.Trim() -notin @('TO_BE_FILLED', 'none', 'n/a', 'N/A'))
}

function Get-MetadataValue {
    param(
        [string]$Text,
        [string]$Key
    )

    $pattern = '(?m)^-\s*' + [regex]::Escape($Key) + ':\s*(?<value>.*)$'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Groups['value'].Value.Trim()
    }

    return ''
}

function Get-LedgerRows {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LedgerPath,
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $rows = @()
    $ledgerText = Get-Content -LiteralPath $LedgerPath -Raw -Encoding UTF8

    foreach ($line in ($ledgerText -split "`r`n|`n|`r")) {
        if ($line -notmatch '^\|\s*T-\d{4,}\s*\|') {
            continue
        }

        $cells = @($line.Trim().Trim('|') -split '(?<!\\)\|')
        if ($cells.Count -lt 9) {
            continue
        }

        $taskId = ConvertFrom-MarkdownCell -Value $cells[0]
        $taskPath = Join-Path (Join-Path $Root 'TASKS') ($taskId + '.md')
        $risk = 'unknown'
        if (Test-Path -LiteralPath $taskPath) {
            $taskText = Get-Content -LiteralPath $taskPath -Raw -Encoding UTF8
            $taskRisk = Get-MetadataValue -Text $taskText -Key 'risk'
            if (Test-Filled $taskRisk) {
                $risk = $taskRisk
            }
        }

        $rows += [PSCustomObject]@{
            task_id = $taskId
            slice = ConvertFrom-MarkdownCell -Value $cells[1]
            status = (ConvertFrom-MarkdownCell -Value $cells[2]).ToLowerInvariant()
            owner = ConvertFrom-MarkdownCell -Value $cells[3]
            scope = ConvertFrom-MarkdownCell -Value $cells[4]
            files_modules = ConvertFrom-MarkdownCell -Value $cells[5]
            verification = ConvertFrom-MarkdownCell -Value $cells[6]
            blocker = ConvertFrom-MarkdownCell -Value $cells[7]
            evidence = ConvertFrom-MarkdownCell -Value $cells[8]
            risk = $risk
        }
    }

    return @($rows)
}

function Get-FirstOpenMilestone {
    param(
        [string]$Root
    )

    $deliveryPlanPath = Join-Path $Root 'DELIVERY_PLAN.md'
    if (-not (Test-Path -LiteralPath $deliveryPlanPath)) {
        return 'none'
    }

    $text = Get-Content -LiteralPath $deliveryPlanPath -Raw -Encoding UTF8
    foreach ($line in ($text -split "`r`n|`n|`r")) {
        if ($line -notmatch '^\|\s*M\d+\s*\|') {
            continue
        }

        $cells = @($line.Trim().Trim('|') -split '(?<!\\)\|')
        if ($cells.Count -ge 3) {
            $status = (ConvertFrom-MarkdownCell -Value $cells[2]).ToLowerInvariant()
            if ($status -ne 'done') {
                return (ConvertFrom-MarkdownCell -Value $cells[0])
            }
        }
    }

    return 'none'
}

function New-TableLines {
    param(
        [string[]]$Header,
        [object[]]$Rows
    )

    $safeRows = @($Rows)
    $lines = @()
    $lines += '| ' + ($Header -join ' | ') + ' |'
    $lines += '| ' + (($Header | ForEach-Object { '---' }) -join ' | ') + ' |'
    if ($safeRows.Count -eq 0) {
        $lines += '| none | ' + (($Header | Select-Object -Skip 1 | ForEach-Object { 'none' }) -join ' | ') + ' |'
        return $lines
    }

    foreach ($row in $safeRows) {
        $cells = @()
        foreach ($column in $Header) {
            $propertyName = ($column.ToLowerInvariant() -replace '[^a-z0-9]+', '_').Trim('_')
            $cells += ConvertTo-MarkdownCell ([string]$row.$propertyName)
        }
        $lines += '| ' + ($cells -join ' | ') + ' |'
    }

    return $lines
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$ledgerPath = Join-Path $resolvedRoot 'TASK_LEDGER.md'
$projectStatusPath = Join-Path $resolvedRoot 'PROJECT_STATUS.md'

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    throw "TASK_LEDGER.md does not exist: $ledgerPath"
}

$rows = @(Get-LedgerRows -LedgerPath $ledgerPath -Root $resolvedRoot)
$total = $rows.Count
$todoCount = @($rows | Where-Object { $_.status -eq 'todo' }).Count
$doingCount = @($rows | Where-Object { $_.status -eq 'doing' }).Count
$blockedCount = @($rows | Where-Object { $_.status -eq 'blocked' }).Count
$reviewCount = @($rows | Where-Object { $_.status -eq 'review' }).Count
$doneCount = @($rows | Where-Object { $_.status -eq 'done' }).Count

$missingVerificationRows = @($rows | Where-Object { -not (Test-Filled $_.verification) })
$missingEvidenceRows = @($rows | Where-Object { $_.status -in @('review', 'done') -and (-not (Test-Filled $_.evidence)) })
$blockedRows = @($rows | Where-Object { $_.status -eq 'blocked' -or (Test-Filled $_.blocker) })
$activeRows = @($rows | Where-Object { $_.status -in @('doing', 'review') })
$todoRows = @($rows | Where-Object { $_.status -eq 'todo' })
$riskRows = @($rows | Where-Object { $_.risk -in @('high', 'medium') -or $_.status -eq 'blocked' })

$effectiveMilestone = if (Test-Filled $CurrentMilestone) { $CurrentMilestone.Trim() } else { Get-FirstOpenMilestone -Root $resolvedRoot }
$effectiveActiveSlice = if (Test-Filled $ActiveSlice) {
    $ActiveSlice.Trim()
} elseif ($activeRows.Count -gt 0) {
    $activeRows[0].slice
} elseif ($todoRows.Count -gt 0) {
    $todoRows[0].slice
} else {
    'none'
}

$effectiveOverallStatus = if (Test-Filled $OverallStatus) {
    $OverallStatus.Trim()
} elseif ($total -eq 0) {
    'red'
} elseif ($blockedCount -gt 0 -and $blockedCount -eq $total) {
    'red'
} elseif ($blockedCount -gt 0 -or $missingVerificationRows.Count -gt 0 -or $missingEvidenceRows.Count -gt 0) {
    'yellow'
} else {
    'green'
}

$nextActions = @()
if ($NextAction.Count -gt 0) {
    $nextActions = @($NextAction | Where-Object { Test-Filled $_ })
}

if ($nextActions.Count -eq 0) {
    if ($blockedRows.Count -gt 0) {
        $nextActions += 'Resolve blocker for ' + $blockedRows[0].task_id + ': ' + $blockedRows[0].blocker
    }

    if ($missingVerificationRows.Count -gt 0) {
        $nextActions += 'Define or run verification for ' + $missingVerificationRows[0].task_id
    }

    if ($activeRows.Count -gt 0) {
        $nextActions += 'Continue active task ' + $activeRows[0].task_id + ' and update evidence before completion'
    } elseif ($todoRows.Count -gt 0) {
        $nextActions += 'Start next todo task ' + $todoRows[0].task_id
    } elseif ($total -gt 0 -and $doneCount -eq $total) {
        $nextActions += 'Run final audit or prepare release'
    } else {
        $nextActions += 'Create the next bounded work item'
    }
}

$activeTableRows = @($activeRows | ForEach-Object {
    [PSCustomObject]@{
        task_id = $_.task_id
        slice = $_.slice
        status = $_.status
        owner_agent = $_.owner
        scope = $_.scope
        verification = $_.verification
        evidence = $_.evidence
    }
})

$riskTableRows = @($riskRows | ForEach-Object {
    [PSCustomObject]@{
        risk = $_.task_id + ' (' + $_.risk + ')'
        owner = $_.owner
        mitigation = if (Test-Filled $_.blocker) { $_.blocker } else { 'Track verification and scope boundary.' }
        status = $_.status
    }
})

$blockedTableRows = @($blockedRows | ForEach-Object {
    [PSCustomObject]@{
        task_id = $_.task_id
        blocker = $_.blocker
        needed_decision = if (Test-Filled $_.blocker) { 'Resolve blocker or re-scope task.' } else { 'Clarify why task is blocked.' }
    }
})

$verificationTableRows = @(
    [PSCustomObject]@{
        area = 'task_count'
        current_evidence = "$total total; $doneCount done; $reviewCount review; $doingCount doing; $blockedCount blocked; $todoCount todo"
        gap = if ($total -eq 0) { 'No work items created.' } else { 'none' }
    },
    [PSCustomObject]@{
        area = 'verification'
        current_evidence = (($total - $missingVerificationRows.Count).ToString() + '/' + $total + ' tasks have verification')
        gap = if ($missingVerificationRows.Count -gt 0) { ($missingVerificationRows.task_id -join ', ') } else { 'none' }
    },
    [PSCustomObject]@{
        area = 'completion_evidence'
        current_evidence = (@($rows | Where-Object { Test-Filled $_.evidence }).Count.ToString() + '/' + $total + ' tasks have evidence')
        gap = if ($missingEvidenceRows.Count -gt 0) { ($missingEvidenceRows.task_id -join ', ') } else { 'none' }
    }
)

$lines = @(
    '# PROJECT_STATUS.md',
    '',
    'Generated by `Sync-ProjectStatus.ps1` from `TASK_LEDGER.md` and `TASKS/*.md`.',
    '',
    '## Current Snapshot',
    '',
    ('- current_milestone: {0}' -f $effectiveMilestone),
    ('- active_slice: {0}' -f $effectiveActiveSlice),
    ('- overall_status: {0}' -f $effectiveOverallStatus),
    ('- total_tasks: {0}' -f $total),
    ('- todo: {0}' -f $todoCount),
    ('- doing: {0}' -f $doingCount),
    ('- blocked: {0}' -f $blockedCount),
    ('- review: {0}' -f $reviewCount),
    ('- done: {0}' -f $doneCount),
    ('- last_updated: {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')),
    '',
    '## Active Tasks',
    ''
) + (New-TableLines -Header @('Task ID', 'Slice', 'Status', 'Owner Agent', 'Scope', 'Verification', 'Evidence') -Rows $activeTableRows) + @(
    '',
    '## Open Risks',
    ''
) + (New-TableLines -Header @('Risk', 'Owner', 'Mitigation', 'Status') -Rows $riskTableRows) + @(
    '',
    '## Blocked Tasks',
    ''
) + (New-TableLines -Header @('Task ID', 'Blocker', 'Needed Decision') -Rows $blockedTableRows) + @(
    '',
    '## Verification Coverage',
    ''
) + (New-TableLines -Header @('Area', 'Current Evidence', 'Gap') -Rows $verificationTableRows) + @(
    '',
    '## Next Recommended Actions',
    ''
) + @($nextActions | ForEach-Object { '- ' + $_ })

Write-Utf8NoBom -Path $projectStatusPath -Lines $lines

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    project_status_path = $projectStatusPath
    overall_status = $effectiveOverallStatus
    active_slice = $effectiveActiveSlice
    total_tasks = $total
    todo = $todoCount
    doing = $doingCount
    blocked = $blockedCount
    review = $reviewCount
    done = $doneCount
    missing_verification = $missingVerificationRows.Count
    missing_completion_evidence = $missingEvidenceRows.Count
    next_actions = $nextActions
}

if ($Json) {
    $report | ConvertTo-Json -Depth 5
    return
}

Write-Output "Project status synced: $projectStatusPath"
Write-Output "Overall status: $effectiveOverallStatus"
Write-Output "Tasks: total=$total todo=$todoCount doing=$doingCount blocked=$blockedCount review=$reviewCount done=$doneCount"
