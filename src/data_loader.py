"""
Data loading and preprocessing utilities for JIRA exports.
"""

import pandas as pd
from typing import Optional, List
from datetime import datetime


class JIRADataLoader:
    """Load and preprocess JIRA CSV exports."""

    def __init__(self, file_path: str):
        """
        Initialize the data loader.

        Args:
            file_path: Path to the JIRA CSV export file
        """
        self.file_path = file_path
        self.df = None

    def load(self, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Load JIRA data from CSV.

        Args:
            encoding: File encoding (default: utf-8)

        Returns:
            Loaded DataFrame
        """
        try:
            self.df = pd.read_csv(self.file_path, encoding=encoding)
            print(f"✅ Loaded {len(self.df)} records from {self.file_path}")
            return self.df
        except UnicodeDecodeError:
            # Try alternative encodings
            print("⚠️ UTF-8 failed, trying latin-1 encoding...")
            self.df = pd.read_csv(self.file_path, encoding='latin-1')
            print(f"✅ Loaded {len(self.df)} records from {self.file_path}")
            return self.df

    def convert_dates(self, date_columns: List[str]) -> pd.DataFrame:
        """
        Convert specified columns to datetime format.

        Args:
            date_columns: List of column names to convert

        Returns:
            DataFrame with converted dates
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")

        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                print(f"✅ Converted {col} to datetime")
            else:
                print(f"⚠️ Column '{col}' not found")

        return self.df

    def filter_delayed_issues(
        self,
        created_start: str,
        created_end: str,
        resolved_start: str,
        created_col: str = 'Created',
        resolved_col: str = 'Resolved'
    ) -> pd.DataFrame:
        """
        Filter issues created in one period and resolved in another.

        Args:
            created_start: Start date for creation period (YYYY-MM-DD)
            created_end: End date for creation period (YYYY-MM-DD)
            resolved_start: Start date for resolution period (YYYY-MM-DD)
            created_col: Name of created date column
            resolved_col: Name of resolved date column

        Returns:
            Filtered DataFrame with delayed issues
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")

        created_start_dt = pd.Timestamp(created_start)
        created_end_dt = pd.Timestamp(created_end)
        resolved_start_dt = pd.Timestamp(resolved_start)

        delayed = self.df[
            (self.df[created_col] >= created_start_dt) &
            (self.df[created_col] <= created_end_dt) &
            (
                (self.df[resolved_col] >= resolved_start_dt) |
                (self.df[resolved_col].isnull())
            )
        ].copy()

        print(f"✅ Found {len(delayed)} delayed issues")
        return delayed

    def validate_required_columns(
        self,
        required_columns: List[str]
    ) -> bool:
        """
        Validate that required columns exist in the DataFrame.

        Args:
            required_columns: List of required column names

        Returns:
            True if all columns exist, False otherwise
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")

        missing = [col for col in required_columns if col not in self.df.columns]

        if missing:
            print(f"⚠️ Missing required columns: {missing}")
            print(f"Available columns: {list(self.df.columns)}")
            return False

        print("✅ All required columns present")
        return True

    def get_summary(self) -> dict:
        """
        Get summary statistics of the loaded data.

        Returns:
            Dictionary with summary statistics
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")

        return {
            'total_records': len(self.df),
            'columns': list(self.df.columns),
            'null_counts': self.df.isnull().sum().to_dict(),
            'dtypes': self.df.dtypes.to_dict()
        }

    def clean_comments(
        self,
        comment_column: str = 'Comment',
        min_length: int = 10
    ) -> pd.DataFrame:
        """
        Clean and filter comment data.

        Args:
            comment_column: Name of the comment column
            min_length: Minimum comment length to keep

        Returns:
            DataFrame with cleaned comments
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")

        if comment_column not in self.df.columns:
            print(f"⚠️ Column '{comment_column}' not found")
            return self.df

        # Remove null comments
        cleaned = self.df[self.df[comment_column].notna()].copy()

        # Convert to string and filter by length
        cleaned[comment_column] = cleaned[comment_column].astype(str)
        cleaned = cleaned[
            cleaned[comment_column].str.len() >= min_length
        ].copy()

        print(f"✅ Retained {len(cleaned)} issues with valid comments")
        return cleaned

    def export_processed(
        self,
        output_path: str,
        df: Optional[pd.DataFrame] = None
    ):
        """
        Export processed data to CSV.

        Args:
            output_path: Path for the output file
            df: DataFrame to export (uses self.df if not provided)
        """
        export_df = df if df is not None else self.df

        if export_df is None:
            raise ValueError("No data to export")

        export_df.to_csv(output_path, index=False)
        print(f"✅ Exported {len(export_df)} records to {output_path}")
