param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

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

function Test-File {
    param(
        [string]$Root,
        [string]$RelativePath
    )

    return Test-Path -LiteralPath (Join-Path $Root $RelativePath)
}

function Get-PackageManager {
    param(
        [string]$Root
    )

    if (Test-File -Root $Root -RelativePath 'pnpm-lock.yaml') { return 'pnpm' }
    if (Test-File -Root $Root -RelativePath 'yarn.lock') { return 'yarn' }
    if ((Test-File -Root $Root -RelativePath 'bun.lockb') -or (Test-File -Root $Root -RelativePath 'bun.lock')) { return 'bun' }
    if (Test-File -Root $Root -RelativePath 'package-lock.json') { return 'npm' }
    return 'npm'
}

function New-RunCommand {
    param(
        [string]$PackageManager,
        [string]$ScriptName
    )

    switch ($PackageManager) {
        'pnpm' { return 'pnpm ' + $ScriptName }
        'yarn' { return 'yarn ' + $ScriptName }
        'bun' { return 'bun run ' + $ScriptName }
        default { return 'npm run ' + $ScriptName }
    }
}

function New-InstallCommand {
    param(
        [string]$PackageManager
    )

    switch ($PackageManager) {
        'pnpm' { return 'pnpm install' }
        'yarn' { return 'yarn install' }
        'bun' { return 'bun install' }
        default { return 'npm install' }
    }
}

function Add-Signal {
    param(
        [string[]]$Signals,
        [string]$Signal
    )

    if ([string]::IsNullOrWhiteSpace($Signal)) {
        return $Signals
    }

    if ($Signal -notin $Signals) {
        return @($Signals + $Signal)
    }

    return $Signals
}

function Get-DependencyNames {
    param(
        $PackageJson
    )

    $names = @()
    foreach ($section in @('dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies')) {
        if ($PackageJson.PSObject.Properties.Name -contains $section) {
            $obj = $PackageJson.$section
            if ($obj) {
                $names += @($obj.PSObject.Properties.Name)
            }
        }
    }

    return @($names | Select-Object -Unique)
}

function Get-FileCount {
    param(
        [string]$Root
    )

    $excluded = '\\(node_modules|\.git|dist|build|\.next|coverage|\.turbo|target|vendor)\\'
    $files = @(Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        $_.FullName -notmatch $excluded
    })
    return $files.Count
}

$resolvedRoot = Resolve-ProjectRoot -Path $ProjectRoot
$projectName = Split-Path -Leaf $resolvedRoot
$projectType = 'unknown'
$projectSize = 'custom'
$riskLevel = 'unknown'
$dataSensitivity = 'internal'
$productionStatus = 'local_only'
$teamMode = 'solo'
$stack = @()
$signals = @()
$installCommand = ''
$devCommand = ''
$buildCommand = ''
$testCommand = ''
$lintCommand = ''
$confidence = 'low'

