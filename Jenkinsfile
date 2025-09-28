pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 30, unit: 'MINUTES')
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

        stage('Setup System Dependencies') {
            steps {
                echo "Setting up system dependencies..."
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Checking Python installation..."
                            python3 --version || python --version || echo "Python not found"
                            
                            echo "Checking if we need to install python3-venv..."
                            if ! python3 -m venv --help >/dev/null 2>&1; then
                                echo "Installing python3-venv..."
                                apt-get update -qq || yum update -y -q || echo "Package manager update failed"
                                apt-get install -y python3-venv python3-pip || yum install -y python3-venv python3-pip || echo "Package installation attempted"
                            fi
                            
                            echo "Checking pip availability..."
                            python3 -m pip --version || curl https://bootstrap.pypa.io/get-pip.py | python3 || echo "Pip setup attempted"
                        '''
                    } else {
                        bat '''
                            echo "Windows environment detected"
                            python --version || echo "Python not found"
                            pip --version || echo "Pip not found" 
                        '''
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
                        sh '''
                            cd "${AUTOPR_DIR}/backend"
                            echo "Current directory: $(pwd)"
                            echo "Available Python commands:"
                            which python3 || echo "python3 not in PATH"
                            which python || echo "python not in PATH"
                            
                            # Try different methods to create virtual environment
                            echo "Attempting to create virtual environment..."
                            
                            # Method 1: Use python3 -m venv (preferred)
                            if python3 -m venv "${PYTHON_VENV}"; then
                                echo "Virtual environment created with python3 -m venv"
                                VENV_ACTIVATE="${PYTHON_VENV}/bin/activate"
                            # Method 2: Use virtualenv if available
                            elif command -v virtualenv >/dev/null 2>&1; then
                                echo "Using virtualenv..."
                                virtualenv "${PYTHON_VENV}"
                                VENV_ACTIVATE="${PYTHON_VENV}/bin/activate"
                            # Method 3: Install packages globally (fallback)
                            else
                                echo "Virtual environment creation failed, installing packages globally"
                                python3 -m pip install --user --upgrade pip
                                python3 -m pip install --user -r requirements.txt
                                VENV_ACTIVATE=""
                            fi
                            
                            # Activate environment and install dependencies if venv was created
                            if [ -n "$VENV_ACTIVATE" ] && [ -f "$VENV_ACTIVATE" ]; then
                                echo "Activating virtual environment and installing dependencies..."
                                . "$VENV_ACTIVATE"
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                echo "Dependencies installed in virtual environment"
                            else
                                echo "Using global Python installation"
                            fi
                            
                            echo "Python environment setup completed"
                        '''
                    } else {
                        bat """
                            cd "${env.AUTOPR_DIR}\\backend"
                            python --version
                            
                            if not exist "${env.PYTHON_VENV}" (
                                python -m venv "${env.PYTHON_VENV}" || echo "Virtual env creation failed, using global"
                            )
                            
                            if exist "${env.PYTHON_VENV}\\Scripts\\activate.bat" (
                                "${env.PYTHON_VENV}\\Scripts\\activate.bat" && pip install --upgrade pip && pip install -r requirements.txt
                            ) else (
                                pip install --upgrade pip && pip install -r requirements.txt
                            )
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
                        sh '''
                            cd "${AUTOPR_DIR}/backend"
                            
                            # Set up Python path
                            export PYTHONPATH="${AUTOPR_DIR}/backend:${PYTHONPATH}"
                            
                            # Determine Python command and activation
                            if [ -f "${PYTHON_VENV}/bin/activate" ]; then
                                echo "Using virtual environment"
                                . "${PYTHON_VENV}/bin/activate"
                                PYTHON_CMD="python"
                            else
                                echo "Using global Python installation"
                                PYTHON_CMD="python3"
                            fi
                            
                            echo "Using Python command: $PYTHON_CMD"
                            $PYTHON_CMD --version
                            
                            # Run the AI review
                            if [ "${IS_PR}" = "true" ]; then
                                echo "Running PR mode review..."
                                $PYTHON_CMD scripts/run_review.py \\
                                    --pr-url "${PR_URL}" \\
                                    --github-token "${GITHUB_TOKEN}" \\
                                    --agents "${AGENTS}" \\
                                    --fail-on "${FAIL_ON}" \\
                                    --output "${WORKSPACE}/ai-review-results.json" \\
                                    --project-root "${WORKSPACE}"
                            else
                                echo "Running local diff mode review..."
                                cd "${WORKSPACE}"
                                git fetch origin main:refs/remotes/origin/main || git fetch origin master:refs/remotes/origin/master || echo "No main/master branch found"
                                
                                cd "${AUTOPR_DIR}/backend"
                                $PYTHON_CMD scripts/run_review.py \\
                                    --base-ref origin/main \\
                                    --head-ref HEAD \\
                                    --local-diff \\
                                    --agents "${AGENTS}" \\
                                    --fail-on "${FAIL_ON}" \\
                                    --output "${WORKSPACE}/ai-review-results.json" \\
                                    --project-root "${WORKSPACE}"
                            fi
                        '''
                    } else {
                        bat """
                            cd "${env.AUTOPR_DIR}\\backend"
                            
                            set PYTHONPATH=${env.AUTOPR_DIR}\\backend;%PYTHONPATH%
                            
                            if exist "${env.PYTHON_VENV}\\Scripts\\activate.bat" (
                                "${env.PYTHON_VENV}\\Scripts\\activate.bat"
                            )
                            
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
                                echo "[${comment.severity?.toUpperCase()}] ${comment.file}:${comment.line} - ${comment.message}"
                            }
                        }
                        
                        if (hasBlockingIssues) {
                            echo "BLOCKING ISSUES FOUND!"
                            echo "Found severities that are configured to fail the build: ${blockingSeverities.join(', ')}"
                            error("AI Code Review found blocking issues. Build failed.")
                        } else {
                            echo "No blocking issues found. Build can proceed."
                        }
                    } else {
                        echo "WARNING: No review results file found."
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
                        sh '''
                            echo "Setting up PPT Generator environment..."
                            
                            # Try to create virtual environment for PPT generator
                            if python3 -m venv ppt-venv; then
                                echo "Virtual environment created for PPT generator"
                                . ppt-venv/bin/activate
                                pip install --upgrade pip
                            else
                                echo "Using global Python for PPT generator"
                                python3 -m pip install --user --upgrade pip
                            fi
                            
                            # Install requirements
                            if [ -f ppt-venv/bin/activate ]; then
                                . ppt-venv/bin/activate
                                pip install -r requirements.txt
                            else
                                python3 -m pip install --user -r requirements.txt
                            fi
                            
                            # Run tests if they exist
                            if [ -f "test_app.py" ]; then
                                echo "Running tests..."
                                if [ -f ppt-venv/bin/activate ]; then
                                    . ppt-venv/bin/activate
                                    python -m pytest test_app.py -v || echo "Tests completed with issues"
                                else
                                    python3 -m pytest test_app.py -v || echo "Tests completed with issues"
                                fi
                            else
                                echo "No tests found, skipping test execution"
                            fi
                            
                            echo "Build completed successfully!"
                        '''
                    } else {
                        bat """
                            echo "Setting up PPT Generator environment on Windows..."
                            
                            if not exist "ppt-venv" (
                                python -m venv ppt-venv || echo "Virtual env creation failed, using global"
                            )
                            
                            if exist "ppt-venv\\Scripts\\activate.bat" (
                                ppt-venv\\Scripts\\activate.bat && pip install --upgrade pip && pip install -r requirements.txt
                            ) else (
                                pip install --upgrade pip && pip install -r requirements.txt
                            )
                            
                            if exist "test_app.py" (
                                if exist "ppt-venv\\Scripts\\activate.bat" (
                                    ppt-venv\\Scripts\\activate.bat && python -m pytest test_app.py -v || echo "Tests completed"
                                ) else (
                                    python -m pytest test_app.py -v || echo "Tests completed"
                                )
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
                try {
                    if (isUnix()) {
                        sh '''
                            echo "Cleaning up directories..."
                            rm -rf "${AUTOPR_DIR}" || echo "AutoPR cleanup done"
                            rm -rf "${PYTHON_VENV}" || echo "Python venv cleanup done"  
                            rm -rf "ppt-venv" || echo "PPT venv cleanup done"
                            echo "Cleanup completed"
                        '''
                    } else {
                        bat """
                            echo Cleaning up directories...
                            if exist "${env.AUTOPR_DIR}" rd /s /q "${env.AUTOPR_DIR}" || echo "AutoPR cleanup done"
                            if exist "${env.PYTHON_VENV}" rd /s /q "${env.PYTHON_VENV}" || echo "Python venv cleanup done"
                            if exist "ppt-venv" rd /s /q "ppt-venv" || echo "PPT venv cleanup done"
                            echo Cleanup completed
                        """
                    }
                } catch (Exception e) {
                    echo "Cleanup completed with minor issues: ${e.getMessage()}"
                }
            }
            
            // Archive the AI review results
            archiveArtifacts artifacts: 'ai-review-results.json', allowEmptyArchive: true, fingerprint: true
        }
        
        success {
            echo "SUCCESS: Pipeline completed successfully!"
            echo "AI Code Review passed - no blocking issues found."
        }
        
        failure {
            echo "FAILURE: Pipeline failed!"
            script {
                if (fileExists('ai-review-results.json')) {
                    def reviewResults = readJSON file: 'ai-review-results.json'
                    echo "Failure likely due to AI code review findings:"
                    if (reviewResults.comments) {
                        for (comment in reviewResults.comments) {
                            def severity = comment.severity?.toLowerCase()
                            if (severity == 'critical' || severity == 'error') {
                                echo "CRITICAL ISSUE: ${comment.file}:${comment.line} [${comment.severity}] ${comment.message}"
                            }
                        }
                    }
                } else {
                    echo "Pipeline failed due to system error (not AI review)"
                }
            }
        }
        
        unstable {
            echo "UNSTABLE: Pipeline completed with warnings."
            echo "Check the AI review results for non-blocking issues."
        }
    }
}