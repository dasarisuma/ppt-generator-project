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

- âœ… **PASS**: No critical or error-level issues found
- âŒ **FAIL**: Critical or error-level issues found - PR is blocked
- âš ï¸ **UNSTABLE**: Warnings found but PR can proceed

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
