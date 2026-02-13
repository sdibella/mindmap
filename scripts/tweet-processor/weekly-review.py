#!/usr/bin/env python3
"""
Weekly Review Process
Surfaces anomalies, edge cases, and emerging patterns for human review

Reads metadata from vault-intelligence-engine.py and generates review report
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from collections import Counter


def load_metadata(metadata_file: str) -> Dict:
    """Load vault metadata"""
    try:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Metadata file not found: {metadata_file}")
        print("Run vault-intelligence-engine.py first")
        sys.exit(1)


def identify_low_confidence(metadata: Dict, threshold: float = 0.65) -> List[str]:
    """Find files with low confidence categorization"""
    low_conf = []

    for file_id, file_data in metadata['files'].items():
        if file_data['confidence'] < threshold:
            low_conf.append({
                'file': file_id,
                'confidence': file_data['confidence'],
                'categories': file_data['primary_categories'],
                'tags': file_data['secondary_tags'],
            })

    return sorted(low_conf, key=lambda x: x['confidence'])


def identify_uncategorized(metadata: Dict) -> List[str]:
    """Find files with no categories"""
    uncategorized = []

    for file_id, file_data in metadata['files'].items():
        if not file_data['primary_categories']:
            uncategorized.append({
                'file': file_id,
                'tags': file_data['secondary_tags'],
            })

    return uncategorized


def identify_edge_cases(metadata: Dict) -> Dict:
    """Find edge cases and unusual patterns"""

    edge_cases = {
        'multi_category_abundance': [],  # Files with 5+ categories
        'single_secondary': [],  # Files with only secondary tags
        'no_keywords': [],  # Files with no extractable keywords
    }

    for file_id, file_data in metadata['files'].items():
        if len(file_data['primary_categories']) >= 5:
            edge_cases['multi_category_abundance'].append(file_id)

        if not file_data['primary_categories'] and file_data['secondary_tags']:
            edge_cases['single_secondary'].append(file_id)

    return edge_cases


def detect_emerging_patterns(metadata: Dict) -> Dict:
    """Detect patterns that might indicate new categories"""

    patterns = {
        'category_clusters': {},  # Categories often appearing together
        'secondary_tag_trends': {},  # Secondary tags by category
        'common_author_groups': {},  # Authors with multiple files
    }

    # Category co-occurrence
    for file_data in metadata['files'].values():
        cats = tuple(sorted(file_data['primary_categories']))
        if cats and len(cats) > 1:
            patterns['category_clusters'][cats] = patterns['category_clusters'].get(cats, 0) + 1

    # Secondary tags by category
    for file_data in metadata['files'].values():
        for cat in file_data['primary_categories']:
            for tag in file_data['secondary_tags']:
                key = f"{cat}+{tag}"
                patterns['secondary_tag_trends'][key] = patterns['secondary_tag_trends'].get(key, 0) + 1

    # Author groups
    for file_data in metadata['files'].values():
        author = file_data['author']
        if author:
            patterns['common_author_groups'][author] = patterns['common_author_groups'].get(author, 0) + 1

    return patterns


def generate_review_report(metadata: Dict, output_file: str = 'WEEKLY_REVIEW.md'):
    """Generate markdown review report"""

    low_conf = identify_low_confidence(metadata)
    uncategorized = identify_uncategorized(metadata)
    edge_cases = identify_edge_cases(metadata)
    patterns = detect_emerging_patterns(metadata)

    report = [
        "---",
        "title: Weekly Vault Intelligence Review",
        f"generated: {datetime.now().isoformat()}",
        "---",
        "",
        "# Weekly Vault Intelligence Review",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Summary
    report.extend([
        "## Summary",
        "",
        f"- Total files analyzed: {metadata['statistics']['total_files']}",
        f"- Files with low confidence: {len(low_conf)}",
        f"- Uncategorized files: {len(uncategorized)}",
        f"- Strong relationships found: {metadata['statistics']['total_strong_relationships']}",
        "",
    ])

    # Low Confidence Items (INTERACTIVE)
    if low_conf:
        report.extend([
            "## ⚠️ Low Confidence Categorizations (Review Needed)",
            "",
            "These files have unclear or weak categorization. Consider reviewing or providing guidance.",
            "",
        ])

        for item in low_conf[:20]:  # Show top 20
            report.append(f"- **{item['file']}** (confidence: {item['confidence']:.2f})")
            if item['categories']:
                report.append(f"  - Categories: {', '.join(item['categories'])}")
            if item['tags']:
                report.append(f"  - Secondary: {', '.join(item['tags'])}")

        if len(low_conf) > 20:
            report.append(f"\n... and {len(low_conf) - 20} more")

        report.append("")

    # Uncategorized Items
    if uncategorized:
        report.extend([
            "## 🔍 Uncategorized Files",
            "",
            f"Found {len(uncategorized)} files with no primary categories.",
            "",
        ])

        for item in uncategorized[:10]:
            report.append(f"- **{item['file']}**")

        if len(uncategorized) > 10:
            report.append(f"\n... and {len(uncategorized) - 10} more")

        report.append("")

    # Edge Cases
    if any(edge_cases.values()):
        report.extend([
            "## 🎯 Edge Cases & Anomalies",
            "",
        ])

        if edge_cases['multi_category_abundance']:
            report.append(f"**Files with 5+ categories ({len(edge_cases['multi_category_abundance'])}):**")
            for f in edge_cases['multi_category_abundance'][:5]:
                report.append(f"- {f}")
            if len(edge_cases['multi_category_abundance']) > 5:
                report.append(f"- ... and {len(edge_cases['multi_category_abundance']) - 5} more")
            report.append("")

        if edge_cases['single_secondary']:
            report.append(f"**Files with only secondary tags ({len(edge_cases['single_secondary'])}):**")
            for f in edge_cases['single_secondary'][:5]:
                report.append(f"- {f}")
            if len(edge_cases['single_secondary']) > 5:
                report.append(f"- ... and {len(edge_cases['single_secondary']) - 5} more")
            report.append("")

    # Emerging Patterns
    report.extend([
        "## 💡 Emerging Patterns",
        "",
    ])

    # Top category co-occurrences
    if patterns['category_clusters']:
        report.append("**Frequently Co-Occurring Categories:**")
        sorted_clusters = sorted(patterns['category_clusters'].items(), key=lambda x: -x[1])
        for cats, count in sorted_clusters[:10]:
            cat_str = " + ".join(cats)
            report.append(f"- {cat_str} ({count} files)")
        report.append("")

    # Top secondary tag trends
    if patterns['secondary_tag_trends']:
        report.append("**Secondary Tag Trends (top 10):**")
        sorted_trends = sorted(patterns['secondary_tag_trends'].items(), key=lambda x: -x[1])
        for combo, count in sorted_trends[:10]:
            report.append(f"- {combo}: {count} files")
        report.append("")

    # Prolific authors
    if patterns['common_author_groups']:
        report.append("**Most Prolific Authors:**")
        sorted_authors = sorted(patterns['common_author_groups'].items(), key=lambda x: -x[1])
        for author, count in sorted_authors[:5]:
            if author:  # Skip empty authors
                report.append(f"- {author}: {count} files")
        report.append("")

    # Suggestions
    report.extend([
        "## 🎓 Suggestions for Next Month",
        "",
        "- [ ] Review all low-confidence items above",
        "- [ ] Consider creating guides for commonly co-occurring categories",
        "- [ ] Investigate uncategorized files for new patterns",
        "- [ ] Verify secondary tag accuracy",
        "",
        "---",
        "",
        "*Review this report and provide feedback to improve next month's categorization.*",
    ])

    # Write report
    report_text = "\n".join(report)

    with open(output_file, 'w') as f:
        f.write(report_text)

    print(f"📝 Review report saved to: {output_file}")
    return report_text


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Weekly Vault Intelligence Review')
    parser.add_argument('--metadata', default='vault-metadata.json',
                        help='Input metadata file')
    parser.add_argument('--output', default='WEEKLY_REVIEW.md',
                        help='Output review file')

    args = parser.parse_args()

    print("=" * 70)
    print("📋 WEEKLY VAULT INTELLIGENCE REVIEW")
    print("=" * 70)
    print()

    # Load metadata
    metadata = load_metadata(args.metadata)

    # Generate report
    report_text = generate_review_report(metadata, args.output)

    print("\n" + "=" * 70)
    print("✅ Weekly review complete!")
    print("=" * 70)
    print()

    # Print summary
    low_conf = identify_low_confidence(metadata)
    uncategorized = identify_uncategorized(metadata)

    print(f"📊 Summary:")
    print(f"  Total files: {metadata['statistics']['total_files']}")
    print(f"  Low confidence: {len(low_conf)}")
    print(f"  Uncategorized: {len(uncategorized)}")
    print(f"  Strong relationships: {metadata['statistics']['total_strong_relationships']}")
    print()
    print(f"👁️  Review report: {args.output}")
    print()


if __name__ == '__main__':
    main()
