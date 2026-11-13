param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [ValidateSet('auto', 'custom', 'tiny', 'small', 'standard', 'enterprise')]
    [string]$ProjectSize = 'auto',

    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Add-ReadinessCheck {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [ValidateSet('PASS', 'WARN', 'FAIL')]
        [string]$Status,
        [Parameter(Mandatory = $true)]
        [string]$Details,
        [int]$Penalty = 0
    )

    $script:checks += [PSCustomObject]@{
        name = $Name
        status = $Status
        details = $Details
        penalty = $Penalty
    }

    $script:score -= $Penalty
}

function Read-TextFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ''
    }

    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8)
}

function Test-ContainsAny {
    param(
        [string]$Text,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if ($Text -match $pattern) {
            return $true
        }
    }

    return $false
}

function Get-ProjectSignals {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $signals = @()
    $candidates = @(
        @{ path = 'package.json'; signal = 'node_package' },
        @{ path = 'pnpm-lock.yaml'; signal = 'pnpm' },
        @{ path = 'yarn.lock'; signal = 'yarn' },
        @{ path = 'package-lock.json'; signal = 'npm' },
        @{ path = 'pyproject.toml'; signal = 'python_pyproject' },
        @{ path = 'requirements.txt'; signal = 'python_requirements' },
        @{ path = 'go.mod'; signal = 'go' },
        @{ path = 'Cargo.toml'; signal = 'rust' },
        @{ path = 'pom.xml'; signal = 'java_maven' },
        @{ path = 'build.gradle'; signal = 'java_gradle' },
        @{ path = 'pubspec.yaml'; signal = 'flutter_dart' }
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath (Join-Path $Root $candidate.path)) {
            $signals += $candidate.signal
        }
    }

    $csproj = @(Get-ChildItem -LiteralPath $Root -Filter '*.csproj' -File -ErrorAction SilentlyContinue)
    if ($csproj.Count -gt 0) {
        $signals += 'dotnet'
    }

    return @($signals | Select-Object -Unique)
}

function Get-PackageScripts {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $packagePath = Join-Path $Root 'package.json'
    if (-not (Test-Path -LiteralPath $packagePath)) {
        return @()
    }

    try {
        $package = Get-Content -LiteralPath $packagePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($package.PSObject.Properties.Name -contains 'scripts') {
            return @($package.scripts.PSObject.Properties.Name)
        }
    } catch {
        return @()
    }

    return @()
}

function Get-SecretLikeFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,
        [int]$MaxDepth = 4
    )

    $exactNames = @('.env', '.env.local', '.env.production', '.env.development')
    $wildcardNames = @('*.pem', '*.key', '*secret*', '*credential*')
    $skipDirs = @('.git', 'node_modules', 'dist', 'build', '.next', 'out', 'coverage', 'vendor', 'target')
    $found = @()
    $queue = New-Object System.Collections.Generic.Queue[object]
    $queue.Enqueue([PSCustomObject]@{ path = $Root; depth = 0 })

    while ($queue.Count -gt 0 -and $found.Count -lt 50) {
        $current = $queue.Dequeue()
        $files = @(Get-ChildItem -LiteralPath $current.path -File -Force -ErrorAction SilentlyContinue)
        foreach ($file in $files) {
            $name = $file.Name
            $isMatch = $exactNames -contains $name
            if (-not $isMatch) {
                foreach ($pattern in $wildcardNames) {
                    if ($name -like $pattern) {
                        $isMatch = $true
                        break
                    }
                }
            }

            if ($isMatch) {
                $found += $file.FullName
            }
        }

        if ($current.depth -lt $MaxDepth) {
            $dirs = @(Get-ChildItem -LiteralPath $current.path -Directory -Force -ErrorAction SilentlyContinue)
            foreach ($dir in $dirs) {
                if ($skipDirs -notcontains $dir.Name) {
                    $queue.Enqueue([PSCustomObject]@{ path = $dir.FullName; depth = ($current.depth + 1) })
                }
            }
        }
    }

    return @($found | Select-Object -Unique)
}

