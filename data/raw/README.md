# Raw Data Directory

Place your JIRA CSV export files in this directory.

## Required Data Format

Your JIRA CSV export should include the following columns (adjust names as needed):

### Essential Columns:
- **Issue Key/ID**: Unique identifier for the JIRA issue (e.g., "PROJ-123")
- **Summary**: Brief description of the issue
- **Created**: Date when the issue was created
- **Resolved** or **Updated**: Date when the issue was resolved/updated
- **Status**: Current status (e.g., Done, In Progress, etc.)
- **Comment** or **Comments**: Text comments from the issue

### Optional but Helpful Columns:
- **Assignee**: Person assigned to the issue
- **Priority**: Issue priority level
- **Issue Type**: Bug, Story, Task, etc.
- **Labels**: Tags associated with the issue
- **Description**: Detailed issue description

## How to Export from JIRA

1. Go to your JIRA project
2. Click on **Filters** > **View all issues**
3. Apply filters for October issues (Created >= 2024-10-01)
4. Click **Export** > **Export CSV (All fields)**
5. Save the file to this directory

## Example Filename

```
jira_export_october_november_2024.csv
```

## Data Privacy

⚠️ **Important**: This directory is ignored by git (see `.gitignore`)
- Raw data files are NOT committed to version control
- Keep sensitive JIRA data confidential
- Only share processed/anonymized results

## Multiple Files

You can place multiple CSV files here. The analysis notebook will need to be updated to load the specific file you want to analyze.
