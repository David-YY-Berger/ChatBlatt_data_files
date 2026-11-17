# Merge Candidates Review - Role and Time Period Notes

## Summary

Added informative notes to merge candidate confidence files to highlight when candidates have **different roles** or **different time periods**. This helps reviewers quickly identify potentially problematic merges.

## What Was Done

### Files Updated
1. `C:\ChatBlatt_data_files\real_data\merge_review\confidence_person_same_name_matches.md`
2. `C:\ChatBlatt_data_files\real_data\merge_review\prefix_matches\confidence_person_prefix_matches.md`

### Changes Made

Added inline notes (formatted as `*Note: <message>*`) immediately following the merge-confidence comment for groups where candidates have:
- **Different roles**: Multiple candidates have different role assignments (e.g., one is a rabbi, another is a judge)
- **Different time periods**: Multiple candidates belong to different historical periods (e.g., one from the Second Temple period, another from the Talmudic period)

### Logic Applied

Notes are only added when:
- Two or more candidates have actual role/time period values
- Those values **differ** from each other

Notes are **NOT** added when:
- All candidates have the same roles and time periods (or both are null)
- Only one candidate has a role/time period and others are null
- No candidates have the field populated

## Results

### Same-name Matches File
- **Total notes added**: 206 groups
  - Different roles: 16 groups
  - Different time periods: 202 groups

### Prefix Matches File  
- **Total notes added**: 116 groups
  - Different roles: 32 groups
  - Different time periods: 113 groups

### Combined
- **Total notes across both files**: 322 groups

## Examples

### Example 1: Different Roles (Same-name match)
```
9. **30%** "samuel" (2 entities) <!-- merge-confidence: {"id": "same_name:samuel", "confidence": 30, "keys": ["6ae8d876dafb34fd0cdc27be", "6ae8e3e6733d1062d7902bac"]} -->
*Note: Different roles*
   - weakest pair: `samuel` vs `samuel`
   - base 40% (same name)
   - +5: same Hebrew name
   - -25: different parents
   - +10: 4 shared related entities
```

### Example 2: Different Time Periods (Prefix match)
```
50. **90%** "elazar bar yosei" (2 entities) <!-- merge-confidence: {"id": "prefix:elazar bar yosei", "confidence": 90, "keys": ["6aeaaa6b696908d815876301", "6aea568e77173b9acdf2806c"]} -->
*Note: Different time periods*
   - weakest pair: `elazar bar yosei` vs `rabbi elazar bar yosei`
   - base 85% (title-prefix)
   - +5: same Hebrew name
```

## How to Use

When reviewing merge candidates:
1. Review the notes immediately following the confidence percentages
2. Groups flagged with role or time period differences merit extra scrutiny
3. These differences often indicate the candidates are actually different people despite similar names
4. The underlying entity data (roles, time periods) is already visible in the individual review files if you need more detail

## Script Details

The script (`add_role_timeperiod_notes.py`) works by:
1. Parsing each confidence file to extract group IDs and entity keys
2. Finding the corresponding review file for each group
3. Extracting entity role and time period information from the review file markdown
4. Comparing roles and time periods across candidates in each group
5. Adding notes only when meaningful differences are found
6. Inserting notes directly into the confidence files with proper formatting and indentation