function Get-ProjectProfileValue {
    param(
        [string]$Text,
        [string]$Key
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $null
    }

    $match = [regex]::Match($Text, ('(?im)^\s*[-*]?\s*' + [regex]::Escape($Key) + '\s*:\s*(?<value>[^\r\n]+)\s*$'))
    if ($match.Success) {
        return $match.Groups['value'].Value.Trim(' ', '`')
    }

    return $null
}

function Add-SizeRequiredPathCheck {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Label,
        [string]$RequiredFor
    )

    if (Test-Path -LiteralPath $Path) {
        Add-ReadinessCheck -Name $Name -Status 'PASS' -Details "$Label present for $RequiredFor profile."
    } else {
        Add-ReadinessCheck -Name $Name -Status 'FAIL' -Details "$Label is required for $RequiredFor profile." -Penalty 12
        $script:recommendations += "Create $Label for $RequiredFor project readiness."
    }
}

$checks = @()
$score = 100
$recommendations = @()

if (-not (Test-Path -LiteralPath $ProjectRoot)) {
    $report = [PSCustomObject]@{
        project_root = $ProjectRoot
        status = 'missing_project'
        score = 0
        checks = @([PSCustomObject]@{
            name = 'project_root'
            status = 'FAIL'
            details = 'Project root does not exist.'
            penalty = 100
        })
        recommendations = @('Create the project folder or pass the correct ProjectRoot.')
        detected_signals = @()
        package_scripts = @()
        secret_like_files = @()
    }

    if ($Json) {
        $report | ConvertTo-Json -Depth 6
        return
    }

    Write-Output 'Project readiness: missing_project'
    Write-Output 'Score: 0'
    Write-Output '[FAIL] project_root - Project root does not exist.'
    return
}

$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
Add-ReadinessCheck -Name 'project_root' -Status 'PASS' -Details $resolvedRoot

$agentsPath = Join-Path $resolvedRoot 'AGENTS.md'
$projectProfilePath = Join-Path $resolvedRoot 'PROJECT_PROFILE.md'
$projectMapPath = Join-Path $resolvedRoot 'PROJECT_MAP.md'
$architecturePath = Join-Path $resolvedRoot 'ARCHITECTURE.md'
$runbookPath = Join-Path $resolvedRoot 'RUNBOOK.md'
$securityNotesPath = Join-Path $resolvedRoot 'SECURITY_NOTES.md'
$decisionsReadmePath = Join-Path $resolvedRoot 'docs\decisions\README.md'
$experimentsReadmePath = Join-Path $resolvedRoot 'experiments\README.md'
$deliveryPlanPath = Join-Path $resolvedRoot 'DELIVERY_PLAN.md'
$taskLedgerPath = Join-Path $resolvedRoot 'TASK_LEDGER.md'
$tasksReadmePath = Join-Path $resolvedRoot 'TASKS\README.md'
$projectStatusPath = Join-Path $resolvedRoot 'PROJECT_STATUS.md'
$handoffsReadmePath = Join-Path $resolvedRoot 'HANDOFFS\README.md'
$qualityGatesPath = Join-Path $resolvedRoot 'QUALITY_GATES.md'
$requirementsReadmePath = Join-Path $resolvedRoot 'requirements\README.md'
$businessRulesPath = Join-Path $resolvedRoot 'requirements\business-rules.md'
$userFlowsPath = Join-Path $resolvedRoot 'requirements\user-flows.md'
$featureRequirementsReadmePath = Join-Path $resolvedRoot 'requirements\features\README.md'
$diagramsReadmePath = Join-Path $resolvedRoot 'docs\diagrams\README.md'
$diagramProjectMapPath = Join-Path $resolvedRoot 'docs\diagrams\PROJECT_MAP.md'
$moduleDependenciesPath = Join-Path $resolvedRoot 'docs\diagrams\MODULE_DEPENDENCIES.md'
$dataFlowPath = Join-Path $resolvedRoot 'docs\diagrams\DATA_FLOW.md'
$featureFlowsReadmePath = Join-Path $resolvedRoot 'docs\diagrams\FEATURE_FLOWS\README.md'
$riskRegisterPath = Join-Path $resolvedRoot 'RISK_REGISTER.md'
$dataClassificationPath = Join-Path $resolvedRoot 'DATA_CLASSIFICATION.md'
$operationsPath = Join-Path $resolvedRoot 'OPERATIONS.md'
$incidentRunbookPath = Join-Path $resolvedRoot 'INCIDENT_RUNBOOK.md'
$releaseChecklistPath = Join-Path $resolvedRoot 'RELEASE_CHECKLIST.md'
$backupRestorePath = Join-Path $resolvedRoot 'BACKUP_RESTORE.md'

