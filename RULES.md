# Development Workflow Rules

## Core Principles

### 1. Incremental Changes

- Make ONE change at a time
- Don't fix multiple issues in parallel
- Avoid creating "a big mess" by jumping between files

### 2. Documentation-Driven Development

- After each change that improves test results, document it in PROGRESS.md
- Document what was changed AND why
- Include error messages, root causes, and solutions

### 3. Commit After Each Success

- After documenting in PROGRESS.md, commit the changes
- Only move to the next issue after committing
- Keep commits focused and atomic

### 4. Testing Protocol

- **User runs all tests, not Claude**
- User will execute `./run_tests.sh`
- Claude waits for test results before proceeding
- Claude analyzes test results when shared

## Workflow Steps

For each issue:

1. **User runs tests** and shares results (test_results.txt)
2. **Read test output** to identify the error
3. **Analyze the problem**:
   - Read relevant test file
   - Read relevant source code
   - Understand the root cause
4. **Add debug prints** (if needed) to pinpoint the exact issue:
   - Add prints to test to show expected vs actual values
   - Add prints to source code to trace execution
   - User runs tests again with debug output
5. **Make the fix** in code
6. **Remove debug prints** after fixing
7. **Update PROGRESS.md** with:
   - Problem description
   - Root cause analysis
   - Solution applied
   - Files modified
   - Result/outcome
8. **User runs tests** to verify the fix
9. **DO NOT stage or commit until tests pass**
10. **Once tests pass**, stage files with git add
11. **Commit if successful**
12. **Move to next issue**

**IMPORTANT**: Never stage changes with `git add` until the user confirms tests are passing!

### Debug Print Strategy

When adding debug prints:
- Add prints at key decision points
- Show input values, intermediate results, and output values
- Label prints clearly: `print("\n=== DEBUG: TestName ===")`
- Use f-strings for clarity: `print(f"Variable: {var}")`
- Always remove debug prints after issue is resolved

## Commit Message Guidelines

Based on user preferences:

- No references to Claude or Anthropic
- No "Generated with Claude Code" footers
- Focus on the technical change
- Keep it concise and clear

## Testing

- Tests are run by the user only
- Test command: `./run_tests.sh`
- Test results saved to: `test_results.txt`
- Never push unless user explicitly asks

## Branch Strategy

- Never commit to main/master branch
- Current working branch: `toavina/update-python`
- Create feature branches as needed

## Documentation Files

- **PROGRESS.md**: Detailed log of all changes, similar to PROGRESS_CKANEXT_VALIDATION.md
- **RULES.md**: This file - workflow and development rules
- Keep both updated as work progresses

## Files to Never Commit

The following files are for local development only and should NOT be committed:

- `RULES.md` - Local workflow documentation
- `run_tests.sh` - Local test runner script
- `.actrc` - Local act configuration
- `test_results_new.txt` - Test output files

## Pattern to Follow

This project follows the same methodical approach used in ckanext-validation migration:

- Batch-by-batch fixes
- Detailed progress tracking
- One issue at a time
- Thorough documentation of root causes
- Clear before/after comparisons
