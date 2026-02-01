import re

with open("wttj_source.html", "r", encoding="utf-8") as f:
    content = f.read()

output = []

# Find "algolia"
indices = [m.start() for m in re.finditer('algolia', content, re.IGNORECASE)]
for i in indices[:3]: # first 3 matches
    start = max(0, i - 1000)
    end = min(len(content), i + 1000)
    output.append(f"--- MATCH at {i} ---\n")
    output.append(content[start:end])
    output.append("\n\n")

# Find "appId"
indices_id = [m.start() for m in re.finditer('appId', content)]
for i in indices_id[:3]:
    start = max(0, i - 200)
    end = min(len(content), i + 500)
    output.append(f"--- APPID MATCH at {i} ---\n")
    output.append(content[start:end])
    output.append("\n\n")

with open("wttj_snippets.txt", "w", encoding="utf-8") as f:
    f.writelines(output)

print("Saved snippets to wttj_snippets.txt")
