# utils/chunker.py
import textwrap, tiktoken, re, math, json

TOKEN_LIMIT = 400    # adjust later
TABLE_LIMIT = 2000   # separate limit for tables
enc = tiktoken.get_encoding("cl100k_base")

def split_markdown(md: str, limit=TOKEN_LIMIT):
    paragraphs, chunk, count = [], [], 0
    lines = md.splitlines(keepends=False)

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle table blocks
        if line.lstrip().startswith("|"):
            table = [line]
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table.append(lines[i])
                i += 1
            para = "\n".join(table)
            delta = len(enc.encode(para))

            # Use TABLE_LIMIT for table chunks
            if count + delta > TABLE_LIMIT and chunk:
                paragraphs.append("\n".join(chunk))
                chunk, count = [], 0
            chunk.append(para)
            count += delta
        else:
            para = line
            delta = len(enc.encode(para))
            if count + delta > limit and chunk:
                paragraphs.append("\n".join(chunk))
                chunk, count = [], 0
            chunk.append(para)
            count += delta
            i += 1

    if chunk:
        paragraphs.append("\n".join(chunk))
    return paragraphs
