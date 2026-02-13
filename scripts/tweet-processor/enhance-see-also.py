#!/usr/bin/env python3
"""
Rich Graph Backlink Generation System
Phase 3: See Also Section Enhancement

Enhances ## See Also sections with descriptive text for medium-link recommendations
"""

import re
import json
import sys
from pathlib import Path
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


def extract_first_line(content: str) -> str:
    """Extract first meaningful line/sentence from content"""
    # Remove frontmatter
    content = re.sub(r'^---[\s\S]*?---\n', '', content)

    # Find first non-empty line that's not a heading
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 10:
            # Truncate to first sentence or 60 characters
            if '.' in line:
                desc = line.split('.')[0] + '.'
            else:
                desc = line

            # Limit to 60 characters
            if len(desc) > 60:
                desc = desc[:57] + '...'

            return desc

    return "Related topic"


def extract_categories(content: str) -> Set[str]:
    """Extract categories from atom content (matching tags)"""
    categories = set()

    # Match common category keywords
    category_keywords = {
        'trading': ['trade', 'trading', 'polymarket', 'kalshi', 'forecast'],
        'ai': ['ai', 'agent', 'llm', 'model', 'openai', 'anthropic', 'claude'],
        'crypto': ['crypto', 'blockchain', 'bitcoin', 'ethereum', 'defi', 'dao', 'nft'],
        'development': ['code', 'programming', 'api', 'sdk', 'github', 'python', 'javascript'],
        'learning': ['guide', 'tutorial', 'how', 'roadmap', 'course', 'blueprint'],
    }

    content_lower = content.lower()
    for cat, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                categories.add(cat)
                break

    return categories


def generate_description(atom_id: str, atom_file: Path, shared_tags: Set[str]) -> str:
    """Generate a contextual description for a medium link"""
    try:
        content = atom_file.read_text(encoding='utf-8')
        first_line = extract_first_line(content)

        # Add context based on shared tags
        categories = extract_categories(content)
        context_hints = []

        if 'polymarket' in atom_id.lower() or 'trading' in categories:
            context_hints.append('prediction market')
        if 'ai' in categories or 'agent' in categories:
            context_hints.append('AI/agent')
        if 'crypto' in categories or 'defi' in categories:
            context_hints.append('crypto')

        if context_hints:
            context = f" ({', '.join(context_hints[:2])})"
        else:
            context = ""

        return f"{first_line}{context}"

    except Exception:
        return "Related topic"


def get_see_also_section_bounds(content: str) -> Tuple[int, int, bool]:
    """Find the bounds of the ## See Also section"""
    pattern = r'## See Also\n'
    match = re.search(pattern, content)

    if not match:
        return -1, -1, False

    start = match.start()

    # Find end (next ## section or end of file)
    next_section = re.search(r'\n## ', content[match.end():])
    if next_section:
        end = match.end() + next_section.start()
    else:
        end = len(content)

    return start, end, True


def extract_existing_see_also_links(content: str) -> Dict[str, str]:
    """Extract existing See Also links and their descriptions"""
    start, end, exists = get_see_also_section_bounds(content)

    if not exists:
        return {}

    section_content = content[start + len('## See Also\n'):end]

    links = {}
    for line in section_content.split('\n'):
        line = line.strip()
        if line.startswith('- [['):
            # Parse format: - [[link-name]] — description
            match = re.match(r'- \[\[([^\]]+)\]\](?:\s+—\s+(.*))?', line)
            if match:
                link = match.group(1)
                desc = match.group(2) if match.group(2) else "See Also link"
                links[link] = desc

    return links


def enhance_see_also(content: str, medium_links: List[str], atoms_dir: Path, atom_id: str) -> str:
    """
    Enhance ## See Also section with medium-link recommendations
    Preserves existing MOC links, adds top medium links with descriptions
    """

    # Extract existing See Also links
    existing_see_also = extract_existing_see_also_links(content)

    # Build new See Also section
    see_also_links = []

    # First, add existing MOC links (preserved)
    for link, desc in existing_see_also.items():
        if link.startswith('maps/'):
            see_also_links.append((link, desc))

    # Then add top medium links (up to 3) that aren't already there
    added = 0
    for medium_link in medium_links:
        if added >= 3:  # Limit to 3 new links
            break

        if medium_link not in existing_see_also and medium_link not in [l[0] for l in see_also_links]:
            medium_atom_file = atoms_dir / f"{medium_link}.md"

            if medium_atom_file.exists():
                desc = generate_description(medium_link, medium_atom_file, set())
                see_also_links.append((medium_link, desc))
                added += 1

    if not see_also_links:
        return content

    # Build new See Also section content
    new_section_lines = ['## See Also']
    for link, desc in see_also_links:
        if desc:
            new_section_lines.append(f'- [[{link}]] — {desc}')
        else:
            new_section_lines.append(f'- [[{link}]]')
    new_section_lines.append('')  # Blank line after section

    new_section_content = '\n'.join(new_section_lines)

    # Replace existing See Also section
    start, end, exists = get_see_also_section_bounds(content)

    if exists:
        return content[:start] + new_section_content + content[end:]
    else:
        # Append at end
        if content.endswith('\n'):
            return content + new_section_content
        else:
            return content + '\n' + new_section_content


def process_atoms(relationships: Dict, atoms_dir: Path, dry_run: bool = True) -> Tuple[int, int]:
    """Process all atoms and enhance See Also sections"""

    updated = 0
    skipped = 0

    print(f"🔄 Enhancing See Also sections...")
    if dry_run:
        print("   (DRY RUN - no files will be modified)")

    for i, (atom_id, rels) in enumerate(relationships.items()):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(relationships)}")

        medium_links = rels.get('medium_links', [])

        if not medium_links:
            skipped += 1
            continue

        atom_file = atoms_dir / f"{atom_id}.md"
        if not atom_file.exists():
            skipped += 1
            continue

        try:
            original_content = atom_file.read_text(encoding='utf-8')
        except:
            skipped += 1
            continue

        # Enhance See Also
        updated_content = enhance_see_also(original_content, medium_links, atoms_dir, atom_id)

        if updated_content == original_content:
            skipped += 1
            continue

        updated += 1

        if not dry_run:
            try:
                atom_file.write_text(updated_content, encoding='utf-8')
            except Exception as e:
                print(f"⚠️  Failed to update {atom_id}: {e}")

    return updated, skipped


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

    # Process atoms
    updated, skipped = process_atoms(relationships, atoms_dir, dry_run=dry_run)

    print("\n" + "=" * 70)
    print(f"{'📊 SEE ALSO ENHANCEMENT REPORT (DRY RUN)' if dry_run else '✅ SEE ALSO ENHANCEMENT COMPLETE'}")
    print("=" * 70)
    print(f"\n  Atoms processed: {len(relationships)}")
    print(f"  See Also sections enhanced: {updated}")
    print(f"  Atoms skipped: {skipped}")

    if not dry_run:
        print(f"\n✅ All See Also sections have been enhanced with descriptions")

    print("\n" + "=" * 70 + "\n")

    if dry_run:
        print("💡 Run with --apply flag to actually modify files")


if __name__ == '__main__':
    main()