if (Test-Path -LiteralPath $agentsPath) {
    Add-ReadinessCheck -Name 'agents_doc' -Status 'PASS' -Details 'AGENTS.md present.'
} else {
    Add-ReadinessCheck -Name 'agents_doc' -Status 'FAIL' -Details 'Missing AGENTS.md.' -Penalty 25
    $recommendations += 'Run New-ProjectAgentDocs.ps1 to create AGENTS.md.'
}

if (Test-Path -LiteralPath $projectMapPath) {
    Add-ReadinessCheck -Name 'project_map_doc' -Status 'PASS' -Details 'PROJECT_MAP.md present.'
} else {
    Add-ReadinessCheck -Name 'project_map_doc' -Status 'FAIL' -Details 'Missing PROJECT_MAP.md.' -Penalty 20
    $recommendations += 'Create PROJECT_MAP.md so agents can inspect the repo index-first.'
}

$profileText = Read-TextFile -Path $projectProfilePath
$declaredProjectSize = Get-ProjectProfileValue -Text $profileText -Key 'project_size'
$effectiveProjectSize = if ($ProjectSize -ne 'auto') {
    $ProjectSize
} elseif ($declaredProjectSize -in @('tiny', 'small', 'standard', 'enterprise')) {
    $declaredProjectSize
} else {
    'custom'
}

Add-ReadinessCheck -Name 'effective_project_size' -Status 'PASS' -Details $effectiveProjectSize

$optionalDocs = @(
    @{ path = $projectProfilePath; name = 'project_profile_doc'; label = 'PROJECT_PROFILE.md' },
    @{ path = $architecturePath; name = 'architecture_doc'; label = 'ARCHITECTURE.md' },
    @{ path = $runbookPath; name = 'runbook_doc'; label = 'RUNBOOK.md' },
    @{ path = $securityNotesPath; name = 'security_notes_doc'; label = 'SECURITY_NOTES.md' },
    @{ path = $decisionsReadmePath; name = 'decisions_readme'; label = 'docs/decisions/README.md' },
    @{ path = $experimentsReadmePath; name = 'experiments_readme'; label = 'experiments/README.md' }
)

if ($effectiveProjectSize -eq 'custom') {
    foreach ($doc in $optionalDocs) {
        if (Test-Path -LiteralPath $doc.path) {
            Add-ReadinessCheck -Name $doc.name -Status 'PASS' -Details ($doc.label + ' present.')
        } else {
            Add-ReadinessCheck -Name $doc.name -Status 'WARN' -Details ($doc.label + ' not present.') -Penalty 3
        }
    }
}

