param(
  [string]$RepoUrl = "",

  [int]$DaysBefore = 365,
  [int]$DaysAfter = 0,
  [int]$MaxCommits = 10,
  [int]$Frequency = 80,
  [switch]$NoWeekends,

  [string]$UserName,
  [string]$UserEmail,
  [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$configPath = Join-Path $PSScriptRoot "config.json"
if (Test-Path $configPath) {
  try {
    $config = Get-Content -Raw $configPath | ConvertFrom-Json
  } catch {
    throw "Failed to parse config.json: $_"
  }

  if (-not $PSBoundParameters.ContainsKey("RepoUrl") -and $config.RepoUrl) {
    $RepoUrl = $config.RepoUrl
  }
  if (-not $PSBoundParameters.ContainsKey("DaysBefore") -and $config.DaysBefore) {
    $DaysBefore = [int]$config.DaysBefore
  }
  if (-not $PSBoundParameters.ContainsKey("DaysAfter") -and $config.DaysAfter) {
    $DaysAfter = [int]$config.DaysAfter
  }
  if (-not $PSBoundParameters.ContainsKey("MaxCommits") -and $config.MaxCommits) {
    $MaxCommits = [int]$config.MaxCommits
  }
  if (-not $PSBoundParameters.ContainsKey("Frequency") -and $config.Frequency) {
    $Frequency = [int]$config.Frequency
  }
  if (-not $PSBoundParameters.ContainsKey("NoWeekends") -and $config.NoWeekends -eq $true) {
    $NoWeekends = $true
  }
  if (-not $PSBoundParameters.ContainsKey("UserName") -and $config.UserName) {
    $UserName = $config.UserName
  }
  if (-not $PSBoundParameters.ContainsKey("UserEmail") -and $config.UserEmail) {
    $UserEmail = $config.UserEmail
  }
  if (-not $PSBoundParameters.ContainsKey("PythonPath") -and $config.PythonPath) {
    $PythonPath = $config.PythonPath
  }
}

if (-not $RepoUrl) {
  throw "RepoUrl is required. Provide -RepoUrl or set RepoUrl in automation/config.json."
}

if ($DaysBefore -lt 0 -or $DaysAfter -lt 0) {
  throw "DaysBefore and DaysAfter must be zero or greater."
}

if ($MaxCommits -lt 1 -or $MaxCommits -gt 20) {
  throw "MaxCommits must be between 1 and 20."
}

if ($Frequency -lt 0 -or $Frequency -gt 100) {
  throw "Frequency must be between 0 and 100."
}

$root = Split-Path -Parent $PSScriptRoot
$generatorPath = Join-Path $root "github-activity-generator"
$scriptPath = Join-Path $generatorPath "contribute.py"

if (-not (Test-Path $scriptPath)) {
  throw "Could not find contribute.py at: $scriptPath. Make sure github-activity-generator is cloned next to this folder."
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd -and $PythonPath) {
  $pythonCmd = Get-Command $PythonPath -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
  throw "Python is not available on PATH. Install Python 3.8+ or set PythonPath in automation/config.json."
}

$argList = @(
  $scriptPath,
  "-r", $RepoUrl,
  "-db", $DaysBefore,
  "-da", $DaysAfter,
  "-mc", $MaxCommits,
  "-fr", $Frequency
)

if ($NoWeekends) {
  $argList += "-nw"
}

if ($UserName) {
  $argList += "-un"
  $argList += $UserName
}

if ($UserEmail) {
  $argList += "-ue"
  $argList += $UserEmail
}

& $pythonCmd.Source @argList
