# GitHub Repository Setup Guide

This guide helps you properly configure your GitHub repository to avoid issues with bots, unwanted branches, and security problems.

## 🔒 Security Configuration

### 1. Remove Personal Access Tokens from Git URLs

**Issue**: Never include personal access tokens in git remote URLs as they can be exposed in logs.

**Fix Applied**: 
```bash
# Changed from (INSECURE):
# https://username:token@github.com/user/repo.git

# To (SECURE):
# https://github.com/user/repo.git
```

**For Authentication**: Use one of these secure methods:
- **SSH Keys** (Recommended): `git@github.com:user/repo.git`
- **GitHub CLI**: `gh auth login`
- **Git Credential Manager**: Stores tokens securely
- **Personal Access Token via Git Credential Helper**

### 2. Set up SSH Authentication (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Paste this in GitHub Settings > SSH and GPG keys

# Update remote to use SSH
git remote set-url origin git@github.com:gorantlatejamanikanta/operations-dashboard.git
```

## 🤖 Bot and Branch Management

### 1. Dependabot Configuration

**Issues Fixed**:
- Removed non-existent team reviewers/assignees
- Reduced frequency from weekly to monthly
- Limited open PRs from 10 to 3 per ecosystem
- Removed Docker and Terraform updates (not needed for this project)

**Current Configuration**:
- **Python deps**: Monthly, max 3 PRs
- **npm deps**: Monthly, max 3 PRs  
- **GitHub Actions**: Monthly, max 2 PRs
- **Major version updates**: Ignored for critical dependencies

### 2. Branch Protection Rules

Configure these in GitHub Settings > Branches:

```yaml
Branch Protection Rules for 'main':
- Require pull request reviews before merging
- Require status checks to pass before merging
  - Required checks: CI, Security Scan
- Require branches to be up to date before merging
- Require conversation resolution before merging
- Restrict pushes that create files larger than 100MB
- Allow force pushes: NO
- Allow deletions: NO
```

### 3. Repository Settings

Configure these in GitHub Settings > General:

```yaml
Features:
- Wikis: Disabled (use docs/ folder instead)
- Issues: Enabled
- Sponsorships: Disabled
- Projects: Enabled
- Preserve this repository: Enabled

Pull Requests:
- Allow merge commits: YES
- Allow squash merging: YES  
- Allow rebase merging: NO
- Always suggest updating pull request branches: YES
- Allow auto-merge: NO
- Automatically delete head branches: YES

Archives:
- Include Git LFS objects in archives: NO
```

## 🚫 Preventing Unwanted Branches

### 1. Limit Dependabot PRs

The updated `.github/dependabot.yml` now limits:
- Maximum 3 open PRs for Python dependencies
- Maximum 3 open PRs for npm dependencies
- Maximum 2 open PRs for GitHub Actions
- Monthly schedule instead of weekly

### 2. Auto-delete Merged Branches

Enable in GitHub Settings > General > Pull Requests:
- ✅ "Automatically delete head branches"

### 3. Branch Naming Convention

For any manual branches, use this convention:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `security/description` - Security fixes

## 🔐 Repository Secrets

Configure these secrets in GitHub Settings > Secrets and variables > Actions:

### Required for CI/CD
```
AZURE_CREDENTIALS          # Azure service principal
AZURE_CLIENT_ID            # Azure AD client ID
AZURE_TENANT_ID            # Azure AD tenant ID
AZURE_OPENAI_API_KEY       # Azure OpenAI API key
AZURE_OPENAI_ENDPOINT      # Azure OpenAI endpoint
```

### Required for Deployment
```
STAGING_DB_PASSWORD        # Staging database password
PRODUCTION_DB_PASSWORD     # Production database password
STAGING_SECRET_KEY         # Staging app secret key
PRODUCTION_SECRET_KEY      # Production app secret key
TERRAFORM_STORAGE_ACCOUNT  # Terraform state storage
TERRAFORM_CONTAINER        # Terraform state container
```

### Optional Integrations
```
SNYK_TOKEN                 # Snyk security scanning
SLACK_WEBHOOK_URL          # Slack notifications
SECURITY_SLACK_WEBHOOK_URL # Security notifications
CODECOV_TOKEN              # Code coverage reporting
```

## 📊 Repository Insights

### 1. Enable Security Features

In GitHub Settings > Security:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Code scanning alerts
- ✅ Secret scanning alerts

### 2. Code Analysis

The repository includes:
- **CodeQL Analysis**: Automated security scanning
- **Dependency Review**: PR-based dependency analysis
- **Security Scanning**: Multiple security tools in CI
- **Code Coverage**: Automated coverage reporting

## 🧹 Cleaning Up Existing Issues

### 1. Close Unwanted PRs

If you have many dependabot PRs:
```bash
# List all open PRs
gh pr list

# Close specific PRs
gh pr close PR_NUMBER --comment "Closing due to repository cleanup"

# Close all dependabot PRs (if needed)
gh pr list --author "app/dependabot" --json number --jq '.[].number' | xargs -I {} gh pr close {}
```

### 2. Delete Unwanted Branches

```bash
# List all branches
git branch -a

# Delete local branches
git branch -d branch-name

# Delete remote branches
git push origin --delete branch-name

# Prune deleted remote branches
git remote prune origin
```

### 3. Clean Git History (if needed)

**⚠️ WARNING**: Only do this if you haven't shared the repository yet.

```bash
# Remove sensitive data from history
git filter-branch --env-filter '
if [ "$GIT_AUTHOR_EMAIL" = "wrong-email@example.com" ]; then
    export GIT_AUTHOR_EMAIL="correct-email@example.com"
fi
' --all

# Force push (DANGEROUS - only if repository is private and not shared)
git push --force-with-lease origin main
```

## 📋 Repository Maintenance Checklist

### Weekly
- [ ] Review and merge dependabot PRs
- [ ] Check security alerts
- [ ] Review failed CI runs

### Monthly  
- [ ] Update dependencies manually if needed
- [ ] Review and rotate secrets
- [ ] Clean up merged branches
- [ ] Review repository settings

### Quarterly
- [ ] Security audit
- [ ] Performance review
- [ ] Documentation updates
- [ ] Backup verification

## 🚨 Troubleshooting

### Issue: Too Many Dependabot PRs
**Solution**: The updated dependabot.yml limits PRs to 3 per ecosystem

### Issue: Failed CI Runs
**Solution**: Check required secrets are configured properly

### Issue: Branch Protection Violations
**Solution**: Ensure all required status checks are passing

### Issue: Large Repository Size
**Solution**: Use Git LFS for large files, clean up old branches

## 📞 Getting Help

1. **GitHub Docs**: https://docs.github.com
2. **Git Documentation**: https://git-scm.com/doc
3. **Security Best Practices**: https://docs.github.com/en/code-security

## ✅ Verification

After applying these changes:

1. **Check Remote URL**: `git remote -v` (should not contain tokens)
2. **Test Push**: `git push origin main` (should work with proper auth)
3. **Verify Dependabot**: Check Settings > Security > Dependabot
4. **Check Secrets**: Verify all required secrets are configured
5. **Test CI**: Push a small change and verify CI runs successfully

Your repository should now be clean, secure, and properly configured!