if ($effectiveProjectSize -ne 'custom') {
    $requiredBySize = @()
    switch ($effectiveProjectSize) {
        'tiny' {
            $requiredBySize = @(
                @{ name = 'size_required_profile'; path = $projectProfilePath; label = 'PROJECT_PROFILE.md' },
                @{ name = 'size_required_runbook'; path = $runbookPath; label = 'RUNBOOK.md' }
            )
        }
        'small' {
            $requiredBySize = @(
                @{ name = 'size_required_profile'; path = $projectProfilePath; label = 'PROJECT_PROFILE.md' },
                @{ name = 'size_required_runbook'; path = $runbookPath; label = 'RUNBOOK.md' },
                @{ name = 'size_required_architecture'; path = $architecturePath; label = 'ARCHITECTURE.md' },
                @{ name = 'size_required_security_notes'; path = $securityNotesPath; label = 'SECURITY_NOTES.md' }
            )
        }
        'standard' {
            $requiredBySize = @(
                @{ name = 'size_required_profile'; path = $projectProfilePath; label = 'PROJECT_PROFILE.md' },
                @{ name = 'size_required_runbook'; path = $runbookPath; label = 'RUNBOOK.md' },
                @{ name = 'size_required_architecture'; path = $architecturePath; label = 'ARCHITECTURE.md' },
                @{ name = 'size_required_security_notes'; path = $securityNotesPath; label = 'SECURITY_NOTES.md' },
                @{ name = 'size_required_decisions'; path = $decisionsReadmePath; label = 'docs/decisions/README.md' },
                @{ name = 'size_required_experiments'; path = $experimentsReadmePath; label = 'experiments/README.md' },
                @{ name = 'size_required_delivery_plan'; path = $deliveryPlanPath; label = 'DELIVERY_PLAN.md' },
                @{ name = 'size_required_task_ledger'; path = $taskLedgerPath; label = 'TASK_LEDGER.md' },
                @{ name = 'size_required_tasks_readme'; path = $tasksReadmePath; label = 'TASKS/README.md' },
                @{ name = 'size_required_quality_gates'; path = $qualityGatesPath; label = 'QUALITY_GATES.md' },
                @{ name = 'size_required_diagrams'; path = $diagramsReadmePath; label = 'docs/diagrams/README.md' }
            )
        }
        'enterprise' {
            $requiredBySize = @(
                @{ name = 'size_required_profile'; path = $projectProfilePath; label = 'PROJECT_PROFILE.md' },
                @{ name = 'size_required_runbook'; path = $runbookPath; label = 'RUNBOOK.md' },
                @{ name = 'size_required_architecture'; path = $architecturePath; label = 'ARCHITECTURE.md' },
                @{ name = 'size_required_security_notes'; path = $securityNotesPath; label = 'SECURITY_NOTES.md' },
                @{ name = 'size_required_decisions'; path = $decisionsReadmePath; label = 'docs/decisions/README.md' },
                @{ name = 'size_required_experiments'; path = $experimentsReadmePath; label = 'experiments/README.md' },
                @{ name = 'size_required_delivery_plan'; path = $deliveryPlanPath; label = 'DELIVERY_PLAN.md' },
                @{ name = 'size_required_task_ledger'; path = $taskLedgerPath; label = 'TASK_LEDGER.md' },
                @{ name = 'size_required_tasks_readme'; path = $tasksReadmePath; label = 'TASKS/README.md' },
                @{ name = 'size_required_project_status'; path = $projectStatusPath; label = 'PROJECT_STATUS.md' },
                @{ name = 'size_required_handoffs'; path = $handoffsReadmePath; label = 'HANDOFFS/README.md' },
                @{ name = 'size_required_quality_gates'; path = $qualityGatesPath; label = 'QUALITY_GATES.md' },
                @{ name = 'size_required_requirements'; path = $requirementsReadmePath; label = 'requirements/README.md' },
                @{ name = 'size_required_business_rules'; path = $businessRulesPath; label = 'requirements/business-rules.md' },
                @{ name = 'size_required_user_flows'; path = $userFlowsPath; label = 'requirements/user-flows.md' },
                @{ name = 'size_required_feature_requirements'; path = $featureRequirementsReadmePath; label = 'requirements/features/README.md' },
                @{ name = 'size_required_diagrams'; path = $diagramsReadmePath; label = 'docs/diagrams/README.md' },
                @{ name = 'size_required_risk_register'; path = $riskRegisterPath; label = 'RISK_REGISTER.md' },
                @{ name = 'size_required_data_classification'; path = $dataClassificationPath; label = 'DATA_CLASSIFICATION.md' },
                @{ name = 'size_required_operations'; path = $operationsPath; label = 'OPERATIONS.md' },
                @{ name = 'size_required_incident_runbook'; path = $incidentRunbookPath; label = 'INCIDENT_RUNBOOK.md' },
                @{ name = 'size_required_release_checklist'; path = $releaseChecklistPath; label = 'RELEASE_CHECKLIST.md' },
                @{ name = 'size_required_backup_restore'; path = $backupRestorePath; label = 'BACKUP_RESTORE.md' }
            )
        }
    }

    foreach ($required in $requiredBySize) {
        Add-SizeRequiredPathCheck -Name $required.name -Path $required.path -Label $required.label -RequiredFor $effectiveProjectSize
    }
}

