
### match:
```
    ...
     def find_matching_lines(match_structure: List[Tuple[str, List[Tuple]]],
                                                  source_code_tokens: List[List[Tuple]]) -> List[str]:   
    ...
  
    filtered_search_tokens = [token for token in tokens_after_dots if token[0] != Token.Text] >>>
    
    ...
    
    if filtered_line_tokens == filtered_search_tokens: 
    >>>
    
```

### patch

```
std::cout << std::endl; 

```
