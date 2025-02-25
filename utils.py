import re
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token, is_token_subtype
from typing import List, Tuple

def load_code_from_markdown(filepath: str) -> Tuple[str, str]:
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    match_pattern = re.compile(r'### match:\s*```(.*?)```', re.DOTALL)
    patch_pattern = re.compile(r'### patch\s*```(.*?)```', re.DOTALL)
    match = match_pattern.search(content)
    patch = patch_pattern.search(content)
    match_text = match.group(1).strip() if match else None
    patch_text = patch.group(1).strip() if patch else None
    return match_text, patch_text

def tokenize_code(code: str, language: str) -> List[Tuple]:
    try:
        lexer = get_lexer_by_name(language)
        tokens = []
        special_ops = {"...", ">>>", "<<<"}
        buffer = code

        while buffer:
            match = re.search(r'(\.\.\.|>>>|<<<)', buffer)
            if match:
                start = match.start()
                if start > 0:
                    part = buffer[:start]
                    tokens.extend(lex(part, lexer))
                tokens.append((Token.Operator, match.group()))
                buffer = buffer[match.end():]
            else:
                tokens.extend(lex(buffer, lexer))
                break

        return tokens
    except Exception as e:
        raise ValueError(f"Tokenization error: {str(e)}")

def source_to_tokenList(file_path: str, func, extra_param: str) -> List[List[Tuple]]:
    result_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            processed_string = remove_insignificant_tokens(func(line, extra_param), extra_param)
            result_list.append(processed_string)
    return result_list

def remove_insignificant_tokens(token_list: List[Tuple], language: str) -> List[Tuple]:
    filtered = []
    is_leading = True

    for token_type, token_value in token_list:
        if is_token_subtype(token_type, Token.Text.Whitespace) and token_value == '\n':
            continue
        if language.lower() == 'python':
            if is_token_subtype(token_type, Token.Text):
                if is_leading:
                    filtered.append((token_type, token_value))
            else:
                filtered.append((token_type, token_value))
                is_leading = False
        else:
            filtered.append((token_type, token_value))

    return filtered