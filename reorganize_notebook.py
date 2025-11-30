"""
Reorganize the JIRA delay analysis notebook to match the methodology document.
"""

import json

# Read the current notebook
with open('notebooks/jira_delay_analysis_backup.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

cells = notebook['cells']
print(f"Total cells in original notebook: {len(cells)}")

# Define the new order following methodology.txt structure:
# 1. Setup and Imports
# 2. Load Data
# 3. Data Preprocessing
# 4. Data Aggregation Strategy (GROUP BY ISSUEKEY)
# 5. LLM-Based Theme Extraction
# 6. Post-Processing and Theme Clustering
# 7. Comprehensive Reporting
# 8. Executive Summary
# 9. Visualizations
# 10. Export Results

new_cells = []

# SECTION 1: Setup and Imports (cells 0-2)
print("Adding Section 1: Setup and Imports")
new_cells.extend(cells[0:3])

# SECTION 2: Load Data (cells 3-5)
print("Adding Section 2: Load Data")
new_cells.extend(cells[3:6])

# SECTION 3: Data Preprocessing (cells 6-7)
print("Adding Section 3: Data Preprocessing")
new_cells.extend(cells[6:8])

# Add date range check and extract comments (cells 9-10)
new_cells.extend(cells[9:11])

# SECTION 4: Data Aggregation Strategy - GROUP BY ISSUEKEY
print("Adding Section 4: Data Aggregation Strategy")
section_4_header = {
    "cell_type": "markdown",
    "id": "section-4-header",
    "metadata": {},
    "source": [
        "## 4. Data Aggregation Strategy (GROUP BY ISSUEKEY)\n",
        "\n",
        "**Methodology Section 1.2**: Group comments by IssueKey to reduce API calls from 241 to 39.\n",
        "\n",
        "This provides:\n",
        "1. Complete conversational context for the LLM\n",
        "2. More accurate thematic inference\n",
        "3. Significant cost reduction"
    ]
}
new_cells.append(section_4_header)
new_cells.append(cells[26])  # Grouping logic

# SECTION 5: LLM-Based Theme Extraction
print("Adding Section 5: LLM-Based Theme Extraction")
section_5_header = {
    "cell_type": "markdown",
    "id": "section-5-header",
    "metadata": {},
    "source": [
        "## 5. LLM-Based Theme Extraction\n",
        "\n",
        "**Methodology Section 1.3**: Analyze each aggregated issue conversation with GPT-4.\n",
        "\n",
        "Extract:\n",
        "- Primary delay factors (thematic categories)\n",
        "- Sentiment indicators\n",
        "- Root cause attribution\n",
        "- Structured output in JSON format"
    ]
}
new_cells.append(section_5_header)
new_cells.append(cells[12])  # LLM analyzer initialization
new_cells.append(cells[27])  # LLM analysis on grouped data
new_cells.append(cells[28])  # Merge themes with metrics

# SECTION 6: Post-Processing and Theme Clustering
print("Adding Section 6: Post-Processing and Theme Clustering")
section_6_header = {
    "cell_type": "markdown",
    "id": "section-6-header",
    "metadata": {},
    "source": [
        "## 6. Post-Processing and Theme Clustering\n",
        "\n",
        "**Methodology Section 1.4**: Use K-means clustering to group similar themes into 5 major clusters.\n",
        "\n",
        "This addresses semantic redundancy and consolidates thematically similar delay factors."
    ]
}
new_cells.append(section_6_header)
new_cells.extend(cells[30:33])  # Clustering cells (30, 31, 32)

# SECTION 7: Comprehensive Reporting
print("Adding Section 7: Comprehensive Reporting")
new_cells.append(cells[36])  # "COMPREHENSIVE REPORTING" header
new_cells.append(cells[37])  # Comprehensive report CSV
new_cells.append(cells[38])  # Cluster summary

# SECTION 8: Executive Summary
print("Adding Section 8: Executive Summary")
new_cells.append(cells[39])  # "EXECUTIVE SUMMARY" header
new_cells.append(cells[40])  # Executive summary print

# SECTION 9: Visualizations
print("Adding Section 9: Visualizations")
section_9_header = {
    "cell_type": "markdown",
    "id": "section-9-header",
    "metadata": {},
    "source": [
        "## 9. Visualizations and Analysis\n",
        "\n",
        "Comprehensive visual analysis of the 5 theme clusters."
    ]
}
new_cells.append(section_9_header)

# Add all visualization cells
new_cells.extend(cells[34:36])  # Cluster distribution and PCA (cells 34-35)
new_cells.extend(cells[41:50])  # Remaining visualizations (41-49)

# Add detailed reasoning analysis
new_cells.append(cells[50])  # Detailed reasoning with wrapped text

# SECTION 10: Export Results
print("Adding Section 10: Export Results")
section_10_header = {
    "cell_type": "markdown",
    "id": "section-10-header",
    "metadata": {},
    "source": [
        "## 10. Export Results\n",
        "\n",
        "Generate final PDF report with cluster reasoning analysis."
    ]
}
new_cells.append(section_10_header)
new_cells.append(cells[51])  # PDF export

# Create new notebook with reorganized cells
new_notebook = {
    "cells": new_cells,
    "metadata": notebook['metadata'],
    "nbformat": notebook['nbformat'],
    "nbformat_minor": notebook['nbformat_minor']
}

# Save reorganized notebook
with open('notebooks/jira_delay_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(new_notebook, f, indent=1, ensure_ascii=False)

print("\nNotebook reorganized successfully!")
print(f"   Original cells: {len(cells)}")
print(f"   New cells: {len(new_cells)}")
print(f"   Removed cells: {len(cells) - len(new_cells)}")
print(f"   Backup saved: notebooks/jira_delay_analysis_backup.ipynb")

# Print summary of removed sections
print("\nRemoved sections (old incorrect approach):")
print("   - Cells 11-16: Individual comment LLM analysis")
print("   - Cells 17-24: Theme clustering and insights on individual comments")
print("   - Cell 8: Duplicate GROUP COMMENTS header")
print("   - Cell 19: Test visualization")
print("   - Cell 25: Duplicate GROUP COMMENTS header (replaced with new one)")
print("   - Cell 29: Old clustering header (replaced with new one)")
print("   - Cell 33: Old visualizations header (replaced with new one)")
print("   - Cell 52: Investigation cell (optional debugging)")
