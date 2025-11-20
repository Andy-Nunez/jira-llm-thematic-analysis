"""
Theme clustering and analysis utilities.
Groups similar delay themes and generates actionable insights.
"""

import pandas as pd
from typing import List, Dict, Tuple
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns


class ThemeClusterer:
    """Cluster and analyze delay themes from LLM outputs."""

    def __init__(self, themes_df: pd.DataFrame):
        """
        Initialize with theme analysis results.

        Args:
            themes_df: DataFrame with columns: issue_key, theme, sentiment, reasoning
        """
        self.themes_df = themes_df
        self.theme_counts = None
        self.sentiment_by_theme = None

    def count_themes(self) -> pd.Series:
        """
        Count frequency of each theme.

        Returns:
            Series with theme counts, sorted by frequency
        """
        self.theme_counts = self.themes_df['theme'].value_counts()
        return self.theme_counts

    def get_top_themes(self, n: int = 10) -> pd.Series:
        """
        Get top N themes by frequency.

        Args:
            n: Number of top themes to return

        Returns:
            Series with top N themes
        """
        if self.theme_counts is None:
            self.count_themes()

        return self.theme_counts.head(n)

    def analyze_sentiment_by_theme(self) -> pd.DataFrame:
        """
        Analyze sentiment distribution for each theme.

        Returns:
            DataFrame with sentiment counts per theme
        """
        self.sentiment_by_theme = pd.crosstab(
            self.themes_df['theme'],
            self.themes_df['sentiment']
        )
        return self.sentiment_by_theme

    def get_theme_details(self, theme_name: str) -> pd.DataFrame:
        """
        Get all issues and reasoning for a specific theme.

        Args:
            theme_name: Name of the theme to analyze

        Returns:
            DataFrame with all issues matching the theme
        """
        return self.themes_df[
            self.themes_df['theme'] == theme_name
        ].copy()

    def create_summary_report(self, top_n: int = 10) -> Dict:
        """
        Create comprehensive summary report.

        Args:
            top_n: Number of top themes to include

        Returns:
            Dictionary with summary statistics
        """
        top_themes = self.get_top_themes(top_n)
        total_issues = len(self.themes_df)

        report = {
            'total_analyzed': total_issues,
            'unique_themes': self.themes_df['theme'].nunique(),
            'top_themes': [],
            'sentiment_distribution': self.themes_df['sentiment'].value_counts().to_dict()
        }

        for theme, count in top_themes.items():
            percentage = (count / total_issues) * 100
            theme_data = self.get_theme_details(theme)

            report['top_themes'].append({
                'theme': theme,
                'count': int(count),
                'percentage': round(percentage, 1),
                'sentiment_breakdown': theme_data['sentiment'].value_counts().to_dict(),
                'sample_reasoning': theme_data['reasoning'].head(3).tolist()
            })

        return report

    def visualize_top_themes(
        self,
        top_n: int = 10,
        save_path: Optional[str] = None
    ):
        """
        Create bar chart of top themes.

        Args:
            top_n: Number of themes to visualize
            save_path: Optional path to save the figure
        """
        top_themes = self.get_top_themes(top_n)

        plt.figure(figsize=(12, 6))
        sns.barplot(
            x=top_themes.values,
            y=top_themes.index,
            palette='viridis'
        )
        plt.xlabel('Number of Issues', fontsize=12)
        plt.ylabel('Delay Theme', fontsize=12)
        plt.title(
            f'Top {top_n} Delay Themes',
            fontsize=14,
            fontweight='bold'
        )
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved visualization to {save_path}")

        plt.show()

    def visualize_sentiment_distribution(
        self,
        save_path: Optional[str] = None
    ):
        """
        Create pie chart of sentiment distribution.

        Args:
            save_path: Optional path to save the figure
        """
        sentiment_counts = self.themes_df['sentiment'].value_counts()

        colors = {
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'positive': '#2ecc71'
        }

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            sentiment_counts.values,
            labels=sentiment_counts.index,
            autopct='%1.1f%%',
            colors=[colors.get(x, '#3498db') for x in sentiment_counts.index],
            startangle=90
        )
        ax.set_title(
            'Sentiment Distribution in Delayed Issues',
            fontsize=14,
            fontweight='bold'
        )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Saved sentiment chart to {save_path}")

        plt.show()

    def export_actionable_insights(
        self,
        output_path: str,
        top_n: int = 10
    ):
        """
        Export actionable insights to CSV.

        Args:
            output_path: Path for output CSV
            top_n: Number of top themes to include
        """
        top_themes = self.get_top_themes(top_n)
        total_issues = len(self.themes_df)

        insights = []
        for rank, (theme, count) in enumerate(top_themes.items(), 1):
            percentage = (count / total_issues) * 100
            theme_data = self.get_theme_details(theme)

            insights.append({
                'Rank': rank,
                'Theme': theme,
                'Issue_Count': count,
                'Percentage': round(percentage, 1),
                'Negative_Sentiment_Count': (theme_data['sentiment'] == 'negative').sum(),
                'Sample_Issue_Keys': ', '.join(theme_data['issue_key'].head(5).astype(str)),
                'Recommended_Action': self._generate_recommendation(theme)
            })

        insights_df = pd.DataFrame(insights)
        insights_df.to_csv(output_path, index=False)
        print(f"✅ Exported actionable insights to {output_path}")

        return insights_df

    def _generate_recommendation(self, theme: str) -> str:
        """
        Generate management recommendation based on theme.

        Args:
            theme: Theme name

        Returns:
            Recommended action string
        """
        recommendations = {
            'Technical Debt': 'Schedule dedicated refactoring sprints; allocate 20% of capacity to debt reduction',
            'Resource Constraints': 'Review team capacity planning; consider additional hiring or workload redistribution',
            'Dependencies': 'Improve cross-team communication; establish clear SLAs with dependencies',
            'Requirements Issues': 'Implement stricter requirements review process; involve stakeholders earlier',
            'Testing/QA': 'Expand test automation; allocate more QA resources or improve test infrastructure',
            'Environment Issues': 'Invest in DevOps infrastructure; improve environment stability and tooling',
            'Communication Gaps': 'Establish regular sync meetings; improve documentation and handoff processes',
            'Complexity': 'Break down large tasks into smaller units; improve estimation practices',
            'Process Issues': 'Review and streamline approval workflows; remove unnecessary bureaucracy',
            'External Factors': 'Build in buffer time for external dependencies; improve vendor management'
        }

        return recommendations.get(
            theme,
            'Review root causes and develop targeted improvement plan'
        )


from typing import Optional
