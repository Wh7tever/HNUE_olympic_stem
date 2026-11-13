param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [switch]$AutoSync,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$validStatuses = @('todo', 'doing', 'blocked', 'review', 'done')
$checks = @()
$recommendations = @()
$score = 100

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

function Add-DeliveryCheck {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [ValidateSet('PASS', 'WARN', 'FAIL')]
        [string]$Status,
        [string]$Details = '',
        [int]$Penalty = 0
    )

    $script:checks += [PSCustomObject]@{
        name = $Name
        status = $Status
        details = $Details
    }

    if ($Penalty -gt 0) {
        $script:score = [Math]::Max(0, $script:score - $Penalty)
    }
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

function Test-Filled {
    param(
        [string]$Value
    )

    return (-not [string]::IsNullOrWhiteSpace($Value)) -and ($Value.Trim() -notin @('TO_BE_FILLED', 'none', 'n/a', 'N/A'))
}

function Read-TextFile {
    param(
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ''
    }

    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
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

function Get-ProjectStatusValue {
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
        [string]$LedgerPath
    )

    $rows = @()
    $ledgerText = Read-TextFile -Path $LedgerPath

    foreach ($line in ($ledgerText -split "`r`n|`n|`r")) {
        if ($line -notmatch '^\|\s*T-\d{4,}\s*\|') {
            continue
        }

        $cells = @($line.Trim().Trim('|') -split '(?<!\\)\|')
        if ($cells.Count -lt 9) {
            $rows += [PSCustomObject]@{
                task_id = 'INVALID'
                slice = ''
                status = ''
                owner = ''
                scope = ''
                files_modules = ''
                verification = ''
                blocker = ''
                evidence = ''
                parse_error = 'Ledger row has fewer than 9 cells.'
            }
            continue
        }

        $rows += [PSCustomObject]@{
            task_id = ConvertFrom-MarkdownCell -Value $cells[0]
            slice = ConvertFrom-MarkdownCell -Value $cells[1]
            status = (ConvertFrom-MarkdownCell -Value $cells[2]).ToLowerInvariant()
            owner = ConvertFrom-MarkdownCell -Value $cells[3]
            scope = ConvertFrom-MarkdownCell -Value $cells[4]
            files_modules = ConvertFrom-MarkdownCell -Value $cells[5]
            verification = ConvertFrom-MarkdownCell -Value $cells[6]
            blocker = ConvertFrom-MarkdownCell -Value $cells[7]
            evidence = ConvertFrom-MarkdownCell -Value $cells[8]
            parse_error = ''
        }
    }

    return @($rows)
}

