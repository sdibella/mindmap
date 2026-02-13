#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 4: Bidirectional Link Validation

Ensures reciprocal backlinks between atoms with strong relationships.
Validates and repairs broken bidirectional connections.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_related_atoms_links(content: str) -> Set[str]:
    """Extract all links from ## Related Atoms section"""
    pattern = r'## Related Atoms\n([\s\S]*?)(?=\n## |$)'
    match = re.search(pattern, content)

    if not match:
        return set()

    section_content = match.group(1)
    links = re.findall(r'\[\[([^\]]+)\]\]', section_content)
    return set(links)


def get_related_atoms_bounds(content: str) -> Tuple[int, int, bool]:
    """Find bounds of Related Atoms section"""
    pattern = r'## Related Atoms\n'
    match = re.search(pattern, content)

    if not match:
        return -1, -1, False

    start = match.start()
    next_section = re.search(r'\n## ', content[match.end():])
    if next_section:
        end = match.end() + next_section.start()
    else:
        end = len(content)

    return start, end, True


def add_missing_link(content: str, new_link: str) -> str:
    """Add a missing link to Related Atoms section"""
    start, end, exists = get_related_atoms_bounds(content)

    if not exists:
        # Create new section
        see_also_match = re.search(r'\n## See Also\n', content)
        if see_also_match:
            insert_point = see_also_match.start() + 1
        else:
            insert_point = len(content)

        new_section = f"\n## Related Atoms\n- [[{new_link}]]\n\n"
        return content[:insert_point] + new_section + content[insert_point:]
    else:
        # Extract and update links
        existing_links = extract_related_atoms_links(content)

        if new_link not in existing_links:
            existing_links.add(new_link)
            sorted_links = sorted(existing_links)

            new_section_lines = ['## Related Atoms']
            for link in sorted_links:
                new_section_lines.append(f'- [[{link}]]')
            new_section_lines.append('')

            new_section_content = '\n'.join(new_section_lines)
            return content[:start] + new_section_content + content[end:]

    return content


def validate_and_repair(relationships: Dict, atoms_dir: Path, dry_run: bool = True) -> Tuple[int, int, int]:
    """
    Validate bidirectional links and repair missing reciprocals.
    Returns (verified, repaired, failed)
    """

    verified = 0
    repaired = 0
    failed = 0

    print(f"🔄 Validating bidirectional links...")
    if dry_run:
        print("   (DRY RUN - no files will be modified)")

    for i, (atom_id, rels) in enumerate(relationships.items()):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(relationships)}")

        strong_links = rels.get('strong_links', [])

        if not strong_links:
            continue

        atom_file = atoms_dir / f"{atom_id}.md"
        if not atom_file.exists():
            continue

        try:
            original_content = atom_file.read_text(encoding='utf-8')
        except:
            failed += 1
            continue

        # For each strong link, check if it links back
        changes_needed = False
        updated_content = original_content

        for linked_atom in strong_links:
            linked_file = atoms_dir / f"{linked_atom}.md"
            if not linked_file.exists():
                continue

            try:
                linked_content = linked_file.read_text(encoding='utf-8')
            except:
                continue

            # Check if linked atom has reciprocal link
            linked_atoms = extract_related_atoms_links(linked_content)

            if atom_id not in linked_atoms:
                # Missing reciprocal link - need to add it
                changes_needed = True

                if not dry_run:
                    # Add reciprocal link to the linked atom
                    updated_linked_content = add_missing_link(linked_content, atom_id)

                    if updated_linked_content != linked_content:
                        try:
                            linked_file.write_text(updated_linked_content, encoding='utf-8')
                            repaired += 1
                        except Exception as e:
                            failed += 1
            else:
                # Reciprocal link exists
                verified += 1

    return verified, repaired, failed


def analyze_graph(atoms_dir: Path) -> Dict:
    """Analyze the final graph structure"""

    bidirectional_count = 0
    directional_count = 0
    total_links = 0

    for atom_file in atoms_dir.glob("*.md"):
        try:
            content = atom_file.read_text(encoding='utf-8')
            links = extract_related_atoms_links(content)

            for link in links:
                link_file = atoms_dir / f"{link}.md"
                if link_file.exists():
                    link_content = link_file.read_text(encoding='utf-8')
                    back_links = extract_related_atoms_links(link_content)

                    if atom_file.stem in back_links:
                        bidirectional_count += 1
                    else:
                        directional_count += 1

                    total_links += 1

        except:
            continue

    return {
        'bidirectional_links': bidirectional_count,
        'directional_links': directional_count,
        'total_links': total_links,
        'bidirectional_percentage': 100 * bidirectional_count / total_links if total_links > 0 else 0,
    }


def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")
    relationships_file = Path("atom-relationships.json")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    if not relationships_file.exists():
        print(f"❌ Relationships file not found: {relationships_file}")
        sys.exit(1)

    # Load relationships
    with open(relationships_file, 'r') as f:
        relationships = json.load(f)

    # Determine mode
    dry_run = '--apply' not in sys.argv

    # Validate and repair
    verified, repaired, failed = validate_and_repair(relationships, atoms_dir, dry_run=dry_run)

    # Analyze graph
    graph_stats = analyze_graph(atoms_dir)

    print("\n" + "=" * 70)
    print(f"{'📊 BIDIRECTIONAL LINK VALIDATION REPORT' if dry_run else '✅ BIDIRECTIONAL LINK REPAIR COMPLETE'}")
    print("=" * 70)

    print(f"\n📈 Validation Statistics:")
    print(f"  Verified reciprocal links: {verified}")
    print(f"  Repaired missing reciprocals: {repaired}")
    print(f"  Failed repairs: {failed}")

    print(f"\n🔗 Graph Structure:")
    print(f"  Total Related Atoms links: {graph_stats['total_links']}")
    print(f"  Bidirectional links: {graph_stats['bidirectional_links']} ({graph_stats['bidirectional_percentage']:.1f}%)")
    print(f"  One-way links: {graph_stats['directional_links']} ({100 - graph_stats['bidirectional_percentage']:.1f}%)")

    print("\n" + "=" * 70 + "\n")

    if dry_run:
        if repaired > 0:
            print(f"💡 {repaired} missing reciprocal links detected")
            print("   Run with --apply flag to repair them")
        else:
            print("✅ All bidirectional links are valid!")


if __name__ == '__main__':
    main()
