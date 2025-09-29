# PowerShell Setup Script for PPT Generator AI Code Review Integration
# Run this script in your ppt-generator-project repository root

param(
    [string]$ProjectName = "ppt-generator-project",
    [string]$AutoPRRepo = "https://github.com/dasarisuma/AI-based-Code-reviews.git",
    [string]$AutoPRBranch = "test-ai-review"
)

Write-Host "🚀 Setting up AI Code Review Integration for PPT Generator Project" -ForegroundColor Green

# Check if we're in the right repository
if (-not (Test-Path "app.py") -or -not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: This script must be run in the ppt-generator-project repository root" -ForegroundColor Red
    Write-Host "Expected files: app.py, requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Confirmed we're in the PPT Generator project directory" -ForegroundColor Green

# Create backup of existing Jenkinsfile if it exists
if (Test-Path "Jenkinsfile") {
    $backupName = "Jenkinsfile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "⚠️  Jenkinsfile already exists. Creating backup: $backupName" -ForegroundColor Yellow
    Copy-Item "Jenkinsfile" $backupName
}

Write-Host "📄 Creating Jenkinsfile for AI Code Review integration..." -ForegroundColor Cyan

# Create the Jenkinsfile content
$jenkinsfileContent = @'
pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 30, unit: 'MINUTES')
        ansiColor('xterm')
    }

    parameters {
        string(name: 'AUTOPR_REPO_URL', defaultValue: 'https://github.com/dasarisuma/AI-based-Code-reviews.git', description: 'AutoPR System Repository URL')
        string(name: 'AUTOPR_BRANCH', defaultValue: 'test-ai-review', description: 'AutoPR System Branch')
        string(name: 'FAIL_ON', defaultValue: 'critical,error', description: 'Severities that will fail the build')
        string(name: 'AGENTS', defaultValue: 'security,bug_detection,code_quality', description: 'AI agents to run')
    }

    environment {
        GITHUB_TOKEN = credentials('github-pat')
        GROQ_API_KEY = credentials('groq-api-key')
        AUTOPR_DIR = "${WORKSPACE}/autopr-system"
        PYTHON_VENV = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo "Checking out PPT Generator source code..."
                checkout scm
                
                script {
                    env.IS_PR = env.CHANGE_ID ? 'true' : 'false'
                    if (env.IS_PR == 'true') {
                        env.PR_URL = env.CHANGE_URL ?: "https://github.com/dasarisuma/ppt-generator-project/pull/${env.CHANGE_ID}"
                        echo "PR build detected: ${env.PR_URL} (${env.CHANGE_BRANCH} -> ${env.CHANGE_TARGET})"
                    } else {
                        echo "Regular branch build - AI review will use local diff mode"
                    }
                }
            }
        }

        stage('Setup AutoPR System') {
            steps {
                echo "Cloning AutoPR AI Review System..."
                script {
                    bat """
                        if exist "${env.AUTOPR_DIR}" rd /s /q "${env.AUTOPR_DIR}"
                        git clone -b ${params.AUTOPR_BRANCH} ${params.AUTOPR_REPO_URL} "${env.AUTOPR_DIR}"
                    """
                }
                
                echo "Setting up Python environment for AI review..."
                script {
                    bat """
                        cd "${env.AUTOPR_DIR}\\backend"
                        python --version
                        
                        if not exist "${env.PYTHON_VENV}" (
                            python -m venv "${env.PYTHON_VENV}"
                        )
                        
                        "${env.PYTHON_VENV}\\Scripts\\activate.bat" && pip install --upgrade pip && pip install -r requirements.txt
                    """
                }
            }
        }

        stage('AI Code Review') {
            steps {
                echo "Running AI-powered code review..."
                script {
                    bat """
                        cd "${env.AUTOPR_DIR}\\backend"
                        "${env.PYTHON_VENV}\\Scripts\\activate.bat"
                        
                        set PYTHONPATH=${env.AUTOPR_DIR}\\backend;%PYTHONPATH%
                        
                        if "${env.IS_PR}"=="true" (
                            python scripts\\run_review.py --pr-url "${env.PR_URL}" --github-token "${env.GITHUB_TOKEN}" --agents "${params.AGENTS}" --fail-on "${params.FAIL_ON}" --output "${WORKSPACE}\\ai-review-results.json" --project-root "${WORKSPACE}"
                        ) else (
                            cd "${WORKSPACE}"
                            git fetch origin main:refs/remotes/origin/main || git fetch origin master:refs/remotes/origin/master || echo "No main/master branch"
                            
                            cd "${env.AUTOPR_DIR}\\backend"
                            python scripts\\run_review.py --base-ref origin/main --head-ref HEAD --local-diff --agents "${params.AGENTS}" --fail-on "${params.FAIL_ON}" --output "${WORKSPACE}\\ai-review-results.json" --project-root "${WORKSPACE}"
                        )
                    """
                }
            }
        }

        stage('Process Review Results') {
            steps {
                script {
                    if (fileExists('ai-review-results.json')) {
                        echo "Processing AI review results..."
                        def reviewResults = readJSON file: 'ai-review-results.json'
                        
                        def severities = reviewResults.comments?.collect { comment ->
                            (comment.severity ?: '').toLowerCase()
                        } ?: []
                        
                        def blockingSeverities = params.FAIL_ON.toLowerCase().split(',')*.trim()
                        
                        def hasBlockingIssues = severities.any { severity ->
                            blockingSeverities.contains(severity)
                        }
                        
                        echo "=== AI CODE REVIEW SUMMARY ==="
                        echo "Total comments: ${reviewResults.comments?.size() ?: 0}"
                        echo "Summary: ${reviewResults.summary ?: 'No summary available'}"
                        
                        if (reviewResults.comments) {
                            reviewResults.comments.each { comment ->
                                echo "📍 ${comment.file}:${comment.line} [${comment.severity?.toUpperCase()}] ${comment.message}"
                            }
                        }
                        
                        if (hasBlockingIssues) {
                            echo "❌ BLOCKING ISSUES FOUND!"
                            error("AI Code Review found blocking issues. Build failed.")
                        } else {
                            echo "✅ No blocking issues found. Build can proceed."
                        }
                    } else {
                        echo "⚠️ No review results file found."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Build PPT Generator') {
            when {
                expression { currentBuild.result != 'FAILURE' }
            }
            steps {
                echo "Building PPT Generator application..."
                script {
                    bat """
                        if not exist "ppt-venv" (
                            python -m venv ppt-venv
                        )
                        
                        ppt-venv\\Scripts\\activate.bat && pip install --upgrade pip && pip install -r requirements.txt
                        
                        if exist "test_app.py" (
                            ppt-venv\\Scripts\\activate.bat && python -m pytest test_app.py -v
                        )
                        
                        echo Build completed successfully!
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace..."
            script {
                bat """
                    if exist "${env.AUTOPR_DIR}" rd /s /q "${env.AUTOPR_DIR}" || echo "Cleanup done"
                    if exist "${env.PYTHON_VENV}" rd /s /q "${env.PYTHON_VENV}" || echo "Cleanup done"
                    if exist "ppt-venv" rd /s /q "ppt-venv" || echo "Cleanup done"
                """
            }
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
        }
        
        failure {
            echo "❌ Pipeline failed due to AI code review findings!"
        }
    }
}
'@

# Write the Jenkinsfile
$jenkinsfileContent | Out-File -FilePath "Jenkinsfile" -Encoding UTF8
Write-Host "✅ Jenkinsfile created successfully" -ForegroundColor Green

# Update .gitignore
Write-Host "📝 Updating .gitignore for AI review artifacts..." -ForegroundColor Cyan
if (-not (Test-Path ".gitignore")) {
    New-Item -Path ".gitignore" -ItemType File
}

$gitignoreEntries = @(
    "ai-review-results.json",
    "autopr-system/",
    "venv/",
    "ppt-venv/"
)

$currentGitignore = if (Test-Path ".gitignore") { Get-Content ".gitignore" } else { @() }

foreach ($entry in $gitignoreEntries) {
    if ($currentGitignore -notcontains $entry) {
        Add-Content -Path ".gitignore" -Value $entry
        Write-Host "Added to .gitignore: $entry" -ForegroundColor Gray
    }
}

Write-Host "✅ .gitignore updated" -ForegroundColor Green

# Create AI Code Review documentation
Write-Host "📚 Creating AI Code Review documentation..." -ForegroundColor Cyan

$aiDocContent = @'
# AI Code Review Integration

This project is integrated with an AI-powered code review system that automatically analyzes code changes in pull requests.

## How It Works

1. **Automatic Trigger**: When you create a pull request, Jenkins automatically triggers the AI code review pipeline
2. **AI Analysis**: The system analyzes your code using multiple AI agents:
   - **Security Agent**: Identifies potential security vulnerabilities
   - **Bug Detection Agent**: Finds potential bugs and logic issues  
   - **Code Quality Agent**: Reviews code style, maintainability, and best practices
3. **Review Results**: The AI provides detailed feedback with severity levels:
   - `info`: General suggestions and information
   - `warning`: Issues that should be addressed but don't block the PR
   - `error`: Serious issues that block the PR
   - `critical`: Critical issues that must be fixed before merging

## Build Status

- ✅ **PASS**: No critical or error-level issues found
- ❌ **FAIL**: Critical or error-level issues found - PR is blocked
- ⚠️ **UNSTABLE**: Warnings found but PR can proceed

## Configuration

The AI review can be configured via Jenkins parameters:
- `AGENTS`: Which AI agents to run (default: security,bug_detection,code_quality)
- `FAIL_ON`: Severity levels that will fail the build (default: critical,error)

## Bypassing Review (Emergency Only)

In emergency situations, you can bypass the AI review by:
1. Adding `[skip-ai-review]` to your commit message
2. Or contact the project maintainer to manually override

## Getting Help

If you have questions about the AI review feedback:
1. Check the build logs for detailed explanations
2. Review the `ai-review-results.json` artifact for full details
3. Contact the development team for clarification
'@

$aiDocContent | Out-File -FilePath "AI_CODE_REVIEW.md" -Encoding UTF8
Write-Host "✅ AI_CODE_REVIEW.md created" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 AI Code Review integration setup completed!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push the new Jenkinsfile and documentation" -ForegroundColor White
Write-Host "2. Configure Jenkins credentials (github-pat, groq-api-key)" -ForegroundColor White
Write-Host "3. Set up multibranch pipeline in Jenkins pointing to this repository" -ForegroundColor White
Write-Host "4. Test with a sample pull request" -ForegroundColor White
Write-Host ""
Write-Host "Files created/modified:" -ForegroundColor Yellow
Write-Host "- Jenkinsfile (AI-integrated pipeline)" -ForegroundColor White
Write-Host "- AI_CODE_REVIEW.md (documentation)" -ForegroundColor White
Write-Host "- .gitignore (updated with AI artifacts)" -ForegroundColor White
Write-Host ""
Write-Host "✨ Integration ready! Your PPT Generator project now has AI-powered code reviews!" -ForegroundColor Green