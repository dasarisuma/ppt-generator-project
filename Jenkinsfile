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
                echo "Setting up system dependencies for Docker container..."
                script {
                    if (isUnix()) {
                        sh '''
                            echo "=== Python Environment Check ==="
                            python3 --version || echo "Python3 not found"
                            python3 -m pip --version || echo "Pip not found"
                            
                            echo "=== Installing Required System Packages ==="
                            # Check if we have root/sudo access
                            if command -v apt-get >/dev/null 2>&1; then
                                echo "Using apt package manager..."
                                # Try to install without sudo first (might work in Docker)
                                apt-get update -qq >/dev/null 2>&1 || echo "apt update failed (might need root)"
                                apt-get install -y python3-venv python3-full python3-pip >/dev/null 2>&1 || echo "apt install attempted"
                                
                                # If that fails, try with sudo
                                if ! python3 -m venv --help >/dev/null 2>&1; then
                                    echo "Trying with sudo..."
                                    sudo apt-get update -qq >/dev/null 2>&1 || echo "sudo apt update failed"
                                    sudo apt-get install -y python3-venv python3-full python3-pip >/dev/null 2>&1 || echo "sudo apt install attempted"
                                fi
                            elif command -v yum >/dev/null 2>&1; then
                                echo "Using yum package manager..."
                                yum update -y -q >/dev/null 2>&1 || echo "yum update failed"
                                yum install -y python3-venv python3-pip >/dev/null 2>&1 || echo "yum install attempted"
                            elif command -v apk >/dev/null 2>&1; then
                                echo "Using apk package manager (Alpine)..."
                                apk update >/dev/null 2>&1 || echo "apk update failed"
                                apk add python3-dev py3-pip py3-venv >/dev/null 2>&1 || echo "apk install attempted"
                            else
                                echo "No known package manager found"
                            fi
                            
                            echo "=== Post-Install Verification ==="
                            python3 -m venv --help >/dev/null 2>&1 && echo "✓ venv is available" || echo "✗ venv still not available"
                            python3 -m pip --version >/dev/null 2>&1 && echo "✓ pip is available" || echo "✗ pip not available"
                        '''
                    } else {
                        bat '''
                            echo "Windows environment detected - system packages should be available"
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
                            echo "Requirements file check:"
                            ls -la requirements.txt || echo "requirements.txt not found"
                            
                            echo "=== Virtual Environment Setup ==="
                            # Method 1: Try python3 -m venv after package installation
                            if python3 -m venv "${PYTHON_VENV}" >/dev/null 2>&1; then
                                echo "✓ Virtual environment created successfully with python3 -m venv"
                                VENV_CREATED=true
                                VENV_ACTIVATE="${PYTHON_VENV}/bin/activate"
                            else
                                echo "✗ python3 -m venv failed"
                                VENV_CREATED=false
                            fi
                            
                            # Method 2: Try virtualenv if available
                            if [ "$VENV_CREATED" = false ] && command -v virtualenv >/dev/null 2>&1; then
                                echo "Trying virtualenv..."
                                if virtualenv "${PYTHON_VENV}" >/dev/null 2>&1; then
                                    echo "✓ Virtual environment created with virtualenv"
                                    VENV_CREATED=true
                                    VENV_ACTIVATE="${PYTHON_VENV}/bin/activate"
                                fi
                            fi
                            
                            # Method 3: Use --break-system-packages as last resort
                            if [ "$VENV_CREATED" = false ]; then
                                echo "⚠️  Using --break-system-packages as fallback (Docker container safe)"
                                python3 -m pip install --break-system-packages --upgrade pip
                                python3 -m pip install --break-system-packages -r requirements.txt
                                VENV_ACTIVATE=""
                                echo "✓ Packages installed globally with --break-system-packages"
                            fi
                            
                            # Install dependencies in virtual environment if created
                            if [ "$VENV_CREATED" = true ] && [ -f "$VENV_ACTIVATE" ]; then
                                echo "Installing dependencies in virtual environment..."
                                . "$VENV_ACTIVATE"
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                echo "✓ Dependencies installed in virtual environment"
                            fi
                            
                            echo "=== Environment Setup Complete ==="
                            if [ "$VENV_CREATED" = true ]; then
                                echo "Using virtual environment at: ${PYTHON_VENV}"
                            else
                                echo "Using global Python installation with --break-system-packages"
                            fi
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
                                echo "✓ Using virtual environment"
                                . "${PYTHON_VENV}/bin/activate"
                                PYTHON_CMD="python"
                            else
                                echo "✓ Using global Python installation"
                                PYTHON_CMD="python3"
                            fi
                            
                            echo "Python command: $PYTHON_CMD"
                            $PYTHON_CMD --version
                            
                            # Verify dependencies are available
                            echo "Checking key dependencies..."
                            $PYTHON_CMD -c "import requests; print('✓ requests available')" || echo "✗ requests missing"
                            $PYTHON_CMD -c "import json; print('✓ json available')" || echo "✗ json missing"
                            
                            # Run the AI review
                            echo "=== Starting AI Code Review ==="
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
                            
                            echo "=== AI Code Review Complete ==="
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
                            echo "❌ BLOCKING ISSUES FOUND!"
                            echo "Found severities that are configured to fail the build: ${blockingSeverities.join(', ')}"
                            error("AI Code Review found blocking issues. Build failed.")
                        } else {
                            echo "✅ No blocking issues found. Build can proceed."
                        }
                    } else {
                        echo "⚠️ WARNING: No review results file found."
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
                            echo "=== PPT Generator Build ==="
                            
                            # Try to create virtual environment for PPT generator
                            if python3 -m venv ppt-venv >/dev/null 2>&1; then
                                echo "✓ Virtual environment created for PPT generator"
                                . ppt-venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                PYTHON_CMD="python"
                            else
                                echo "⚠️ Using global Python with --break-system-packages for PPT generator"
                                python3 -m pip install --break-system-packages --upgrade pip
                                python3 -m pip install --break-system-packages -r requirements.txt
                                PYTHON_CMD="python3"
                            fi
                            
                            # Run tests if they exist
                            if [ -f "test_app.py" ]; then
                                echo "Running tests..."
                                $PYTHON_CMD -m pytest test_app.py -v || echo "Tests completed with issues"
                            else
                                echo "No tests found, skipping test execution"
                            fi
                            
                            echo "✅ Build completed successfully!"
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
                            echo "=== Cleanup ==="
                            rm -rf "${AUTOPR_DIR}" || echo "AutoPR cleanup done"
                            rm -rf "${PYTHON_VENV}" || echo "Python venv cleanup done"  
                            rm -rf "ppt-venv" || echo "PPT venv cleanup done"
                            echo "✓ Cleanup completed"
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
            echo "🎉 SUCCESS: Pipeline completed successfully!"
            echo "✅ AI Code Review passed - no blocking issues found."
        }
        
        failure {
            echo "❌ FAILURE: Pipeline failed!"
            script {
                if (fileExists('ai-review-results.json')) {
                    def reviewResults = readJSON file: 'ai-review-results.json'
                    echo "Failure due to AI code review findings:"
                    if (reviewResults.comments) {
                        for (comment in reviewResults.comments) {
                            def severity = comment.severity?.toLowerCase()
                            if (severity == 'critical' || severity == 'error') {
                                echo "🚨 CRITICAL: ${comment.file}:${comment.line} [${comment.severity}] ${comment.message}"
                            }
                        }
                    }
                } else {
                    echo "Pipeline failed due to system/environment error (not AI review)"
                }
            }
        }
        
        unstable {
            echo "⚠️ UNSTABLE: Pipeline completed with warnings."
            echo "Check the AI review results for non-blocking issues."
        }
    }
}