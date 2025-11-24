#!/usr/bin/env python3
"""
Results Analysis Script for QuantumBench

This script analyzes benchmark results by difficulty level and expertise level,
calculating pass rates and generating detailed reports.

Usage:
    python code/analyze_results.py --results-file outputs/run_XXX/quantumbench_results_model_0.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description='Analyze QuantumBench results by difficulty and expertise levels'
    )
    parser.add_argument(
        '--results-file',
        type=str,
        required=True,
        help='Path to the results CSV file'
    )
    parser.add_argument(
        '--human-eval-file',
        type=str,
        default='./quantumbench/human-evaluation.csv',
        help='Path to human evaluation CSV file'
    )
    parser.add_argument(
        '--category-file',
        type=str,
        default='./quantumbench/category.csv',
        help='Path to category CSV file'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default=None,
        help='Path to save analysis report (optional, defaults to same dir as results)'
    )

    return parser.parse_args()


def load_data(results_file, human_eval_file, category_file):
    """Load and merge all necessary data files"""

    # Load results
    print(f"Loading results from: {results_file}")
    results_df = pd.read_csv(results_file)
    print(f"  Loaded {len(results_df)} results")

    # Load human evaluation
    print(f"Loading human evaluation from: {human_eval_file}")
    human_eval_df = pd.read_csv(human_eval_file)
    print(f"  Loaded {len(human_eval_df)} evaluations")

    # Load categories
    print(f"Loading categories from: {category_file}")
    category_df = pd.read_csv(category_file)
    print(f"  Loaded {len(category_df)} categories")

    # Calculate average difficulty and expertise for each question
    # Handle missing values by calculating mean of available ratings
    human_eval_df['Avg_Difficulty'] = human_eval_df[
        ['Difficulty1', 'Difficulty2', 'Difficulty3']
    ].mean(axis=1, skipna=True)

    human_eval_df['Avg_Expertise'] = human_eval_df[
        ['Expertise1', 'Expertise2', 'Expertise3']
    ].mean(axis=1, skipna=True)

    # Merge all dataframes
    merged_df = results_df.merge(
        human_eval_df[['Question id', 'Avg_Difficulty', 'Avg_Expertise']],
        on='Question id',
        how='left'
    )

    merged_df = merged_df.merge(
        category_df[['Question id', 'Subdomain_question', 'QuestionType']],
        on='Question id',
        how='left'
    )

    return merged_df


def calculate_statistics(df):
    """Calculate overall statistics"""

    total_questions = len(df)
    correct_answers = df['Correct'].sum()
    pass_rate = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    avg_difficulty = df['Avg_Difficulty'].mean()
    avg_expertise = df['Avg_Expertise'].mean()

    # Calculate token statistics if available
    total_prompt_tokens = df['Prompt tokens'].sum() if 'Prompt tokens' in df.columns else 0
    total_completion_tokens = df['Completion tokens'].sum() if 'Completion tokens' in df.columns else 0
    total_tokens = total_prompt_tokens + total_completion_tokens

    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'pass_rate': pass_rate,
        'avg_difficulty': avg_difficulty,
        'avg_expertise': avg_expertise,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'total_tokens': total_tokens
    }


def analyze_by_difficulty(df):
    """Analyze results grouped by difficulty level"""

    # Filter out rows with missing difficulty values
    df_valid = df.dropna(subset=['Avg_Difficulty']).copy()

    # Create difficulty bins
    df_valid['Difficulty_Level'] = pd.cut(
        df_valid['Avg_Difficulty'],
        bins=[0, 1.5, 2.5, 3.5, 4.5, 5.5],
        labels=['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        include_lowest=True
    )

    difficulty_stats = df_valid.groupby('Difficulty_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean'],
        'Avg_Difficulty': 'mean'
    }).round(4)

    difficulty_stats.columns = ['Total_Questions', 'Correct_Answers', 'Pass_Rate', 'Avg_Difficulty']
    difficulty_stats['Pass_Rate'] = difficulty_stats['Pass_Rate'] * 100

    # Note: Questions with missing difficulty annotations are excluded from this analysis
    return difficulty_stats


def analyze_by_expertise(df):
    """Analyze results grouped by expertise level"""

    # Filter out rows with missing expertise values
    df_valid = df.dropna(subset=['Avg_Expertise']).copy()

    # Create expertise bins
    df_valid['Expertise_Level'] = pd.cut(
        df_valid['Avg_Expertise'],
        bins=[0, 1.5, 2.5, 3.5, 4.5],
        labels=['Level 1', 'Level 2', 'Level 3', 'Level 4'],
        include_lowest=True
    )

    expertise_stats = df_valid.groupby('Expertise_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean'],
        'Avg_Expertise': 'mean'
    }).round(4)

    expertise_stats.columns = ['Total_Questions', 'Correct_Answers', 'Pass_Rate', 'Avg_Expertise']
    expertise_stats['Pass_Rate'] = expertise_stats['Pass_Rate'] * 100

    # Note: Questions with missing expertise annotations are excluded from this analysis
    return expertise_stats


def analyze_by_subdomain(df):
    """Analyze results grouped by subdomain"""

    subdomain_stats = df.groupby('Subdomain_question').agg({
        'Correct': ['count', 'sum', 'mean'],
        'Avg_Difficulty': 'mean',
        'Avg_Expertise': 'mean'
    }).round(4)

    subdomain_stats.columns = ['Total_Questions', 'Correct_Answers', 'Pass_Rate',
                                'Avg_Difficulty', 'Avg_Expertise']
    subdomain_stats['Pass_Rate'] = subdomain_stats['Pass_Rate'] * 100
    subdomain_stats = subdomain_stats.sort_values('Pass_Rate', ascending=False)

    return subdomain_stats


def analyze_by_question_type(df):
    """Analyze results grouped by question type"""

    qtype_stats = df.groupby('QuestionType').agg({
        'Correct': ['count', 'sum', 'mean'],
        'Avg_Difficulty': 'mean',
        'Avg_Expertise': 'mean'
    }).round(4)

    qtype_stats.columns = ['Total_Questions', 'Correct_Answers', 'Pass_Rate',
                           'Avg_Difficulty', 'Avg_Expertise']
    qtype_stats['Pass_Rate'] = qtype_stats['Pass_Rate'] * 100
    qtype_stats = qtype_stats.sort_values('Pass_Rate', ascending=False)

    return qtype_stats


def analyze_difficulty_expertise_matrix(df):
    """Analyze results in a difficulty x expertise matrix"""

    # Filter out rows with missing difficulty or expertise values
    df_valid = df.dropna(subset=['Avg_Difficulty', 'Avg_Expertise']).copy()

    # Create bins for both dimensions
    df_valid['Difficulty_Level'] = pd.cut(
        df_valid['Avg_Difficulty'],
        bins=[0, 1.5, 2.5, 3.5, 4.5, 5.5],
        labels=['D1', 'D2', 'D3', 'D4', 'D5'],
        include_lowest=True
    )

    df_valid['Expertise_Level'] = pd.cut(
        df_valid['Avg_Expertise'],
        bins=[0, 1.5, 2.5, 3.5, 4.5],
        labels=['E1', 'E2', 'E3', 'E4'],
        include_lowest=True
    )

    # Create matrix of pass rates
    matrix = df_valid.pivot_table(
        values='Correct',
        index='Difficulty_Level',
        columns='Expertise_Level',
        aggfunc=['mean', 'count']
    )

    # Convert pass rates to percentages
    if ('mean',) in matrix.columns.droplevel(1).unique():
        for col in matrix['mean'].columns:
            matrix[('mean', col)] *= 100

    return matrix


def generate_report(stats, difficulty_stats, expertise_stats, subdomain_stats,
                   qtype_stats, matrix, output_file=None):
    """Generate and print a comprehensive analysis report"""

    report_lines = []

    # Header
    report_lines.append("=" * 100)
    report_lines.append("QUANTUMBENCH RESULTS ANALYSIS - QISKIT CODE ASSISTANT")
    report_lines.append("=" * 100)
    report_lines.append("")

    # Overall Statistics
    report_lines.append("OVERALL STATISTICS")
    report_lines.append("-" * 100)
    report_lines.append(f"Total Questions:           {stats['total_questions']}")
    report_lines.append(f"Correct Answers:           {stats['correct_answers']}")
    report_lines.append(f"Overall Pass Rate:         {stats['pass_rate']:.2f}%")
    report_lines.append(f"Average Difficulty Level:  {stats['avg_difficulty']:.2f}")
    report_lines.append(f"Average Expertise Level:   {stats['avg_expertise']:.2f}")
    if stats['total_tokens'] > 0:
        report_lines.append(f"Total Tokens Used:         {stats['total_tokens']:,} (Prompt: {stats['total_prompt_tokens']:,}, Completion: {stats['total_completion_tokens']:,})")
    report_lines.append("")

    # Analysis by Difficulty Level
    report_lines.append("ANALYSIS BY DIFFICULTY LEVEL")
    report_lines.append("-" * 100)
    report_lines.append("")
    report_lines.append("Difficulty Level Criteria:")
    report_lines.append("  Level 1: A problem whose correct answer can be obtained immediately")
    report_lines.append("  Level 2: A problem with an obvious solution that can be solved with simple calculations")
    report_lines.append("  Level 3: A problem whose solution comes to mind quickly but requires somewhat tedious steps")
    report_lines.append("  Level 4: A problem that requires some thought to discover the solution")
    report_lines.append("  Level 5: A problem whose solution cannot be easily identified")
    report_lines.append("")
    report_lines.append(difficulty_stats.to_string())
    report_lines.append("")

    # Analysis by Expertise Level
    report_lines.append("ANALYSIS BY EXPERTISE LEVEL")
    report_lines.append("-" * 100)
    report_lines.append("")
    report_lines.append("Expertise Level Criteria:")
    report_lines.append("  Level 1: An elementary problem; non-specialists can understand the question")
    report_lines.append("  Level 2: People who studied physics can understand the question")
    report_lines.append("  Level 3: Understanding requires having read technical texts in the field")
    report_lines.append("  Level 4: Only experts who conduct research in that field can understand the question")
    report_lines.append("")
    report_lines.append(expertise_stats.to_string())
    report_lines.append("")

    # Analysis by Subdomain
    report_lines.append("ANALYSIS BY SUBDOMAIN")
    report_lines.append("-" * 100)
    report_lines.append(subdomain_stats.to_string())
    report_lines.append("")

    # Analysis by Question Type
    report_lines.append("ANALYSIS BY QUESTION TYPE")
    report_lines.append("-" * 100)
    report_lines.append(qtype_stats.to_string())
    report_lines.append("")

    # Difficulty x Expertise Matrix
    report_lines.append("DIFFICULTY × EXPERTISE MATRIX")
    report_lines.append("-" * 100)
    report_lines.append("")
    report_lines.append("Pass Rates (%):")
    if not matrix.empty and 'mean' in matrix.columns.get_level_values(0):
        report_lines.append(matrix['mean'].round(2).to_string())
    else:
        report_lines.append("No data available")
    report_lines.append("")
    report_lines.append("Question Counts:")
    if not matrix.empty and 'count' in matrix.columns.get_level_values(0):
        report_lines.append(matrix['count'].fillna(0).astype(int).to_string())
    else:
        report_lines.append("No data available")
    report_lines.append("")

    # Footer
    report_lines.append("=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)

    # Join all lines
    report = "\n".join(report_lines)

    # Print to console
    print(report)

    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

    return report


def main():
    args = parse_args()

    # Validate input files
    if not Path(args.results_file).exists():
        print(f"Error: Results file not found: {args.results_file}")
        sys.exit(1)

    if not Path(args.human_eval_file).exists():
        print(f"Error: Human evaluation file not found: {args.human_eval_file}")
        sys.exit(1)

    if not Path(args.category_file).exists():
        print(f"Error: Category file not found: {args.category_file}")
        sys.exit(1)

    # Determine output file path
    if args.output_file is None:
        results_path = Path(args.results_file)
        output_file = results_path.parent / f"{results_path.stem}_analysis.txt"
    else:
        output_file = args.output_file

    print("=" * 100)
    print("Starting Analysis")
    print("=" * 100)
    print()

    # Load data
    df = load_data(args.results_file, args.human_eval_file, args.category_file)

    print()
    print("Calculating statistics...")

    # Calculate statistics
    stats = calculate_statistics(df)
    difficulty_stats = analyze_by_difficulty(df)
    expertise_stats = analyze_by_expertise(df)
    subdomain_stats = analyze_by_subdomain(df)
    qtype_stats = analyze_by_question_type(df)
    matrix = analyze_difficulty_expertise_matrix(df)

    print()

    # Generate report
    generate_report(
        stats, difficulty_stats, expertise_stats, subdomain_stats,
        qtype_stats, matrix, output_file
    )


if __name__ == "__main__":
    main()
