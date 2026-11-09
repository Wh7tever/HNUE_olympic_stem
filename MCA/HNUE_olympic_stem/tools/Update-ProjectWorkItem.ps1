param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [string]$Status = '',
    [string]$SliceId = '',
    [string]$OwnerAgent = '',
    [string]$Risk = '',
    [string]$Goal = '',
    [string]$Scope = '',
    [string]$FilesModules = '',
    [string]$Verification = '',
    [string]$Blocker = '',
    [string]$Evidence = '',
    [string]$Event = '',
    [string]$Actor = 'agent',
    [string[]]$BlockedBy = @(),

    [ValidateSet('', 'AFK', 'HITL', 'unknown')]
    [string]$InteractionMode = '',

    [switch]$AllowIncomplete,
    [switch]$NoSync,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$validStatuses = @('todo', 'doing', 'blocked', 'review', 'done')
$validRisks = @('low', 'medium', 'high', 'unknown')

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

function Write-Utf8NoBomText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($false)))
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

function Select-NonEmptyValue {
    param(
        [string]$Candidate,
        [string]$Fallback
    )

    if (-not [string]::IsNullOrWhiteSpace($Candidate)) {
        return $Candidate.Trim()
    }

    if (-not [string]::IsNullOrWhiteSpace($Fallback)) {
        return $Fallback.Trim()
    }

    return 'TO_BE_FILLED'
}

function Test-FilledValue {
    param(
        [string]$Value
    )

    return (-not [string]::IsNullOrWhiteSpace($Value)) -and ($Value.Trim() -notin @('TO_BE_FILLED', 'none', 'n/a', 'N/A'))
}

function Get-MetadataValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    $pattern = '(?m)^-\s*' + [regex]::Escape($Key) + ':\s*(?<value>.*)$'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Groups['value'].Value.Trim()
    }

    return ''
}

function Set-MetadataValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Key,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Text
    }

    $pattern = '(?m)^-\s*' + [regex]::Escape($Key) + ':\s*.*$'
    $line = '- ' + $Key + ': ' + $Value.Trim()

    if ([regex]::IsMatch($Text, $pattern)) {
        return [regex]::Replace($Text, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $line }, 1)
    }

    $metadataPattern = '(?ms)(^## Metadata\s*\r?\n\r?\n)'
    if ([regex]::IsMatch($Text, $metadataPattern)) {
        return [regex]::Replace(
            $Text,
            $metadataPattern,
            [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $m.Groups[1].Value + $line + [Environment]::NewLine },
            1
        )
    }

    return $Text.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + '## Metadata' + [Environment]::NewLine + [Environment]::NewLine + $line + [Environment]::NewLine
}

function Get-MarkdownSection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Heading
    )

    $pattern = '(?ms)^## ' + [regex]::Escape($Heading) + '\s*\r?\n\r?\n(?<body>.*?)(?=^## |\z)'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Groups['body'].Value.Trim()
    }

    return ''
}

function Set-MarkdownSection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Heading,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Text
    }

    $normalized = $Value.Trim()
    $pattern = '(?ms)(^## ' + [regex]::Escape($Heading) + '\s*\r?\n\r?\n).*?(?=^## |\z)'

    if ([regex]::IsMatch($Text, $pattern)) {
        return [regex]::Replace(
            $Text,
            $pattern,
            [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $m.Groups[1].Value + $normalized + [Environment]::NewLine + [Environment]::NewLine },
            1
        )
    }

    return $Text.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + '## ' + $Heading + [Environment]::NewLine + [Environment]::NewLine + $normalized + [Environment]::NewLine
}

function Add-ExecutionLogRow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [string]$Row
    )

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in ($Text -split "`r`n|`n|`r")) {
        [void]$lines.Add($line)
    }

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\|\s*---\s*\|\s*---\s*\|\s*---\s*\|\s*---\s*\|') {
            $lines.Insert($i + 1, $Row)
            return ($lines -join [Environment]::NewLine).TrimEnd() + [Environment]::NewLine
        }
    }

    return $Text.TrimEnd() + [Environment]::NewLine + $Row + [Environment]::NewLine
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

