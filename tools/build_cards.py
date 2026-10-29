"""Stage 3: flashcards. One card per important Black decision in the tree:
the board after the shown moves, 'what does Carlsen play?', and the answer with his counts.
Run from the repo root:  python tools/build_cards.py   (then build_pages.py writes nothing about cards; this writes 07-flashcards.md)"""
import os, chess, chess.svg
import common

ROOT = os.path.abspath(os.path.join(common.HERE, ".."))
COLORS = {"square light": "#DEE3E6", "square dark": "#8CA2AD", "margin": "#5B6F79"}
PER_GROUP = {"e4": 24, "d4": 24, "c4": 14, "nf3": 14}
MIN_N = 12
MAX_PLY = 15        # Black to move after at most 8 White moves

def pick_nodes(first, k):
    cand = []
    stack = [first]
    while stack:
        x = stack.pop()
        if x.ply % 2 == 1 and x.n >= MIN_N and len(x.kids) >= 1 and x.ply <= MAX_PLY:
            # a decision worth a card: at least two Black options, or one move played in a big sample
            if len(x.kids) >= 2 or x.n >= 40:
                cand.append(x)
        stack.extend(x.kids.values())
    cand.sort(key=lambda x: -x.n)
    chosen = cand[:k]
    chosen.sort(key=lambda x: (x.ply, -x.n))
    return chosen

def svg_board(path, name, outdir):
    b = chess.Board(); last = None
    for san in path:
        last = b.push_san(san)
    arrows = [chess.svg.Arrow(last.from_square, last.to_square, color="#15781B")] if last else []
    svg = chess.svg.board(board=b, size=300, arrows=arrows, colors=COLORS, orientation=chess.BLACK)
    open(os.path.join(outdir, name), "w", encoding="utf-8").write(svg)

def main():
    games, _ = common.load_games(); root = common.build_tree(games)
    outdir = os.path.join(ROOT, "static", "cards"); os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir): os.remove(os.path.join(outdir, f))
    groups = []
    # the very first decision
    total = 0
    for san, label, slug in common.FIRST_MOVES:
        node = root.kids[san]
        cards = []
        for i, x in enumerate(pick_nodes(node, PER_GROUP[slug]), 1):
            path = x.path(); name = f"{slug}-{i:02d}.svg"
            svg_board(path, name, outdir)
            kids = sorted(x.kids.values(), key=lambda k: -k.n)
            best = kids[0]
            seq = common.pgn_moves_text(path)
            q = f"{seq} — what does Carlsen play?"
            mv = common.move_label(best.ply, best.san)
            ans = f"**{mv}** · {best.n} of {x.n} games ({best.n/x.n:.0%}), he scores {best.score:.0%}"
            alts = [f"{common.move_label(k.ply, k.san)} ({k.n})" for k in kids[1:4]]
            if alts: ans += "\n\nAlso: " + ", ".join(alts)
            cards.append(f'{{{{< flashcard question="{q}" board="cards/{name}" >}}}}\n{ans}\n{{{{< /flashcard >}}}}\n')
        total += len(cards)
        groups.append(f'{{{{< flashcards title="{label}" >}}}}\n' + "\n".join(cards) + '{{< /flashcards >}}\n')
    ch = os.path.join(ROOT, "content", "en", "homepage")
    # weight: after the first-move sections (2-6), before "how"
    body = ('---\ntitle: "Flashcards"\nheader_menu_title: "Flashcards"\nnavigation_menu_title: "Flashcards"\nweight: 7\nheader_menu: true\n---\n'
            f"{total} cards to learn his choices. Each shows a position (from Black's side) and asks what Carlsen plays next. "
            "Click a card to reveal his move, how many games, and his score. Open a first move below to see its cards.\n\n"
            '{{< flashcards tools="true" >}}{{< /flashcards >}}\n\n'
            "\n".join(groups))
    open(os.path.join(ch, "07-flashcards.md"), "w", encoding="utf-8").write(body)
    print(total, "cards")

if __name__ == "__main__":
    main()
