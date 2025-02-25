from typing import List, Dict, Tuple, Any
from pygments.token import Token, is_token_subtype  # Добавляем импорт
from utils import load_code_from_markdown, source_to_tokenList, tokenize_code  # Добавляем tokenize_code для полноты

def insert_patch(source_file: str, markdown_file: str, match_results: Dict) -> None:
    _, patch_text = load_code_from_markdown(markdown_file)
    source_tokens = source_to_tokenList(source_file, tokenize_code, "python")

    with open(source_file, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    def get_token_positions(line: str, line_tokens: List[Tuple]) -> List[Tuple[int, int, Tuple]]:
        positions = []
        current_pos = 0
        for token in line_tokens:
            token_type, token_value = token
            try:
                start = line.index(token_value, current_pos)
                end = start + len(token_value)
                positions.append((start, end, token))
                current_pos = end
            except ValueError:
                break
        return positions

    processed_lines = set()
    for operator_num, matches in match_results.items():
        if 'before_lines' in matches and matches['before_lines']:
            before_group = matches['before_group']
            for line_num, token_start_idx in matches['before_lines']:
                line_idx = line_num - 1
                if line_idx in processed_lines:
                    continue

                line = source_lines[line_idx]
                line_tokens = source_tokens[line_idx]
                filtered_line = [t for t in line_tokens if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
                token_positions = get_token_positions(line, line_tokens)
                filtered_indices = [i for i, t in enumerate(line_tokens) if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
                actual_start_idx = filtered_indices[token_start_idx]

                group_size = len(before_group)
                end_idx = actual_start_idx + group_size - 1
                if end_idx < len(token_positions):
                    _, end_pos, _ = token_positions[end_idx]
                    source_lines[line_idx] = line[:end_pos] + " " + patch_text + line[end_pos:]
                else:
                    source_lines[line_idx] = line.rstrip() + " " + patch_text

                processed_lines.add(line_idx)

        if 'after_lines' in matches and matches['after_lines']:
            after_group = matches['after_group']
            for line_num, token_start_idx in matches['after_lines']:
                line_idx = line_num - 1
                if line_idx in processed_lines:
                    continue

                line = source_lines[line_idx]
                line_tokens = source_tokens[line_idx]
                filtered_line = [t for t in line_tokens if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
                token_positions = get_token_positions(line, line_tokens)
                filtered_indices = [i for i, t in enumerate(line_tokens) if not (is_token_subtype(t[0], Token.Text) and t[1].isspace())]
                actual_start_idx = filtered_indices[token_start_idx]

                start_pos, _, _ = token_positions[actual_start_idx]
                source_lines[line_idx] = line[:start_pos] + patch_text + " " + line[start_pos:]

                processed_lines.add(line_idx)

    with open(source_file, 'w', encoding='utf-8') as f:
        f.writelines(source_lines)

def insert_patch_based_on_alternative(source_file: str, markdown_file: str, alternative_results: Dict) -> None:
    _, patch_text = load_code_from_markdown(markdown_file)
    with open(source_file, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    line_offset = 0
    for operator_num, matches in alternative_results.items():
        if 'prev_line_matches' in matches:
            for line_num in matches['prev_line_matches']:
                insert_idx = line_num + line_offset
                source_lines.insert(insert_idx, patch_text + '\n')
                line_offset += 1
                print(f"Патч вставлен после строки {line_num} для '>>>' (номер {operator_num})")

        if 'next_line_matches' in matches:
            for line_num in matches['next_line_matches']:
                insert_idx = line_num - 1 + line_offset
                source_lines.insert(insert_idx, patch_text + '\n')
                line_offset += 1
                print(f"Патч вставлен перед строкой {line_num} для '>>>' (номер {operator_num})")

    with open(source_file, 'w', encoding='utf-8') as f:
        f.writelines(source_lines)