if ($TaskId -notmatch '^T-\d{4,}$') {
    throw 'TaskId must use format T-0001, T-0002, ...'
}

if (-not [string]::IsNullOrWhiteSpace($Status) -and ($Status -notin $validStatuses)) {
    throw ('Status must be one of: ' + ($validStatuses -join ', '))
}

if (-not [string]::IsNullOrWhiteSpace($Risk) -and ($Risk -notin $validRisks)) {
    throw ('Risk must be one of: ' + ($validRisks -join ', '))
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$taskPath = Join-Path (Join-Path $resolvedRoot 'TASKS') ($TaskId + '.md')
$ledgerPath = Join-Path $resolvedRoot 'TASK_LEDGER.md'

if (-not (Test-Path -LiteralPath $taskPath)) {
    throw "Task file does not exist: $taskPath"
}

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    throw "Task ledger does not exist: $ledgerPath"
}

$taskText = Get-Content -LiteralPath $taskPath -Raw -Encoding UTF8

$currentSliceId = Get-MetadataValue -Text $taskText -Key 'slice_id'
$currentStatus = Get-MetadataValue -Text $taskText -Key 'status'
$currentRisk = Get-MetadataValue -Text $taskText -Key 'risk'
$currentOwner = Get-MetadataValue -Text $taskText -Key 'owner_agent'
$currentGoal = Get-MarkdownSection -Text $taskText -Heading 'Goal'
$currentScope = Get-MarkdownSection -Text $taskText -Heading 'Scope'
$currentFiles = Get-MarkdownSection -Text $taskText -Heading 'Files / Modules'
$currentVerification = Get-MarkdownSection -Text $taskText -Heading 'Verification'
$currentBlocker = Get-MarkdownSection -Text $taskText -Heading 'Blocker'
$currentEvidence = Get-MarkdownSection -Text $taskText -Heading 'Evidence'
$currentBlockedBy = Get-MarkdownSection -Text $taskText -Heading 'Blocked By'
$currentInteractionMode = Get-MetadataValue -Text $taskText -Key 'interaction_mode'

$effectiveSliceId = Select-NonEmptyValue -Candidate $SliceId -Fallback $currentSliceId
$effectiveStatus = Select-NonEmptyValue -Candidate $Status -Fallback $currentStatus
$effectiveRisk = Select-NonEmptyValue -Candidate $Risk -Fallback $currentRisk
$effectiveOwner = Select-NonEmptyValue -Candidate $OwnerAgent -Fallback $currentOwner
$effectiveGoal = Select-NonEmptyValue -Candidate $Goal -Fallback $currentGoal
$effectiveScope = Select-NonEmptyValue -Candidate $Scope -Fallback $currentScope
$effectiveFiles = Select-NonEmptyValue -Candidate $FilesModules -Fallback $currentFiles
$effectiveVerification = Select-NonEmptyValue -Candidate $Verification -Fallback $currentVerification
$effectiveBlocker = Select-NonEmptyValue -Candidate $Blocker -Fallback $currentBlocker
$effectiveEvidence = Select-NonEmptyValue -Candidate $Evidence -Fallback $currentEvidence
$blockedByCandidate = if ($BlockedBy.Count -gt 0) {
    ($BlockedBy | ForEach-Object { '- ' + $_ }) -join [Environment]::NewLine
} else {
    ''
}
$effectiveBlockedBy = Select-NonEmptyValue -Candidate $blockedByCandidate -Fallback $currentBlockedBy
if ($effectiveBlockedBy -eq 'TO_BE_FILLED') {
    $effectiveBlockedBy = '- none'
}

