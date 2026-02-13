#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 6: Graph Validation and Metrics

Comprehensive validation of the generated knowledge graph:
- Graph density metrics
- Broken link detection
- Orphaned atom identification
- Bidirectional link coverage analysis
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_related_atoms_links(content: str) -> Set[str]:
    """Extract Related Atoms links"""
    pattern = r'## Related Atoms\n([\s\S]*?)(?=\n## |$)'
    match = re.search(pattern, content)

    if not match:
        return set()

    section_content = match.group(1)
    links = re.findall(r'\[\[([^\]]+)\]\]', section_content)
    return set(links)


def extract_see_also_links(content: str) -> Set[str]:
    """Extract See Also links"""
    pattern = r'## See Also\n([\s\S]*?)(?=\n## |$)'
    match = re.search(pattern, content)

    if not match:
        return set()

    section_content = match.group(1)
    links = re.findall(r'\[\[([^\]]+)\]\]', section_content)
    return set(links)


def validate_atom_graph(atoms_dir: Path) -> Dict:
    """Comprehensive graph validation"""

    results = {
        'total_atoms': 0,
        'atoms_with_related': 0,
        'atoms_with_see_also': 0,
        'total_related_links': 0,
        'total_see_also_links': 0,
        'broken_links': [],
        'orphaned_atoms': [],
        'bidirectional_verified': 0,
        'unidirectional_links': 0,
        'atoms_by_connection_count': {},
    }

    atom_files = {}
    all_atoms = set()

    print("📖 Loading atoms...")

    # First pass: collect all atoms
    for atom_file in sorted(atoms_dir.glob("*.md")):
        atom_id = atom_file.stem
        all_atoms.add(atom_id)

        try:
            content = atom_file.read_text(encoding='utf-8')
            atom_files[atom_id] = {
                'file': atom_file,
                'content': content,
                'related': extract_related_atoms_links(content),
                'see_also': extract_see_also_links(content),
            }
        except Exception as e:
            print(f"⚠️  Error loading {atom_file.name}: {e}")

    results['total_atoms'] = len(atom_files)

    print(f"✅ Loaded {len(atom_files)} atoms")
    print("🔍 Validating links...")

    # Second pass: validate links
    for atom_id, atom_data in atom_files.items():
        related = atom_data['related']
        see_also = atom_data['see_also']

        all_links = related | see_also

        # Track atoms with links
        if related:
            results['atoms_with_related'] += 1
        if see_also:
            results['atoms_with_see_also'] += 1

        # Count total links
        results['total_related_links'] += len(related)
        results['total_see_also_links'] += len(see_also)

        # Track connection count
        total_links = len(all_links)
        results['atoms_by_connection_count'][atom_id] = total_links

        # Validate each link exists (excluding MOCs which are separate)
        for link in all_links:
            if link.startswith('maps/'):
                # MOC references are handled separately
                continue

            if link not in atom_files:
                results['broken_links'].append({
                    'from': atom_id,
                    'to': link,
                    'in_section': 'Related' if link in related else 'See Also'
                })

        # Check for bidirectional links
        for link in related:
            if link.startswith('maps/'):
                continue

            if link in atom_files:
                backlinks = atom_files[link]['related'] | atom_files[link]['see_also']

                if atom_id in backlinks:
                    results['bidirectional_verified'] += 1
                else:
                    results['unidirectional_links'] += 1

    # Identify orphaned atoms (no connections at all)
    for atom_id in atom_files:
        if atom_id not in results['atoms_by_connection_count'] or results['atoms_by_connection_count'][atom_id] == 0:
            results['orphaned_atoms'].append(atom_id)

    return results


def calculate_graph_density(atoms_count: int, links_count: int) -> float:
    """
    Calculate graph density.
    For a directed graph: density = links / (nodes * (nodes - 1))
    """

    if atoms_count < 2:
        return 0.0

    max_possible_links = atoms_count * (atoms_count - 1)
    density = links_count / max_possible_links if max_possible_links > 0 else 0

    return density


def get_top_atoms(results: Dict, top_n: int = 10) -> List[Tuple[str, int]]:
    """Get most-connected atoms"""

    sorted_atoms = sorted(
        results['atoms_by_connection_count'].items(),
        key=lambda x: -x[1]
    )

    return sorted_atoms[:top_n]


