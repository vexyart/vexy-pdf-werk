##### 4. Create Basic Git Configuration

```bash
## 21. Create .gitignore
cat > .gitignore << 'EOF'
## 22. Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

## 23. Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

## 24. IDE
.vscode/
.idea/
*.swp
*.swo
*~

## 25. Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

## 26. Jupyter
.ipynb_checkpoints

## 27. OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

## 28. Project specific
output/
temp/
*.pdf
*.epub
test_output/
logs/
*.log

## 29. Configuration (don't commit secrets)
config.local.toml
.env.local

## 30. External integrations
external/ai-inference/*.key
external/datalab/*.key
EOF
```

##### 5. Install Dependencies and Verify Setup

```bash
## 31. Install core dependencies
uv add fire rich loguru platformdirs pydantic pathvalidate unicode-slugify pypdf pikepdf pyyaml toml requests aiohttp ebooklib

## 32. Install development dependencies
uv add --dev pytest pytest-cov pytest-asyncio ruff mypy pre-commit

## 33. Verify the installation
uv run python -c "import vexy_pdf_werk; print(f'VPW version: {vexy_pdf_werk.__version__}')"

## 34. Test the CLI
uv run vpw --help
uv run vpw version

## 35. Test basic functionality (should show "not implemented" message)
echo "Test PDF" > test.pdf
uv run vpw process test.pdf --verbose
rm test.pdf
```
