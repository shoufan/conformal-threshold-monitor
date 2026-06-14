# PDF export notes

- Source: [`two_page_report.md`](two_page_report.md)
- Output: [`two_page_report.pdf`](two_page_report.pdf)
- Page count: 2
- Page size: US Letter
- Status: visually reviewed and ready for submission

## Export route

The PDF was generated locally with ReportLab from the Markdown source:

```bash
/Users/shoufan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /private/tmp/render_two_page_report.py
```

The report uses a balanced two-column first page and a centered single-column
second page. Tables are kept intact so they cannot split across columns.

## Quality check

Both pages were rasterized with the bundled PDF.js and canvas libraries and
reviewed at full resolution. The title, tables, headings, body text, bullets,
and page numbers render cleanly with no clipping or overlap.

The first attempted raster check used the bundled Poppler binary, whose local
font cache was misconfigured. That process was stopped; it did not alter the
PDF. The PDF.js raster check completed successfully.

A final human glance in the submission portal's PDF preview is still
recommended because browser viewers can apply their own scaling.
