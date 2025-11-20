# Automated Theme Analysis with OpenAI
# Add these cells to your Jupyter notebook after the existing cleaning cells

"""
CELL: Markdown
## 7. Automated Theme Discovery with OpenAI API

This replaces manual copying/pasting to ChatGPT with automated API calls.
"""

"""
CELL: Code
# Setup OpenAI API
"""

from openai import OpenAI
import os
import json

# Set your API key (choose ONE method):
# Method 1: Environment variable (recommended for security)
# Run in terminal: setx OPENAI_API_KEY "your-api-key-here"
# Then restart your kernel

# Method 2: Direct assignment (NOT recommended for production)
# os.environ["OPENAI_API_KEY"] = "sk-your-key-here"

# Initialize client
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    print("✅ OpenAI client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing OpenAI: {e}")
    print("\nPlease set your API key using one of these methods:")
    print("1. Set environment variable: OPENAI_API_KEY")
    print("2. Or uncomment the line above and add your key directly")

"""
CELL: Code
# Function to discover themes automatically
"""

def discover_themes_with_llm(comments_df, num_themes=10, model="gpt-4o-mini"):
    """
    Automatically discover themes from Jira comments using OpenAI API

    Parameters:
    - comments_df: DataFrame with 'IssueKey' and 'text_clean' columns
    - num_themes: Number of themes to identify (default: 10)
    - model: OpenAI model to use (gpt-4o-mini is cheaper, gpt-4o is better quality)

    Returns:
    - Dictionary with 'themes' list
    """

    # Prepare the input text
    rows_for_llm = []
    for issue, grp in comments_df.groupby("IssueKey", sort=True):
        rows_for_llm.append(f"Issue {issue}:")
        for _, row in grp.iterrows():
            txt = row["text_clean"]
            rows_for_llm.append(f"  - {txt}")
        rows_for_llm.append("")

    llm_input = "\n".join(rows_for_llm)

    # Create the prompt
    prompt = f"""Analyze these Jira comments about project delays and identify the root causes.

{llm_input}

Based on all comments above, identify exactly {num_themes} high-level themes that explain why work wasn't completed on time.

Return your analysis as a JSON object with this structure:
{{
  "themes": [
    {{
      "theme": "Short theme name (3-6 words)",
      "description": "One sentence describing this delay pattern",
      "examples": ["phrase 1 from comments", "phrase 2 from comments", "phrase 3 from comments"]
    }}
  ]
}}

Important:
- Themes should be distinct and non-overlapping
- Examples should be actual phrases from the comments
- Focus on actionable root causes, not symptoms"""

    print(f"🤖 Sending {len(comments_df)} comments to {model}...")
    print(f"📊 Requesting {num_themes} themes...\n")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing project management data and identifying patterns in delays."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temperature for more consistent results
        )

        result = json.loads(response.choices[0].message.content)

        print(f"✅ Successfully discovered {len(result['themes'])} themes")
        print(f"💰 Tokens used: {response.usage.total_tokens}")

        return result

    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None

"""
CELL: Code
# Run automated theme discovery
"""

# Discover themes automatically
themes_result = discover_themes_with_llm(
    data,
    num_themes=10,
    model="gpt-4o-mini"  # Use "gpt-4o" for better quality (more expensive)
)

if themes_result:
    # Display discovered themes
    themes_df_auto = pd.DataFrame(themes_result["themes"])
    print("\n" + "="*80)
    print("DISCOVERED THEMES")
    print("="*80 + "\n")

    for idx, row in themes_df_auto.iterrows():
        print(f"{idx+1}. {row['theme']}")
        print(f"   {row['description']}")
        print(f"   Examples: {', '.join(row['examples'][:2])}")
        print()

"""
CELL: Markdown
## 8. Assign Themes to Each Issue (Automated)

Now automatically assign themes to each issue using the LLM.
"""

"""
CELL: Code
# Function to assign themes to issues
"""