function Compare-Count {
    param(
        [string]$Name,
        [string]$Actual,
        [int]$Expected
    )

    if ([string]::IsNullOrWhiteSpace($Actual)) {
        Add-DeliveryCheck -Name ('project_status_' + $Name) -Status 'WARN' -Details ('PROJECT_STATUS.md missing ' + $Name + ' count.') -Penalty 3
        $script:recommendations += 'Run Sync-ProjectStatus.ps1 to refresh PROJECT_STATUS.md.'
        return
    }

    $actualNumber = 0
    if (-not [int]::TryParse($Actual, [ref]$actualNumber)) {
        Add-DeliveryCheck -Name ('project_status_' + $Name) -Status 'FAIL' -Details ('PROJECT_STATUS.md has non-numeric ' + $Name + ': ' + $Actual) -Penalty 12
        return
    }

    if ($actualNumber -eq $Expected) {
        Add-DeliveryCheck -Name ('project_status_' + $Name) -Status 'PASS' -Details ($Name + '=' + $Expected)
    } else {
        Add-DeliveryCheck -Name ('project_status_' + $Name) -Status 'FAIL' -Details ('Expected ' + $Expected + ', found ' + $actualNumber + '.') -Penalty 12
        $script:recommendations += 'Run Sync-ProjectStatus.ps1 because PROJECT_STATUS.md is out of sync.'
    }
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$ledgerPath = Join-Path $resolvedRoot 'TASK_LEDGER.md'
$tasksDir = Join-Path $resolvedRoot 'TASKS'
$projectStatusPath = Join-Path $resolvedRoot 'PROJECT_STATUS.md'

if ($AutoSync) {
    $syncTool = Join-Path $PSScriptRoot 'Sync-ProjectStatus.ps1'
    if (Test-Path -LiteralPath $syncTool) {
        & $syncTool -ProjectRoot $resolvedRoot -Json | Out-Null
    } else {
        Add-DeliveryCheck -Name 'auto_sync_tool' -Status 'WARN' -Details 'Sync-ProjectStatus.ps1 is not available.' -Penalty 3
    }
}

if (Test-Path -LiteralPath $ledgerPath) {
    Add-DeliveryCheck -Name 'task_ledger_present' -Status 'PASS' -Details 'TASK_LEDGER.md present.'
} else {
    Add-DeliveryCheck -Name 'task_ledger_present' -Status 'FAIL' -Details 'Missing TASK_LEDGER.md.' -Penalty 30
    $recommendations += 'Run New-ProjectAgentDocs.ps1 or New-ProjectWorkItem.ps1 to create delivery state.'
}

if (Test-Path -LiteralPath $tasksDir) {
    Add-DeliveryCheck -Name 'tasks_dir_present' -Status 'PASS' -Details 'TASKS directory present.'
} else {
    Add-DeliveryCheck -Name 'tasks_dir_present' -Status 'WARN' -Details 'TASKS directory is missing.' -Penalty 8
    $recommendations += 'Create bounded work items with New-ProjectWorkItem.ps1.'
}

$rows = @(if (Test-Path -LiteralPath $ledgerPath) { Get-LedgerRows -LedgerPath $ledgerPath })

if ($rows.Count -gt 0) {
    Add-DeliveryCheck -Name 'ledger_rows_present' -Status 'PASS' -Details ($rows.Count.ToString() + ' task rows found.')
} else {
    Add-DeliveryCheck -Name 'ledger_rows_present' -Status 'WARN' -Details 'No task rows found in TASK_LEDGER.md.' -Penalty 10
    $recommendations += 'Create at least one bounded work item before implementation.'
}

$rowIds = @($rows | ForEach-Object { $_.task_id })
foreach ($row in $rows) {
    if (Test-Filled $row.parse_error) {
        Add-DeliveryCheck -Name 'ledger_row_parse' -Status 'FAIL' -Details $row.parse_error -Penalty 12
        continue
    }

    if ($row.task_id -notmatch '^T-\d{4,}$') {
        Add-DeliveryCheck -Name ('task_id_format_' + $row.task_id) -Status 'FAIL' -Details 'Invalid task id format.' -Penalty 8
        continue
    }

    if ($row.status -notin $validStatuses) {
        Add-DeliveryCheck -Name ('status_valid_' + $row.task_id) -Status 'FAIL' -Details ('Invalid status: ' + $row.status) -Penalty 10
    } else {
        Add-DeliveryCheck -Name ('status_valid_' + $row.task_id) -Status 'PASS' -Details $row.status
    }

    $taskPath = Join-Path $tasksDir ($row.task_id + '.md')
    if (-not (Test-Path -LiteralPath $taskPath)) {
        Add-DeliveryCheck -Name ('task_file_present_' + $row.task_id) -Status 'FAIL' -Details ('Missing task file: TASKS/' + $row.task_id + '.md') -Penalty 12
        $recommendations += 'Recreate or restore the missing task file for ' + $row.task_id + '.'
        continue
    }

    Add-DeliveryCheck -Name ('task_file_present_' + $row.task_id) -Status 'PASS' -Details ('TASKS/' + $row.task_id + '.md present.')
    $taskText = Read-TextFile -Path $taskPath
    $taskStatus = (Get-MetadataValue -Text $taskText -Key 'status').ToLowerInvariant()
    $taskSlice = Get-MetadataValue -Text $taskText -Key 'slice_id'

    if ((Test-Filled $taskStatus) -and ($taskStatus -ne $row.status)) {
        Add-DeliveryCheck -Name ('task_status_matches_ledger_' + $row.task_id) -Status 'FAIL' -Details ('Task file status=' + $taskStatus + '; ledger status=' + $row.status) -Penalty 12
        $recommendations += 'Run Update-ProjectWorkItem.ps1 or Sync-ProjectStatus.ps1 to repair state drift.'
    } else {
        Add-DeliveryCheck -Name ('task_status_matches_ledger_' + $row.task_id) -Status 'PASS' -Details $row.status
    }

    if ((Test-Filled $taskSlice) -and ($taskSlice -ne $row.slice)) {
        Add-DeliveryCheck -Name ('task_slice_matches_ledger_' + $row.task_id) -Status 'FAIL' -Details ('Task file slice=' + $taskSlice + '; ledger slice=' + $row.slice) -Penalty 8
    } else {
        Add-DeliveryCheck -Name ('task_slice_matches_ledger_' + $row.task_id) -Status 'PASS' -Details $row.slice
    }

    if ($row.status -eq 'blocked' -and (-not (Test-Filled $row.blocker))) {
        Add-DeliveryCheck -Name ('blocked_has_blocker_' + $row.task_id) -Status 'FAIL' -Details 'Blocked task has no blocker.' -Penalty 12
        $recommendations += 'Add a concrete blocker before keeping ' + $row.task_id + ' blocked.'
    }

    if ($row.status -in @('review', 'done')) {
        if (Test-Filled $row.verification) {
            Add-DeliveryCheck -Name ('completion_has_verification_' + $row.task_id) -Status 'PASS' -Details $row.verification
        } else {
            Add-DeliveryCheck -Name ('completion_has_verification_' + $row.task_id) -Status 'FAIL' -Details 'Missing verification for review/done task.' -Penalty 15
        }

        if (Test-Filled $row.evidence) {
            Add-DeliveryCheck -Name ('completion_has_evidence_' + $row.task_id) -Status 'PASS' -Details $row.evidence
        } else {
            Add-DeliveryCheck -Name ('completion_has_evidence_' + $row.task_id) -Status 'FAIL' -Details 'Missing evidence for review/done task.' -Penalty 15
        }
    }
}

if (Test-Path -LiteralPath $tasksDir) {
    $taskFiles = @(Get-ChildItem -LiteralPath $tasksDir -File -Filter 'T-*.md' -ErrorAction SilentlyContinue)
    foreach ($file in $taskFiles) {
        if ($file.BaseName -notin $rowIds) {
            Add-DeliveryCheck -Name ('task_file_has_ledger_row_' + $file.BaseName) -Status 'FAIL' -Details ($file.Name + ' has no TASK_LEDGER.md row.') -Penalty 12
            $recommendations += 'Add a TASK_LEDGER.md row for ' + $file.BaseName + ' or remove stale task file.'
        }
    }
}

$todoCount = @($rows | Where-Object { $_.status -eq 'todo' }).Count
$doingCount = @($rows | Where-Object { $_.status -eq 'doing' }).Count
$blockedCount = @($rows | Where-Object { $_.status -eq 'blocked' }).Count
$reviewCount = @($rows | Where-Object { $_.status -eq 'review' }).Count
$doneCount = @($rows | Where-Object { $_.status -eq 'done' }).Count
$totalCount = $rows.Count

if (Test-Path -LiteralPath $projectStatusPath) {
    Add-DeliveryCheck -Name 'project_status_present' -Status 'PASS' -Details 'PROJECT_STATUS.md present.'
    $projectStatusText = Read-TextFile -Path $projectStatusPath
    Compare-Count -Name 'total_tasks' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'total_tasks') -Expected $totalCount
    Compare-Count -Name 'todo' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'todo') -Expected $todoCount
    Compare-Count -Name 'doing' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'doing') -Expected $doingCount
    Compare-Count -Name 'blocked' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'blocked') -Expected $blockedCount
    Compare-Count -Name 'review' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'review') -Expected $reviewCount
    Compare-Count -Name 'done' -Actual (Get-ProjectStatusValue -Text $projectStatusText -Key 'done') -Expected $doneCount
} else {
    Add-DeliveryCheck -Name 'project_status_present' -Status 'WARN' -Details 'PROJECT_STATUS.md missing.' -Penalty 8
    $recommendations += 'Run Sync-ProjectStatus.ps1 to generate PROJECT_STATUS.md.'
}

$failures = @($checks | Where-Object { $_.status -eq 'FAIL' })
$warnings = @($checks | Where-Object { $_.status -eq 'WARN' })
$overallStatus = if ($failures.Count -gt 0) {
    'FAIL'
} elseif ($warnings.Count -gt 0) {
    'WARN'
} else {
    'PASS'
}

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    overall_status = $overallStatus
    score = $score
    counts = [PSCustomObject]@{
        total = $totalCount
        todo = $todoCount
        doing = $doingCount
        blocked = $blockedCount
        review = $reviewCount
        done = $doneCount
    }
    checks = $checks
    recommendations = @($recommendations | Select-Object -Unique)
}

if ($Json) {
    $report | ConvertTo-Json -Depth 8
    return
}

Write-Output "Project delivery state: $overallStatus"
Write-Output "Score: $score"
Write-Output "Tasks: total=$totalCount todo=$todoCount doing=$doingCount blocked=$blockedCount review=$reviewCount done=$doneCount"
if ($recommendations.Count -gt 0) {
    Write-Output 'Recommendations:'
    foreach ($recommendation in @($recommendations | Select-Object -Unique)) {
        Write-Output ('- ' + $recommendation)
    }
}