$agentsText = Read-TextFile -Path $agentsPath
if ($agentsText) {
    $requiredSections = @(
        @{ name = 'allowed_actions_policy'; patterns = @('(?im)^##\s+Allowed Actions', 'Allowed Actions') },
        @{ name = 'ask_before_policy'; patterns = @('(?im)^##\s+Ask Before', 'Ask Before') },
        @{ name = 'production_plugin_safety_policy'; patterns = @('(?im)^##\s+Production Plugin Safety', 'Production Plugin Safety') },
        @{ name = 'private_context_policy'; patterns = @('(?im)^##\s+Private Context', 'Private Context') },
        @{ name = 'model_quota_policy'; patterns = @('GPT-5\.5 medium', 'GPT-5\.5 extra high', 'Model And Quota') },
        @{ name = 'model_allowlist_policy'; patterns = @('Allowed project models', 'GPT-5\.5 medium.*GPT-5\.5 extra high.*only', 'Do not route project work to any other model') },
        @{ name = 'model_recommendation_policy'; patterns = @('recommended model', 'At the start of every task', 'tell the user the recommended model') },
        @{ name = 'code_quality_policy'; patterns = @('Code Quality Standard', 'module boundaries', 'verification evidence') }
    )

    foreach ($section in $requiredSections) {
        if (Test-ContainsAny -Text $agentsText -Patterns $section.patterns) {
            Add-ReadinessCheck -Name $section.name -Status 'PASS' -Details 'Required policy signal found.'
        } else {
            Add-ReadinessCheck -Name $section.name -Status 'FAIL' -Details 'Required policy signal missing from AGENTS.md.' -Penalty 8
            $recommendations += ('Update AGENTS.md with ' + $section.name + '.')
        }
    }

    if ($agentsText -match '(?i)GPT-5\.(?:[0-4]|[6-9])|gpt-5\.(?:[0-4]|[6-9])') {
        Add-ReadinessCheck -Name 'model_disallowlist_policy' -Status 'FAIL' -Details 'AGENTS.md mentions a non-allowed GPT-5 model. Project work should use only GPT-5.5 medium or GPT-5.5 extra high.' -Penalty 12
        $recommendations += 'Remove non-allowed model references from AGENTS.md.'
    } else {
        Add-ReadinessCheck -Name 'model_disallowlist_policy' -Status 'PASS' -Details 'No non-allowed GPT-5 model reference found.'
    }
}

$signals = @(Get-ProjectSignals -Root $resolvedRoot)
if ($signals.Count -gt 0) {
    Add-ReadinessCheck -Name 'project_stack_signals' -Status 'PASS' -Details ($signals -join ', ')
} else {
    Add-ReadinessCheck -Name 'project_stack_signals' -Status 'WARN' -Details 'No common project stack files detected.' -Penalty 4
}

$packageScripts = @(Get-PackageScripts -Root $resolvedRoot)
if ($packageScripts.Count -gt 0) {
    Add-ReadinessCheck -Name 'package_scripts' -Status 'PASS' -Details ($packageScripts -join ', ')
} elseif ($signals -contains 'node_package') {
    Add-ReadinessCheck -Name 'package_scripts' -Status 'WARN' -Details 'package.json has no readable scripts.' -Penalty 5
}

