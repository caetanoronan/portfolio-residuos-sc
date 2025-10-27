# Copilot Instructions - [PROJECT NAME]

## Project Overview
[Brief description of the project - 1-2 sentences about what it does and its main purpose]

**Key Outputs:** [List main deliverables: web apps, APIs, datasets, reports, etc.]

## Architecture & Data Flow

### Core Pipeline Pattern
[Describe the main workflow/pipeline of your project - the sequence of operations]

1. **[Stage 1]** → [Input/Action/Output]
2. **[Stage 2]** → [Input/Action/Output]
3. **[Stage 3]** → [Input/Action/Output]
4. **[Stage 4]** → [Input/Action/Output]
5. **[Stage 5]** → [Input/Action/Output]

**Example:** See `[key_script.py]` (lines X-Y) for canonical implementation.

### Directory Structure
```
project_root/
├── src/                          # Source code
│   ├── main.py                  # Entry point
│   └── utils/                   # Helper modules
├── data/                         # Input data (not in Git)
│   └── raw/                     # Original datasets
├── outputs/                      # Generated artifacts
│   ├── *.html                   # Reports/visualizations
│   ├── *.csv                    # Processed data
│   └── *.json                   # API responses/configs
├── tests/                        # Unit/integration tests
├── docs/                         # Documentation
└── README.md                     # Project documentation
```

**Convention:** [State your main conventions - e.g., "Never modify source data", "All outputs go to outputs/", etc.]

## Critical Developer Workflows

### Running the Application
```bash
# Setup environment
[command to create/activate virtual environment]

# Install dependencies
[pip install -r requirements.txt / npm install / etc.]

# Run main application
[python src/main.py / npm start / etc.]

# Run tests
[pytest / npm test / etc.]
```

**Testing Strategy:** [Describe how validation works - automated tests, manual checks, etc.]

### [Key Workflow 2 - e.g., "API Integration"]
[Describe important patterns for common tasks]
1. **[Step 1]:** [Description]
2. **[Step 2]:** [Description]
3. **[Step 3]:** [Description]

**Why?** [Explain rationale for this approach]

### Git Workflow
```bash
# Standard commit pattern
git add [files]
git commit -m "[prefix]: [description in appropriate language]"
git push origin main
```

**Convention:** Commit messages use prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Project-Specific Conventions

### [Critical Convention 1 - e.g., "Code Style"]
[Describe NON-NEGOTIABLE standards]
- **[Aspect 1]:** [Requirement and rationale]
- **[Aspect 2]:** [Requirement and rationale]
- **[Aspect 3]:** [Requirement and rationale]

**Implementation:** See `[reference_file.py]` (lines X-Y) for examples.

### [Critical Convention 2 - e.g., "Data Handling"]
1. **[Rule 1]** - [Description]
2. **[Rule 2]** - [Description]
3. **[Rule 3]** - [Description]
4. **[Rule 4]** - [Description]

**Example:**
```python
# [Show code example demonstrating the pattern]
```

### [API/External Service] Usage
**Pattern:** [Describe retry/fallback strategy if applicable]

```python
# Primary: [URL or method]
# Fallback: [Alternative URL or method]
# Last resort: [Final fallback]
```

**Why?** [Explain reasoning - reliability, performance, etc.]

### Output Standards
[Describe consistent formatting/structure for outputs]
1. **[Element 1]:** [Description]
2. **[Element 2]:** [Description]
3. **[Element 3]:** [Description]
4. **[Element 4]:** [Description]

**[Platform] support:** [Describe responsive/adaptive requirements if applicable]

## Integration Points

### External APIs/Services
- **[API/Service 1]:** [Description and endpoint]
- **[API/Service 2]:** [Description and endpoint]
- **[API/Service 3]:** [Description and endpoint]

**Rate limits:** [Document known limits or state "None documented"]

### Dependencies
```[language]
# [Category 1 - e.g., "Core"]
[package1]  # [version] - [purpose]
[package2]  # [version] - [purpose]

# [Category 2 - e.g., "Testing"]
[package3]  # [version] - [purpose]

# [Category 3 - e.g., "Dev tools"]
[package4]  # [version] - [purpose]
```

**Dependency management:** [Location of requirements file, lock file strategy, etc.]

## Common Gotchas

### 1. [Gotcha Title]
[Description of the issue/quirk]
```bash
# How to handle it correctly
[command or code example]
```

### 2. [Gotcha Title]
[Description] - [Explanation of why this happens]

### 3. [Gotcha Title]
[Description]. Do NOT [what to avoid] - [explain consequences]

### 4. [Performance/Size Considerations]
- [Issue 1]: [Details and mitigation]
- [Issue 2]: [Details and mitigation]

### 5. [Platform-Specific Issues]
[Description of OS/environment-specific behavior and how to handle it]

## Key Files to Reference

- **`[critical_file_1.ext]`** ([lines]) - [What makes it important: patterns, complexity, canonical example]
- **`[critical_file_2.ext]`** ([lines]) - [Key aspects to learn from this file]
- **`[critical_file_3.ext]`** ([lines]) - [Important patterns or features]
- **`[README.md]`** - [What type of documentation it contains]

## When Making Changes

1. **[Change Type 1]:** [Pattern to follow or file to reference]
2. **[Change Type 2]:** [What to check first before implementing]
3. **[Change Type 3]:** [Strategy for this type of modification]
4. **[Change Type 4]:** [Where to put new outputs/files]
5. **[Documentation Updates]:** [When and what to update]

**Testing Checklist:**
- [ ] [Test requirement 1]
- [ ] [Test requirement 2]
- [ ] [Test requirement 3]
- [ ] [Test requirement 4]

---

## Template Usage Instructions

**This is a TEMPLATE file. To use it:**

1. **Copy** to `.github/copilot-instructions.md` in your new project
2. **Replace** all `[PLACEHOLDER]` sections with project-specific information:
   - `[PROJECT NAME]` - Your project's name
   - `[Brief description...]` - Actual project description
   - `[Stage 1]`, `[Stage 2]`, etc. - Your actual pipeline stages
   - `[key_script.py]` - Your actual important files
   - All other bracketed placeholders
3. **Remove** sections that don't apply to your project
4. **Add** new sections specific to your domain/technology
5. **Delete** these "Template Usage Instructions" when done
6. **Commit** to Git so Copilot can use it automatically

**Sections to customize first (priority order):**
1. Project Overview
2. Directory Structure
3. Running the Application
4. Project-Specific Conventions
5. Common Gotchas

**Optional sections (add if relevant):**
- Security considerations
- Performance optimization patterns
- Deployment procedures
- Environment-specific configurations
- Team conventions (code review, PR templates, etc.)

---

**Last Updated:** [Date] | **Language:** [Primary language for code/comments] | **Deployment:** [Platform/method]
