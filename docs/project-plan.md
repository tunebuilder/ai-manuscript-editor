## 1  Streamlit UI (minimal first)
Sidebar ➜ password field OPENAI_API_KEY, file-uploader, “Begin Processing” button.

Main area ➜ st.status & st.progress placeholders (cleared/reused per run).

Disable all inputs while a job is running; re-enable on finish/error.

## 2  Document Ingestion
Detect filetype (pdf, docx) ⇒ pull raw text preserving every \n.

Unit-test both extractors with 1–2-page fixtures.

## 3  Chunking Engine (docs-driven)
Load and adapt the starter function from docs/chunk-logic.md.

Replace its truncated regex with:

python
Copy
Edit
DAY_RE = re.compile(r'^\s*Day\s+(\d+)\b.*', re.I)
Return List[dict] objects: {"day": <int>, "text": <full_entry_with_header>}.

Log chunk count to sidebar. 

## 4  Batched Editing via OpenAI
System prompt — read exactly from docs/openai-api.md at runtime (1-liner file read) so non-coders can tweak rules. 

Request payload mirrors template:

python
Copy
Edit
client.chat.completions.create(
    model="gpt-4.5-preview",
    messages=[SYSTEM_MSG, USER_MSG],
    temperature=0.43,
    max_completion_tokens=16_384,
    top_p=1,
)
Pass edited entry back in response.choices[0].message.content.

Batch size = 4 chunks (fits token window + keeps UI responsive).

Retry with exponential back-off if status ≥ 500 or RateLimitError.

Store results in a list (order preserved) — pandas unnecessary here.

## 5  Re-assembly & Export
Concatenate edited chunks with two blank lines between days.

Use ReportLab to write a simple PDF (single style, A4 portrait).

Render st.download_button with in-memory bytes (no disk I/O).

## 6  UX Polish
st.status messages:

“Parsed ✓ — 38 entries”

“Sending batch 3/10 …”

“Done — generating PDF”

Write error banners via st.error(); keep partial progress data so user can retry without re-uploading.


## 7  Documentation
create README.md file
optimize gitignore
confirm that requirements.txt has all dependencies
