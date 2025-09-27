# 🔒 DJ AI System - Security Best Practices

## 🚨 API Key Security - CRITICAL

**NEVER commit API keys to GitHub!** API keys exposed on GitHub are automatically invalidated for security.

## 🛡️ Secure Setup Process

### 1. Quick Secure Setup
```bash
# Run the secure setup script
python setup_secure.py
```

### 2. Manual Setup
```bash
# Copy the template
cp .env.example .env

# Edit .env with your real API key
nano .env

# Set secure permissions (Unix/macOS)
chmod 600 .env
```

### 3. Verify Security
```bash
# Check .env is in .gitignore
grep ".env" .gitignore

# Verify file permissions
ls -la .env
# Should show: -rw------- (owner read/write only)
```

## 🔍 Security Checklist

### Before Every Commit
- [ ] ✅ `.env` file is in `.gitignore`
- [ ] ✅ No API keys in source code
- [ ] ✅ No hardcoded secrets anywhere
- [ ] ✅ Run: `git status` to check staged files
- [ ] ✅ Review: `git diff --cached` before commit

### Environment Variables Best Practices
```bash
# ✅ CORRECT - Load from environment
api_key = os.getenv('OPENROUTER_API_KEY')

# ❌ WRONG - Hardcoded in source
api_key = "sk-or-v1-12345..."  # NEVER DO THIS!
```

### File Security
```bash
# Protected files (NEVER commit these)
.env                    # Environment variables
.env.local              # Local overrides
*.key                   # Any key files
*api_key*               # Files with 'api_key' in name
*secret*                # Files with 'secret' in name
*password*              # Files with 'password' in name
credentials.json        # Credential files
secrets.json            # Secret files
```

## 🚨 Emergency Response

### If API Key is Exposed on GitHub

1. **Immediate Action**
   ```bash
   # The key is automatically invalidated by GitHub/OpenRouter
   # Get a new key immediately from https://openrouter.ai
   ```

2. **Update System**
   ```bash
   # Update .env with new key
   nano .env

   # Test the new key
   python setup_secure.py
   ```

3. **Clean Git History** (if needed)
   ```bash
   # WARNING: This rewrites Git history - use with caution
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all

   # Force push to clean remote history
   git push origin --force --all
   ```

## 🔐 Advanced Security

### GitHub Actions Secrets
For CI/CD pipelines, use GitHub repository secrets:

1. Go to: `Repository > Settings > Secrets and variables > Actions`
2. Click: `New repository secret`
3. Name: `OPENROUTER_API_KEY`
4. Value: Your API key
5. Use in workflow: `${{ secrets.OPENROUTER_API_KEY }}`

### Environment-Specific Keys
```bash
# Development
OPENROUTER_API_KEY_DEV=sk-or-v1-dev-key...

# Production
OPENROUTER_API_KEY_PROD=sk-or-v1-prod-key...

# Testing
OPENROUTER_API_KEY_TEST=sk-or-v1-test-key...
```

### Secret Scanning Tools
```bash
# Install git-secrets to prevent commits with secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && make install

# Configure for your repo
git secrets --register-aws
git secrets --install
git secrets --scan
```

## 📋 Security Validation Commands

### Check Current Security Status
```bash
# 1. Verify .env is ignored
git check-ignore .env
# Should output: .env

# 2. Check for exposed secrets in history
git log --oneline | head -10

# 3. Scan for potential secrets
grep -r "sk-or-v1" . --exclude-dir=.git --exclude="*.md"
# Should only find .env (if any)

# 4. Test API key loading
python -c "from config import get_config; print('API Key loaded:', bool(get_config().openrouter_api_key))"
```

### Pre-commit Security Check
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -q ".env"; then
    echo "❌ BLOCKED: Attempting to commit .env file!"
    echo "🔒 This file contains secrets and must never be committed."
    exit 1
fi

# Check for API keys in staged files
if git diff --cached | grep -q "sk-or-v1-"; then
    echo "❌ BLOCKED: API key found in staged changes!"
    echo "🔒 Remove API keys from source code."
    exit 1
fi
```

## 🛠️ Development Workflow

### Safe Development Process
1. **Always start with**: `python setup_secure.py`
2. **Before coding**: Verify `.env` exists and is ignored
3. **Before commits**: Run security checks
4. **Use environment variables**: Never hardcode secrets
5. **Regular audits**: Scan for accidentally committed secrets

### Team Collaboration
```bash
# Share the template (safe)
git add .env.example
git commit -m "Add environment template"

# Never share the actual secrets
# Each developer runs: python setup_secure.py
```

## 📞 Security Support

### If You Need Help
1. **Check**: This SECURITY.md file
2. **Run**: `python setup_secure.py` for guided setup
3. **Verify**: Security checklist above
4. **Test**: All validation commands

### Reporting Security Issues
- **Email**: (if you find vulnerabilities in the codebase)
- **GitHub Issues**: For security questions (never include actual keys!)

---

## 🎯 Remember

**🔒 Security is not optional - it's essential for protecting your API access and preventing abuse.**

**💡 When in doubt, run `python setup_secure.py` to ensure your setup is secure.**