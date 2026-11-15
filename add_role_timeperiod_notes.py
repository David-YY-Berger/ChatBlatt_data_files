#!/usr/bin/env python3
"""
Add notes to confidence files when merge candidates have different roles or time periods.
Reads entity information from the review files themselves (which already contain this data).
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

def extract_entity_info_from_review_file(review_file_path):
    """Extract entity info (name, roles, time_period) from review file."""
    entity_info = {}
    
    with open(review_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match entity blocks
    entity_pattern = r"#### Entity \d+: `([^`]+)` \(key: `([^`]+)`\).*?\n(.*?)(?=#### Entity|\</details>)"
    
    for match in re.finditer(entity_pattern, content, re.DOTALL):
        entity_name = match.group(1)
        entity_key = match.group(2)
        entity_block = match.group(3)
        
        # Extract time period line
        time_period_match = re.search(r"- Time period: ([^|]+?)\s*\|", entity_block)
        time_period = None
        if time_period_match:
            time_period_str = time_period_match.group(1).strip()
            if time_period_str and time_period_str != "-":
                time_period = time_period_str
        
        # Extract roles line
        roles_match = re.search(r"- Roles: (.+?)(?:\n|$)", entity_block)
        roles = []
        if roles_match:
            roles_str = roles_match.group(1).strip()
            if roles_str and roles_str != "-":
                roles = [r.strip() for r in roles_str.split(",")]
        
        entity_info[entity_key] = {
            'name': entity_name,
            'roles': roles,
            'time_period': time_period
        }
    
    return entity_info

def analyze_group_from_review(review_file_path, group_id):
    """Analyze a specific group from a review file."""
    entity_info = extract_entity_info_from_review_file(review_file_path)
    
    if len(entity_info) < 2:
        return None
    
    # Extract roles and time periods
    all_roles = [set(info['roles']) for info in entity_info.values()]
    all_time_periods = [info['time_period'] for info in entity_info.values()]
    
    notes = []
    
    # Check for role differences
    non_empty_roles = [r for r in all_roles if r]
    
    if len(non_empty_roles) >= 2:
        # Multiple entities have roles - check if they differ
        if not all(r == non_empty_roles[0] for r in non_empty_roles):
            notes.append("Different roles")
    
    # Check for time period differences
    non_empty_time_periods = [tp for tp in all_time_periods if tp]
    
    if len(non_empty_time_periods) >= 2:
        # Multiple entities have time periods - check if they differ
        if not all(tp == non_empty_time_periods[0] for tp in non_empty_time_periods):
            notes.append("Different time periods")
    
    return notes if notes else None

def find_review_file_for_group(confidence_id, review_dir):
    """Find the review file containing a specific group."""
    # Extract group name and number from id like "same_name:rebekah" or "prefix:akiva"
    group_type, group_name = confidence_id.split(":", 1)
    
    # Determine file prefix
    if group_type == "same_name":
        file_prefix = "person_same_name_matches"
    elif group_type == "prefix":
        file_prefix = "person_prefix_matches"
    else:
        return None
    
    # Search through review files
    for review_file in sorted(review_dir.glob(f"{file_prefix}_*.md")):
        with open(review_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if f'"{group_name}"' in content and confidence_id in content:
                return review_file
    
    return None

def extract_entity_keys_from_confidence(confidence_line):
    """Extract entity keys from a merge-confidence comment line."""
    pattern = r'<!-- merge-confidence: (\{[^}]+\}) -->'
    match = re.search(pattern, confidence_line)
    if match:
        try:
            data = json.loads(match.group(1))
            return data.get('keys', [])
        except json.JSONDecodeError:
            pass
    return []

def get_entity_info_from_confidence_file(confidence_file):
    """Extract entity information from the review files referenced by a confidence file."""
    review_dir = confidence_file.parent
    
    # Map of confidence_id -> entity_info from review files
    group_analysis = {}
    
    with open(confidence_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        pattern = r'<!-- merge-confidence: (\{[^}]+\}) -->'
        match = re.search(pattern, line)
        if match:
            try:
                data = json.loads(match.group(1))
                group_id = data.get('id')
                keys = data.get('keys', [])
                
                if len(keys) >= 2:
                    # Find review file for this group
                    review_file = find_review_file_for_group(group_id, review_dir)
                    if review_file:
                        entity_info = extract_entity_info_from_review_file(review_file)
                        
                        # Analyze roles and time periods
                        notes = []
                        
                        # Get info for entities in this group
                        group_entity_info = [entity_info.get(k) for k in keys if k in entity_info]
                        if len(group_entity_info) >= 2:
                            # Check roles
                            all_roles = [set(info['roles']) if info else set() for info in group_entity_info]
                            non_empty_roles = [r for r in all_roles if r]
                            if len(non_empty_roles) >= 2:
                                if not all(r == non_empty_roles[0] for r in non_empty_roles):
                                    notes.append("Different roles")
                            
                            # Check time periods
                            all_time_periods = [info['time_period'] if info else None for info in group_entity_info]
                            non_empty_time_periods = [tp for tp in all_time_periods if tp]
                            if len(non_empty_time_periods) >= 2:
                                if not all(tp == non_empty_time_periods[0] for tp in non_empty_time_periods):
                                    notes.append("Different time periods")
                        
                        if notes:
                            group_analysis[group_id] = notes
            except json.JSONDecodeError:
                pass
    
    return group_analysis

def update_confidence_file(confidence_file):
    """Update a confidence file to add role/timeperiod notes."""
    print(f"Processing {confidence_file.name}...")
    
    group_analysis = get_entity_info_from_confidence_file(confidence_file)
    
    if not group_analysis:
        print(f"  No role/timeperiod differences found")
        return False
    
    print(f"  Found {len(group_analysis)} group(s) with role/timeperiod differences")
    
    # Read current file
    with open(confidence_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update the file
    updated_lines = []
    for line in lines:
        updated_lines.append(line)
        
        # Check if this line contains a merge-confidence comment
        pattern = r'<!-- merge-confidence: (\{[^}]+\}) -->'
        match = re.search(pattern, line)
        if match:
            try:
                data = json.loads(match.group(1))
                group_id = data.get('id')
                if group_id in group_analysis:
                    notes = group_analysis[group_id]
                    note_text = " | ".join(notes)
                    # Find the indentation
                    indent = len(line) - len(line.lstrip())
                    updated_lines.append(" " * indent + f"*Note: {note_text}*\n")
                    print(f"    Added note to '{group_id}': {note_text}")
            except json.JSONDecodeError:
                pass
    
    # Write back
    with open(confidence_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def main():
    # Update both confidence files
    base_dir = Path("C:/ChatBlatt_data_files/real_data/merge_review")
    
    files_to_update = [
        base_dir / "confidence_person_same_name_matches.md",
        base_dir / "prefix_matches" / "confidence_person_prefix_matches.md"
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            try:
                update_confidence_file(file_path)
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
