"""Remove the superseded attribution subsection (its numbers came from an optimiser that
stalled on dead parameters) and clean the abstract."""
p = "paper/main.tex"
s = open(p, encoding="utf-8").read()
BS = chr(92)

# 1) drop the old attribution subsection and its table
start = s.find(BS + "subsection{Which shared parameter costs")
end = s.find(BS + "subsection{Ablation: removing the session context}")
if start > 0 and end > start:
    s = s[:start] + s[end:]
    print("removed superseded attribution subsection")
else:
    print("attribution subsection bounds not found:", start, end)

# 2) abstract: replace the stale 'floor is attributable' sentence
old_a = ("ladder. The floor is attributable: at the" + chr(10)
         + "highest budget, releasing the relaxation time per field setting removes it entirely"
         + chr(10)
         + "(RMSE $371\to73$~nT), whereas releasing the contrast or the stretch exponent changes nothing,"
         + chr(10)
         + "so the practical rule is to share only what is genuinely common --- the phase frame and the"
         + chr(10)
         + "contrast --- and to leave the relaxation time free once photons stop being the limit.")
new_a = ("ladder. The practical rule that follows is not"
         + chr(10)
         + "\"pool then stop sharing\" but \"pool over settings you can also constrain"
         + chr(10)
         + "individually\": an instrument's sweep often contains records that a single trace cannot"
         + chr(10)
         + "identify, and those records corrupt the very shared nuisance that pooling is meant to"
         + chr(10)
         + "estimate.")
if old_a in s:
    s = s.replace(old_a, new_a)
    print("abstract cleaned")
else:
    print("abstract pattern not found; manual check needed")
    i = s.find("The floor is attributable")
    print(repr(s[i - 40:i + 420]))

open(p, "w", encoding="utf-8").write(s)
