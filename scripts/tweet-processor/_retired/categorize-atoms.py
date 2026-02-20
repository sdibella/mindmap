#!/usr/bin/env python3
"""
Atom Categorization Engine
Based on deep analysis of 266 atoms in StefanEternal vault
See ATOM_CATEGORIZATION_ANALYSIS.md for methodology
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# New categorization patterns (validated against 266 atoms)
PATTERNS = {
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

def categorize_atom(filepath: Path) -> Tuple[List[str], float]:
    """
    Categorize an atom file and return (categories, confidence)
    """
    try:
        content = filepath.read_text(encoding='utf-8').lower()
    except:
        return [], 0.0

    matches = []
    for category, pattern in PATTERNS.items():
        if re.search(pattern, content, re.IGNORECASE):
            matches.append(category)

    # Confidence scoring
    if len(matches) == 0:
        confidence = 0.0
    elif len(matches) == 1:
        confidence = 0.95
    elif len(matches) <= 3:
        confidence = 0.85
    else:
        confidence = 0.7

    return matches, confidence

def extract_frontmatter(content: str) -> Dict:
    """Extract frontmatter from atom"""
    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm

def analyze(atoms_dir: Path) -> Dict:
    """Analyze all atoms and suggest categories"""
    results = {}

    for atom_file in sorted(atoms_dir.glob("*.md")):
        categories, confidence = categorize_atom(atom_file)
        content = atom_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        results[atom_file.stem] = {
            'suggested_tags': categories,
            'confidence': confidence,
            'current_tags': frontmatter.get('tags', '').split(', ') if 'tags' in frontmatter else [],
            'author': frontmatter.get('author', ''),
            'filename': atom_file.name
        }

    return results

def report(results: Dict):
    """Generate analysis report"""
    print("\n📊 CATEGORIZATION ANALYSIS REPORT\n")
    print("=" * 60)

    # Coverage
    tagged = sum(1 for r in results.values() if r['suggested_tags'])
    print(f"\nCoverage: {tagged}/{len(results)} atoms ({100*tagged/len(results):.1f}%)")

    # Tag distribution
    tag_counts = {}
    for r in results.values():
        for tag in r['suggested_tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print(f"\nTag Distribution:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count}")

    # Confidence breakdown
    high = sum(1 for r in results.values() if r['confidence'] >= 0.9)
    med = sum(1 for r in results.values() if 0.7 <= r['confidence'] < 0.9)
    low = sum(1 for r in results.values() if r['confidence'] < 0.7)

    print(f"\nConfidence Levels:")
    print(f"  High (≥0.9): {high}")
    print(f"  Medium (0.7-0.9): {med}")
    print(f"  Low (<0.7): {low}")

    # Multi-tag atoms
    multi = sum(1 for r in results.values() if len(r['suggested_tags']) > 1)
    print(f"\nMulti-category atoms: {multi} ({100*multi/len(results):.1f}%)")

    print("\n" + "=" * 60 + "\n")

def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    print(f"🔍 Analyzing atoms in {atoms_dir}")
    results = analyze(atoms_dir)

    if '--report' in sys.argv:
        report(results)

    # Save results
    output_file = Path("categorization_suggestions.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Analyzed {len(results)} atoms")
    print(f"📁 Results saved to: {output_file}")

if __name__ == '__main__':
    main()
