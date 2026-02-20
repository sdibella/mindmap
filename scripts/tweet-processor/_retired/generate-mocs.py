#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 5: MOC Auto-Generation

Creates category-specific Maps of Content with:
- Overview descriptions
- Foundational concepts (most-connected atoms)
- Related topics (cross-category connections)
- Complete atom listings
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


def extract_frontmatter(content: str) -> Dict:
    """Extract frontmatter from markdown"""
    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm


def extract_categories(content: str) -> Set[str]:
    """Extract categories from atom content"""
    categories = {
        'ai-agents': r'\bagent\b|\bagentic\b|\bautonomous\s+system|\borchestr',
        'prediction-markets': r'polymarket|kalshi|prediction\s+market|\bforecast\b|weather\s+bot',
        'crypto-defi': r'\bcrypto\b|\bblockchain\b|bitcoin|ethereum|\bdefi\b|\bdao\b|\bnft\b',
        'software-development': r'\bcode\b|\bprogramming\b|\bsdk\b|\bapi\b|\bgithub\b|python|javascript|typescript|react',
        'ai-models-research': r'\bllm\b|large\s+language\s+model|\bmachine\s+learning\b|\bgpu\b|anthropic|openai|claude',
        'stock-trading-finance': r'\bstock\b|\bportfolio\b|\bdividend\b|\bswing\s+trade|oversold',
        'business-entrepreneurship': r'\bstartup\b|\bentrepreneur\b|\bfounder\b|\bbusiness\s+model\b|\bgrowth\b|\bsaas\b',
        'systems-architecture': r'\barchitecture\b|\bsystem\s+design\b|\bscalability\b|\binfrastructure\b',
        'learning-resources': r'\bguide\b|\btutorial\b|\bhow\s+to\b|\broadmap\b|\bcourse\b|\bblueprint\b',
    }

    matched = set()
    content_lower = content.lower()

    for cat, pattern in categories.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            matched.add(cat)

    return matched


def categorize_atoms(atoms_dir: Path) -> Dict[str, List[str]]:
    """Categorize all atoms"""
    category_atoms = {}

    for atom_file in sorted(atoms_dir.glob("*.md")):
        try:
            content = atom_file.read_text(encoding='utf-8')
            cats = extract_categories(content)

            for cat in cats:
                if cat not in category_atoms:
                    category_atoms[cat] = []
                category_atoms[cat].append(atom_file.stem)

        except:
            continue

    return category_atoms


def get_top_atoms(category: str, atom_ids: List[str], relationships: Dict, top_n: int = 5) -> List[str]:
    """Get most-connected atoms in a category"""

    # Count strong connections within category
    connection_counts = {}

    for atom_id in atom_ids:
        if atom_id in relationships:
            strong_links = relationships[atom_id].get('strong_links', [])
            connection_counts[atom_id] = len([l for l in strong_links if l in atom_ids])

    # Sort by connection count
    sorted_atoms = sorted(connection_counts.items(), key=lambda x: -x[1])

    return [atom for atom, _ in sorted_atoms[:top_n]]


def get_cross_category_atoms(category: str, atom_ids: List[str], relationships: Dict, top_n: int = 5) -> List[str]:
    """Get atoms with cross-category connections"""

    cross_category = {}

    for atom_id in atom_ids:
        if atom_id in relationships:
            strong_links = relationships[atom_id].get('strong_links', [])
            # Count links outside category
            external_links = [l for l in strong_links if l not in atom_ids]
            if external_links:
                cross_category[atom_id] = len(external_links)

    # Sort by cross-category connections
    sorted_atoms = sorted(cross_category.items(), key=lambda x: -x[1])

    return [atom for atom, _ in sorted_atoms[:top_n]]


def create_moc(category: str, atom_ids: List[str], relationships: Dict, atoms_dir: Path) -> str:
    """Generate MOC content"""

    # Category descriptions
    descriptions = {
        'prediction-markets': 'Market prediction, forecasting, and trading on platforms like Polymarket and Kalshi',
        'crypto-defi': 'Cryptocurrency, blockchain, DeFi protocols, and decentralized applications',
        'learning-resources': 'Guides, tutorials, courses, blueprints, and educational materials',
        'software-development': 'Programming, APIs, SDKs, architecture patterns, and development practices',
        'people-personas': 'Notable people, thought leaders, and personality profiles in tech and finance',
        'ai-agents': 'AI agents, autonomous systems, and agentic architectures',
        'ai-models-research': 'Large language models, machine learning, and AI research',
        'stock-trading-finance': 'Stock trading, portfolio management, and financial strategies',
        'business-entrepreneurship': 'Startups, entrepreneurship, business models, and growth strategies',
    }

    description = descriptions.get(category, 'A collection of related topics')

    # Get representative atoms
    top_atoms = get_top_atoms(category, atom_ids, relationships)
    cross_atoms = get_cross_category_atoms(category, atom_ids, relationships)

    today = datetime.now().strftime('%Y-%m-%d')

    # Build MOC content
    lines = [
        '---',
        'tags: [moc, category]',
        f'created: {today}',
        f'updated: {today}',
        '---',
        '',
        f'# {category.replace("-", " ").title()} MOC',
        '',
        '## Overview',
        '',
        description,
        '',
        f'This Map of Content organizes {len(atom_ids)} atoms across this topic area.',
        '',
    ]

    # Foundational Concepts
    if top_atoms:
        lines.extend([
            '## Foundational Concepts',
            '',
            'Most-connected atoms in this category:',
            '',
        ])

        for atom_id in top_atoms:
            lines.append(f'- [[{atom_id}]]')

        lines.append('')

    # Related Topics (cross-category)
    if cross_atoms:
        lines.extend([
            '## Related Topics',
            '',
            'Atoms with strong cross-category connections:',
            '',
        ])

        for atom_id in cross_atoms[:3]:
            lines.append(f'- [[{atom_id}]]')

        lines.append('')

    # All Atoms
    lines.extend([
        f'## All Atoms ({len(atom_ids)} total)',
        '',
    ])

    sorted_atoms = sorted(atom_ids)
    for atom_id in sorted_atoms:
        lines.append(f'- [[{atom_id}]]')

    return '\n'.join(lines)


