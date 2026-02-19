# pyOpenSci Package Dashboard Development Workflow

## Overview
This guide covers the development workflow for the package-activity.qmd dashboard located in metrics/pyos-packages/. This dashboard specifically focuses on **identifying packages that have been inactive for 6+ months** to help the pyOpenSci team prioritize maintenance efforts.

## File Purpose
The `package-activity.qmd` creates a focused dashboard that shows:
- **Inactive Package Identification** - Primary focus on packages needing attention (6+ months without commits)
- **Package Activity Timeline** - All packages sorted by last commit date for context
- **Maintenance Prioritization** - Clear separation between active and inactive packages
- **Summary Statistics** - Quick overview of package health across the ecosystem

## Prerequisites

### System Requirements
- **Python**: 3.9+ (3.10+ recommended for full functionality)
- **Quarto**: Installed and accessible via command line
- **Git**: For version control

### Required Python Packages
```bash
pandas>=1.5.0
altair>=4.2.0
plotly>=5.0.0
itables>=1.0.0
jupyter>=1.0.0
pyarrow>=10.0.0
```

### Data Dependencies
- `_data/package_data.csv` - Contains package metadata with GitHub metrics
- GitHub metadata in `gh_meta` column with fields:
  - `last_commit` - Date of last repository commit
  - `stargazers_count` - Number of GitHub stars
  - `forks_count` - Number of repository forks
  - `contrib_count` - Number of contributors
  - `open_issues_count` - Number of open issues

## Development Environment Setup

### Recommended: Nox-Based Development (Preferred)
This project uses Nox for automated environment management and task execution.

```bash
# Navigate to project directory
cd /path/to/metrics

# Install nox (can be installed globally or in a base environment)
pip install nox

# Verify Quarto installation
quarto --version

# Nox will handle the rest automatically
```

### Alternative: Manual Python Setup

#### Option 1: Python 3.9 Setup (Current Working)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install pandas altair plotly itables jupyter pyarrow
```

#### Option 2: Python 3.10+ Setup (Full Functionality)
```bash
# Install Python 3.10+ (using pyenv example)
pyenv install 3.10.12
pyenv local 3.10.12

# Create virtual environment
python -m venv venv310
source venv310/bin/activate

# Install all dependencies including pyosmeta
pip install -r requirements.txt
```

## Development Workflow

### Nox-Based Workflow (Recommended)

#### 1. Making Changes
```bash
# Navigate to project directory
cd /path/to/metrics

# Open the dashboard file for editing
# Edit: pyos-packages/package-activity.qmd
```

#### 2. Testing Changes with Nox
```bash
# Option A: Build static HTML (faster for testing)
nox -s html

# View output
open _site/pyos-packages/package-activity.html
```

#### 3. Live Development with Nox
```bash
# Option B: Live preview with auto-reload (best for development)
nox -s serve

# This will:
# - Install all dependencies automatically
# - Start quarto preview
# - Open browser with live reload
# - Watch for file changes and rebuild automatically
```

### Manual Workflow (Alternative)

#### 1. Making Changes
```bash
# Activate your virtual environment
source venv/bin/activate  # or source venv310/bin/activate

# Edit: pyos-packages/package-activity.qmd
```

#### 2. Testing Changes Manually
```bash
# Render single dashboard (fast testing)
quarto render pyos-packages/package-activity.qmd

# View output
open _site/pyos-packages/package-activity.html
```

#### 3. Full Site Testing (Optional)
```bash
# Render entire site (slower, requires all dependencies)
quarto render

