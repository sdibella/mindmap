#!/usr/bin/env python3
"""
Monthly Synthesis & Evolution Process
Deep analysis of vault patterns, learning, and evolution recommendations

Reads metadata and generates executive summary + proposes protocol updates
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter


def load_metadata(metadata_file: str) -> Dict:
    """Load vault metadata"""
    try:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Metadata file not found: {metadata_file}")
        sys.exit(1)


def analyze_category_coverage(metadata: Dict) -> Dict:
    """Analyze coverage and distribution of categories"""

    analysis = {
        'total_files': metadata['statistics']['total_files'],
        'categories': {},
        'coverage': {},
    }

    # Category coverage
    category_counts = Counter()
    for file_data in metadata['files'].values():
        for cat in file_data['primary_categories']:
            category_counts[cat] += 1

    for cat, count in category_counts.items():
        pct = 100 * count / analysis['total_files']
        analysis['categories'][cat] = {
            'count': count,
            'percentage': pct,
        }

    # Overall coverage
    files_with_cats = sum(1 for f in metadata['files'].values() if f['primary_categories'])
    analysis['coverage']['with_categories'] = {
        'count': files_with_cats,
        'percentage': 100 * files_with_cats / analysis['total_files'],
    }

    files_with_secondary = sum(1 for f in metadata['files'].values() if f['secondary_tags'])
    analysis['coverage']['with_secondary_tags'] = {
        'count': files_with_secondary,
        'percentage': 100 * files_with_secondary / analysis['total_files'],
    }

    return analysis


def analyze_confidence_distribution(metadata: Dict) -> Dict:
    """Analyze confidence score distribution"""

    analysis = {
        'high': {'count': 0, 'threshold': 0.85},
        'medium': {'count': 0, 'threshold': 0.65},
        'low': {'count': 0, 'threshold': 0.0},
    }

    for file_data in metadata['files'].values():
        conf = file_data['confidence']
        if conf >= 0.85:
            analysis['high']['count'] += 1
        elif conf >= 0.65:
            analysis['medium']['count'] += 1
        else:
            analysis['low']['count'] += 1

    total = metadata['statistics']['total_files']
    for level in analysis.values():
        level['percentage'] = 100 * level['count'] / total if total > 0 else 0

    return analysis


def analyze_relationship_patterns(metadata: Dict) -> Dict:
    """Analyze relationship patterns and hub atoms"""

    analysis = {
        'total_strong_relationships': metadata['statistics']['total_strong_relationships'],
        'total_medium_relationships': metadata['statistics']['total_medium_relationships'],
        'hub_atoms': [],
        'isolated_atoms': [],
        'average_connections': 0.0,
    }

    # Find hub atoms and isolated atoms
    connection_counts = {}

    for file_id, rels in metadata['relationships'].items():
        connections = len(rels['strong_links']) + len(rels['medium_links'])
        connection_counts[file_id] = connections

    if connection_counts:
        analysis['average_connections'] = sum(connection_counts.values()) / len(connection_counts)

        # Top 10 most connected
        sorted_atoms = sorted(connection_counts.items(), key=lambda x: -x[1])
        analysis['hub_atoms'] = [
            {'atom': atom, 'connections': count}
            for atom, count in sorted_atoms[:10]
        ]

        # Isolated atoms (0 strong, 0 medium)
        analysis['isolated_atoms'] = [
            atom for atom, count in connection_counts.items() if count == 0
        ]

    return analysis


def detect_emerging_categories(metadata: Dict) -> List[Dict]:
    """Detect potential new categories from co-occurrence patterns"""

    emerging = []

    # Find strong category co-occurrences
    co_occurrence = Counter()

    for file_data in metadata['files'].values():
        cats = tuple(sorted(file_data['primary_categories']))
        if len(cats) >= 2:
            co_occurrence[cats] += 1

    # Find patterns that appear in 5+ files
    for cat_combo, count in co_occurrence.most_common(10):
        if count >= 5:
            emerging.append({
                'pattern': ' + '.join(cat_combo),
                'frequency': count,
                'recommendation': f"Consider consolidating or clarifying relationship between {' and '.join(cat_combo)}"
            })

    return emerging


def calculate_metrics_trends(metadata: Dict, previous_synthesis: Dict = None) -> Dict:
    """Calculate metrics and compare with previous month if available"""

    current = {
        'timestamp': metadata['generated'],
        'total_files': metadata['statistics']['total_files'],
        'categorized_files': metadata['statistics']['files_with_categories'],
        'files_with_secondary': metadata['statistics']['files_with_secondary_tags'],
        'strong_relationships': metadata['statistics']['total_strong_relationships'],
        'medium_relationships': metadata['statistics']['total_medium_relationships'],
    }

    # Calculate coverage metrics
    current['coverage_percentage'] = (
        100 * current['categorized_files'] / current['total_files']
        if current['total_files'] > 0 else 0
    )

    # Compare with previous if available
    trends = {'current': current}

    if previous_synthesis:
        trends['previous'] = previous_synthesis.get('current', {})
        trends['changes'] = {}

        for key in current:
            if key in trends['previous']:
                prev_val = trends['previous'][key]
                curr_val = current[key]
                if isinstance(curr_val, (int, float)):
                    trends['changes'][key] = curr_val - prev_val

    return trends


def generate_synthesis_report(metadata: Dict, output_file: str = 'MONTHLY_SYNTHESIS.md'):
    """Generate comprehensive monthly synthesis report"""

    # Analysis
    category_analysis = analyze_category_coverage(metadata)
    confidence_analysis = analyze_confidence_distribution(metadata)
    relationship_analysis = analyze_relationship_patterns(metadata)
    emerging_cats = detect_emerging_categories(metadata)
    metrics = calculate_metrics_trends(metadata)

    report = [
        "---",
        "title: Monthly Vault Intelligence Synthesis",
        f"generated: {datetime.now().isoformat()}",
        f"month: {datetime.now().strftime('%Y-%m')}",
        "---",
        "",
        "# Monthly Vault Intelligence Synthesis",
        "",
        f"**Month:** {datetime.now().strftime('%B %Y')}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Executive Summary
    report.extend([
        "## Executive Summary",
        "",
        f"- Total files in vault: {metadata['statistics']['total_files']}",
        f"- Files with primary categories: {metadata['statistics']['files_with_categories']} ({100*metadata['statistics']['files_with_categories']/metadata['statistics']['total_files']:.1f}%)",
        f"- Strong relationships discovered: {metadata['statistics']['total_strong_relationships']}",
        f"- Average connections per file: {relationship_analysis['average_connections']:.1f}",
        "",
    ])

    # Category Distribution
    report.extend([
        "## 📊 Category Distribution",
        "",
    ])

    sorted_cats = sorted(category_analysis['categories'].items(), key=lambda x: -x[1]['count'])
    for cat, data in sorted_cats:
        report.append(f"- **{cat}**: {data['count']} files ({data['percentage']:.1f}%)")

    report.extend([
        "",
        f"**Coverage:** {category_analysis['coverage']['with_categories']['percentage']:.1f}% of files have categories",
        "",
    ])

    # Confidence Analysis
    report.extend([
        "## 🎯 Confidence Analysis",
        "",
        f"- **High confidence (≥0.85):** {confidence_analysis['high']['count']} files ({confidence_analysis['high']['percentage']:.1f}%)",
        f"- **Medium confidence (0.65-0.84):** {confidence_analysis['medium']['count']} files ({confidence_analysis['medium']['percentage']:.1f}%)",
        f"- **Low confidence (<0.65):** {confidence_analysis['low']['count']} files ({confidence_analysis['low']['percentage']:.1f}%)",
        "",
    ])

    # Relationship Insights
    report.extend([
        "## 🔗 Relationship Insights",
        "",
        f"- **Total strong relationships:** {relationship_analysis['total_strong_relationships']}",
        f"- **Total medium relationships:** {relationship_analysis['total_medium_relationships']}",
        f"- **Average connections per file:** {relationship_analysis['average_connections']:.2f}",
        "",
    ])

    if relationship_analysis['hub_atoms']:
        report.append("**Hub Atoms (most connected):**")
        for item in relationship_analysis['hub_atoms'][:5]:
            report.append(f"- **{item['atom']}**: {item['connections']} connections")
        report.append("")

    if relationship_analysis['isolated_atoms']:
        report.append(f"**Isolated Atoms (no connections):** {len(relationship_analysis['isolated_atoms'])}")
        for atom in relationship_analysis['isolated_atoms'][:5]:
            report.append(f"- {atom}")
        if len(relationship_analysis['isolated_atoms']) > 5:
            report.append(f"- ... and {len(relationship_analysis['isolated_atoms']) - 5} more")
        report.append("")

    # Emerging Patterns
    if emerging_cats:
        report.extend([
            "## 💡 Emerging Patterns & Opportunities",
            "",
            "These category combinations appear frequently and might warrant protocol updates:",
            "",
        ])

        for pattern in emerging_cats[:5]:
            report.append(f"- **{pattern['pattern']}** ({pattern['frequency']} files)")
            report.append(f"  - {pattern['recommendation']}")

        report.append("")

    # Recommendations
    report.extend([
        "## 🎓 Recommendations for Next Month",
        "",
        "- [ ] Review low-confidence files from weekly reviews",
        "- [ ] Investigate emerging category patterns above",
        "- [ ] Connect with isolated atoms through manual review",
        "- [ ] Consider protocol updates based on patterns",
        "- [ ] Monitor hub atoms for overcrowding",
        "",
    ])

    # Protocol Update Proposals
    report.extend([
        "## 📋 Proposed Protocol Updates",
        "",
        "Based on this month's data, consider:",
        "",
        "- [ ] Merge or clarify overlapping categories",
        "- [ ] Update category patterns if false positives detected",
        "- [ ] Adjust confidence thresholds if needed",
        "- [ ] Create new secondary tags based on trends",
        "- [ ] Document new edge cases discovered",
        "",
    ])

    # Next Steps
    report.extend([
        "## 🚀 Action Items",
        "",
        "1. **Review** this synthesis with Stefan",
        "2. **Approve** or modify recommendations",
        "3. **Update** OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md with approved changes",
        "4. **Archive** this synthesis in docs/syntheses/",
        "5. **Continue** nightly categorization with updated protocol",
        "",
    ])

    # Footer
    report.extend([
        "---",
        "",
        "*This synthesis was automatically generated by the monthly intelligence process.*",
        "*Archive this report for future reference and trend tracking.*",
    ])

    report_text = "\n".join(report)

    with open(output_file, 'w') as f:
        f.write(report_text)

    print(f"📄 Synthesis report saved to: {output_file}")
    return report_text


def propose_protocol_updates(analysis: Dict) -> List[str]:
    """Generate specific protocol update proposals"""

    proposals = []

    # Check for overcrowded hub atoms
    # (Implementation would go here)

    return proposals


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Monthly Vault Intelligence Synthesis')
    parser.add_argument('--metadata', default='vault-metadata.json',
                        help='Input metadata file')
    parser.add_argument('--output', default='MONTHLY_SYNTHESIS.md',
                        help='Output synthesis file')
    parser.add_argument('--protocol', default='docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md',
                        help='Protocol file to propose updates for')

    args = parser.parse_args()

    print("=" * 70)
    print("📊 MONTHLY VAULT INTELLIGENCE SYNTHESIS")
    print("=" * 70)
    print()

    # Load metadata
    metadata = load_metadata(args.metadata)

    # Generate synthesis
    report_text = generate_synthesis_report(metadata, args.output)

    print("\n" + "=" * 70)
    print("✅ Monthly synthesis complete!")
    print("=" * 70)
    print()

    # Print highlights
    category_analysis = analyze_category_coverage(metadata)
    relationship_analysis = analyze_relationship_patterns(metadata)

    print(f"📈 Key Metrics:")
    print(f"  Total files: {metadata['statistics']['total_files']}")
    print(f"  Categorized: {metadata['statistics']['files_with_categories']} ({100*metadata['statistics']['files_with_categories']/metadata['statistics']['total_files']:.1f}%)")
    print(f"  Strong relationships: {metadata['statistics']['total_strong_relationships']}")
    print(f"  Avg connections: {relationship_analysis['average_connections']:.2f} per file")
    print()
    print(f"📄 Synthesis report: {args.output}")
    print()


if __name__ == '__main__':
    main()
