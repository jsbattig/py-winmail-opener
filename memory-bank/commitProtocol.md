# Commit and Push Protocol

When a user requests to commit and push changes:

1. ALWAYS run the pre-commit checks first using the `./scripts/pre-commit.sh` script.
2. If any checks fail:
   - Show the user the full output of the failed checks
   - Ask if they still want to proceed with the commit and push despite the issues
   - Recommend fixing the issues before proceeding
3. Only proceed with the commit and push if:
   - All checks pass, OR
   - The user explicitly confirms they want to proceed despite the failures
4. When committing, include information about whether checks passed or were overridden

Example response when checks fail:
```
I ran the pre-commit checks and found some issues:

[Output of failed checks]

Would you like me to:
1. Help you fix these issues before committing
2. Proceed with the commit and push anyway
3. Skip the commit for now

I recommend option 1 to maintain code quality.
```

This protocol ensures code quality while respecting user autonomy.