def add_moc_backlinks(moc_file: Path, atom_ids: List[str], atoms_dir: Path):
    """Add MOC reference to atom See Also sections"""

    moc_name = moc_file.stem
    moc_link = f"maps/{moc_name}"

    for atom_id in atom_ids:
        atom_file = atoms_dir / f"{atom_id}.md"

        if not atom_file.exists():
            continue

        try:
            content = atom_file.read_text(encoding='utf-8')

            # Check if MOC link already in See Also
            if moc_link in content:
                continue

            # Find See Also section
            see_also_match = re.search(r'## See Also\n', content)

            if see_also_match:
                # Insert MOC link at end of See Also
                insert_pos = see_also_match.end()

                # Find next section
                next_section = re.search(r'\n## ', content[insert_pos:])
                if next_section:
                    end_pos = insert_pos + next_section.start()
                else:
                    end_pos = len(content)

                # Extract existing See Also content
                see_also_content = content[insert_pos:end_pos]

                # Find last link line
                lines = see_also_content.split('\n')
                last_link_idx = -1

                for i, line in enumerate(lines):
                    if line.strip().startswith('- [['):
                        last_link_idx = i

                if last_link_idx >= 0:
                    # Insert after last link
                    insert_line = last_link_idx + 1
                    lines.insert(insert_line, f'- [[{moc_link}]]')
                    new_see_also = '\n'.join(lines)
                    updated_content = content[:insert_pos] + new_see_also + content[end_pos:]

                    atom_file.write_text(updated_content, encoding='utf-8')

        except Exception as e:
            print(f"⚠️  Failed to update {atom_id} with MOC reference: {e}")


def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")
    maps_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/maps")
    relationships_file = Path("atom-relationships.json")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    if not relationships_file.exists():
        print(f"❌ Relationships file not found: {relationships_file}")
        sys.exit(1)

    # Create maps directory if needed
    maps_dir.mkdir(exist_ok=True)

    # Target categories for new MOCs
    target_categories = [
        'prediction-markets',
        'crypto-defi',
        'learning-resources',
        'software-development',
    ]

    # Load relationships
    with open(relationships_file, 'r') as f:
        relationships = json.load(f)

    # Categorize all atoms
    print("📊 Categorizing atoms...")
    category_atoms = categorize_atoms(atoms_dir)

    print(f"🗺️  Generating MOCs for {len(target_categories)} categories...")

    created = 0

    for category in target_categories:
        atom_ids = category_atoms.get(category, [])

        if not atom_ids:
            print(f"  ⚠️  {category}: No atoms found")
            continue

        # Generate MOC content
        moc_content = create_moc(category, atom_ids, relationships, atoms_dir)

        # Write MOC file
        moc_file = maps_dir / f"{category}.md"

        try:
            moc_file.write_text(moc_content, encoding='utf-8')
            created += 1
            print(f"  ✓ {category}: {len(atom_ids)} atoms")

            # Add MOC backlinks to atoms
            if '--add-backlinks' in sys.argv:
                add_moc_backlinks(moc_file, atom_ids, atoms_dir)

        except Exception as e:
            print(f"  ✗ {category}: {e}")

    print("\n" + "=" * 70)
    print("✅ MOC GENERATION COMPLETE")
    print("=" * 70)

    print(f"\n📈 Results:")
    print(f"  MOCs created: {created}")
    print(f"  Location: {maps_dir}")

    print(f"\n📂 New MOCs:")
    for category in target_categories:
        moc_file = maps_dir / f"{category}.md"
        if moc_file.exists():
            print(f"  - [[maps/{category}]]")

    print("\n" + "=" * 70 + "\n")

    if '--add-backlinks' not in sys.argv:
        print("💡 Run with --add-backlinks to add MOC references to atom See Also sections")


if __name__ == '__main__':
    main()
