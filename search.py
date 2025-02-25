from typing import List, Dict, Tuple, Any
from pygments.token import Token, is_token_subtype
from utils import tokenize_code, remove_insignificant_tokens

def find_matching_lines(match_structure: List[Tuple[str, List[Tuple]]], source_code_tokens: List[List[Tuple]]) -> List[str]:
    matched_lines = set()
    flat_tokens = []
    line_numbers = []

    for line_idx, line in enumerate(source_code_tokens):
        for token_info in line:
            token_type, token_value = token_info
            if not is_token_subtype(token_type, Token.Text):
                flat_tokens.append(token_info)
                line_numbers.append(line_idx + 1)

    for operator, tokens in match_structure:
        if operator != '...':
            continue

        match_tokens = [t for t in tokens if not is_token_subtype(t[0], Token.Text) and not (is_token_subtype(t[0], Token.Operator) and t[1] == '>>>')]
        if not match_tokens:
            continue

        match_idx = 0
        source_idx = 0
        start_line = None
        paren_level = 0

        while source_idx < len(flat_tokens) and match_idx < len(match_tokens):
            match_type, match_value = match_tokens[match_idx]
            source_type, source_value = flat_tokens[source_idx]

            if match_type == Token.Punctuation and match_value == '(':
                paren_level += 1
                if start_line is None:
                    start_line = line_numbers[source_idx]
                match_idx += 1
                source_idx += 1
            elif match_type == Token.Punctuation and match_value == ')':
                paren_level -= 1
                while source_idx < len(flat_tokens) and (flat_tokens[source_idx][0] != Token.Punctuation or flat_tokens[source_idx][1] != ')'):
                    source_idx += 1
                if source_idx < len(flat_tokens):
                    source_idx += 1
                match_idx += 1
            elif match_type == source_type and match_value == source_value:
                if start_line is None:
                    start_line = line_numbers[source_idx]
                match_idx += 1
                source_idx += 1
            elif paren_level > 0:
                source_idx += 1
            else:
                match_idx = 0
                source_idx += 1
                start_line = None
                paren_level = 0

            if match_idx == len(match_tokens) and start_line is not None:
                matched_lines.update(range(start_line, line_numbers[source_idx - 1] + 1))

        if match_idx == len(match_tokens) and start_line is not None:
            matched_lines.update(range(start_line, line_numbers[source_idx - 1] + 1))

    sorted_lines = sorted(matched_lines)
    ranges = []
    if not sorted_lines:
        return []

    start = sorted_lines[0]
    prev = start
    for curr in sorted_lines[1:] + [None]:
        if curr != prev + 1:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = curr
        prev = curr if curr is not None else prev

    return ranges

