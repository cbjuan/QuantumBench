#!/usr/bin/env python3
"""
Compare Results Between Different Prompt Types

This script compares benchmark results from two different runs (e.g., zeroshot vs zeroshot-CoT)
and generates a detailed comparison report.

Usage:
    python code/compare_prompts.py \
        --results1 outputs/run1/quantumbench_results_model_0.csv \
        --results2 outputs/run2/quantumbench_results_model_0.csv \
        --label1 "Zero-Shot" \
        --label2 "Zero-Shot CoT"
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description='Compare results between different prompt types or models'
    )
    parser.add_argument(
        '--results1',
        type=str,
        required=True,
        help='Path to first results CSV file'
    )
    parser.add_argument(
        '--results2',
        type=str,
        required=True,
        help='Path to second results CSV file'
    )
    parser.add_argument(
        '--label1',
        type=str,
        default='Run 1',
        help='Label for first results (e.g., "Zero-Shot")'
    )
    parser.add_argument(
        '--label2',
        type=str,
        default='Run 2',
        help='Label for second results (e.g., "Zero-Shot CoT")'
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
        help='Path to save comparison report'
    )

    return parser.parse_args()


def load_and_enrich_results(results_file, human_eval_file, category_file):
    """Load results and add human evaluation and category data"""

    # Load results
    results_df = pd.read_csv(results_file)

    # Load human evaluation
    human_eval_df = pd.read_csv(human_eval_file)
    human_eval_df['Avg_Difficulty'] = human_eval_df[
        ['Difficulty1', 'Difficulty2', 'Difficulty3']
    ].mean(axis=1, skipna=True)
    human_eval_df['Avg_Expertise'] = human_eval_df[
        ['Expertise1', 'Expertise2', 'Expertise3']
    ].mean(axis=1, skipna=True)

    # Load categories
    category_df = pd.read_csv(category_file)

    # Merge
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

    # Add level bins
    merged_df['Difficulty_Level'] = pd.cut(
        merged_df['Avg_Difficulty'],
        bins=[0, 1.5, 2.5, 3.5, 4.5, 5.5],
        labels=['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        include_lowest=True
    )
    merged_df['Expertise_Level'] = pd.cut(
        merged_df['Avg_Expertise'],
        bins=[0, 1.5, 2.5, 3.5, 4.5],
        labels=['Level 1', 'Level 2', 'Level 3', 'Level 4'],
        include_lowest=True
    )

    return merged_df


def compare_overall_stats(df1, df2, label1, label2):
    """Compare overall statistics"""

    stats = {
        'Metric': [
            'Total Questions',
            'Correct Answers',
            'Pass Rate (%)',
            'Avg Difficulty',
            'Avg Expertise',
            'Total Tokens',
            'Prompt Tokens',
            'Completion Tokens'
        ],
        label1: [
            len(df1),
            df1['Correct'].sum(),
            df1['Correct'].mean() * 100,
            df1['Avg_Difficulty'].mean(),
            df1['Avg_Expertise'].mean(),
            df1['Prompt tokens'].sum() + df1['Completion tokens'].sum() if 'Prompt tokens' in df1.columns else 0,
            df1['Prompt tokens'].sum() if 'Prompt tokens' in df1.columns else 0,
            df1['Completion tokens'].sum() if 'Completion tokens' in df1.columns else 0
        ],
        label2: [
            len(df2),
            df2['Correct'].sum(),
            df2['Correct'].mean() * 100,
            df2['Avg_Difficulty'].mean(),
            df2['Avg_Expertise'].mean(),
            df2['Prompt tokens'].sum() + df2['Completion tokens'].sum() if 'Prompt tokens' in df2.columns else 0,
            df2['Prompt tokens'].sum() if 'Prompt tokens' in df2.columns else 0,
            df2['Completion tokens'].sum() if 'Completion tokens' in df2.columns else 0
        ]
    }

    # Calculate differences
    diffs = []
    for i, metric in enumerate(stats['Metric']):
        val1 = stats[label1][i]
        val2 = stats[label2][i]

        if metric in ['Total Questions', 'Correct Answers', 'Total Tokens', 'Prompt Tokens', 'Completion Tokens']:
            diff = val2 - val1
            diffs.append(f"+{diff:.0f}" if diff > 0 else f"{diff:.0f}")
        else:
            diff = val2 - val1
            diffs.append(f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}")

    stats['Difference'] = diffs

    return pd.DataFrame(stats)


def compare_by_difficulty(df1, df2, label1, label2):
    """Compare results by difficulty level"""

    # Get stats for each
    stats1 = df1.groupby('Difficulty_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean']
    })
    stats1.columns = ['Count', 'Correct', 'Pass_Rate']
    stats1['Pass_Rate'] *= 100

    stats2 = df2.groupby('Difficulty_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean']
    })
    stats2.columns = ['Count', 'Correct', 'Pass_Rate']
    stats2['Pass_Rate'] *= 100

    # Combine
    comparison = pd.DataFrame({
        'Difficulty': stats1.index,
        f'{label1}_Pass_Rate': stats1['Pass_Rate'].values,
        f'{label2}_Pass_Rate': stats2['Pass_Rate'].values,
        'Questions': stats1['Count'].values
    })
    comparison['Difference'] = comparison[f'{label2}_Pass_Rate'] - comparison[f'{label1}_Pass_Rate']

    return comparison


def compare_by_expertise(df1, df2, label1, label2):
    """Compare results by expertise level"""

    # Get stats for each
    stats1 = df1.groupby('Expertise_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean']
    })
    stats1.columns = ['Count', 'Correct', 'Pass_Rate']
    stats1['Pass_Rate'] *= 100

    stats2 = df2.groupby('Expertise_Level', observed=True).agg({
        'Correct': ['count', 'sum', 'mean']
    })
    stats2.columns = ['Count', 'Correct', 'Pass_Rate']
    stats2['Pass_Rate'] *= 100

    # Combine
    comparison = pd.DataFrame({
        'Expertise': stats1.index,
        f'{label1}_Pass_Rate': stats1['Pass_Rate'].values,
        f'{label2}_Pass_Rate': stats2['Pass_Rate'].values,
        'Questions': stats1['Count'].values
    })
    comparison['Difference'] = comparison[f'{label2}_Pass_Rate'] - comparison[f'{label1}_Pass_Rate']

    return comparison


def compare_by_subdomain(df1, df2, label1, label2):
    """Compare results by subdomain"""

    # Get stats for each
    stats1 = df1.groupby('Subdomain_question').agg({
        'Correct': ['count', 'mean']
    })
    stats1.columns = ['Count', 'Pass_Rate']
    stats1['Pass_Rate'] *= 100

    stats2 = df2.groupby('Subdomain_question').agg({
        'Correct': ['count', 'mean']
    })
    stats2.columns = ['Count', 'Pass_Rate']
    stats2['Pass_Rate'] *= 100

    # Combine (use all subdomains from both)
    all_subdomains = set(stats1.index) | set(stats2.index)

    comparison = pd.DataFrame({
        'Subdomain': list(all_subdomains),
        f'{label1}_Pass_Rate': [stats1.loc[s, 'Pass_Rate'] if s in stats1.index else 0 for s in all_subdomains],
        f'{label2}_Pass_Rate': [stats2.loc[s, 'Pass_Rate'] if s in stats2.index else 0 for s in all_subdomains],
        'Questions': [stats1.loc[s, 'Count'] if s in stats1.index else stats2.loc[s, 'Count'] for s in all_subdomains]
    })
    comparison['Difference'] = comparison[f'{label2}_Pass_Rate'] - comparison[f'{label1}_Pass_Rate']
    comparison = comparison.sort_values('Difference', ascending=False)

    return comparison


def compare_by_question_type(df1, df2, label1, label2):
    """Compare results by question type"""

    # Get stats for each
    stats1 = df1.groupby('QuestionType').agg({
        'Correct': ['count', 'mean']
    })
    stats1.columns = ['Count', 'Pass_Rate']
    stats1['Pass_Rate'] *= 100

    stats2 = df2.groupby('QuestionType').agg({
        'Correct': ['count', 'mean']
    })
    stats2.columns = ['Count', 'Pass_Rate']
    stats2['Pass_Rate'] *= 100

    # Combine
    all_types = set(stats1.index) | set(stats2.index)

    comparison = pd.DataFrame({
        'Question_Type': list(all_types),
        f'{label1}_Pass_Rate': [stats1.loc[t, 'Pass_Rate'] if t in stats1.index else 0 for t in all_types],
        f'{label2}_Pass_Rate': [stats2.loc[t, 'Pass_Rate'] if t in stats2.index else 0 for t in all_types],
        'Questions': [stats1.loc[t, 'Count'] if t in stats1.index else stats2.loc[t, 'Count'] for t in all_types]
    })
    comparison['Difference'] = comparison[f'{label2}_Pass_Rate'] - comparison[f'{label1}_Pass_Rate']
    comparison = comparison.sort_values('Difference', ascending=False)

    return comparison


def analyze_question_level_differences(df1, df2, label1, label2):
    """Analyze which questions were answered differently"""

    # Merge on question ID
    merged = df1[['Question id', 'Correct', 'Question']].merge(
        df2[['Question id', 'Correct', 'Question']],
        on='Question id',
        suffixes=('_1', '_2')
    )

    # Both correct
    both_correct = merged[(merged['Correct_1'] == True) & (merged['Correct_2'] == True)]

    # Both incorrect
    both_incorrect = merged[(merged['Correct_1'] == False) & (merged['Correct_2'] == False)]

    # Only first correct
    only_first = merged[(merged['Correct_1'] == True) & (merged['Correct_2'] == False)]

    # Only second correct
    only_second = merged[(merged['Correct_1'] == False) & (merged['Correct_2'] == True)]

    return {
        'both_correct': len(both_correct),
        'both_incorrect': len(both_incorrect),
        'only_first': len(only_first),
        'only_second': len(only_second),
        'total': len(merged)
    }


def generate_report(overall_stats, difficulty_comp, expertise_comp, subdomain_comp,
                   qtype_comp, question_diffs, label1, label2, output_file=None):
    """Generate comprehensive comparison report"""

    report_lines = []

    # Header
    report_lines.append("=" * 100)
    report_lines.append(f"QUANTUMBENCH COMPARISON: {label1} vs {label2}")
    report_lines.append("=" * 100)
    report_lines.append("")

    # Overall Statistics
    report_lines.append("OVERALL STATISTICS")
    report_lines.append("-" * 100)
    report_lines.append(overall_stats.to_string(index=False))
    report_lines.append("")

    # Summary interpretation
    pass_rate_diff = overall_stats[overall_stats['Metric'] == 'Pass Rate (%)']['Difference'].values[0]
    token_diff = overall_stats[overall_stats['Metric'] == 'Total Tokens']['Difference'].values[0]

    report_lines.append("SUMMARY:")
    if float(pass_rate_diff) > 0:
        report_lines.append(f"  • {label2} performs BETTER by {pass_rate_diff} percentage points")
    elif float(pass_rate_diff) < 0:
        report_lines.append(f"  • {label1} performs BETTER by {abs(float(pass_rate_diff)):.2f} percentage points")
    else:
        report_lines.append(f"  • Both approaches have EQUAL performance")

    if float(token_diff) != 0:
        tokens_run1 = float(overall_stats[overall_stats['Metric'] == 'Total Tokens'][label1].values[0])
        if tokens_run1 > 0:
            pct_change = abs(float(token_diff) / tokens_run1 * 100)
            report_lines.append(f"  • {label2} uses {token_diff} more tokens ({pct_change:.1f}% {'increase' if float(token_diff) > 0 else 'decrease'})")
        else:
            report_lines.append(f"  • {label2} uses {token_diff} more tokens")
    report_lines.append("")

    # Question-level differences
    report_lines.append("QUESTION-LEVEL COMPARISON")
    report_lines.append("-" * 100)
    report_lines.append(f"Both Correct:          {question_diffs['both_correct']} ({question_diffs['both_correct']/question_diffs['total']*100:.1f}%)")
    report_lines.append(f"Both Incorrect:        {question_diffs['both_incorrect']} ({question_diffs['both_incorrect']/question_diffs['total']*100:.1f}%)")
    report_lines.append(f"Only {label1} Correct: {question_diffs['only_first']} ({question_diffs['only_first']/question_diffs['total']*100:.1f}%)")
    report_lines.append(f"Only {label2} Correct: {question_diffs['only_second']} ({question_diffs['only_second']/question_diffs['total']*100:.1f}%)")
    report_lines.append("")

    # By Difficulty
    report_lines.append("COMPARISON BY DIFFICULTY LEVEL")
    report_lines.append("-" * 100)
    report_lines.append(difficulty_comp.to_string(index=False))
    report_lines.append("")

    # By Expertise
    report_lines.append("COMPARISON BY EXPERTISE LEVEL")
    report_lines.append("-" * 100)
    report_lines.append(expertise_comp.to_string(index=False))
    report_lines.append("")

    # By Question Type
    report_lines.append("COMPARISON BY QUESTION TYPE")
    report_lines.append("-" * 100)
    report_lines.append(qtype_comp.to_string(index=False))
    report_lines.append("")

    # By Subdomain
    report_lines.append("COMPARISON BY SUBDOMAIN")
    report_lines.append("-" * 100)
    report_lines.append(subdomain_comp.to_string(index=False))
    report_lines.append("")

    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 100)

    if float(pass_rate_diff) > 2:
        report_lines.append(f"  ✓ {label2} shows significant improvement (+{pass_rate_diff}%)")
        if float(token_diff) > 0:
            tokens_run1 = float(overall_stats[overall_stats['Metric'] == 'Total Tokens'][label1].values[0])
            if tokens_run1 > 0:
                token_pct_increase = float(token_diff) / tokens_run1 * 100
                cost_benefit = float(pass_rate_diff) / token_pct_increase
                if cost_benefit > 0.5:
                    report_lines.append(f"  ✓ The performance gain justifies the increased token usage")
                else:
                    report_lines.append(f"  ⚠ Consider whether the performance gain justifies {abs(token_pct_increase):.1f}% more tokens")
            else:
                report_lines.append(f"  ✓ {label2} uses more tokens but shows performance improvement")
    elif float(pass_rate_diff) < -2:
        report_lines.append(f"  ✓ {label1} performs better - stick with this approach")
    else:
        report_lines.append(f"  • Performance is similar - choose based on cost/speed preferences")
        if float(token_diff) > 0:
            report_lines.append(f"  • {label1} is more cost-effective (fewer tokens)")

    report_lines.append("")

    # Footer
    report_lines.append("=" * 100)
    report_lines.append("END OF COMPARISON")
    report_lines.append("=" * 100)

    # Join all lines
    report = "\n".join(report_lines)

    # Print to console
    print(report)

    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nComparison report saved to: {output_file}")

    return report


def main():
    args = parse_args()

    # Validate input files
    for file_path in [args.results1, args.results2, args.human_eval_file, args.category_file]:
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

    # Determine output file path
    if args.output_file is None:
        results1_path = Path(args.results1)
        output_file = results1_path.parent / f"comparison_{args.label1.replace(' ', '_')}_vs_{args.label2.replace(' ', '_')}.txt"
    else:
        output_file = args.output_file

    print("=" * 100)
    print("Loading and Processing Data")
    print("=" * 100)
    print()

    # Load data
    print(f"Loading {args.label1} results...")
    df1 = load_and_enrich_results(args.results1, args.human_eval_file, args.category_file)
    print(f"  Loaded {len(df1)} results")

    print(f"Loading {args.label2} results...")
    df2 = load_and_enrich_results(args.results2, args.human_eval_file, args.category_file)
    print(f"  Loaded {len(df2)} results")

    print()
    print("Comparing results...")
    print()

    # Compare
    overall_stats = compare_overall_stats(df1, df2, args.label1, args.label2)
    difficulty_comp = compare_by_difficulty(df1, df2, args.label1, args.label2)
    expertise_comp = compare_by_expertise(df1, df2, args.label1, args.label2)
    subdomain_comp = compare_by_subdomain(df1, df2, args.label1, args.label2)
    qtype_comp = compare_by_question_type(df1, df2, args.label1, args.label2)
    question_diffs = analyze_question_level_differences(df1, df2, args.label1, args.label2)

    # Generate report
    generate_report(
        overall_stats, difficulty_comp, expertise_comp, subdomain_comp,
        qtype_comp, question_diffs, args.label1, args.label2, output_file
    )


if __name__ == "__main__":
    main()
