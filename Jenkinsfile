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
                }
                
                echo "Setting up Python environment for AI review..."
                script {
                    if (isUnix()) {
                        sh """
                            cd "${env.AUTOPR_DIR}/backend"
                            python3 --version || python --version
                            
                            if [ ! -d "${env.PYTHON_VENV}" ]; then
                                python3 -m venv "${env.PYTHON_VENV}" 2>/dev/null || python -m venv "${env.PYTHON_VENV}"
                            fi
                            
                            . "${env.PYTHON_VENV}/bin/activate"
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        """
                    } else {
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
        }

        stage('AI Code Review') {
            steps {
                echo "Running AI-powered code review..."
                script {
                    if (isUnix()) {
                        sh """
                            cd "${env.AUTOPR_DIR}/backend"
                            . "${env.PYTHON_VENV}/bin/activate"
                            
                            export PYTHONPATH="${env.AUTOPR_DIR}/backend:\${PYTHONPATH}"
                            
                            if [ "${env.IS_PR}" = "true" ]; then
                                python scripts/run_review.py \\
                                    --pr-url "${env.PR_URL}" \\
                                    --github-token "${env.GITHUB_TOKEN}" \\
                                    --agents "${params.AGENTS}" \\
                                    --fail-on "${params.FAIL_ON}" \\
                                    --output "${WORKSPACE}/ai-review-results.json" \\
                                    --project-root "${WORKSPACE}"
                            else
                                cd "${WORKSPACE}"
                                git fetch origin main:refs/remotes/origin/main || git fetch origin master:refs/remotes/origin/master || echo "No main/master branch"
                                
                                cd "${env.AUTOPR_DIR}/backend"
                                python scripts/run_review.py \\
                                    --base-ref origin/main \\
                                    --head-ref HEAD \\
                                    --local-diff \\
                                    --agents "${params.AGENTS}" \\
                                    --fail-on "${params.FAIL_ON}" \\
                                    --output "${WORKSPACE}/ai-review-results.json" \\
                                    --project-root "${WORKSPACE}"
                            fi
                        """
                    } else {
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
        }

        stage('Process Review Results') {
            steps {
                script {
                    if (fileExists('ai-review-results.json')) {
                        echo "Processing AI review results..."
                        def reviewResults = readJSON file: 'ai-review-results.json'
                        
                        // Get all severity levels from comments
                        def severities = []
                        if (reviewResults.comments) {
                            for (comment in reviewResults.comments) {
                                def severity = comment.severity ?: ''
                                severities.add(severity.toLowerCase())
                            }
                        }
                        
                        // Parse blocking severities from parameter
                        def blockingSeverities = []
                        def failOnParam = params.FAIL_ON.toLowerCase()
                        def parts = failOnParam.split(',')
                        for (part in parts) {
                            blockingSeverities.add(part.trim())
                        }
                        
                        // Check if any blocking issues were found
                        def hasBlockingIssues = false
                        for (severity in severities) {
                            if (blockingSeverities.contains(severity)) {
                                hasBlockingIssues = true
                                break
                            }
                        }
                        
                        echo "=== AI CODE REVIEW SUMMARY ==="
                        echo "Total comments: ${reviewResults.comments?.size() ?: 0}"
                        echo "Summary: ${reviewResults.summary ?: 'No summary available'}"
                        
                        if (reviewResults.comments) {
                            for (comment in reviewResults.comments) {
                                echo "📍 ${comment.file}:${comment.line} [${comment.severity?.toUpperCase()}] ${comment.message}"
                            }
                        }
                        
                        if (hasBlockingIssues) {
                            echo "❌ BLOCKING ISSUES FOUND!"
                            echo "Found severities that are configured to fail the build: ${blockingSeverities.join(', ')}"
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
                    if (isUnix()) {
                        sh """
                            if [ ! -d "ppt-venv" ]; then
                                python3 -m venv ppt-venv
                            fi
                            
                            . ppt-venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            
                            if [ -f "test_app.py" ]; then
                                python -m pytest test_app.py -v
                            fi
                            
                            echo "Build completed successfully!"
                        """
                    } else {
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
    }

    post {
        always {
            echo "Cleaning up workspace..."
            script {
                if (isUnix()) {
                    sh """
                        rm -rf "${env.AUTOPR_DIR}" || echo "Cleanup done"
                        rm -rf "${env.PYTHON_VENV}" || echo "Cleanup done"
                        rm -rf "ppt-venv" || echo "Cleanup done"
                    """
                } else {
                    bat """
                        if exist "${env.AUTOPR_DIR}" rd /s /q "${env.AUTOPR_DIR}" || echo "Cleanup done"
                        if exist "${env.PYTHON_VENV}" rd /s /q "${env.PYTHON_VENV}" || echo "Cleanup done"
                        if exist "ppt-venv" rd /s /q "ppt-venv" || echo "Cleanup done"
                    """
                }
            }
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
        }
        
        failure {
            echo "❌ Pipeline failed!"
            script {
                if (fileExists('ai-review-results.json')) {
                    def reviewResults = readJSON file: 'ai-review-results.json'
                    echo "Failure likely due to AI code review findings:"
                    if (reviewResults.comments) {
                        for (comment in reviewResults.comments) {
                            def severity = comment.severity?.toLowerCase()
                            if (severity == 'critical' || severity == 'error') {
                                echo "🚨 ${comment.file}:${comment.line} [${comment.severity}] ${comment.message}"
                            }
                        }
                    }
                }
            }
        }
    }
}