$commandText = $agentsText + [Environment]::NewLine + (Read-TextFile -Path $runbookPath)
$hasVerificationCommand = Test-ContainsAny -Text $commandText -Patterns @('(?im)Test:\s*`?(?!TO_BE_FILLED)', '(?im)Lint:\s*`?(?!TO_BE_FILLED)', '(?im)Build:\s*`?(?!TO_BE_FILLED)', 'npm test', 'pnpm test', 'pytest', 'go test', 'cargo test', 'dotnet test')
$matchingVerificationScripts = @($packageScripts | Where-Object { $_ -match 'test|lint|build|typecheck' })
if ($hasVerificationCommand -or $matchingVerificationScripts.Count -gt 0) {
    Add-ReadinessCheck -Name 'verification_commands' -Status 'PASS' -Details 'Verification command signal found.'
} else {
    Add-ReadinessCheck -Name 'verification_commands' -Status 'WARN' -Details 'No concrete verification command found.' -Penalty 8
    $recommendations += 'Add concrete build/test/lint commands to AGENTS.md or RUNBOOK.md.'
}

try {
    $gitRoot = (& git -C $resolvedRoot rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -eq 0 -and $gitRoot) {
        $normalizedGitRoot = [System.IO.Path]::GetFullPath([string]$gitRoot).TrimEnd('\', '/')
        $normalizedProjectRoot = [System.IO.Path]::GetFullPath($resolvedRoot).TrimEnd('\', '/')
        if ($normalizedGitRoot -eq $normalizedProjectRoot) {
            Add-ReadinessCheck -Name 'git_repo' -Status 'PASS' -Details $gitRoot
        } else {
            Add-ReadinessCheck -Name 'git_repo' -Status 'WARN' -Details "Inside parent git repo: $gitRoot" -Penalty 2
        }
    } else {
        Add-ReadinessCheck -Name 'git_repo' -Status 'WARN' -Details 'Not detected as a git repository.' -Penalty 5
    }
} catch {
    Add-ReadinessCheck -Name 'git_repo' -Status 'WARN' -Details 'Git command unavailable or repo not initialized.' -Penalty 5
}

$secretLikeFiles = @(Get-SecretLikeFiles -Root $resolvedRoot)
if ($secretLikeFiles.Count -gt 0) {
    Add-ReadinessCheck -Name 'secret_like_files' -Status 'WARN' -Details (($secretLikeFiles | ForEach-Object { Split-Path -Leaf $_ } | Select-Object -Unique) -join ', ') -Penalty 5
    $recommendations += 'Keep secret-like files out of agent context unless explicitly approved.'
} else {
    Add-ReadinessCheck -Name 'secret_like_files' -Status 'PASS' -Details 'No common secret-like files detected.'
}

if ($score -lt 0) {
    $score = 0
}

$failCount = @($checks | Where-Object { $_.status -eq 'FAIL' }).Count
$warnCount = @($checks | Where-Object { $_.status -eq 'WARN' }).Count
$status = if ($failCount -gt 0) {
    'needs_docs'
} elseif ($score -ge 90) {
    'ready'
} elseif ($warnCount -gt 0) {
    'ready_with_warnings'
} else {
    'ready'
}

if ($recommendations.Count -eq 0) {
    $recommendations += 'No blocking readiness issue detected.'
}

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    status = $status
    score = [int]$score
    checks = $checks
    recommendations = @($recommendations | Select-Object -Unique)
    project_size = $effectiveProjectSize
    declared_project_size = $declaredProjectSize
    detected_signals = $signals
    package_scripts = $packageScripts
    secret_like_files = $secretLikeFiles
}

if ($Json) {
    $report | ConvertTo-Json -Depth 7
    return
}

Write-Output "Project readiness: $status"
Write-Output "Score: $score"
foreach ($check in $checks) {
    Write-Output ("[{0}] {1} - {2}" -f $check.status, $check.name, $check.details)
}
Write-Output 'Recommendations:'
foreach ($recommendation in @($recommendations | Select-Object -Unique)) {
    Write-Output ("- " + $recommendation)
}