$packageJsonPath = Join-Path $resolvedRoot 'package.json'
if (Test-Path -LiteralPath $packageJsonPath) {
    try {
        $packageJson = Get-Content -LiteralPath $packageJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $signals = Add-Signal -Signals $signals -Signal 'package.json'
        $packageManager = Get-PackageManager -Root $resolvedRoot
        $installCommand = New-InstallCommand -PackageManager $packageManager
        $stack += 'Node.js'

        if ($packageJson.PSObject.Properties.Name -contains 'name' -and -not [string]::IsNullOrWhiteSpace($packageJson.name)) {
            $projectName = $packageJson.name
        }

        if ($packageJson.PSObject.Properties.Name -contains 'scripts') {
            $scripts = $packageJson.scripts
            if ($scripts.PSObject.Properties.Name -contains 'start') {
                if ([string]::IsNullOrWhiteSpace($devCommand)) { $devCommand = New-RunCommand -PackageManager $packageManager -ScriptName 'start' }
                $signals = Add-Signal -Signals $signals -Signal 'start_script'
            }
            if ($scripts.PSObject.Properties.Name -contains 'dev') { $devCommand = New-RunCommand -PackageManager $packageManager -ScriptName 'dev' }
            if ($scripts.PSObject.Properties.Name -contains 'build') { $buildCommand = New-RunCommand -PackageManager $packageManager -ScriptName 'build' }
            if ($scripts.PSObject.Properties.Name -contains 'test') { $testCommand = New-RunCommand -PackageManager $packageManager -ScriptName 'test' }
            if ($scripts.PSObject.Properties.Name -contains 'lint') { $lintCommand = New-RunCommand -PackageManager $packageManager -ScriptName 'lint' }
        }

        $deps = Get-DependencyNames -PackageJson $packageJson
        $hasFrontend = $false
        $hasBackend = $false

        foreach ($dep in $deps) {
            switch -Regex ($dep) {
                '^next$' { $stack += 'Next.js'; $hasFrontend = $true; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'next' }
                '^react$' { $stack += 'React'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'react' }
                '^vite$' { $stack += 'Vite'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'vite' }
                '^vue$' { $stack += 'Vue'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'vue' }
                '^svelte$|^@sveltejs/' { $stack += 'Svelte'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'svelte' }
                '^express$' { $stack += 'Express'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'express' }
                '^fastify$' { $stack += 'Fastify'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'fastify' }
                '^@nestjs/' { $stack += 'NestJS'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'nestjs' }
                '^hono$' { $stack += 'Hono'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'hono' }
                '^expo$' { $stack += 'Expo'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'expo' }
                '^react-native$' { $stack += 'React Native'; $hasFrontend = $true; $signals = Add-Signal -Signals $signals -Signal 'react-native' }
                '^typescript$' { $stack += 'TypeScript'; $signals = Add-Signal -Signals $signals -Signal 'typescript' }
                '^tailwindcss$' { $stack += 'Tailwind CSS'; $signals = Add-Signal -Signals $signals -Signal 'tailwind' }
                '^prisma$|^@prisma/' { $stack += 'Prisma'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'prisma' }
                '^drizzle-orm$' { $stack += 'Drizzle ORM'; $hasBackend = $true; $signals = Add-Signal -Signals $signals -Signal 'drizzle' }
            }
        }

        if ((Test-File -Root $resolvedRoot -RelativePath 'tsconfig.json') -and ('TypeScript' -notin $stack)) {
            $stack += 'TypeScript'
            $signals = Add-Signal -Signals $signals -Signal 'tsconfig'
        }

        if ('expo' -in $signals -or 'react-native' -in $signals) {
            $projectType = 'mobile_app'
        } elseif ($hasFrontend -and $hasBackend) {
            $projectType = 'full_stack'
        } elseif ($hasFrontend) {
            $projectType = 'web_app'
        } elseif ($hasBackend) {
            $projectType = 'api_service'
        } elseif ((Test-File -Root $resolvedRoot -RelativePath 'src/server.js') -or (Test-File -Root $resolvedRoot -RelativePath 'src/server.mjs') -or (Test-File -Root $resolvedRoot -RelativePath 'server.js') -or (Test-File -Root $resolvedRoot -RelativePath 'server.mjs')) {
            $projectType = 'api_service'
            $signals = Add-Signal -Signals $signals -Signal 'node_server_entry'
        } elseif (($packageJson.PSObject.Properties.Name -contains 'main') -or ($packageJson.PSObject.Properties.Name -contains 'module') -or ($packageJson.PSObject.Properties.Name -contains 'types')) {
            $projectType = 'library'
        }

        $confidence = 'medium'
    } catch {
        $signals = Add-Signal -Signals $signals -Signal 'package.json_parse_failed'
    }
}

if (Test-File -Root $resolvedRoot -RelativePath 'pyproject.toml') {
    $signals = Add-Signal -Signals $signals -Signal 'pyproject.toml'
    $pyprojectText = Get-Content -LiteralPath (Join-Path $resolvedRoot 'pyproject.toml') -Raw -Encoding UTF8
    if ($pyprojectText -match 'fastapi|flask|django') {
        $projectType = 'api_service'
        $stack += 'Python API'
    } elseif ($projectType -eq 'unknown') {
        $projectType = 'data_tool'
        $stack += 'Python'
    }

    if ([string]::IsNullOrWhiteSpace($installCommand)) { $installCommand = 'pip install -e .' }
    if ([string]::IsNullOrWhiteSpace($testCommand)) { $testCommand = 'pytest' }
    if ([string]::IsNullOrWhiteSpace($lintCommand)) { $lintCommand = 'ruff check .' }
    $confidence = 'medium'
}

