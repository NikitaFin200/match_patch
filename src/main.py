from utils import load_code_from_markdown, source_to_tokenList, tokenize_code
from token_processing import remove_in_tok_match, process_match_structure
from search import find_matching_lines, check_ggg_in_lines, find_tokens_in_source, find_alternative_tokens
from patch import insert_patch, insert_patch_based_on_alternative

# Пути к файлам
source_file = "xpressions.py"
markdown_file = "add_function_end.md"

# Загрузка данных
match_text, _ = load_code_from_markdown(markdown_file)
source_tokens = source_to_tokenList(source_file, tokenize_code, "python")
tr4 = remove_in_tok_match(markdown_file, "python")

# Вывод результатов
print("Match:", tr4)
print("Source:", source_tokens)
process_match_structure(tr4)

# Поиск совпадающих строк
matched_lines = find_matching_lines(tr4, source_tokens)
print("Matched lines indices:", matched_lines)

# Основной процесс
ggg_data = check_ggg_in_lines(match_text, "python")
match_results = find_tokens_in_source(ggg_data, source_tokens)
insert_patch(source_file, markdown_file, match_results)

# Альтернативный процесс
alternative_results = find_alternative_tokens(ggg_data, match_results, source_tokens, match_text)
insert_patch_based_on_alternative(source_file, markdown_file, alternative_results)