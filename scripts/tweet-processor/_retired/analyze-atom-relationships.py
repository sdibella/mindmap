#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 1: Similarity Analysis Engine

Analyzes relationships between all atoms using:
- Tag overlap (40% weight)
- Content keyword matching (30% weight)
- Category clustering (20% weight)
- Author connection (10% weight)

Output: atom-relationships.json with relationship scores and recommendations
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import Counter
import string

# Category patterns from categorize-atoms.py
CATEGORY_PATTERNS = {
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

# Common stop words to exclude from keyword analysis
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 'just', 'your', 'my', 'his', 'her', 'its', 'our',
    'their', 'if', 'then', 'because', 'while', 'before', 'after', 'above', 'below',
    'am', 'being', 'about', 'through', 'during', 'up', 'down', 'out', 'off', 'over', 'under',
    'it', 'me', 'him', 'her', 'us', 'them', 'that', 'this', 'which', 'who', 'what',
}


def extract_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter from markdown file"""
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
    content_lower = content.lower()
    categories = set()

    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            categories.add(category)

    return categories


def extract_tags(frontmatter: Dict) -> Set[str]:
    """Extract tags from frontmatter"""
    tags_str = frontmatter.get('tags', '')
    if not tags_str:
        return set()

    # Handle both comma-separated and bracketed formats
    tags_str = tags_str.strip('[]')
    tags = [t.strip() for t in tags_str.split(',')]
    return {t for t in tags if t}


def extract_keywords(content: str, top_n: int = 10) -> List[str]:
    """Extract top keywords from content (excluding stop words)"""
    # Remove frontmatter
    content = re.sub(r'^---[\s\S]*?---\n', '', content)

    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-z]+\b', content.lower())

    # Filter out stop words and short words
    words = [w for w in words if w not in STOP_WORDS and len(w) > 3]

    # Get frequency count
    counter = Counter(words)

    # Return top N keywords
    return [word for word, _ in counter.most_common(top_n)]


def calculate_tag_overlap_score(tags1: Set[str], tags2: Set[str]) -> float:
    """Calculate similarity based on tag overlap (40% weight)"""
    if not tags1 or not tags2:
        return 0.0

    overlap = len(tags1 & tags2)

    if overlap == 0:
        return 0.0
    elif overlap >= 3:
        return 0.9  # High relevance
    elif overlap == 2:
        return 0.7  # Medium relevance
    else:  # overlap == 1
        return 0.4  # Low relevance


def calculate_keyword_score(keywords1: List[str], keywords2: List[str]) -> float:
    """Calculate similarity based on keyword overlap (30% weight)"""
    if not keywords1 or not keywords2:
        return 0.0

    set1 = set(keywords1)
    set2 = set(keywords2)

    overlap = len(set1 & set2)

    if overlap == 0:
        return 0.0
    elif overlap >= 5:
        return 0.9  # Strong
    elif overlap >= 2:
        return 0.5  # Moderate
    else:
        return 0.2  # Weak


def calculate_category_score(categories1: Set[str], categories2: Set[str]) -> float:
    """Calculate similarity based on category overlap (20% weight)"""
    if not categories1 or not categories2:
        return 0.0

    overlap = len(categories1 & categories2)

    if overlap > 0:
        return 0.7  # Same/complementary category

    return 0.0


def calculate_author_score(author1: str, author2: str) -> float:
    """Calculate similarity based on author (10% weight)"""
    if author1 and author1 == author2:
        return 0.5  # Potential thematic connection
    return 0.0


def calculate_relationship_score(atom1_data: Dict, atom2_data: Dict) -> float:
    """Calculate overall relationship score between two atoms"""
    # Extract data
    tags1 = atom1_data['tags']
    tags2 = atom2_data['tags']
    keywords1 = atom1_data['keywords']
    keywords2 = atom2_data['keywords']
    categories1 = atom1_data['categories']
    categories2 = atom2_data['categories']
    author1 = atom1_data['author']
    author2 = atom2_data['author']

    # Calculate component scores
    tag_score = calculate_tag_overlap_score(tags1, tags2)
    keyword_score = calculate_keyword_score(keywords1, keywords2)
    category_score = calculate_category_score(categories1, categories2)
    author_score = calculate_author_score(author1, author2)

    # Weighted combination (adjusted to generate more connections)
    overall_score = (
        tag_score * 0.35 +
        keyword_score * 0.35 +
        category_score * 0.20 +
        author_score * 0.10
    )

    # Apply boosting for multi-category atoms (56% of atoms)
    # This increases scores for atoms that span multiple categories
    if len(categories1) > 1 and len(categories2) > 1:
        overall_score *= 1.15

    return overall_score


def analyze_atoms(atoms_dir: Path) -> Tuple[Dict, Dict]:
    """Analyze all atoms and calculate relationships"""

    atom_data = {}
    atoms_list = []

    print("📖 Loading and analyzing atoms...")

    # Load all atoms
    for atom_file in sorted(atoms_dir.glob("*.md")):
        try:
            content = atom_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)

            atom_id = atom_file.stem

            atom_data[atom_id] = {
                'filename': atom_file.name,
                'tags': extract_tags(frontmatter),
                'keywords': extract_keywords(content),
                'categories': extract_categories(content),
                'author': frontmatter.get('author', ''),
            }

            atoms_list.append(atom_id)

        except Exception as e:
            print(f"⚠️  Error loading {atom_file.name}: {e}")
            continue

    print(f"✅ Loaded {len(atoms_list)} atoms")

    # Calculate all pairwise relationships
    print("🔗 Calculating relationships...")
    relationships = {}

    for i, atom1_id in enumerate(atoms_list):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(atoms_list)}")

        strong_links = []
        medium_links = []
        scores = {}

        for atom2_id in atoms_list:
            if atom1_id == atom2_id:
                continue

            score = calculate_relationship_score(
                atom_data[atom1_id],
                atom_data[atom2_id]
            )

            # Adjusted thresholds for richer graph
            # Strong: >= 0.65 (target 3-5 per atom)
            # Medium: 0.50-0.64 (broader context)
            if score >= 0.65:
                strong_links.append(atom2_id)
                scores[atom2_id] = score
            elif score >= 0.50:
                medium_links.append(atom2_id)
                scores[atom2_id] = score

        # Sort by score
        strong_links.sort(key=lambda x: scores.get(x, 0), reverse=True)
        medium_links.sort(key=lambda x: scores.get(x, 0), reverse=True)

        relationships[atom1_id] = {
            'strong_links': strong_links,
            'medium_links': medium_links,
            'scores': scores,
        }

    return atom_data, relationships


def generate_report(atom_data: Dict, relationships: Dict):
    """Generate analysis report"""

    print("\n" + "=" * 70)
    print("📊 RELATIONSHIP ANALYSIS REPORT")
    print("=" * 70)

    total_atoms = len(relationships)

    # Overall statistics
    total_strong = sum(len(r['strong_links']) for r in relationships.values())
    total_medium = sum(len(r['medium_links']) for r in relationships.values())
    atoms_with_strong = sum(1 for r in relationships.values() if r['strong_links'])
    atoms_with_medium = sum(1 for r in relationships.values() if r['medium_links'])

    print(f"\n📈 Overall Statistics:")
    print(f"  Total atoms: {total_atoms}")
    print(f"  Total strong relationships: {total_strong}")
    print(f"  Total medium relationships: {total_medium}")
    print(f"  Total relationships: {total_strong + total_medium}")
    print(f"  Atoms with strong links: {atoms_with_strong} ({100*atoms_with_strong/total_atoms:.1f}%)")
    print(f"  Atoms with medium links: {atoms_with_medium} ({100*atoms_with_medium/total_atoms:.1f}%)")

    avg_strong = total_strong / total_atoms if total_atoms > 0 else 0
    avg_medium = total_medium / total_atoms if total_atoms > 0 else 0
    avg_total = (total_strong + total_medium) / total_atoms if total_atoms > 0 else 0

    print(f"\n📊 Average Links Per Atom:")
    print(f"  Strong links: {avg_strong:.2f}")
    print(f"  Medium links: {avg_medium:.2f}")
    print(f"  Total: {avg_total:.2f}")

    # Category distribution
    print(f"\n🏷️  Category Distribution:")
    category_counts = {}
    for data in atom_data.values():
        for cat in data['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Top connected atoms
    print(f"\n🌟 Top 10 Most Connected Atoms (by strong links):")
    sorted_atoms = sorted(
        relationships.items(),
        key=lambda x: len(x[1]['strong_links']),
        reverse=True
    )

    for atom_id, rels in sorted_atoms[:10]:
        strong = len(rels['strong_links'])
        medium = len(rels['medium_links'])
        print(f"  {atom_id}: {strong} strong, {medium} medium")

    # Orphaned atoms (no relationships)
    orphaned = [
        atom_id for atom_id, rels in relationships.items()
        if not rels['strong_links'] and not rels['medium_links']
    ]

    print(f"\n⚠️  Orphaned Atoms (no relationships): {len(orphaned)}")
    if orphaned and len(orphaned) <= 20:
        for atom_id in orphaned[:20]:
            print(f"  - {atom_id}")

    print("\n" + "=" * 70 + "\n")


def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    # Analyze atoms
    atom_data, relationships = analyze_atoms(atoms_dir)

    # Generate report if requested
    if '--report' in sys.argv:
        generate_report(atom_data, relationships)

    # Save results
    output_file = Path("atom-relationships.json")
    with open(output_file, 'w') as f:
        # Convert sets to lists for JSON serialization
        relationships_serializable = {}
        for atom_id, rels in relationships.items():
            relationships_serializable[atom_id] = {
                'strong_links': sorted(rels['strong_links']),
                'medium_links': sorted(rels['medium_links']),
                'scores': {k: round(v, 3) for k, v in rels['scores'].items()},
            }

        json.dump(relationships_serializable, f, indent=2)

    print(f"✅ Analysis complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Analyzed {len(relationships)} atoms")
    print(f"💡 Run with --report flag for detailed metrics")


if __name__ == '__main__':
    main()
