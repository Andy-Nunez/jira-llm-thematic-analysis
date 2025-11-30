# Project Context for Claude Code

## Project Overview

This is a **JIRA Text Data Analysis** project that uses LLM-assisted sentiment analysis to identify top delay themes from October JIRA issues that were delayed into November. The analysis aims to provide actionable insights for management to improve team processes and reduce future delays.

**Key Goal**: Identify the top 5 and top 10 actionable themes causing project delays through automated analysis of JIRA comments.

## Environment Preferences

**IMPORTANT**: This project runs on Windows. Always use **PowerShell** as the default shell for all command-line operations. Do not use bash unless explicitly requested.

## Current Dataset

- **Data File**: [JiraComments_FromJql.csv](JiraComments_FromJql.csv) (241 comments, 39 unique issues)
- **Average Comment Length**: ~276 characters (~70 words)
- **Total Text Volume**: ~66K characters
- **Time Period**: October 2025 issues delayed to November 2025

**CSV Structure:**
```
IssueKey, CommentId, Author, AuthorEmail, Created, Updated, Body
```

## Project Architecture

### Current Approach: Direct LLM Analysis

**Why this approach?**
- Dataset is small (241 comments)
- Total API cost: $0.25-0.50 per full analysis
- Processing time: ~2-12 minutes depending on batching
- Simple, maintainable, easy to debug

**Architecture Flow:**
```
JiraComments_FromJql.csv → Load & Filter →
Group by IssueKey (39 groups) →
Send to GPT-4 (1 call per issue) →
Extract Themes & Sentiment →
Cluster Similar Themes →
Rank Top 5/10 →
Generate Reports
```

**Optimization Strategy:**
- Group comments by `IssueKey` before sending to LLM
- Send all comments for one issue in a single API call
- Result: 39 API calls instead of 241 (6x more efficient)

### When to Consider Vector Database

Only implement FAISS/Pinecone/Chroma if:
- Dataset grows to 10,000+ comments
- API costs exceed $50-100 per analysis
- Need ongoing semantic search capabilities
- Processing same data repeatedly

**Current verdict**: Vector DB is overkill for this dataset size.

## Core Components

1. **Data Loading** ([src/data_loader.py](src/data_loader.py))
   - Loads [JiraComments_FromJql.csv](JiraComments_FromJql.csv)
   - Filters October → November delayed issues
   - Groups comments by IssueKey for efficient processing
   - Validates data quality and handles missing values

2. **LLM Analysis** ([src/llm_analyzer.py](src/llm_analyzer.py))
   - OpenAI GPT-4 API integration
   - Sends grouped comments per issue (39 API calls)
   - Extracts delay themes from comment text
   - Performs sentiment analysis
   - Prompt engineering for actionable insights

3. **Theme Clustering** ([src/theme_clustering.py](src/theme_clustering.py))
   - Groups similar themes using scikit-learn
   - Deduplicates LLM-generated themes
   - Clusters delay reasons into categories
   - Generates frequency and impact metrics

4. **Vector Store** ([src/vector_store.py](src/vector_store.py))
   - Currently unused for main workflow
   - Available for future scaling or experimentation
   - Can be used if dataset grows significantly

## Directory Structure

```
Text_Analysis/
├── JiraComments_FromJql.csv    # Main data file (241 comments)
├── data/
│   ├── raw/                    # Additional JIRA exports
│   └── processed/              # Cleaned/filtered data
├── notebooks/
│   └── jira_delay_analysis.ipynb  # Main analysis notebook
├── src/                        # Core Python modules
│   ├── data_loader.py          # CSV loading and grouping
│   ├── llm_analyzer.py         # OpenAI API integration
│   ├── theme_clustering.py     # Theme grouping
│   └── vector_store.py         # (unused, for future scaling)
├── reports/                    # Generated outputs
│   ├── top_5_critical_themes.csv
│   └── top_10_themes_summary.csv
├── config/                     # Configuration files
├── .env                        # Environment variables (not committed)
└── .env.example               # Template for environment setup
```

## Environment Setup

### Required Environment Variables

