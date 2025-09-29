// Enhanced Jenkins Pipeline for PPT Generator with Automatic Latest PR Detection
// Compatible with all Jenkins versions - Automatically reviews the most recent PR

properties([
    buildDiscarder(logRotator(numToKeepStr: '15')),
    parameters([
        string(name: 'PPT_GENERATOR_REPO_URL', defaultValue: 'https://github.com/dasarisuma/ppt-generator-project.git', description: 'PPT Generator Repository URL'),
        string(name: 'AUTOPR_REPO_URL', defaultValue: 'https://github.com/dasarisuma/AI-based-Code-reviews.git', description: 'AutoPR System Repository URL'),
        string(name: 'AUTOPR_BRANCH', defaultValue: 'test-ai-review', description: 'AutoPR System Branch'),
        choice(name: 'PR_SELECTION_MODE', choices: ['latest', 'all_open', 'manual'], description: 'How to select PR for review'),
        string(name: 'MANUAL_PR_NUMBER', defaultValue: '', description: 'Manual PR number (only used if mode is manual)'),
        string(name: 'FAIL_ON', defaultValue: 'critical,error', description: 'Severities that will fail the build'),
        string(name: 'AGENTS', defaultValue: 'security,bug_detection,code_quality', description: 'AI agents to run')
    ])
])

