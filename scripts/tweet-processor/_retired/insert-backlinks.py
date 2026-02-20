#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 2: Markdown Link Inserter

Safely updates atom files with generated backlinks from Phase 1.
Supports dry-run preview and actual file modifications with backups.
"""

import re
import json
import sys
from pathlib import Path
from shutil import copy2
from datetime import datetime
from typing import Dict, List, Tuple, Set


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


def extract_existing_links(content: str, section: str) -> Set[str]:
    """Extract existing links from a given section"""
    # Find section
    pattern = rf'## {section}\n([\s\S]*?)(?=\n## |$)'
    match = re.search(pattern, content)

    if not match:
        return set()

    section_content = match.group(1)

    # Extract all [[link]] references
    links = re.findall(r'\[\[([^\]]+)\]\]', section_content)
    return set(links)


def get_related_atoms_section_bounds(content: str) -> Tuple[int, int, bool]:
    """
    Find the bounds of the ## Related Atoms section.
    Returns (start_pos, end_pos, section_exists)
    """
    pattern = r'## Related Atoms\n'
    match = re.search(pattern, content)

    if not match:
        return -1, -1, False

    start = match.start()

    # Find the end (next ## section or end of file)
    next_section = re.search(r'\n## ', content[match.end():])
    if next_section:
        end = match.end() + next_section.start()
    else:
        end = len(content)

    return start, end, True


def insert_related_atoms(content: str, new_links: List[str]) -> str:
    """
    Safely insert Related Atoms links into atom content.
    Preserves existing links and prevents duplicates.
    """

    # Extract existing links
    existing_links = extract_existing_links(content, 'Related Atoms')

    # Merge and deduplicate
    all_links = sorted(set(list(existing_links) + new_links))

    if not all_links:
        # No links to add
        return content

    # Build new section content
    new_section_lines = ['## Related Atoms']
    for link in all_links:
        new_section_lines.append(f'- [[{link}]]')
    new_section_lines.append('')  # Blank line after section

    new_section_content = '\n'.join(new_section_lines)

    # Check if section exists
    start, end, exists = get_related_atoms_section_bounds(content)

    if exists:
        # Replace existing section
        return content[:start] + new_section_content + content[end:]
    else:
        # Insert before ## See Also
        see_also_match = re.search(r'\n## See Also\n', content)

        if see_also_match:
            insert_point = see_also_match.start() + 1  # Right before ## See Also
            return content[:insert_point] + new_section_content + content[insert_point:]
        else:
            # Append before any other trailing sections or at end
            # Try to insert before ## Source or ## Key Takeaways or ## See Also
            for section in ['## Source', '## Key Takeaways']:
                match = re.search(rf'\n{section}\n', content)
                if match:
                    insert_point = match.start() + 1
                    return content[:insert_point] + new_section_content + content[insert_point:]

            # Last resort: append at end
            if content.endswith('\n'):
                return content + new_section_content
            else:
                return content + '\n' + new_section_content


def validate_atom_exists(atom_id: str, atoms_dir: Path) -> bool:
    """Check if target atom file exists"""
    atom_file = atoms_dir / f"{atom_id}.md"
    return atom_file.exists()


def create_backup(atom_file: Path, backup_dir: Path) -> bool:
    """Create backup of original atom file"""
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / atom_file.name
        copy2(atom_file, backup_path)
        return True
    except Exception as e:
        print(f"⚠️  Failed to backup {atom_file.name}: {e}")
        return False


def process_atoms(relationships: Dict, atoms_dir: Path, dry_run: bool = True) -> Dict:
    """
    Process all atoms and generate backlinks.
    Returns statistics and change log.
    """

    stats = {
        'processed': 0,
        'updated': 0,
        'failed': 0,
        'no_links': 0,
        'skipped': 0,
        'total_links_added': 0,
    }

    changelog = []
    backup_dir = atoms_dir.parent / 'atoms-backup'

    print(f"🔄 Processing {len(relationships)} atoms...")
    if dry_run:
        print("   (DRY RUN - no files will be modified)")

    for i, (atom_id, rels) in enumerate(relationships.items()):
        stats['processed'] += 1

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(relationships)}")

        # Get strong links to add
        new_links = rels.get('strong_links', [])

        if not new_links:
            stats['no_links'] += 1
            continue

        # Check if atom file exists
        atom_file = atoms_dir / f"{atom_id}.md"
        if not atom_file.exists():
            stats['failed'] += 1
            changelog.append({
                'atom': atom_id,
                'status': 'FAILED',
                'reason': 'File not found',
            })
            continue

        # Read original content
        try:
            original_content = atom_file.read_text(encoding='utf-8')
        except Exception as e:
            stats['failed'] += 1
            changelog.append({
                'atom': atom_id,
                'status': 'FAILED',
                'reason': f'Read error: {e}',
            })
            continue

        # Extract existing links
        existing_links = extract_existing_links(original_content, 'Related Atoms')

        # Filter new links (only include valid atoms)
        filtered_new_links = []
        for link in new_links:
            if validate_atom_exists(link, atoms_dir) and link not in existing_links:
                filtered_new_links.append(link)

        if not filtered_new_links:
            stats['skipped'] += 1
            continue

        # Generate new content
        updated_content = insert_related_atoms(original_content, filtered_new_links)

        # Check if content changed
        if updated_content == original_content:
            stats['skipped'] += 1
            continue

        stats['updated'] += 1
        stats['total_links_added'] += len(filtered_new_links)

        changelog.append({
            'atom': atom_id,
            'status': 'UPDATED',
            'links_added': len(filtered_new_links),
            'new_links': filtered_new_links[:5],  # Show first 5
        })

        # Apply changes if not dry run
        if not dry_run:
            try:
                # Create backup
                create_backup(atom_file, backup_dir)

                # Write updated content
                atom_file.write_text(updated_content, encoding='utf-8')

            except Exception as e:
                stats['failed'] += 1
                changelog[-1]['status'] = 'BACKUP_FAILED'
                changelog[-1]['reason'] = str(e)

    return stats, changelog


def report(stats: Dict, changelog: List, dry_run: bool = True):
    """Generate processing report"""

    print("\n" + "=" * 70)
    print(f"{'📊 BACKLINK INSERTION REPORT (DRY RUN)' if dry_run else '✅ BACKLINK INSERTION COMPLETE'}")
    print("=" * 70)

    print(f"\n📈 Statistics:")
    print(f"  Total atoms processed: {stats['processed']}")
    print(f"  Atoms updated: {stats['updated']}")
    print(f"  Atoms with no new links: {stats['no_links']}")
    print(f"  Atoms skipped (no changes): {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total links added: {stats['total_links_added']}")

    if stats['updated'] > 0:
        avg_links = stats['total_links_added'] / stats['updated']
        print(f"  Average links per updated atom: {avg_links:.2f}")

    print(f"\n📝 Sample Changes (first 10):")
    for change in changelog[:10]:
        if change['status'] == 'UPDATED':
            links_str = ', '.join(change['new_links'][:3])
            if len(change['new_links']) > 3:
                links_str += f", +{len(change['new_links']) - 3} more"
            print(f"  ✓ {change['atom']}: +{change['links_added']} links ({links_str})")
        elif change['status'] == 'FAILED':
            print(f"  ✗ {change['atom']}: {change['reason']}")

    if not dry_run:
        print(f"\n💾 Backups created in: atoms-backup/")

    print("\n" + "=" * 70 + "\n")


def main():
    atoms_dir = Path("/Users/gw/Workspace/mindmap/StefanEternal/atoms")
    relationships_file = Path("atom-relationships.json")

    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    if not relationships_file.exists():
        print(f"❌ Relationships file not found: {relationships_file}")
        print("Run analyze-atom-relationships.py first")
        sys.exit(1)

    # Load relationships
    with open(relationships_file, 'r') as f:
        relationships = json.load(f)

    # Determine mode
    dry_run = '--apply' not in sys.argv

    # Process atoms
    stats, changelog = process_atoms(relationships, atoms_dir, dry_run=dry_run)

    # Generate report
    report(stats, changelog, dry_run=dry_run)

    if dry_run:
        print("💡 Run with --apply flag to actually modify files")
        print("   Example: python3 insert-backlinks.py --apply")


if __name__ == '__main__':
    main()