Create a `.env` file from `.env.example`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview  # Recommended for this task
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3          # Low = consistent, factual analysis
REQUESTS_PER_MINUTE=20          # Rate limiting
```

### Python Version & Dependencies

- **Python**: 3.9 or higher
- **Virtual Environment**: `.venv/` or `venv/`

**Key Dependencies:**
- `pandas`: CSV manipulation and grouping
- `openai`: GPT API for analysis
- `scikit-learn`: Theme clustering
- `matplotlib/seaborn/plotly`: Visualizations
- `jupyter/notebook`: Interactive analysis

Install: `pip install -r requirements.txt`

## Development Workflow

### Typical Analysis Session

1. **Ensure data file exists**: [JiraComments_FromJql.csv](JiraComments_FromJql.csv) in project root
2. **Activate environment**: `.venv\Scripts\activate` (Windows)
3. **Start Jupyter**: `jupyter notebook`
4. **Open notebook**: [notebooks/jira_delay_analysis.ipynb](notebooks/jira_delay_analysis.ipynb)
5. **Run analysis cells**:
   - Load CSV (241 comments)
   - Filter October → November delays
   - Group by IssueKey (39 groups)
   - Send to GPT-4 for theme extraction
   - Cluster and rank themes
   - Generate top 5/10 reports
6. **Review outputs**: Check `reports/` directory

### Common Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt

# Start Jupyter notebook
jupyter notebook

# Run code quality checks
black src/
flake8 src/
isort src/
```

## Analysis Strategy

### Efficient Processing (Group by Issue)

**Best Practice for This Dataset:**
```python
# Group comments by IssueKey first
grouped = df.groupby('IssueKey')['Body'].apply(list)

# Send all comments for one issue in single API call
for issue_key, comments in grouped.items():
    combined_text = "\n---\n".join(comments)
    themes = llm_analyze(combined_text)
```

**Result**: 39 API calls instead of 241
- **Cost savings**: Same cost, more context per call
- **Better analysis**: LLM sees full issue conversation
- **Processing time**: ~2-3 minutes

### LLM Prompt Engineering

**Recommended Prompt Structure** (in [src/llm_analyzer.py](src/llm_analyzer.py)):

```
Analyze these JIRA comments for issue {IssueKey} which was delayed from October to November.

Comments:
{combined_comments}

Extract:
1. Primary delay reason(s)
2. Sentiment (frustrated/neutral/positive)
3. Actionable theme (management perspective)

Output as JSON: {"themes": [...], "sentiment": "...", "root_cause": "..."}
```

**Settings:**
- Temperature: 0.3 (factual, consistent)
- Max tokens: 2000 (plenty for this dataset)
- Model: gpt-4-turbo-preview (best quality/price ratio)

## Data Format Details

### Input CSV Schema

| Column | Type | Description |
|--------|------|-------------|
| `IssueKey` | String | JIRA issue ID (e.g., SWIFT-7544) |
| `CommentId` | String | Unique comment identifier |
| `Author` | String | Comment author name |
| `AuthorEmail` | String | Author email address |
| `Created` | DateTime | Comment creation timestamp |
| `Updated` | DateTime | Last update timestamp |
| `Body` | String | Comment text (main analysis target) |

### Output Reports

**Generated in `reports/`:**
1. `top_5_critical_themes.csv` - Top 5 delay themes with frequencies
2. `top_10_themes_summary.csv` - Top 10 delay themes with details
3. Visualizations (bar charts, word clouds, sentiment distribution)

## Coding Conventions

### Style Guidelines

- **Formatter**: Black (line length 88)
- **Linter**: Flake8 (configured in [.flake8](.flake8))
- **Import Sorting**: isort
- Follow PEP 8 conventions

### Code Organization Principles

- Keep data loading logic in [src/data_loader.py](src/data_loader.py)
- Keep LLM interactions in [src/llm_analyzer.py](src/llm_analyzer.py)
- Keep clustering/ML in [src/theme_clustering.py](src/theme_clustering.py)
- Use notebook for exploratory analysis and workflow
- Export reusable functions to `src/` modules

### Error Handling

**Always handle:**
- Missing CSV file
- Empty comment bodies
- API rate limits (429 errors)
- API authentication failures
- Malformed JSON responses from LLM
- Network timeouts

## Performance & Cost Analysis

### Current Dataset (241 comments, 39 issues)

**Scenario 1: Direct (241 API calls)**
- Processing time: ~12 minutes
- API cost: ~$0.50
- Context per call: Limited

**Scenario 2: Grouped by Issue (39 API calls)** ✅ RECOMMENDED
- Processing time: ~2-3 minutes
- API cost: ~$0.25-0.50
- Context per call: Full issue conversation
- Better theme extraction

**Monitoring:**
- Log all API calls and token usage
- Track costs per analysis run
- Monitor for rate limit warnings

## Common Pitfalls & Solutions

### 1. Rate Limiting
**Problem**: OpenAI rate limits (20 RPM default)
**Solution**: Set `REQUESTS_PER_MINUTE=20` in `.env`, add delays between calls

### 2. Empty Comments
**Problem**: Some comments have no Body text
**Solution**: Filter out null/empty bodies before processing