node {
    timeout(time: 45, unit: 'MINUTES') {
        try {
            // Set environment variables
            env.AUTOPR_DIR = "${WORKSPACE}/autopr-system"
            env.PPT_DIR = "${WORKSPACE}/ppt-generator"
            env.PYTHON_VENV = "${WORKSPACE}/venv"
            
            withCredentials([
                string(credentialsId: 'github-pat', variable: 'GITHUB_TOKEN'),
                string(credentialsId: 'groq-api-key', variable: 'GROQ_API_KEY')
            ]) {
                
                stage('Discover Latest PR') {
                    echo "🔍 Discovering PRs from PPT Generator repository..."
                    
                    // Create a temporary directory for PR discovery
                    if (isUnix()) {
                        sh """
                            rm -rf ppt-temp
                            git clone ${params.PPT_GENERATOR_REPO_URL} ppt-temp
                            cd ppt-temp
                        """
                    } else {
                        bat """
                            if exist ppt-temp rd /s /q ppt-temp
                            git clone ${params.PPT_GENERATOR_REPO_URL} ppt-temp
                            cd ppt-temp
                        """
                    }
                    
                    // Get PR information using GitHub API
                    script {
                        def prInfo = ""
                        def selectedPR = ""
                        def repoOwner = ""
                        def repoName = ""
                        
                        // Extract owner and repo from URL
                        def repoUrl = params.PPT_GENERATOR_REPO_URL
                        def urlParts = repoUrl.replace('https://github.com/', '').replace('.git', '').split('/')
                        if (urlParts.size() >= 2) {
                            repoOwner = urlParts[0]
                            repoName = urlParts[1]
                        }
                        
                        echo "Repository: ${repoOwner}/${repoName}"
                        
                        if (params.PR_SELECTION_MODE == 'manual' && params.MANUAL_PR_NUMBER?.trim()) {
                            selectedPR = params.MANUAL_PR_NUMBER.trim()
                            echo "📌 Manual PR selection: PR #${selectedPR}"
                        } else {
                            // Use GitHub API to get PR information
                            if (isUnix()) {
                                prInfo = sh(
                                    script: """
                                        echo "Fetching PR information using GitHub API..."
                                        curl -s -H "Authorization: token ${GITHUB_TOKEN}" \\
                                             -H "Accept: application/vnd.github.v3+json" \\
                                             "https://api.github.com/repos/${repoOwner}/${repoName}/pulls?state=open&sort=updated&direction=desc" | \\
                                        python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    if data and len(data) > 0:
        if '${params.PR_SELECTION_MODE}' == 'latest':
            # Get the most recently updated PR
            latest_pr = data[0]
            print(f'LATEST_PR_NUMBER={latest_pr[\"number\"]}')
            print(f'LATEST_PR_TITLE={latest_pr[\"title\"]}')
            print(f'LATEST_PR_BRANCH={latest_pr[\"head\"][\"ref\"]}')
            print(f'LATEST_PR_BASE={latest_pr[\"base\"][\"ref\"]}')
            print(f'LATEST_PR_URL={latest_pr[\"html_url\"]}')
            print(f'LATEST_PR_UPDATED={latest_pr[\"updated_at\"]}')
        else:
            # Show all open PRs
            print('OPEN_PRS_COUNT=' + str(len(data)))
            for i, pr in enumerate(data[:5]):  # Show first 5 PRs
                print(f'PR_{i+1}_NUMBER={pr[\"number\"]}')
                print(f'PR_{i+1}_TITLE={pr[\"title\"]}')
                print(f'PR_{i+1}_BRANCH={pr[\"head\"][\"ref\"]}')
                print(f'PR_{i+1}_UPDATED={pr[\"updated_at\"]}')
    else:
        print('NO_OPEN_PRS=true')
except Exception as e:
    print(f'ERROR_PARSING_PRS={str(e)}')
"
                                    """,
                                    returnStdout: true
                                ).trim()
                            } else {
                                prInfo = bat(
                                    script: """
                                        @echo off
                                        echo Fetching PR information using GitHub API...
                                        curl -s -H "Authorization: token ${GITHUB_TOKEN}" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/${repoOwner}/${repoName}/pulls?state=open&sort=updated&direction=desc" > pr_data.json
                                        python -c "
import json
import sys
try:
    with open('pr_data.json', 'r') as f:
        data = json.load(f)
    if data and len(data) > 0:
        if '${params.PR_SELECTION_MODE}' == 'latest':
            latest_pr = data[0]
            print(f'LATEST_PR_NUMBER={latest_pr[\"number\"]}')
            print(f'LATEST_PR_TITLE={latest_pr[\"title\"]}')
            print(f'LATEST_PR_BRANCH={latest_pr[\"head\"][\"ref\"]}')
            print(f'LATEST_PR_BASE={latest_pr[\"base\"][\"ref\"]}')
            print(f'LATEST_PR_URL={latest_pr[\"html_url\"]}')
            print(f'LATEST_PR_UPDATED={latest_pr[\"updated_at\"]}')
        else:
            print('OPEN_PRS_COUNT=' + str(len(data)))
            for i, pr in enumerate(data[:5]):
                print(f'PR_{i+1}_NUMBER={pr[\"number\"]}')
                print(f'PR_{i+1}_TITLE={pr[\"title\"]}')
                print(f'PR_{i+1}_BRANCH={pr[\"head\"][\"ref\"]}')
                print(f'PR_{i+1}_UPDATED={pr[\"updated_at\"]}')
    else:
        print('NO_OPEN_PRS=true')
except Exception as e:
    print(f'ERROR_PARSING_PRS={str(e)}')
"
                                    """,
                                    returnStdout: true
                                ).trim()
                            }
                            
                            echo "PR Discovery Results:"
                            echo prInfo
                            
                            // Parse the results and set environment variables
                            prInfo.split('\n').each { line ->
                                if (line.contains('=')) {
                                    def parts = line.split('=', 2)
                                    if (parts.size() == 2) {
                                        env."${parts[0]}" = parts[1]
                                    }
                                }
                            }
                            
                            if (env.LATEST_PR_NUMBER) {
                                selectedPR = env.LATEST_PR_NUMBER
                                echo "🎯 Auto-selected latest PR: #${selectedPR} - ${env.LATEST_PR_TITLE}"
                                echo "   Branch: ${env.LATEST_PR_BRANCH} → ${env.LATEST_PR_BASE}"
                                echo "   Updated: ${env.LATEST_PR_UPDATED}"
                                echo "   URL: ${env.LATEST_PR_URL}"
                            } else if (env.NO_OPEN_PRS == 'true') {
                                error("❌ No open PRs found in the PPT Generator repository. Please create a PR to review.")
                            } else if (env.ERROR_PARSING_PRS) {
                                error("❌ Error fetching PR information: ${env.ERROR_PARSING_PRS}")
                            }
                        }
                        
                        if (!selectedPR) {
                            error("❌ Could not determine which PR to review. Check your repository and GitHub token permissions.")
                        }
                        
                        // Set the PR URL for the review
                        env.SELECTED_PR_NUMBER = selectedPR
                        env.SELECTED_PR_URL = "https://github.com/${repoOwner}/${repoName}/pull/${selectedPR}"
                        
                        echo "✅ Selected PR for review: ${env.SELECTED_PR_URL}"
                    }
                    
                    // Clean up temporary directory
                    if (isUnix()) {
                        sh "rm -rf ppt-temp"
                    } else {
                        bat "if exist ppt-temp rd /s /q ppt-temp"
                    }
                }

                stage('Checkout PPT Generator PR') {
                    echo "📥 Checking out PPT Generator PR #${env.SELECTED_PR_NUMBER}..."
                    
                    if (isUnix()) {
                        sh """
                            if [ -d "${env.PPT_DIR}" ]; then
                                rm -rf "${env.PPT_DIR}"
                            fi
                            
                            # Clone the repository
                            git clone ${params.PPT_GENERATOR_REPO_URL} "${env.PPT_DIR}"
                            cd "${env.PPT_DIR}"
                            
                            # Fetch the PR
                            git fetch origin pull/${env.SELECTED_PR_NUMBER}/head:pr-${env.SELECTED_PR_NUMBER}
                            git checkout pr-${env.SELECTED_PR_NUMBER}
                            
                            echo "✅ Successfully checked out PR #${env.SELECTED_PR_NUMBER}"
                            echo "Current commit:"
                            git log --oneline -1
                            echo "Files changed:"
                            git diff --name-only HEAD~1 || echo "No changes detected"
                        """
                    } else {
                        bat """
                            if exist "${env.PPT_DIR}" rd /s /q "${env.PPT_DIR}"
                            
                            git clone ${params.PPT_GENERATOR_REPO_URL} "${env.PPT_DIR}"
                            cd "${env.PPT_DIR}"
                            
                            git fetch origin pull/${env.SELECTED_PR_NUMBER}/head:pr-${env.SELECTED_PR_NUMBER}
                            git checkout pr-${env.SELECTED_PR_NUMBER}
                            
                            echo "✅ Successfully checked out PR #${env.SELECTED_PR_NUMBER}"
                            echo "Current commit:"
                            git log --oneline -1
                            echo "Files changed:"
                            git diff --name-only HEAD~1 || echo "No changes detected"
                        """
                    }
                }

                stage('Setup AutoPR System') {
                    echo "🤖 Setting up AutoPR AI Review System..."
                    if (isUnix()) {
                        sh """
                            if [ -d "${env.AUTOPR_DIR}" ]; then
                                rm -rf "${env.AUTOPR_DIR}"
                            fi
                            git clone -b ${params.AUTOPR_BRANCH} ${params.AUTOPR_REPO_URL} "${env.AUTOPR_DIR}"
                        """
                    } else {
                        bat """
                            if exist "${env.AUTOPR_DIR}" rd /s /q "${env.AUTOPR_DIR}"
                            git clone -b ${params.AUTOPR_BRANCH} ${params.AUTOPR_REPO_URL} "${env.AUTOPR_DIR}"
                        """
                    }
                    
                    echo "🐍 Setting up Python environment for AI review..."
                    if (isUnix()) {
                        sh '''
                            cd "${AUTOPR_DIR}/backend"
                            echo "Current directory: $(pwd)"
                            
                            echo "=== Virtual Environment Setup ==="
                            if python3 -m venv "${PYTHON_VENV}" >/dev/null 2>&1; then
                                echo "✓ Virtual environment created successfully"
                                VENV_CREATED=true
                                VENV_ACTIVATE="${PYTHON_VENV}/bin/activate"
                            else
                                echo "⚠️  Using --break-system-packages as fallback"
                                python3 -m pip install --break-system-packages --upgrade pip
                                python3 -m pip install --break-system-packages -r requirements.txt
                                VENV_CREATED=false
                                echo "✓ Packages installed globally"
                            fi
                            
                            if [ "$VENV_CREATED" = true ] && [ -f "$VENV_ACTIVATE" ]; then
                                echo "Installing dependencies in virtual environment..."
                                . "$VENV_ACTIVATE"
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                echo "✓ Dependencies installed in virtual environment"
                            fi
                            
                            echo "=== Python Environment Ready ==="
                        '''
                    } else {
                        bat """
                            cd "${env.AUTOPR_DIR}\\backend"
                            python --version
                            
                            python -m venv "${env.PYTHON_VENV}" || echo "Using global Python"
                            if exist "${env.PYTHON_VENV}\\Scripts\\activate.bat" (
                                "${env.PYTHON_VENV}\\Scripts\\activate.bat" && pip install --upgrade pip && pip install -r requirements.txt
                            ) else (
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            )
                        """
                    }
                }

                stage('Run AI Code Review') {
                    echo "🔍 Running AI-powered code review on PR #${env.SELECTED_PR_NUMBER}..."
                    
                    if (isUnix()) {
                        sh """
                            cd "${env.AUTOPR_DIR}/backend"
                            
                            # Activate virtual environment if it exists
                            if [ -f "${env.PYTHON_VENV}/bin/activate" ]; then
                                . "${env.PYTHON_VENV}/bin/activate"
                                echo "Using virtual environment"
                            else
                                echo "Using global Python installation"
                            fi
                            
                            export PYTHONPATH="${env.AUTOPR_DIR}/backend:\${PYTHONPATH}"
                            
                            echo "Running AI review for PR: ${env.SELECTED_PR_URL}"
                            echo "Using agents: ${params.AGENTS}"
                            echo "Fail on severities: ${params.FAIL_ON}"
                            
                            python scripts/run_review.py \\
                                --pr-url "${env.SELECTED_PR_URL}" \\
                                --github-token "${GITHUB_TOKEN}" \\
                                --agents "${params.AGENTS}" \\
                                --fail-on "${params.FAIL_ON}" \\
                                --output "${WORKSPACE}/ai-review-results.json" \\
                                --project-root "${env.PPT_DIR}" \\
                                --verbose
                            
                            echo "✅ AI Code Review completed"
                        """
                    } else {
                        bat """
                            cd "${env.AUTOPR_DIR}\\backend"
                            
                            if exist "${env.PYTHON_VENV}\\Scripts\\activate.bat" (
                                "${env.PYTHON_VENV}\\Scripts\\activate.bat"
                                echo "Using virtual environment"
                            ) else (
                                echo "Using global Python installation"
                            )
                            
                            set PYTHONPATH=${env.AUTOPR_DIR}\\backend;%PYTHONPATH%
                            
                            echo "Running AI review for PR: ${env.SELECTED_PR_URL}"
                            echo "Using agents: ${params.AGENTS}"
                            echo "Fail on severities: ${params.FAIL_ON}"
                            
                            python scripts\\run_review.py --pr-url "${env.SELECTED_PR_URL}" --github-token "%GITHUB_TOKEN%" --agents "${params.AGENTS}" --fail-on "${params.FAIL_ON}" --output "${WORKSPACE}\\ai-review-results.json" --project-root "${env.PPT_DIR}" --verbose
                            
                            echo "✅ AI Code Review completed"
                        """
                    }
                }

                stage('Process Review Results') {
                    echo "📊 Processing AI review results..."
                    script {
                        def resultsFile = "${WORKSPACE}/ai-review-results.json"
                        
                        if (fileExists(resultsFile)) {
                            def results
                            if (isUnix()) {
                                results = sh(
                                    script: "cat '${resultsFile}'",
                                    returnStdout: true
                                ).trim()
                            } else {
                                results = bat(
                                    script: "@type \"${resultsFile}\"",
                                    returnStdout: true
                                ).trim()
                            }
                            
                            echo "=== AI CODE REVIEW RESULTS FOR PR #${env.SELECTED_PR_NUMBER} ==="
                            echo results
                            echo "================================================================="
                            
                            // Archive results
                            archiveArtifacts artifacts: 'ai-review-results.json', allowEmptyArchive: true
                            
                            // Parse results for build decision
                            try {
                                def jsonSlurper = new groovy.json.JsonSlurper()
                                def reviewData = jsonSlurper.parseText(results)
                                
                                def hasCriticalIssues = false
                                def hasErrorIssues = false
                                def hasWarningIssues = false
                                def totalIssues = 0
                                def issuesSummary = [:]
                                
                                if (reviewData.results) {
                                    reviewData.results.each { agentResult ->
                                        if (agentResult.issues) {
                                            agentResult.issues.each { issue ->
                                                totalIssues++
                                                def severity = issue.severity
                                                issuesSummary[severity] = (issuesSummary[severity] ?: 0) + 1
                                                
                                                if (severity == 'critical') {
                                                    hasCriticalIssues = true
                                                } else if (severity == 'error') {
                                                    hasErrorIssues = true
                                                } else if (severity == 'warning') {
                                                    hasWarningIssues = true
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                echo "📈 REVIEW SUMMARY FOR PR #${env.SELECTED_PR_NUMBER}:"
                                echo "   Total issues found: ${totalIssues}"
                                echo "   Critical: ${issuesSummary.critical ?: 0}"
                                echo "   Error: ${issuesSummary.error ?: 0}" 
                                echo "   Warning: ${issuesSummary.warning ?: 0}"
                                echo "   Info: ${issuesSummary.info ?: 0}"
                                
                                // Determine if build should fail
                                def shouldFail = false
                                def failReason = ""
                                
                                if (params.FAIL_ON.contains('critical') && hasCriticalIssues) {
                                    shouldFail = true
                                    failReason = "Critical issues found (${issuesSummary.critical} critical issues)"
                                } else if (params.FAIL_ON.contains('error') && hasErrorIssues) {
                                    shouldFail = true
                                    failReason = "Error issues found (${issuesSummary.error} error issues)"
                                } else if (params.FAIL_ON.contains('warning') && hasWarningIssues) {
                                    shouldFail = true
                                    failReason = "Warning issues found (${issuesSummary.warning} warning issues)"
                                }
                                
                                if (shouldFail) {
                                    currentBuild.result = 'FAILURE'
                                    echo "❌ BUILD WILL FAIL: ${failReason}"
                                    echo "   Please address the issues in PR #${env.SELECTED_PR_NUMBER}"
                                    error("AI Code Review found blocking issues: ${failReason}")
                                } else {
                                    echo "✅ AI Code Review passed - no blocking issues found"
                                    echo "   PR #${env.SELECTED_PR_NUMBER} can proceed to build"
                                }
                                
                            } catch (Exception e) {
                                echo "⚠️  Warning: Could not parse review results JSON: ${e.message}"
                                echo "Raw results have been archived for manual review"
                                currentBuild.result = 'UNSTABLE'
                            }
                        } else {
                            echo "❌ Warning: No review results file found"
                            currentBuild.result = 'UNSTABLE'
                        }
                    }
                }

                stage('Build PPT Generator') {
                    when {
                        expression { currentBuild.result != 'FAILURE' }
                    }
                    steps {
                        echo "🏗️ Building PPT Generator from PR #${env.SELECTED_PR_NUMBER}..."
                        script {
                            dir(env.PPT_DIR) {
                                // Check for different build systems and build accordingly
                                if (fileExists('requirements.txt')) {
                                    echo "📦 Found Python project - installing dependencies"
                                    if (isUnix()) {
                                        sh """
                                            if [ -f "${env.PYTHON_VENV}/bin/activate" ]; then
                                                . "${env.PYTHON_VENV}/bin/activate"
                                            fi
                                            pip install -r requirements.txt
                                            echo "✅ Python dependencies installed"
                                        """
                                    } else {
                                        bat """
                                            if exist "${env.PYTHON_VENV}\\Scripts\\activate.bat" (
                                                "${env.PYTHON_VENV}\\Scripts\\activate.bat" && pip install -r requirements.txt
                                            ) else (
                                                pip install -r requirements.txt
                                            )
                                            echo "✅ Python dependencies installed"
                                        """
                                    }
                                }
                                
                                if (fileExists('package.json')) {
                                    echo "📦 Found Node.js project - installing dependencies"
                                    if (isUnix()) {
                                        sh 'npm install && echo "✅ Node.js dependencies installed"'
                                    } else {
                                        bat 'npm install && echo "✅ Node.js dependencies installed"'
                                    }
                                }
                                
                                if (fileExists('Dockerfile')) {
                                    echo "🐳 Found Dockerfile - Docker build available"
                                }
                                
                                echo "✅ Build stage completed successfully for PR #${env.SELECTED_PR_NUMBER}"
                            }
                        }
                    }
                }
            }
            
        } catch (Exception e) {
            echo "❌ Pipeline failed with error: ${e.message}"
            currentBuild.result = 'FAILURE'
            throw e
        }
    }
}

// Post-build actions
if (currentBuild.result == 'SUCCESS') {
    echo "🎉 SUCCESS: PR #${env.SELECTED_PR_NUMBER} passed AI review and built successfully!"
    echo "   Review results: ${WORKSPACE}/ai-review-results.json"
    echo "   PR URL: ${env.SELECTED_PR_URL}"
} else if (currentBuild.result == 'FAILURE') {
    echo "💥 FAILURE: PR #${env.SELECTED_PR_NUMBER} failed AI review or build"
    echo "   Check the AI Code Review results for issues to address"
    echo "   PR URL: ${env.SELECTED_PR_URL}"
} else {
    echo "⚠️  UNSTABLE: Pipeline completed with warnings"
    echo "   PR #${env.SELECTED_PR_NUMBER} may need attention"
    echo "   PR URL: ${env.SELECTED_PR_URL}"
}