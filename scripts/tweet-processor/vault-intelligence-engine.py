#!/usr/bin/env python3
"""
OPENCLAW Vault Intelligence Engine
Unified categorization, backlinking, and relationship discovery system

Nightly routine that intelligently tags and connects all vault content
according to OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter
from datetime import datetime
import hashlib

# Category patterns from OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md
CATEGORY_PATTERNS = {
    'ai-agents': r'\bagent\b|\bagentic\b|\bautonomous\s+system|\borchestr|\bmulti-?agent|\bworkflow\s+automation|\btask\s+automation',
    'prediction-markets': r'polymarket|kalshi|prediction\s+market|\bforecast(ing)?|weather\s+bot|event\s+betting',
    'crypto-defi': r'\bcrypto\b|\bblockchain\b|bitcoin|ethereum|\bdefi\b|\bdao\b|\bnft\b|smart\s+contract|yield\s+farming',
    'software-development': r'\bcode\b|\bprogramming\b|\bsdk\b|\bapi\b|\bgithub\b|python|javascript|typescript|react|\bframework\b|\blibrary\b',
    'ai-models-research': r'\bllm\b|large\s+language\s+model|\bmachine\s+learning\b|\bneural\s+network|\bmodel\s+training|\binference|\bgpu\b|anthropic|openai|claude|gemini',
    'stock-trading-finance': r'\bstock\b|\bportfolio\b|\bdividend|\bswing\s+trade|\btechnical\s+analysis|\btrading\s+strategy|\bmarket\s+analysis|\bequity\b',
    'business-entrepreneurship': r'\bstartup\b|\bentrepreneur|\bfounder|\bbusiness\s+model|\bgrowth\s+strategy|\bsaas\b|\bproduct-?market\s+fit|\bfundraising|\bmarketing',
    'systems-architecture': r'\barchitecture\b|\bsystem\s+design|\bscalability|\binfrastructure|\bdesign\s+pattern|\bdistributed\s+system|\bmicroservice',
    'learning-resources': r'\bguide\b|\btutorial\b|\bhow\s+to|\bhow-?to|\broadmap\b|\bcourse\b|\bblueprint\b|\bstep-?by-?step|\bframework\b',
}

SECONDARY_TAG_PATTERNS = {
    'ai-native': r'prompt\s+template|system\s+prompt|ai\s+consumption|for\s+ai|agent\s+designed',
    'practical-strategy': r'step-?by-?step|how-?to|actionable|framework|blueprint|checklist',
    'research-based': r'research|academic|benchmark|study|experiment|data|analysis',
    'case-study': r'case\s+study|real-?world|example|success\s+story|how\s+i|my\s+experience',
    'tool-recommendation': r'best\s+tool|tool\s+recommendation|tool\s+guide|recommended|using\s+',
    'contrarian': r'everyone|wrong|opposite|unconventional|myth|fallacy|rethink',
}

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
}


def extract_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter"""
    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm


def extract_tags(frontmatter: Dict) -> Set[str]:
    """Extract existing tags from frontmatter"""
    tags_str = frontmatter.get('tags', '')
    if not tags_str:
        return set()

    tags_str = tags_str.strip('[]')
    tags = [t.strip() for t in tags_str.split(',')]
    return {t for t in tags if t}


def extract_keywords(content: str, top_n: int = 10) -> List[str]:
    """Extract top keywords from content"""
    content = re.sub(r'^---[\s\S]*?---\n', '', content)
    words = re.findall(r'\b[a-z]+\b', content.lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 3]

    counter = Counter(words)
    return [word for word, _ in counter.most_common(top_n)]


def categorize_content(content: str) -> Tuple[Set[str], float]:
    """
    Categorize content by primary categories.
    Returns (categories, confidence)
    """
    content_lower = content.lower()
    matched = set()

    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            matched.add(category)

    # Confidence scoring
    if len(matched) == 0:
        confidence = 0.0
    elif len(matched) == 1:
        confidence = 0.85
    elif len(matched) <= 3:
        confidence = 0.75
    else:
        confidence = 0.65

    return matched, confidence


