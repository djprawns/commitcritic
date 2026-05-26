# 🔍 CommitCritic

**AI-powered terminal tool that analyzes commit message quality and helps developers write better commits.**

CommitCritic uses OpenAI's GPT models to review your Git commit history, score each commit, and provide actionable feedback. It can also help you write better commits by analyzing your staged changes and suggesting well-formatted commit messages.

---

## ✨ Features

- **📊 Analyze Mode** - Review existing commits with AI-generated critique
  - Score commits on a 1-10 scale
  - Identify vague, one-word, or poorly formatted commits
  - Get specific improvement suggestions
  - Works on local or remote repositories
  - **⚡ Parallel batch processing** for fast analysis

- **✍️ Write Mode** - Interactive commit message writer
  - Analyzes your staged changes (`git diff --staged`)
  - Generates conventional commit messages
  - Accept, edit, or cancel suggestions
  - Commits directly to git

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLI Layer                                    │
│                      (commit_critic.py)                                 │
│                                                                         │
│    ┌──────────────────┐              ┌──────────────────┐               │
│    │  analyze command │              │  write command   │               │
│    └────────┬─────────┘              └────────┬─────────┘               │
└─────────────┼────────────────────────────────┼──────────────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Git Module                                    │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │ Repository  │    │   Commit    │    │    Diff     │                  │
│  │  - clone    │    │  - sha      │    │  - staged   │                  │
│  │  - open     │    │  - message  │    │  - stats    │                  │
│  │  - commits  │    │  - author   │    │  - execute  │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI Agents                                      │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                      BaseAgent                                 │     │
│  │              (OpenAI client, JSON responses)                   │     │
│  └────────────────────────┬───────────────────────────────────────┘     │
│                           │                                             │
│           ┌───────────────┴───────────────┐                             │
│           ▼                               ▼                             │
│  ┌─────────────────┐            ┌─────────────────┐                     │
│  │ AnalyzerAgent   │            │  WriterAgent    │                     │
│  │                 │            │                 │                     │
│  │ • score_commit  │            │ • analyze_diff  │                     │
│  │ • batch_analyze │            │ • suggest_msg   │                     │
│  │ • create_report │            │ • generate      │                     │
│  └─────────────────┘            └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Rich Terminal Output                             │
│                                                                         │
│  [BAD] Bad Commits  [GEM] Good Commits  [STAT] Statistics  ┏━━Panels━━┓ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Git
- OpenAI API key

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/commitcritic.git
cd commitcritic

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `openai` | LLM API for commit analysis |
| `gitpython` | Git repository operations |
| `typer` | CLI framework |
| `rich` | Beautiful terminal output |
| `pydantic` | Data validation |
| `python-dotenv` | Environment variable management |

---

## 🚀 Usage

### Analyze Mode

Review commit history and get AI-powered feedback:

```bash
# Analyze last 50 commits in current repository
python commit_critic.py analyze

# Analyze specific number of commits
python commit_critic.py analyze --limit=100

# Analyze a remote repository
python commit_critic.py analyze --url="https://github.com/tiangolo/fastapi"

# Combine options
python commit_critic.py analyze --url="https://github.com/user/repo" --limit=25
```

**Example Output:**

```
🔍 Analyzing current repository...
Fetching last 50 commits from myproject...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💩 COMMITS THAT NEED WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "fixed bug"
Score: 2/10
Issue: Too vague - which bug? What was the impact?
Better: "fix(auth): resolve token expiration handling"

Commit: "wip"
Score: 1/10
Issue: No information about what's in progress
Better: Describe what you're working on

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 WELL-WRITTEN COMMITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "feat(api): add Redis caching layer"
Score: 9/10
Why it's good: Clear scope, specific changes, follows conventional commits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 YOUR STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average score:     4.2/10
Vague commits:     34 (68%)
One-word commits:  12 (24%)
Good commits:      8 (16%)
```

### Write Mode

Get AI-powered commit message suggestions for your staged changes:

```bash
# Stage your changes first
git add .

# Run interactive commit writer
python commit_critic.py write
```

**Example Output:**

```
✍️ Interactive Commit Writer

Analyzing staged changes... (12 files changed, +247 -89 lines)

Changes detected:
  • Modified authentication logic
  • Added error handling
  • Updated unit tests

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            Suggested commit message               ┃
┃                                                   ┃
┃  refactor(auth): improve error handling           ┃
┃                                                   ┃
┃  - Add specific error types for auth failures     ┃
┃  - Extract validation into separate methods       ┃
┃  - Update tests to cover edge cases               ┃
┃                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Press Enter to accept, or type your own message (empty to cancel):
> 

✓ Committed: a1b2c3d refactor(auth): improve error handling
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Model selection (default: gpt-4o)
OPENAI_MODEL=gpt-4o

# Optional: Default number of commits to analyze (default: 50)
DEFAULT_COMMIT_LIMIT=50

# Optional: Batch size for LLM calls (default: 10)
BATCH_SIZE=10
```

