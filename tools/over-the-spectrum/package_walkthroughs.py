#!/usr/bin/env python3
"""Prepare current per-program OverTheSpectrum ROM walkthroughs from actual runs.

Inputs: sessions/*/session.json from walk_ots_all.py, screenshots from the
same ROM sessions, plus optional local URL map for Drive previews. The URL map
is a transient staging parameter; the canonical deliverables are each program's
walkthrough.md and walkthrough-screens.png in its authorized Drive folder.
"""
from __future__ import annotations
import argparse,json,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent

DETAIL={
'advent':('At the starting location, `take brass lamp`; check `inventory` says a brass lamp is carried; `north` enters the kitchen, where a table and bottle of rum are visible.', 'Text adventure command parser; use the printed verbs `take`, `inventory`, `north`, not an assumed LOOK verb.', 'The route and initial contents are fixed for this run; encounters in later rooms may differ where RND is used.'),
'alienblitz':('The alien fleet and player gun are visible. Hold `c` to move the gun right; hold `m` to fire; hold `x` to move left.', 'Uses the **original tape**, including its separate known tape line-number typo. No BASIC was patched during the ROM run.', 'Alien movement, enemy shots and collision outcome vary with simulation timing and RND. Captures show motion/shots, not a verified win.'),
'asteroids':('The observed initial game has already crashed and displays `SCORE=6` and `Press any key to try again`; `SPACE` restarts; hold `8` to steer right, then another `CRASH` is seen.', 'This game starts automatically; controls during play are `5` left and `8` right. This specific run used `8`.', 'Asteroid location and time to crash change on other runs. Score 6 and 7 are observed examples only.'),
'blackjack':('From `Kitty stands at $100`, bet `10`; cards are dealt; at `Do you want another card?` answer `n`; the dealer busts at 22 and the next betting prompt shows kitty `$110`.', 'The test does not explore multiple hands or request another card. The 10-unit bankroll gain is one observed outcome.', 'Cards, dealer total and win/loss depend on random draws; $110 is not guaranteed.'),
'bubble':('At `Do you want to choose your own numbers (y or n)?` press `n`; the program sorts 15 randomly generated numbers into ascending order; press `n` at `Do you want to sort again?` to exit.', 'Sorting is observed through the end state. No user-supplied 15-number path was exercised.', 'The values are random; the expected invariant is ascending order once finished.'),
'chess':('Wait until `Your move FROM` appears, enter `e2` then `e4`. The white pawn moves from E2 to E4 and the game displays `THINKING`.', 'The computer had not completed its reply within the recorded 2,400-frame wait; do not claim a completed human/computer turn.', 'The board placement after the human move is deterministic; computer timing/move is not established by this run.'),
'clock':('At the hour/minute/second prompts enter `12`, `34`, `0`; decline the alarm with `n`. The program draws an analogue clock face.', 'No alarm was set, so alarm ringing has not been tested.', 'Displayed time changes as Spectrum frames elapse; the exact hands differ by observation frame.'),
'delete':('ROM `LOAD ""` of `geometry.tzx`, then ROM `MERGE ""` of **separate** `delete.tzx`; `RUN 9973`. Enter inclusive range `100` through `110`. Program says `FINISHED` and `TYPE 100<ENTER> TO DELETE BLOCK`; type `100` plus ENTER. The subsequent ROM listing begins at line `120`.', 'This is a real two-recording working example. It changes only the emulated Spectrum RAM. The original geometry and delete TZX/BAS files remain untouched.', 'No randomness involved. Do not run delete on its own and mistake the missing target program for a defect.'),
'draughts':('At `Your move FROM`, enter `c6`; at `TO`, enter `d5`. The board updates; the computer answers `FROM H3 TO G4`; the next human move is requested.', 'The separate program contains its own machine-code move generator from the original tape.', 'The illustrated reply was observed in this run; do not assume every position or later opponent move is fixed.'),
'eliminator':('The game displays the ship, attackers and damage scenery. Hold `w` to move the player ship upward; hold `p` to fire. Screens change after each key.', 'The main BASIC loop reads `w`/`x` for vertical motion and `p` for firing. Only `w` and `p` were exercised here.', 'Enemy positions and outcomes are affected by RND and elapsed frames; no kill or game-over assertion.'),
'equation':('Enter six coefficients `1`, `1`, `-5`, `2`, `-1`, `-1` for equations X+Y−5=0 and 2X−Y−1=0. The program plots both lines and reports `SOLUTIONS X=2 Y=3`. Answer `n` to more equations to stop.', 'This exercises both input, numeric solution and the graph without patching BASIC.', 'This example is deterministic; other coefficients, including degenerate equations, were not tested.'),
'escape':('The tower and ship appear. Hold `w` to thrust upward and `d` to move horizontally right; snapshots show the changing positions.', 'The game runs continuously and uses `INKEY$`. It was not played to an escape or loss screen.', 'Trap firing and timing use RND, so exact obstacles and travel time vary.'),
'evaluate':('Enter name `HOME`, current year `2026`, inflation `3`, number of items `1`. Enter one `CAMERA`, location `OFFICE`, bought `2022`, life `5`, original cost `100`; press `SPACE` after item display, then `*` to finish. The summary reports replacement value `112`, original value `100`, difference `12`, total current/resale value `20`, and `PROGRAM ENDED`.', 'The values are examples typed by the human operator, not source data. The application finishes with a ROM STOP statement.', 'The arithmetic is deterministic for these inputs.'),
'geometry':('Answer `0` to the observed circumference question for radius 3. The machine displays `SORRY, the answer was 18.849556`. Press ENTER to request another question, observed as area of a circle with radius 17.', 'This exercises both incorrect-answer feedback and advancing to the next test question.', 'Question type and radius are selected by RND; the observed numbers will change between runs.'),
'hires':('At `Which CHARACTER to be redefined?` press `a`, then `1` for one character. In the graphical editor press `1` to set one pixel, `s` to store, `y` to confirm, `n` to skip printer and `n` to finish. The screen shows `SAVED!!`, the character bytes, and a ROM STOP.', 'This is an actual user-defined character edit in Spectrum RAM; there is no exported new TZX and no original recording is changed.', 'The selected character and editor actions are deterministic.'),
'invaders':('The alien formation and `lives ^^^` appear. Hold `c` to shift the gun right; hold `m` to fire a missile.', 'Controls in the original BASIC are `c` right, `z` left and `m` fire. Only right and fire were exercised.', 'Alien positions, projectile hits and score/lives depend on timing and RND; images are one observed run.'),
'kings':('The quiz asks who ruled in 1426 and offers three randomized names. Press `1`; it responds `NO - it was Henry 6`. Press `SPACE` for the next question, observed as year 1126.', 'Choosing option 1 was intentionally a sample answer, not a claim that it is correct in general.', 'Years and the 1–3 answer ordering change randomly; the 1426 example is one captured question.'),
'lunar':('The lunar landscape and lander are drawn. Hold `7` to counter descent and `5` for horizontal control; the lander moves in the captured frames.', 'The tape BASIC uses `7` for upward thrust and `5` for lateral control. No successful landing claimed.', 'Terrain and landing pad are randomized, so exact landing trajectory differs.'),
'mazeman':('The first-person maze view appears. Hold SPACE to step forward, hold `o` to turn left, then hold SPACE to advance. Corridor perspective changes after each action.', 'The program uses SPACE forward, `o` and `p` turns, and `r` reversal. This run exercised SPACE and `o`.', 'The maze data is stored on the tape; outcome depends on the navigation path, not an asserted exit.'),
'meteor':('Wait through `PREPARE FOR FLIGHT INTO METEOR STORM` until active play. Hold `p` to move right, `w` to move up and `0` to fire. The player `+` moves and a life is lost during play.', 'The controls `p` right, `i` left, `x` down, `w` up, and `0` action come from this actual program; only `p`,`w`,`0` were used.', 'Meteor patterns and life loss vary by RND and timing; the observed fall from 3 lives to 2 is not guaranteed.'),
'monitor':('At starting-address prompt enter decimal `16384`. The program rounds it down to `16380` and displays bytes in hex. Press CAPS SHIFT+8 (right) and CAPS SHIFT+6 (down); a second row of addresses is shown.', 'This exercises address entry and cursor navigation without overwriting any byte.', 'The hexadecimal values are those of this ROM session screen memory, not a fixed device specification.'),
'payroll':('Select `e` (new employee), enter `1` employee, name `ADA`, hourly rate `10`, overtime factor `1.5`, decline tape-save using `no`, then enter `40` regular hours and `2` overtime hours. Gross pay displays `430.00` and total wages `430.00`.', 'The example deliberately avoids saving an employee-data cassette; all data stays in emulated RAM.', 'Result is deterministic: 40×10 + 2×10×1.5 = 430.'),
'renum':('ROM `LOAD ""` of `geometry.tzx`; ROM `MERGE ""` of **separate** `renum.tzx`; `RUN 9900`. Enter start `100`, end `260`, new start `500`, increment `10`. Screen says `FINISHED`; enter `*`, then `n` to stop. `LIST 500` shows lines 500,510,…600 and the original 1000+ lines.', 'Renumbering changes the merged BASIC in emulated RAM only. The old GO TO/GOSUB target values are still visible: do not assume line-reference repair.', 'No randomness involved. Standalone renumber-menu demonstration would have no target lines; the two-tape merge is necessary.'),
'sales':('Enter history 2024–2025. Quarterly sales for 2024: 100,200,300,400; 2025: 300,400,500,600. Answer `n` to both printer prompts. Annual averages are 250.00 and 450.00, seasonal-index ratios appear, then a sales graph is plotted.', 'A single-year sample caused a graph arithmetic error because the graph range was zero; the recorded successful walkthrough uses two years with different averages. Originals remain unchanged.', 'The supplied business figures are deterministic samples; there is no randomization here.'),
}