def detect_secondary_tags(content: str) -> Set[str]:
    """Detect secondary tags from content"""
    content_lower = content.lower()
    secondary = set()

    for tag, pattern in SECONDARY_TAG_PATTERNS.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            secondary.add(tag)

    return secondary


def detect_person_tag(filename: str, content: str) -> bool:
    """Detect if this is a people-personas file"""
    # Check if filename looks like a person (no hyphens after title-case)
    stem = Path(filename).stem

    # Simple heuristic: if first word is capitalized and file is about them
    if re.match(r'^[A-Z][a-z]+-?[a-z]*$', stem):
        # Likely a person name
        return True

    return False


def calculate_similarity_score(file1_data: Dict, file2_data: Dict) -> float:
    """Calculate relationship score between two files"""

    # Tag overlap (40%)
    tags1 = file1_data['primary_categories']
    tags2 = file2_data['primary_categories']
    overlap = len(tags1 & tags2)

    if overlap >= 3:
        tag_score = 0.9
    elif overlap == 2:
        tag_score = 0.7
    elif overlap == 1:
        tag_score = 0.4
    else:
        tag_score = 0.0

    # Keyword overlap (30%)
    keywords1 = set(file1_data['keywords'])
    keywords2 = set(file2_data['keywords'])
    keyword_overlap = len(keywords1 & keywords2)

    if keyword_overlap >= 5:
        keyword_score = 0.9
    elif keyword_overlap >= 2:
        keyword_score = 0.5
    elif keyword_overlap >= 1:
        keyword_score = 0.2
    else:
        keyword_score = 0.0

    # Category clustering (20%)
    category_overlap = len(tags1 & tags2)
    category_score = 0.7 if category_overlap > 0 else 0.0

    # Weighted combination
    score = (
        tag_score * 0.40 +
        keyword_score * 0.30 +
        category_score * 0.20
    )

    # Boost for multi-category atoms
    if len(tags1) > 1 and len(tags2) > 1:
        score *= 1.15

    return min(score, 1.0)


def scan_vault(vault_path: Path) -> Dict[str, Dict]:
    """Scan all markdown files in vault"""

    file_data = {}

    print(f"📖 Scanning vault at {vault_path}...")

    for md_file in sorted(vault_path.rglob("*.md")):
        # Skip certain directories
        if any(skip in str(md_file) for skip in ['.obsidian', 'node_modules', '/.git']):
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)

            file_id = md_file.stem

            # Categorize
            primary_cats, confidence = categorize_content(content)
            secondary_tags = detect_secondary_tags(content)
            is_person = detect_person_tag(md_file.name, content)

            if is_person:
                primary_cats.add('people-personas')

            file_data[file_id] = {
                'path': str(md_file.relative_to(vault_path.parent)),
                'filename': md_file.name,
                'primary_categories': primary_cats,
                'secondary_tags': secondary_tags,
                'confidence': confidence,
                'keywords': extract_keywords(content),
                'existing_tags': extract_tags(frontmatter),
                'author': frontmatter.get('author', ''),
                'created': frontmatter.get('created', ''),
                'content_length': len(content),
            }

        except Exception as e:
            print(f"⚠️  Error processing {md_file.name}: {e}")

    print(f"✅ Scanned {len(file_data)} files")
    return file_data


def calculate_relationships(file_data: Dict) -> Dict:
    """Calculate all relationships"""

    print("🔗 Calculating relationships...")

    relationships = {}

    for i, (file_id, data) in enumerate(file_data.items()):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(file_data)}")

        strong_links = []
        medium_links = []
        scores = {}

        for other_id, other_data in file_data.items():
            if file_id == other_id:
                continue

            score = calculate_similarity_score(data, other_data)

            if score >= 0.65:
                strong_links.append(other_id)
                scores[other_id] = score
            elif score >= 0.50:
                medium_links.append(other_id)
                scores[other_id] = score

        # Sort by score
        strong_links.sort(key=lambda x: scores.get(x, 0), reverse=True)
        medium_links.sort(key=lambda x: scores.get(x, 0), reverse=True)

        relationships[file_id] = {
            'strong_links': strong_links,
            'medium_links': medium_links,
            'scores': {k: round(v, 3) for k, v in scores.items()},
        }

    return relationships


