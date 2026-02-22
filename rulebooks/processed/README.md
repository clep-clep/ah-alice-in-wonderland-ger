# Rulebook Processing Output

These files are prepared as reference material for glossary work and translations.

## Structure

- `core/`
  - Core documents (rules reference EN/DE, FAQ DE) as `*.txt` and `*.pages.jsonl`
- `campaigns/`
  - Processed campaign rulebooks (`*_kampagne.txt`, `*_kampagne.pages.jsonl`)
- `investigators/`
  - Processed investigator rulebooks (`*_ermittler.txt`, `*_ermittler.pages.jsonl`)

## Terminology Usage

- Terms can be searched directly in the `*.txt` files.
- For automation or scripting, the `*.pages.jsonl` files are the most stable format.

## Conversion

- The PDF rulebooks were converted to text with `pypdf`.
- This produces both full-text files (`*.txt`) and page-wise outputs (`*.pages.jsonl`).