# Preview with live reload
quarto preview
```

### 4. Validation Checklist
- [ ] Dashboard renders without errors
- [ ] **PRIMARY**: Inactive packages table shows packages with 6+ months no commits
- [ ] Inactive packages table is prominently displayed and easy to identify
- [ ] Value boxes highlight the count of inactive packages
- [ ] All packages table provides context (sorted by last commit date)
- [ ] Interactive features work (sorting, pagination)
- [ ] No broken links or missing data
- [ ] Dashboard clearly serves its purpose: identifying packages needing attention

## Nox Sessions Available

### `nox -s html`
- **Purpose**: Build static HTML for the entire site
- **Use case**: Testing, CI/CD, production builds
- **Output**: Static files in `_site/` directory
- **Dependencies**: Automatically installs requirements.txt and pyosmetrics_pkg

### `nox -s serve`
- **Purpose**: Live development server with auto-reload
- **Use case**: Active development, real-time preview
- **Features**:
  - Watches for file changes
  - Automatically rebuilds on changes
  - Opens browser with live preview
  - Hot reload for immediate feedback

### Nox Configuration
The project uses `nox.options.reuse_existing_virtualenvs = True` for faster subsequent runs.

## File Structure Understanding

### Dashboard Layout
```
## Row {height=0%}     - Data processing section
## Row {height=5%}     - Summary value boxes (total, active, INACTIVE counts)
## Row {height=45%}    - All packages table (sorted by last commit for context)
## Row {height=45%}    - MAIN FOCUS: Inactive packages table (6+ months) ⭐
```

### Key Code Sections

#### Data Loading & Processing
```python
# Lines 14-27: Import statements and setup
# Lines 28-36: Load and parse package data
# Lines 37-60: Extract GitHub metadata fields
```

#### Primary Feature: Inactive Package Identification
```python
# Lines 77-85: MAIN TABLE - Inactive packages (6+ months without commits)
# This is the primary purpose of the dashboard
```

#### Supporting Features
```python
# Lines 61-75: Context table - All packages sorted by last commit date
# Lines 87-120: Summary statistics highlighting inactive package count
```

## Common Development Tasks

### Adding New Metrics
1. **Extract from gh_meta**: Add new field extraction in data processing section
2. **Create visualization**: Add new chart in appropriate row section
3. **Update tables**: Include new field in table displays
4. **Test rendering**: Verify new metrics display correctly

### Modifying Table Columns
1. **Locate table definition**: Find the relevant `show()` function call
2. **Update column selection**: Modify the DataFrame column list
3. **Adjust column names**: Update display names if needed
4. **Test interactivity**: Ensure sorting/filtering still works

### Changing Time Thresholds
1. **Find threshold definition**: Locate `timedelta(days=180)` for 6-month threshold
2. **Update calculation**: Modify days value as needed
3. **Update documentation**: Change titles/descriptions to match new threshold
4. **Verify logic**: Test with different date ranges

### Adding New Visualizations
1. **Choose location**: Select appropriate row section
2. **Create chart code**: Use plotly.express for consistency
3. **Apply styling**: Match existing color schemes and formatting
4. **Add title**: Use `#| title:` directive for chart titles

## Troubleshooting Guide

### Common Issues

#### "Module not found" errors
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip install [missing-package]
```

#### "No such file or directory" for data
```bash
# Solution: Verify data file exists
ls _data/package_data.csv

# Check current working directory in code
# Ensure path: Path.cwd().parents[0] / "_data" / "package_data.csv"
```

#### Quarto rendering fails
```bash
# Solution: Check Quarto installation
which quarto
quarto check

# Verify Python kernel
jupyter kernelspec list
```

#### Empty or broken tables
```bash
# Solution: Check data processing
# Verify gh_meta column parsing
# Ensure DataFrame columns exist before table creation
```

### Performance Issues
- **Slow rendering**: Use `maxBytes=0` in `show()` for large datasets
- **Memory usage**: Consider data filtering for very large package lists
- **Chart loading**: Reduce data points in visualizations if needed

## Best Practices

### Code Organization
- Keep data processing at the top
- Group related visualizations in same rows
- Use consistent variable naming
- Add comments for complex calculations

### Testing
- Always test individual dashboard rendering first
- Verify with different data scenarios
- Check responsive design on different screen sizes
- Test interactive features thoroughly

### Documentation
- Update this workflow guide when making structural changes
- Document any new dependencies or requirements
- Note any breaking changes or migration steps

## Contributing Changes

### Before Submitting
1. Test dashboard rendering locally
2. Verify all interactive features work
3. Check that no new dependencies are required
4. Ensure code follows existing patterns

### Commit Guidelines
- Use descriptive commit messages
- Reference related issues
- Include testing notes in PR description

## Related Files
- `_data/package_data.csv` - Source data
- `_quarto.yml` - Site navigation configuration
- `pyos-packages/package-activity.qmd` - Standalone activity dashboard
- `requirements.txt` - Python dependencies

## Support
For questions about this workflow or dashboard development:
1. Check this documentation first
2. Review existing GitHub issues
3. Create new issue with specific problem details
4. Include error messages and environment details
