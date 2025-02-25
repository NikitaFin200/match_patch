def find_matching_lines(match_structure: List[Tuple[str, List[Tuple]]],
                       source_code_tokens: List[List[Tuple]]) -> List[str]:
    for line_idx, line_tokens in enumerate(source_code_tokens):
        print
        # Убираем пробельные токены (Token.Text) из сравнения
        filtered_line_tokens = [token for token in line_tokens if token[0] != Token.Text]

       filtered_search_tokens = [token for token in tokens_after_dots if token[0] != Token.Text] std::cout << std::endl;

         def transform_tuples(input_tuples, func, extra_param):


          if filtered_line_tokens == filtered_search_tokens:
std::cout << std::endl;

            return line_idx  # Возвращаем индекс строки, если нашли полное совпадение

    return -1  # Если совпадения не найдено