# JIRA Text Data Analysis

LLM-assisted sentiment analysis to identify top delay themes from October JIRA issues delayed to November.

## Project Goal

Analyze JIRA issue comments to identify the top 5 and top 10 actionable themes causing October-to-November delays. Results will inform managerial decisions to improve team processes and reduce future delays.

## Features

- CSV data ingestion from JIRA exports
- OpenAI GPT-powered sentiment analysis
- Theme clustering for delay root causes
- Actionable insights from a managerial perspective
- Visual reports and data exports

## Project Structure

```
Text_Analysis/
├── data/
│   ├── raw/                    # Place your JIRA CSV files here
│   └── processed/              # Cleaned and processed data
├── notebooks/
│   └── jira_delay_analysis.ipynb  # Main analysis notebook
├── src/
│   ├── data_loader.py          # Data loading utilities
│   ├── llm_analyzer.py         # OpenAI API integration
│   └── theme_clustering.py     # Theme extraction and clustering
├── reports/                    # Generated visualizations and reports
├── config/                     # Configuration files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- OpenAI API key
- JIRA CSV export with comments

### 2. Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Data Preparation

1. Export your JIRA data to CSV format
2. Place CSV file(s) in `data/raw/` directory
3. Ensure CSV contains these columns:
   - Issue Key/ID
   - Issue Summary
   - Created Date
   - Resolved/Closed Date
   - Comments
   - Status
   - Any other relevant fields

### 5. Run Analysis

```bash
# Start Jupyter Notebook
jupyter notebook

# Open notebooks/jira_delay_analysis.ipynb
# Follow the notebook steps
```

## Analysis Workflow

1. **Data Loading**: Import JIRA CSV and validate data quality
2. **Data Cleaning**: Filter October issues delayed to November
3. **Comment Extraction**: Parse and prepare comment text
4. **Sentiment Analysis**: Use GPT to analyze comment sentiment
5. **Theme Extraction**: Identify delay reasons from comments
6. **Clustering**: Group similar themes into actionable categories
7. **Ranking**: Identify top 5 and top 10 delay themes
8. **Reporting**: Generate visualizations and management reports

## Expected Outputs

- Top 5 delay themes with frequency and impact
- Top 10 delay themes with detailed breakdown
- Sentiment distribution charts
- Theme cluster visualizations
- Actionable recommendations CSV for management
- Executive summary report

## Usage Tips

- Start with a sample of data to test the pipeline
- Adjust GPT prompts in `src/llm_analyzer.py` for better theme extraction
- Monitor API usage to stay within OpenAI rate limits
- Review and validate LLM outputs for accuracy

## Dependencies

Key libraries:
- `pandas` - Data manipulation
- `openai` - GPT API integration
- `matplotlib/seaborn` - Data visualization
- `scikit-learn` - Clustering algorithms
- `jupyter` - Interactive analysis

See [requirements.txt](requirements.txt) for complete list.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | gpt-4-turbo-preview |
| `OPENAI_TEMPERATURE` | Response randomness (0-1) | 0.3 |
| `OPENAI_MAX_TOKENS` | Max response length | 2000 |

## Troubleshooting

**Issue**: API rate limit errors
- **Solution**: Reduce `REQUESTS_PER_MINUTE` in `.env` or add delays between calls

**Issue**: Poor theme clustering
- **Solution**: Refine GPT prompts, adjust clustering parameters, or increase sample size

**Issue**: Missing data columns
- **Solution**: Check JIRA export settings and ensure all required fields are included

## Contributing

This is an internal analysis project. For improvements:
1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit for review

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

For questions or issues, contact the project maintainer.

---

**Last Updated**: 2025-11-19