def generate_report(results: Dict):
    """Generate comprehensive validation report"""

    print("\n" + "=" * 70)
    print("📊 GRAPH VALIDATION REPORT")
    print("=" * 70)

    print(f"\n📈 Graph Structure Metrics:")
    print(f"  Total atoms: {results['total_atoms']}")
    print(f"  Related Atoms links: {results['total_related_links']}")
    print(f"  See Also links: {results['total_see_also_links']}")
    print(f"  Total connections: {results['total_related_links'] + results['total_see_also_links']}")

    # Coverage
    related_coverage = 100 * results['atoms_with_related'] / results['total_atoms']
    see_also_coverage = 100 * results['atoms_with_see_also'] / results['total_atoms']

    print(f"\n📊 Link Coverage:")
    print(f"  Atoms with Related links: {results['atoms_with_related']} ({related_coverage:.1f}%)")
    print(f"  Atoms with See Also links: {results['atoms_with_see_also']} ({see_also_coverage:.1f}%)")

    # Graph density
    graph_density = calculate_graph_density(
        results['total_atoms'],
        results['total_related_links']
    )

    print(f"\n📐 Graph Density:")
    print(f"  Density (Related Atoms only): {graph_density:.4f} ({100*graph_density:.2f}%)")
    print(f"  Reference: 0.001 = very sparse, 0.1-0.3 = dense network")

    # Bidirectional analysis
    total_directed = results['bidirectional_verified'] + results['unidirectional_links']
    if total_directed > 0:
        bidirectional_pct = 100 * results['bidirectional_verified'] / total_directed
        print(f"\n🔗 Bidirectional Link Analysis:")
        print(f"  Verified bidirectional links: {results['bidirectional_verified']}")
        print(f"  One-way links: {results['unidirectional_links']}")
        print(f"  Bidirectional coverage: {bidirectional_pct:.1f}%")

    # Top connected atoms
    top_atoms = get_top_atoms(results)

    print(f"\n🌟 Most-Connected Atoms (Top 10):")
    for atom_id, count in top_atoms:
        print(f"  {atom_id}: {count} connections")

    # Broken links
    if results['broken_links']:
        print(f"\n⚠️  Broken Links ({len(results['broken_links'])} total):")
        for link_info in results['broken_links'][:10]:
            print(f"  {link_info['from']} → {link_info['to']} ({link_info['in_section']})")
        if len(results['broken_links']) > 10:
            print(f"  ... and {len(results['broken_links']) - 10} more")
    else:
        print(f"\n✅ No broken links detected!")

    # Orphaned atoms
    if results['orphaned_atoms']:
        print(f"\n🔍 Orphaned Atoms ({len(results['orphaned_atoms'])} total):")
        print("  Atoms with no connections:")
        for atom_id in results['orphaned_atoms'][:10]:
            print(f"  - {atom_id}")
        if len(results['orphaned_atoms']) > 10:
            print(f"  ... and {len(results['orphaned_atoms']) - 10} more")
    else:
        print(f"\n✅ No orphaned atoms!")

    # Connection distribution
    connection_counts = list(results['atoms_by_connection_count'].values())
    if connection_counts:
        avg_connections = sum(connection_counts) / len(connection_counts)
        max_connections = max(connection_counts)
        min_connections = min(connection_counts)

        print(f"\n📊 Connection Distribution:")
        print(f"  Average connections per atom: {avg_connections:.2f}")
        print(f"  Maximum connections: {max_connections}")
        print(f"  Minimum connections: {min_connections}")

    # Comparison with targets
    print(f"\n🎯 Target Comparison:")
    print(f"  Target strong links: 800-1200")
    print(f"  Actual Related Atoms links: {results['total_related_links']}")
    status = "✅" if 800 <= results['total_related_links'] <= 1200 else "⚠️"
    print(f"  {status} Status: {'On target' if 800 <= results['total_related_links'] <= 1200 else 'Needs adjustment'}")

    coverage_pct = 100 * (results['atoms_with_related'] + results['atoms_with_see_also']) / (2 * results['total_atoms'])
    print(f"\n  Target coverage: 100%")
    print(f"  Actual coverage: {coverage_pct:.1f}%")

    print("\n" + "=" * 70 + "\n")


def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    # Validate graph
    results = validate_atom_graph(atoms_dir)

    # Generate report
    generate_report(results)

    # Return exit code based on validation
    if results['broken_links'] or len(results['orphaned_atoms']) > 50:
        print("⚠️  Some issues detected. Review the report above.")
        sys.exit(1)
    else:
        print("✅ Graph validation passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