def assign_themes_to_issues(comments_df, themes_list, model="gpt-4o-mini"):
    """
    Automatically assign themes to each issue based on its comments

    Parameters:
    - comments_df: DataFrame with 'IssueKey' and 'text_clean' columns
    - themes_list: List of theme dictionaries from discover_themes_with_llm
    - model: OpenAI model to use

    Returns:
    - DataFrame with columns: issue, themes (list)
    """

    # Create theme reference for the LLM
    theme_names = [t["theme"] for t in themes_list]
    theme_reference = "\n".join([f"{i+1}. {name}" for i, name in enumerate(theme_names)])

    issue_assignments = []
    total_issues = comments_df["IssueKey"].nunique()

    print(f"🔍 Assigning themes to {total_issues} issues...")

    for issue_num, (issue, grp) in enumerate(comments_df.groupby("IssueKey"), 1):
        # Combine all comments for this issue
        all_comments = " | ".join(grp["text_clean"].tolist())

        prompt = f"""Given these comments from Jira issue {issue}:

{all_comments}

Which of the following themes apply to this issue? You can select 1-3 themes.

Available themes:
{theme_reference}

Return ONLY a JSON object with this structure:
{{
  "issue": "{issue}",
  "themes": ["Theme name 1", "Theme name 2"]
}}

Only include theme names that clearly apply based on the comments."""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing project issues."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )

            result = json.loads(response.choices[0].message.content)
            issue_assignments.append(result)

            print(f"  [{issue_num}/{total_issues}] {issue}: {len(result['themes'])} themes assigned")

        except Exception as e:
            print(f"  ❌ Error processing {issue}: {e}")
            issue_assignments.append({"issue": issue, "themes": []})

    print(f"\n✅ Theme assignment complete!")
    return pd.DataFrame(issue_assignments)

"""
CELL: Code
# Run automated theme assignment
"""

if themes_result:
    # Assign themes to issues
    issues_df_auto = assign_themes_to_issues(
        data,
        themes_result["themes"],
        model="gpt-4o-mini"
    )

    print("\n" + "="*80)
    print("ISSUE-THEME ASSIGNMENTS")
    print("="*80 + "\n")
    print(issues_df_auto.head(10))

    # Calculate statistics
    avg_themes = issues_df_auto["themes"].apply(len).mean()
    print(f"\n📊 Average themes per issue: {avg_themes:.2f}")

"""
CELL: Code
# Save results to JSON
"""

if themes_result and len(issues_df_auto) > 0:
    output_data = {
        "themes": themes_result["themes"],
        "issues": issues_df_auto.to_dict('records')
    }

    output_path = r"C:\Users\Andy\Desktop\Text_Analysis\JSON_themes_automated.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    print(f"   - {len(output_data['themes'])} themes")
    print(f"   - {len(output_data['issues'])} issues")

"""
CELL: Markdown
## 9. Visualize Automated Results

Compare automated theme discovery with your manual analysis.
"""

"""
CELL: Code
# Analyze automated theme frequencies
"""

if len(issues_df_auto) > 0:
    from collections import Counter

    # Count theme frequencies
    all_themes_auto = [t for theme_list in issues_df_auto["themes"] for t in theme_list]
    theme_counts_auto = Counter(all_themes_auto)

    theme_freq_auto = (
        pd.DataFrame(theme_counts_auto.items(), columns=["Theme", "Count"])
        .sort_values("Count", ascending=False)
    )

    # Visualize
    plt.figure(figsize=(12, 6))
    plt.barh(theme_freq_auto["Theme"], theme_freq_auto["Count"], color='steelblue')
    plt.gca().invert_yaxis()
    plt.title("Automated Theme Discovery - Top Delay Reasons", fontsize=14, fontweight='bold')
    plt.xlabel("Number of Issues", fontsize=12)
    plt.ylabel("Theme", fontsize=12)
    plt.tight_layout()
    plt.show()

    print("\nTheme Frequency:")
    print(theme_freq_auto.to_string(index=False))