$effectiveInteractionMode = Select-NonEmptyValue -Candidate $InteractionMode -Fallback $currentInteractionMode
if ($effectiveInteractionMode -notin @('AFK', 'HITL', 'unknown')) {
    $effectiveInteractionMode = 'unknown'
}

if (-not $AllowIncomplete) {
    if ($effectiveStatus -eq 'blocked' -and (-not (Test-FilledValue $effectiveBlocker))) {
        throw 'Cannot set status to blocked without a concrete Blocker. Use -Blocker or -AllowIncomplete.'
    }

    if ($effectiveStatus -in @('review', 'done')) {
        if (-not (Test-FilledValue $effectiveVerification)) {
            throw 'Cannot set status to review/done without concrete Verification. Use -Verification or -AllowIncomplete.'
        }

        if (-not (Test-FilledValue $effectiveEvidence)) {
            throw 'Cannot set status to review/done without concrete Evidence. Use -Evidence or -AllowIncomplete.'
        }
    }
}

$taskText = Set-MetadataValue -Text $taskText -Key 'slice_id' -Value $effectiveSliceId
$taskText = Set-MetadataValue -Text $taskText -Key 'status' -Value $effectiveStatus
$taskText = Set-MetadataValue -Text $taskText -Key 'risk' -Value $effectiveRisk
$taskText = Set-MetadataValue -Text $taskText -Key 'owner_agent' -Value $effectiveOwner
$taskText = Set-MetadataValue -Text $taskText -Key 'interaction_mode' -Value $effectiveInteractionMode
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Goal' -Value $effectiveGoal
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Scope' -Value $effectiveScope
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Files / Modules' -Value $effectiveFiles
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Blocked By' -Value $effectiveBlockedBy
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Verification' -Value $effectiveVerification
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Blocker' -Value $effectiveBlocker
$taskText = Set-MarkdownSection -Text $taskText -Heading 'Evidence' -Value $effectiveEvidence

$effectiveEvent = if (-not [string]::IsNullOrWhiteSpace($Event)) {
    $Event.Trim()
} elseif (-not [string]::IsNullOrWhiteSpace($Status)) {
    'status -> ' + $effectiveStatus
} else {
    'task updated'
}

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
$logRow = '| ' + (ConvertTo-MarkdownCell $timestamp) +
    ' | ' + (ConvertTo-MarkdownCell $Actor) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveEvent) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveEvidence) + ' |'

$taskText = Add-ExecutionLogRow -Text $taskText -Row $logRow
Write-Utf8NoBomText -Path $taskPath -Text $taskText

$ledgerText = Get-Content -LiteralPath $ledgerPath -Raw -Encoding UTF8
$ledgerRow = '| ' + (ConvertTo-MarkdownCell $TaskId) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveSliceId) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveStatus) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveOwner) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveScope) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveFiles) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveVerification) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveBlocker) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveEvidence) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveInteractionMode) +
    ' | ' + (ConvertTo-MarkdownCell $effectiveBlockedBy) + ' |'

$ledgerText = Set-LedgerRow -Text $ledgerText -Id $TaskId -Row $ledgerRow
Write-Utf8NoBomText -Path $ledgerPath -Text $ledgerText

$syncedStatus = $false
if (-not $NoSync) {
    $syncedStatus = Invoke-ProjectStatusSync -Root $resolvedRoot
}

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    task_id = $TaskId
    task_path = $taskPath
    ledger_path = $ledgerPath
    status = $effectiveStatus
    slice_id = $effectiveSliceId
    owner_agent = $effectiveOwner
    risk = $effectiveRisk
    interaction_mode = $effectiveInteractionMode
    blocked_by = $effectiveBlockedBy
    event = $effectiveEvent
    synced_project_status = $syncedStatus
}

if ($Json) {
    $report | ConvertTo-Json -Depth 5
    return
}

Write-Output "Project work item updated: $TaskId"
Write-Output "Status: $effectiveStatus"
Write-Output "Task file: $taskPath"
Write-Output "Ledger: $ledgerPath"
