#!/usr/bin/env python3
"""Fast, non-destructive comparison of OTS cassette BASIC listings with the scanned book.

Uses OCR only because the original PDF is image-only. Number mismatches are
candidates for visual inspection, not automatic corrections. Spectrum escape
sequences in braces are treated as expected and never flagged on their own.

Usage: python3 audit_ots_book.py --pdf book.pdf --root OverTheSpectrum \
   --report OverTheSpectrum/audit_book_vs_tape.md --json OverTheSpectrum/audit_book_vs_tape.json
Requires PyMuPDF and system Tesseract OCR. No originals are modified.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path
import argparse, json, os, re, subprocess, sys
import fitz

PDF_SOURCE=''
# Book contents (printed-page starts; order of chapters, not cassette order).
CHAPTERS=[
 ('leapfrog','Leapfrog',1), ('reversal','Number Reversal',4),
 ('asteroids','Asteroids in Space',7), ('clock','Spectrum Clock',10),
 ('mazeman','3-D Mazeman',15), ('geometry','Geometry Test',21),
 ('kings','Kings and Queens',23), ('blackjack','Blackjack',27),
 ('fruit','Fruit Machine',32), ('bubble','Bubble Sort',41),
 ('equation','Simultaneous Equations',47), ('escape','Space Escape',51),
 ('lunar','Lunar Lander',55), ('alienblitz','Alien Blitz',60),
 ('invaders','Spectrum Invaders',64), ('meteor','Meteor Storm',69),
 ('eliminator','Eliminator',77), ('f-way-frog','Freeway Frog',83),
 ('hires','High Resolution Graphics',95), ('renum','Line Renumbering',102),
 ('delete','Block Line Delete',108), ('monitor','Machine Code Monitor',111),
 ('payroll','Payroll',118), ('sales','Sales Analysis',125),
 ('evaluate','Possessions Evaluation',130), ('chess','Chess',135),
 ('draughts','Draughts',141), ('advent','Adventure',152),
]
EXTRA='frogshapes'
BASIC_KW={
 'LET','PRINT','INPUT','IF','THEN','FOR','NEXT','GO','GOTO','GOSUB','SUB','RETURN',
 'REM','DATA','READ','POKE','PEEK','BORDER','PAPER','INK','BRIGHT','FLASH','INVERSE',
 'OVER','CLS','PLOT','DRAW','CIRCLE','RANDOMIZE','DIM','STOP','RUN','LOAD','SAVE',
 'RESTORE','CLEAR','CONTINUE','BEEP','PAUSE','DEF','LPRINT','LLIST','LIST', 'OUT'
}


def _ocr_page(job):
    pdf, index, dpi = job
    doc=fitz.open(pdf)
    pix=doc[index].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),colorspace=fitz.csGRAY,alpha=False)
    png=pix.tobytes('png'); doc.close()
    proc=subprocess.run(['tesseract','stdin','stdout','--psm','6','-l','eng'],
                        input=png,capture_output=True,timeout=35)
    if proc.returncode: raise RuntimeError(f'OCR PDF {index+1}: {proc.stderr[-500:]!r}')
    return index,proc.stdout.decode('utf-8','replace')


def norm(s):
    s=s.upper()
    s=re.sub(r'\{[^}]*\}', ' ',s)  # ZX Spectrum special characters expected
    return re.sub('[^A-Z0-9]+','',s)


def titlekey(s):
    return re.sub('[^A-Z0-9]+','',s.upper())


def page_title_score(text,title):
    head='\n'.join(text.splitlines()[:10])
    exact=titlekey(title)
    ls=[titlekey(x) for x in head.splitlines()]
    return max((SequenceMatcher(None,exact,line).ratio() for line in ls if line),default=0)


def page_for_printed(p):
    # Four unnumbered plates inserted in the original scan: two after book
    # page 24 and two more after page 40. Confirmed on the printed folios.
    return p + (8 if p <= 24 else 10 if p <= 40 else 12)


def print_for_pdf(pdf_page):
    if pdf_page <= 32: return pdf_page-8
    if pdf_page <= 50: return pdf_page-10
    return pdf_page-12


def _select_code_pages(pdf):
    import numpy as np
    with fitz.open(pdf) as book:
        chosen=[]
        for i in range(8,len(book)):
            pix=book[i].get_pixmap(matrix=fitz.Matrix(1,1),colorspace=fitz.csGRAY)
            a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
            y1=int(pix.height*.08);y2=int(pix.height*.87)
            l=(a[y1:y2,int(pix.width*.13):int(pix.width*.22)]<155).sum(axis=1)
            r=(a[y1:y2,int(pix.width*.22):int(pix.width*.29)]<155).sum(axis=1)
            s1=int(sum(l>2));s2=int(sum(r>2))
            # Remove full-bleed illustration plates and prose-only pages.
            if 25<=s1<350 or 45<=s2<350:
                chosen.append(i)
        return chosen

def parse_bas(path):
    out={}
    for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
        m=re.match(r'^\s*(\d{1,4})\s+(.*)$',line)
        if m:out[int(m[1])]=m[2]
    return out


def ocr_lines(text):
    results=[]
    for raw in text.splitlines():
        # OCR confuses leading 5 with S, 3 with S, 0 with O, 1 with I/l.
        m=re.match(r'^\s*([0-9OSIlB]{2,4})[ \t]+([A-Za-z][^\n]*)$',raw)
        if not m: continue
        n=m[1].upper().replace('S','5').replace('O','0').replace('I','1').replace('L','1').replace('B','8')
        if not n.isdigit() or not 1<=int(n)<=9999:continue
        body=m[2]
        first=re.match(r'^([A-Za-z]+)',body)
        kw=first[1].upper() if first else ''
        # OCR can have a malformed first keyword, but 'PRINT' and 'DATA' are common.
        if kw not in BASIC_KW and max((SequenceMatcher(None,kw,k).ratio() for k in BASIC_KW),default=0)<.65:
            continue
        results.append((int(n),body,raw))
    return results


def audit(pdf,root,dpi=165,workers=6):
    basfiles={p.parent.name.split('_',5)[-1]:p for p in root.glob('OTS_tape_*_side_*_*/*.bas')}
    expected=set(k for k,_,_ in CHAPTERS)|{EXTRA}
    if basfiles.keys()!=expected:
        raise RuntimeError('Unexpected BASIC files: '+repr((sorted(set(basfiles)-expected),sorted(expected-set(basfiles)))))
    with fitz.open(pdf) as book: n_pages=len(book)
    chosen=_select_code_pages(pdf)
    ocr={}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs=[pool.submit(_ocr_page,(str(pdf),i,dpi)) for i in chosen]
        for k,fut in enumerate(as_completed(jobs),1):
            index,text=fut.result(); ocr[index]=text
            if k%20==0:print(f'OCR code pages {k}/{len(jobs)}',file=sys.stderr,flush=True)
    starts={slug:(page_for_printed(printed)-1,1.0) for slug,title,printed in CHAPTERS}
    rows=[]
    for pos,(slug,title,printed) in enumerate(CHAPTERS):
        ix,score=starts[slug]
        if ix is None:
            rows.append(dict(program=slug,title=title,printed_page=printed,first_pdf_page=None,
                title_confidence=score,status='title not found',book_line_count=0,tape_line_count=len(parse_bas(basfiles[slug])),
                book_only=[],tape_only=[],body_candidates=[]))
            continue
        next_printed=CHAPTERS[pos+1][2] if pos+1<len(CHAPTERS) else n_pages-11
        end=min(page_for_printed(next_printed)-1,n_pages)
        extracted=[]
        for pi in range(ix,end):
            if pi not in ocr: continue
            for num,body,raw in ocr_lines(ocr[pi]):
                extracted.append(dict(number=num,body=body,pdf_page=pi+1,raw=raw))
        tape=parse_bas(basfiles[slug])
        bynum={}
        for ent in extracted:
            bynum.setdefault(ent['number'],[]).append(ent)
        book_nums=set(bynum)
        tape_nums=set(tape)
        only_book=[]; only_tape=[]
        for number in sorted(book_nums-tape_nums):
            es=bynum[number]
            only_book.append({'line':number,'pdf_page':es[0]['pdf_page'],'ocr':es[0]['raw']})
        for number in sorted(tape_nums-book_nums):
            only_tape.append({'line':number,'tape':tape[number][:130]})
        candidates=[]
        for num in sorted(book_nums&tape_nums):
            body=tape[num]
            sims=[(SequenceMatcher(None,norm(body),norm(e['body'])).ratio(),e) for e in bynum[num]]
            score1,entry=max(sims,key=lambda x:x[0])
            if score1<.46 and len(norm(body))>12 and len(norm(entry['body']))>10:
                candidates.append({'line':num,'similarity':round(score1,3),'pdf_page':entry['pdf_page'],'tape':body[:160], 'ocr':entry['raw'][:160]})
        rows.append(dict(program=slug,title=title,printed_page=printed,first_pdf_page=ix+1,
                title_confidence=score,status='compared',book_line_count=len(book_nums),tape_line_count=len(tape),
                book_only=only_book,tape_only=only_tape,body_candidates=candidates))
    # Frogshapes intentionally analyzed as a support program, not standalone chapter.
    frog=parse_bas(basfiles[EXTRA])
    rows.append(dict(program=EXTRA,title='Frog Shapes (support program)',printed_page=None,
                first_pdf_page=None,title_confidence=0,status='no standalone chapter in contents',
                book_line_count=None,tape_line_count=len(frog),book_only=[],tape_only=[],body_candidates=[]))
    return rows,starts,ocr


def render_report(rows,starts,pdf):
    lines=['# Over the Spectrum: book vs TZX BASIC listings','',
           'Automated first-pass audit using Tesseract on the image-only original book PDF. ',
           'The `{...}` Spectrum glyph escapes from the converter are expected; they are not treated as errors.',
           'OCR guesses can be wrong (especially `5/S`, `0/O`, `1/I`, and special characters). ',
           '**Every candidate below requires checking the scanned page before changing BASIC.**', '',
           f'Book: {Path(pdf).name}', '',
           '| Tape listing | First PDF page | Book lines OCR read | Tape lines | Book-only candidates | Tape-only candidates | Weak body matches |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['program']} | {r['first_pdf_page'] or '—'} | {r['book_line_count'] if r['book_line_count'] is not None else '—'} | {r['tape_line_count']} | {len(r['book_only'])} | {len(r['tape_only'])} | {len(r['body_candidates'])} |")
    lines+=['','## Candidates requiring visual review','']
    for r in rows:
        if not r['book_only'] and not r['tape_only'] and not r['body_candidates']:
            if r['status']!='compared':lines.append(f"- **{r['program']}**: {r['status']}.")
            continue
        lines.append(f"### {r['program']} (PDF p. {r['first_pdf_page']})")
        only_book_text = ", ".join("{} (PDF {})".format(e["line"],e["pdf_page"]) for e in r["book_only"]) or "none"
        lines.append(f"- OCR line numbers absent from tape: {only_book_text}")
        lines.append(f"- Tape line numbers not seen by OCR: {', '.join(str(e['line']) for e in r['tape_only']) or 'none'}")
        if r['body_candidates']:
            lines.append('- Lowest normalized body matches (likely OCR errors on lines with symbols):')
            for e in sorted(r['body_candidates'], key=lambda x:x['similarity'])[:6]:
                lines.append(f"  - Line {e['line']} (PDF {e['pdf_page']}): tape `{e['tape']}` vs scan OCR `{e['ocr']}`")
        lines.append('')
    return '\n'.join(lines)+'\n'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf',type=Path,required=True)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--json',type=Path,required=True)
    ap.add_argument('--dpi',type=int,default=165)
    ap.add_argument('--workers',type=int,default=6)
    args=ap.parse_args()
    rows,starts,ocr=audit(args.pdf,args.root,args.dpi,args.workers)
    args.report.write_text(render_report(rows,starts,args.pdf),encoding='utf-8')
    args.json.write_text(json.dumps({'book_pdf':str(args.pdf),'results':rows},indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Wrote {args.report} and {args.json}.')
    for row in rows:
        print(f"{row['program']:13s}: pdf {str(row['first_pdf_page']):>4s} {row['book_line_count'] or 0:>3d}/{row['tape_line_count']:>3d} lines  +{len(row['book_only'])} -{len(row['tape_only'])} low={len(row['body_candidates'])}")
if __name__=='__main__': main()
