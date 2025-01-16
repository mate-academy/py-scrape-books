import json

# Paths to your input and output files
jl_file_path = 'books.jl'
json_file_path = 'books.json'

books = []

with open(jl_file_path, 'r', encoding='utf-8') as jl_file:
    for line in jl_file:
        book = json.loads(line)
        books.append(book)

with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(books, json_file, ensure_ascii=False, indent=4)

print(f"Converted {jl_file_path} to {json_file_path}")