def generate_metadata(file_data: Dict, relationships: Dict) -> Dict:
    """Generate complete metadata"""

    metadata = {
        'generated': datetime.now().isoformat(),
        'total_files': len(file_data),
        'files': {},
        'relationships': relationships,
        'statistics': {
            'total_files': len(file_data),
            'files_with_categories': sum(1 for f in file_data.values() if f['primary_categories']),
            'files_with_secondary_tags': sum(1 for f in file_data.values() if f['secondary_tags']),
            'files_with_high_confidence': sum(1 for f in file_data.values() if f['confidence'] >= 0.85),
            'files_with_low_confidence': sum(1 for f in file_data.values() if f['confidence'] < 0.65),
            'total_strong_relationships': sum(len(r['strong_links']) for r in relationships.values()),
            'total_medium_relationships': sum(len(r['medium_links']) for r in relationships.values()),
        }
    }

    # Compress file data for metadata
    for file_id, data in file_data.items():
        metadata['files'][file_id] = {
            'primary_categories': sorted(data['primary_categories']),
            'secondary_tags': sorted(data['secondary_tags']),
            'confidence': data['confidence'],
            'author': data['author'],
        }

    return metadata


def main():
    import argparse

    parser = argparse.ArgumentParser(description='OPENCLAW Vault Intelligence Engine')
    parser.add_argument('--mode', choices=['full', 'validate'], default='full',
                        help='Mode: full (analyze + categorize) or validate (check only)')
    parser.add_argument('--vault', default='/Users/gw/Workspace/mindmap/StefanEternal',
                        help='Path to vault root')
    parser.add_argument('--output', default='vault-metadata.json',
                        help='Output metadata file')
    parser.add_argument('--report', action='store_true',
                        help='Generate console report')

    args = parser.parse_args()

    vault_path = Path(args.vault)

    if not vault_path.exists():
        print(f"❌ Vault not found: {vault_path}")
        sys.exit(1)

    print("=" * 70)
    print("🤖 OPENCLAW VAULT INTELLIGENCE ENGINE")
    print("=" * 70)

    # Scan vault
    file_data = scan_vault(vault_path)

    if args.mode == 'validate':
        print("\n✅ Validation mode - stopping after scan")
        print(f"Would process {len(file_data)} files")
        sys.exit(0)

    # Calculate relationships
    relationships = calculate_relationships(file_data)

    # Generate metadata
    metadata = generate_metadata(file_data, relationships)

    # Save metadata
    output_file = Path(args.output)
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Intelligence engine complete!")
    print(f"📁 Metadata saved to: {output_file}")

    if args.report:
        print("\n" + "=" * 70)
        print("📊 CATEGORIZATION REPORT")
        print("=" * 70)

        stats = metadata['statistics']
        print(f"\n📈 Coverage:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Files with categories: {stats['files_with_categories']} ({100*stats['files_with_categories']/stats['total_files']:.1f}%)")
        print(f"  Files with secondary tags: {stats['files_with_secondary_tags']} ({100*stats['files_with_secondary_tags']/stats['total_files']:.1f}%)")

        print(f"\n🎯 Confidence:")
        print(f"  High (≥0.85): {stats['files_with_high_confidence']}")
        print(f"  Low (<0.65): {stats['files_with_low_confidence']}")

        print(f"\n🔗 Relationships:")
        print(f"  Strong links: {stats['total_strong_relationships']}")
        print(f"  Medium links: {stats['total_medium_relationships']}")

        # Category distribution
        category_counts = {}
        for file_data_item in metadata['files'].values():
            for cat in file_data_item['primary_categories']:
                category_counts[cat] = category_counts.get(cat, 0) + 1

        print(f"\n🏷️  Category Distribution:")
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")

        print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
