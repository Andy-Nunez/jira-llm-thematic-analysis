# Processed Data Directory

This directory contains cleaned and processed data from the analysis.

## Generated Files

After running the analysis notebook, you'll find:

- `delay_themes_analysis.csv`: Full analysis results with themes, sentiment, and reasoning for each issue
- `cleaned_jira_data.csv`: Preprocessed JIRA data (optional)

## File Structure

### delay_themes_analysis.csv
Columns:
- `issue_key`: JIRA issue identifier
- `theme`: Identified delay theme category
- `sentiment`: Sentiment analysis result (positive/neutral/negative)
- `reasoning`: Brief explanation of the delay cause
- `raw_response`: Full GPT response (optional)

## Data Privacy

⚠️ **Important**: This directory is also ignored by git
- Processed data may still contain sensitive information
- Review before sharing externally
- Consider anonymizing issue keys if sharing results publicly

## Usage

These files can be used for:
- Further statistical analysis
- Dashboard creation
- Management reporting
- Trend analysis over time