foreach ($fileSignal in @(
    @{ path = 'next.config.js'; stack = 'Next.js'; signal = 'next.config.js'; type = 'full_stack' },
    @{ path = 'next.config.mjs'; stack = 'Next.js'; signal = 'next.config.mjs'; type = 'full_stack' },
    @{ path = 'vite.config.ts'; stack = 'Vite'; signal = 'vite.config.ts'; type = 'web_app' },
    @{ path = 'vite.config.js'; stack = 'Vite'; signal = 'vite.config.js'; type = 'web_app' },
    @{ path = 'wrangler.toml'; stack = 'Cloudflare Workers'; signal = 'wrangler.toml'; type = 'api_service' },
    @{ path = 'vercel.json'; stack = 'Vercel'; signal = 'vercel.json'; type = '' }
)) {
    if (Test-File -Root $resolvedRoot -RelativePath $fileSignal.path) {
        if ($fileSignal.stack -notin $stack) { $stack += $fileSignal.stack }
        $signals = Add-Signal -Signals $signals -Signal $fileSignal.signal
        if (-not [string]::IsNullOrWhiteSpace($fileSignal.type) -and $projectType -eq 'unknown') {
            $projectType = $fileSignal.type
        }
    }
}

if ((Test-File -Root $resolvedRoot -RelativePath 'vercel.json') -or (Test-File -Root $resolvedRoot -RelativePath 'wrangler.toml') -or (Test-File -Root $resolvedRoot -RelativePath 'netlify.toml') -or (Test-File -Root $resolvedRoot -RelativePath 'render.yaml')) {
    $productionStatus = 'staging'
}

$fileCount = Get-FileCount -Root $resolvedRoot
if ($fileCount -le 20) {
    $projectSize = 'tiny'
} elseif ($fileCount -le 100) {
    $projectSize = 'small'
} else {
    $projectSize = 'standard'
}

if ($projectType -in @('full_stack', 'api_service') -and $projectSize -in @('tiny', 'small')) {
    $projectSize = 'standard'
    $signals = Add-Signal -Signals $signals -Signal 'size_promoted_for_backend_or_full_stack'
}

if ($projectType -in @('full_stack', 'api_service') -or $productionStatus -ne 'local_only') {
    $riskLevel = 'medium'
} elseif ($projectSize -eq 'tiny') {
    $riskLevel = 'low'
} else {
    $riskLevel = 'medium'
}

if ($projectSize -in @('standard') -or $projectType -in @('full_stack', 'api_service')) {
    $teamMode = 'multi_agent'
}

$stack = @($stack)
$signals = @($signals)

if ($stack.Count -eq 0) {
    $stack += 'unknown'
}

if ($signals.Count -gt 2 -and $confidence -eq 'medium') {
    $confidence = 'high'
}

$report = [PSCustomObject]@{
    project_root = $resolvedRoot
    project_name = $projectName
    project_type = $projectType
    project_size = $projectSize
    risk_level = $riskLevel
    data_sensitivity = $dataSensitivity
    production_status = $productionStatus
    team_mode = $teamMode
    stack = (($stack | Select-Object -Unique) -join ' ')
    commands = [PSCustomObject]@{
        install = $installCommand
        dev = $devCommand
        build = $buildCommand
        test = $testCommand
        lint = $lintCommand
    }
    confidence = $confidence
    signals = @($signals | Select-Object -Unique)
    file_count = $fileCount
}

if ($Json) {
    $report | ConvertTo-Json -Depth 6
    return
}

Write-Output ("Project profile: " + $report.project_name)
Write-Output ("Type: " + $report.project_type)
Write-Output ("Size: " + $report.project_size)
Write-Output ("Stack: " + $report.stack)
Write-Output ("Confidence: " + $report.confidence)