### CLI Options

| Command | Option | Description |
|---------|--------|-------------|
| `analyze` | `--url`, `-u` | Remote repository URL to analyze |
| `analyze` | `--limit`, `-n` | Number of commits to analyze |
| `write` | - | No options, analyzes staged changes |
| (global) | `--version`, `-v` | Show version information |
| (global) | `--help` | Show help message |

---

## 🔄 How It Works

### Analysis Flow (Parallel Processing)

```
1. User runs: python commit_critic.py analyze --limit=50
                        │
                        ▼
2. Git Module: Opens local repo or clones remote URL
                        │
                        ▼
3. Fetch commits: Gets last N commits (default: 50)
                        │
                        ▼
4. Batch creation: Groups commits into batches of 10
                        │
                        ▼
5. PARALLEL LLM Analysis: All batches processed concurrently
   ┌─────────────────────────────────────────────────────────┐
   │  Batch 1 ──────►  ┐                                     │
   │  Batch 2 ──────►  ├──► Results collected & merged       │
   │  Batch 3 ──────►  ┤                                     │
   │  Batch 4 ──────►  ┤    (max 5 concurrent by default)    │
   │  Batch 5 ──────►  ┘                                     │
   └─────────────────────────────────────────────────────────┘
                        │
                        ▼
6. Results: Categorized into good/bad, stats calculated
                        │
                        ▼
7. Display: Rich terminal output with panels and tables
```

**Performance:** Analyzing 50 commits takes ~10 seconds instead of ~50 seconds with sequential processing.

### Write Flow

```
1. User stages changes: git add <files>
                        │
                        ▼
2. User runs: python commit_critic.py write
                        │
                        ▼
3. Git Module: Gets staged diff (git diff --cached)
                        │
                        ▼
4. LLM Analysis: Analyzes diff to understand changes
   ┌─────────────────────────────────────────────┐
   │  Identifies:                                │
   │  • Type of changes (feat/fix/refactor/etc)  │
   │  • Scope/area affected                      │
   │  • Key modifications                        │
   └─────────────────────────────────────────────┘
                        │
                        ▼
5. LLM Generation: Creates conventional commit message
                        │
                        ▼
6. Interactive prompt: User accepts, edits, or cancels
                        │
                        ▼
7. Git commit: Executes commit with chosen message
```

---

## 📁 Project Structure

```
commitcritic/
├── commit_critic.py          # CLI entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .env                     # Your configuration (gitignored)
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py            # Settings management
│   │
│   ├── git/                 # Git operations
│   │   ├── __init__.py
│   │   ├── repository.py    # Repo clone/open/commits
│   │   ├── commit.py        # Commit data model
│   │   └── diff.py          # Staged diff & execute
│   │
│   ├── agents/              # AI agents
│   │   ├── __init__.py
│   │   ├── base.py          # Base agent (OpenAI client)
│   │   ├── analyzer.py      # Commit analysis agent
│   │   ├── writer.py        # Commit writer agent
│   │   └── prompts/         # LLM prompt templates
│   │       ├── __init__.py
│   │       ├── analyzer.py
│   │       └── writer.py
│   │
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── analysis.py      # CommitAnalysis, AnalysisReport
│   │   └── suggestion.py    # CommitSuggestion, ChangeSummary
│   │
│   └── cli/                 # CLI layer
│       ├── __init__.py
│       ├── commands.py      # analyze & write commands
│       └── formatter.py     # Rich terminal formatting
│
└── tests/                   # Unit tests
    ├── __init__.py
    └── fixtures/
        └── __init__.py
```

---

## 🎯 Commit Scoring Criteria

CommitCritic evaluates commits based on:

| Score | Quality | Description |
|-------|---------|-------------|
| 1-3 | Poor | One word, meaningless, or misleading |
| 4-5 | Below Average | Vague, missing context |
| 6-7 | Average | Acceptable but could be improved |
| 8-9 | Good | Clear, specific, well-formatted |
| 10 | Excellent | Perfect conventional commit with detailed body |

**Best Practices Evaluated:**
- ✅ Uses conventional commit format (`type(scope): subject`)
- ✅ Imperative mood ("add" not "added")
- ✅ Subject line under 50-72 characters
- ✅ Specific about what changed
- ✅ Includes context when needed (body with bullet points)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - feel free to use this project for any purpose.

---

## 🙏 Acknowledgments

- Built with [OpenAI GPT-4](https://openai.com/)
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Terminal UI by [Rich](https://rich.readthedocs.io/)
- Git operations via [GitPython](https://gitpython.readthedocs.io/)