def check_ggg_in_lines(match_text: str, language: str) -> List[Dict[str, Any]]:
    lines = match_text.split('\n')
    ggg_count = 0
    results = []

    for line in lines:
        if not line.strip():
            continue

        tokens = tokenize_code(line.strip(), language)
        filtered_tokens = remove_insignificant_tokens(tokens, language)

        ggg_index = next((i for i, t in enumerate(filtered_tokens) if is_token_subtype(t[0], Token.Operator) and t[1] == '>>>'), -1)

        if ggg_index != -1:
            ggg_count += 1
            before_ggg = [t for t in filtered_tokens[:ggg_index] if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
            after_ggg = [t for t in filtered_tokens[ggg_index + 1:] if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]

            before_ellipsis = []
            after_ellipsis = []
            paren_level = 0
            ellipsis_found = False

            for token_type, token_value in after_ggg:
                if token_type == Token.Punctuation and token_value == '(':
                    paren_level += 1
                    if not ellipsis_found:
                        before_ellipsis.append((token_type, token_value))
                elif token_type == Token.Punctuation and token_value == ')':
                    paren_level -= 1
                    if paren_level == 0 and ellipsis_found:
                        after_ellipsis.append((token_type, token_value))
                    elif not ellipsis_found:
                        before_ellipsis.append((token_type, token_value))
                elif token_type == Token.Operator and token_value == '...' and paren_level > 0:
                    ellipsis_found = True
                elif not ellipsis_found:
                    before_ellipsis.append((token_type, token_value))
                elif ellipsis_found and paren_level == 0:
                    after_ellipsis.append((token_type, token_value))

            results.append({
                'operator_number': ggg_count,
                'before': before_ggg,
                'after': {'before_ellipsis': before_ellipsis, 'after_ellipsis': after_ellipsis}
            })

    return results

def find_tokens_in_source(ggg_data: List[Dict[str, Any]], source_tokens: List[List[Tuple]]) -> Dict:
    def search_token_group(before_group, after_group):
        if not before_group and not after_group:
            return []
        matched_lines = []
        for line_idx, line_tokens in enumerate(source_tokens):
            filtered_line = [t for t in line_tokens if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
            if len(filtered_line) < len(before_group) + len(after_group):
                continue
            for i in range(len(filtered_line) - len(before_group) - len(after_group) + 1):
                if filtered_line[i:i + len(before_group)] == before_group:
                    if not after_group:
                        matched_lines.append((line_idx + 1, i))
                        break
                    remaining_tokens = filtered_line[i + len(before_group):]
                    if len(remaining_tokens) >= len(after_group):
                        for j in range(len(remaining_tokens) - len(after_group) + 1):
                            if remaining_tokens[j:j + len(after_group)] == after_group:
                                matched_lines.append((line_idx + 1, i))
                                break
                        if matched_lines and matched_lines[-1][0] == line_idx + 1:
                            break
        return matched_lines

    results = {}
    for entry in ggg_data:
        operator_num = entry['operator_number']
        before_ggg = entry['before']
        after_ggg = entry['after']
        before_ellipsis = after_ggg['before_ellipsis']
        after_ellipsis = after_ggg['after_ellipsis']

        results[operator_num] = {}
        if before_ggg:
            before_lines = search_token_group(before_ggg, [])
            results[operator_num]['before_lines'] = before_lines
            results[operator_num]['before_group'] = before_ggg
        if before_ellipsis or after_ellipsis:
            after_lines = search_token_group(before_ellipsis, after_ellipsis)
            results[operator_num]['after_lines'] = after_lines
            results[operator_num]['after_group'] = before_ellipsis + after_ellipsis

    return results

def find_alternative_tokens(ggg_data: List[Dict[str, Any]], match_results: Dict, source_tokens: List[List[Tuple]], match_text: str) -> Dict:
    match_lines = match_text.split('\n')

    def search_token_group(group: List[Tuple]) -> List[int]:
        if not group:
            return []
        matched_lines = []
        for line_idx, line_tokens in enumerate(source_tokens):
            filtered_line = [t for t in line_tokens if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
            if len(filtered_line) < len(group):
                continue
            for i in range(len(filtered_line) - len(group) + 1):
                if filtered_line[i:i + len(group)] == group:
                    matched_lines.append(line_idx + 1)
                    break
        return matched_lines

    results = {}
    for entry in ggg_data:
        operator_num = entry['operator_number']
        before_ggg = entry['before']
        after_ggg = entry['after']
        before_ellipsis = after_ggg['before_ellipsis']
        after_ellipsis = after_ggg['after_ellipsis']

        has_tokens = bool(before_ggg or before_ellipsis or after_ellipsis)
        if has_tokens:
            continue

        ggg_line_idx = None
        for i, line in enumerate(match_lines):
            if '>>>' in line:
                temp_ggg_data = check_ggg_in_lines('\n'.join(match_lines[:i + 1]), "python")
                if any(e['operator_number'] == operator_num for e in temp_ggg_data):
                    ggg_line_idx = i
                    break

        if ggg_line_idx is None:
            continue

        results[operator_num] = {}
        if ggg_line_idx > 0:
            prev_line = match_lines[ggg_line_idx - 1].strip()
            prev_tokens = tokenize_code(prev_line, "python")
            filtered_prev_tokens = remove_insignificant_tokens(prev_tokens, "python")
            has_ellipsis = any(t[1] == '...' for t in filtered_prev_tokens)
            if not has_ellipsis and filtered_prev_tokens:
                matched_lines = search_token_group(filtered_prev_tokens)
                results[operator_num]['prev_line_matches'] = matched_lines
                continue

        if ggg_line_idx + 1 < len(match_lines):
            next_line = match_lines[ggg_line_idx + 1].strip()
            next_tokens = tokenize_code(next_line, "python")
            filtered_next_tokens = remove_insignificant_tokens(next_tokens, "python")
            if filtered_next_tokens:
                matched_lines = search_token_group(filtered_next_tokens)
                results[operator_num]['next_line_matches'] = matched_lines

    return results