### 3. Date Parsing
**Problem**: JIRA dates in various formats
**Solution**: Use pandas `pd.to_datetime()` with `errors='coerce'`

### 4. Theme Duplication
**Problem**: LLM generates similar themes with different wording
**Solution**: Use clustering in [src/theme_clustering.py](src/theme_clustering.py) to deduplicate

### 5. Long Comments
**Problem**: Some comments exceed token limits
**Solution**: Truncate or chunk comments >4000 chars

## Analysis Focus & Context

### Target Analysis

- **Period**: October 2025 → November 2025 delays
- **Data Source**: JIRA comment text (Body field)
- **Sample Issue**: SWIFT-7544, SWIFT-7543, etc.
- **Primary Question**: Why were these issues delayed?

### Common Delay Themes (Expected)

Based on sample data:
- Design/requirements not finalized
- Waiting for stakeholder approval
- Technical dependencies not ready
- Resource availability issues
- Testing/validation delays
- CRQ (Change Request) submission timing

### Analysis Audience

- **Primary**: Management/decision-makers
- **Goal**: Actionable insights to reduce future delays
- **Output Style**: Executive-friendly, data-driven, specific

## Git Workflow

- **Main Branch**: `master`
- **Current Status**: Active development
- **Recent Changes**:
  - Modified notebooks for thematic analysis
  - Updated [src/llm_analyzer.py](src/llm_analyzer.py)
  - Added [src/vector_store.py](src/vector_store.py) (currently unused)
  - Generated initial reports

**Don't Commit:**
- `.env` file (contains API keys)
- Large data files in `data/raw/`
- Notebook checkpoint files
- Generated reports (optional)

**Do Commit:**
- Source code (`src/`)
- Notebooks
- Configuration files
- Documentation

## Testing Strategy

### Before Full Analysis

1. **Test with sample** (5-10 comments first)
2. **Validate LLM output** (check theme quality)
3. **Review API costs** (monitor token usage)
4. **Check clustering** (themes make sense?)

### Quality Checks

- Manual review of top themes
- Cross-reference themes with actual comments
- Validate sentiment matches comment tone
- Ensure no PII leaked in outputs

## Future Scaling Considerations

**If dataset grows to 1,000+ comments:**
1. Consider batching (10-20 comments per call)
2. Implement caching for LLM results
3. Add progress bars (tqdm) for long runs

**If dataset grows to 10,000+ comments:**
1. Implement vector database (FAISS/Pinecone)
2. Use semantic clustering before LLM analysis
3. Consider local embeddings to reduce API costs
4. Implement parallel processing

**Current Status**: Dataset too small for these optimizations

## Troubleshooting

### Issue: API Authentication Failed
**Check**: `.env` file has correct `OPENAI_API_KEY`

### Issue: No themes extracted
**Check**: Comments have actual text in Body field, prompt is well-formed

### Issue: Clustering produces bad results
**Check**: LLM is returning consistent theme formats, increase clustering parameters

### Issue: High API costs
**Check**: Not sending same data multiple times, using grouped approach

### Issue: CSV won't load
**Check**: File encoding (UTF-8 with BOM), verify column names match schema

## Key Files Reference

- **Main Data**: [JiraComments_FromJql.csv](JiraComments_FromJql.csv)
- **Analysis Notebook**: [notebooks/jira_delay_analysis.ipynb](notebooks/jira_delay_analysis.ipynb)
- **LLM Integration**: [src/llm_analyzer.py](src/llm_analyzer.py)
- **Data Loading**: [src/data_loader.py](src/data_loader.py)
- **Theme Clustering**: [src/theme_clustering.py](src/theme_clustering.py)
- **Environment Config**: [.env.example](.env.example) (copy to `.env`)

## When Making Code Changes

### Before Modifying

1. Read existing code first
2. Understand current grouping strategy (by IssueKey)
3. Test with small sample data
4. Monitor API costs during testing

### Code Review Checklist

- [ ] Handles missing/null data gracefully
- [ ] API errors have retry logic
- [ ] LLM outputs are validated
- [ ] Grouped comments by IssueKey (not individual)
- [ ] Logging sufficient for debugging
- [ ] Follows existing code style

## Additional Resources

- **OpenAI API**: https://platform.openai.com/docs
- **Pandas Grouping**: https://pandas.pydata.org/docs/user_guide/groupby.html
- **scikit-learn Clustering**: https://scikit-learn.org/stable/modules/clustering.html

---

**Last Updated**: 2025-11-21
**Dataset Version**: JiraComments_FromJql.csv (241 comments, 39 issues)
**Recommended Architecture**: Direct LLM analysis with issue-level grouping
