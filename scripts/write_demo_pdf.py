from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fixtures" / "pilbara-lithium.pdf"
CONTENT = b"""BT /F1 18 Tf 72 720 Td (Pilbara Lithium Resource Statement) Tj ET"""
stream = b"<< /Length %d >>\nstream\n" % len(CONTENT) + CONTENT + b"\nendstream\n"

objects = [
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
    b"4 0 obj\n" + stream + b"endobj\n",
    b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
]

parts = [b"%PDF-1.4\n"]
offsets = [0]
for obj in objects:
    offsets.append(sum(len(p) for p in parts))
    parts.append(obj)
xref_pos = sum(len(p) for p in parts)
xref = [b"xref\n0 6\n0000000000 65535 f \n"]
for off in offsets[1:]:
    xref.append(f"{off:010d} 00000 n \n".encode("ascii"))
trailer = (
    b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
    + f"startxref\n{xref_pos}\n".encode("ascii")
    + b"%%EOF\n"
)
OUT.write_bytes(b"".join(parts + xref + [trailer]))
print(OUT)
