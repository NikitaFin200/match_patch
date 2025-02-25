from typing import List, Tuple
from pygments.token import Token, is_token_subtype
from utils import tokenize_code, remove_insignificant_tokens

def remove_in_tok_match(filepath: str, language: str) -> List[Tuple[str, List[Tuple]]]:
    from utils import load_code_from_markdown
    match, _ = load_code_from_markdown(filepath)
    match = match.split('\n')
    token_list = []

    for mch in match:
        tokens = tokenize_code(mch, language)
        filtered_tokens = remove_insignificant_tokens(tokens, language)

        paren_level = 0
        cleaned_tokens = []
        for token_type, token_value in filtered_tokens:
            if token_type == Token.Punctuation and token_value == '(':
                paren_level += 1
                cleaned_tokens.append((token_type, token_value))
            elif token_type == Token.Punctuation and token_value == ')':
                paren_level -= 1
                cleaned_tokens.append((token_type, token_value))
            elif token_type == Token.Operator and token_value == '...' and paren_level > 0:
                continue
            else:
                cleaned_tokens.append((token_type, token_value))

        token_list.extend(cleaned_tokens)

    return group_tokens(token_list)

def group_tokens(tokens: List[Tuple]) -> List[Tuple[str, List[Tuple]]]:
    result = []
    current_operator = None
    current_group = []
    paren_level = 0

    for token in tokens:
        token_type, token_value = token
        if token_type == Token.Punctuation and token_value == '(':
            paren_level += 1
            current_group.append(token)
        elif token_type == Token.Punctuation and token_value == ')':
            paren_level -= 1
            current_group.append(token)
        elif is_token_subtype(token_type, Token.Operator) and token_value == '...' and paren_level == 0:
            if current_operator or current_group:
                result.append((current_operator, current_group))
            current_operator = token_value
            current_group = []
        elif is_token_subtype(token_type, Token.Operator) and token_value == '>>>':
            current_group.append(token)
        elif is_token_subtype(token_type, Token.Operator) and token_value == '<<<':
            continue
        else:
            current_group.append(token)

    if current_operator or current_group:
        result.append((current_operator, current_group))

    return result

def process_match_structure(match_structure: List[Tuple[str, List[Tuple]]]) -> None:
    tokens_after_ellipsis = []
    for operator, tokens in match_structure:
        if operator == '...':
            if tokens_after_ellipsis:
                print(f'Tokens after "...":')
                for token in tokens_after_ellipsis:
                    print(f'  {token}')
            tokens_after_ellipsis = tokens
        elif operator == '>>>':
            if tokens_after_ellipsis:
                print(f'Tokens after "...":')
                for token in tokens_after_ellipsis:
                    print(f'  {token}')
            tokens_after_ellipsis = []
            print(f'Encountered operator ">>>", stopping token collection.')
    if tokens_after_ellipsis:
        print(f'Tokens after "...":')
        for token in tokens_after_ellipsis:
            print(f'  {token}')