def montage(src, dest):
    captions=[]
    obj=json.loads((src/'session.json').read_text())
    for c in obj['captures']:
        p=src/(c['name']+'.png')
        if p.exists():captions.append((c['name'], c['frame'], p))
    assert captions,src
    # Full screenshot remains readable at native captured pixel density; two columns.
    pad=20; label_height=34; col_w=max(Image.open(p).width for _,_,p in captions)+24
    item_h=max(Image.open(p).height for _,_,p in captions)+label_height+20
    rows=math.ceil(len(captions)/2)
    sheet=Image.new('RGB',(col_w*2+pad*3, rows*item_h+pad*(rows+1)), 'white')
    draw=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    except OSError:font=ImageFont.load_default()
    for k,(label,frame,p) in enumerate(captions):
        x=pad+(k%2)*(col_w+pad);y=pad+(k//2)*(item_h+pad)
        draw.text((x+5,y),f'{label} · frame {frame}',font=font,fill='black')
        with Image.open(p) as im:sheet.paste(im.convert('RGB'),(x,y+label_height))
    dest.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(dest,optimize=True)

def format_events(events):
    out=['| Frame at start/end | Action | Exact key / duration or wait |','|---:|---|---|']
    for e in events:
        if e['event'] not in ('press','wait','load','merge'):continue
        d=e['detail'].replace('|','\\|').replace('\\n','\\\\n')
        out.append(f"| {e['frame']} | {e['event']} | `{d}` |")
    return '\n'.join(out)

def document(name,link):
    dat=json.loads((ROOT/'sessions'/name/'session.json').read_text())
    summary,notes,variation=DETAIL[name]
    ts=[]
    for cap in dat['captures']:
        # Snapshot captures are literal ROM character-cell readings; '?'
        # means sprites/partial graphics, not a speculative OCR character.
        screen=cap['screen']
        readable=[line for line in screen.splitlines() if line[4:].strip() and '?' not in line and len(line)>7]
        excerpts='\n'.join(readable[:10]) or '(graphical frame; see actual screenshot)'
        ts.append(f"#### {cap['name']} — frame {cap['frame']}\n\n```text\n{excerpts}\n```")
    matches='; '.join(f"{x['name']}: {x['bytes']} bytes, exact={x['identical']}" for x in dat['loaded'])
    original=next(p for p in (ROOT/'tapes').glob('*/*.tzx') if p.stem==name)
    return f'''# {name} — human-keyboard ROM walkthrough

**Program recording:** `{original.parent.name}/{original.name}`. Original TZX and exported BASIC were not changed. **ROM load:** {matches}. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

{summary}

{notes}

## Exact frame-by-frame input

At the standard start, the Spectrum boots for 300 frames. `J` in keyword mode types LOAD, `SS+P` types a double quote, and `R` in keyword mode types RUN. `CS` means CAPS SHIFT, `SS` means SYMBOL SHIFT. All ordinary keypresses are **4 frames held, 9 frames released** unless the event explicitly says otherwise. Frames are nominal 1/50 s. A `wait` event logs the frame at the **end** of its no-key wait; keypress events log their **start** frame. `screen` captures do not press keys.

{format_events(dat['events'])}

## Actual states on screen

[Real ROM screenshot contact sheet]({link}) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

{chr(10).join(ts)}

## Expected / variable behavior

{variation}

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case {name}` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--links',type=Path);p.add_argument('--images-only',action='store_true');a=p.parse_args()
    links=json.loads(a.links.read_text()) if a.links and a.links.exists() else {}
    for name in DETAIL:
        s=ROOT/'sessions'/name
        if not (s/'session.json').exists():raise RuntimeError(f'missing real keyboard run: {name}')
        dst=ROOT/'walkthroughs'/name
        dst.mkdir(parents=True,exist_ok=True)
        montage(s,dst/'walkthrough-screens.png')
        if not a.images_only:
            if name not in links:raise RuntimeError(f'missing verified screenshot link {name}')
            (dst/'walkthrough.md').write_text(document(name,links[name]),encoding='utf-8')
    print(f'{len(DETAIL)} complete ROM sessions packaged')

if __name__=='__main__':main()
