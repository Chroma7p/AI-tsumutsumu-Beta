import MeCab
import ipadic
import re

CHASEN_ARGS = r' -F "%m\t%f[7]\t%f[6]\t%F-[0,1,2,3]\t%f[4]\t%f[5]\n"'
CHASEN_ARGS += r' -U "%m\t%m\t%m\t%F-[0,1,2,3]\t\t\n"'

YOMI_ARGS = r' -F "%pS%f[7]" ' + r' -U "%M" ' + ' --eos-format "\n" '
# Taggerクラスのインスタンスを作成
chasen = MeCab.Tagger(ipadic.MECAB_ARGS + CHASEN_ARGS)
yomi = MeCab.Tagger(ipadic.MECAB_ARGS + YOMI_ARGS)
wakati = MeCab.Tagger("-Owakati")


def scoring(inp):
    score = 0
    yomi = ""
    noun = []
    rep = ""
    s_chasen = chasen.parse(inp)
    moji = 0
    for c in s_chasen.split("\n"):
        if c == "EOS":
            break
        ll = c.split("\t")
        yomi += ll[1]
        ind = (moji, len(ll[1]))
        moji += len(ll[1])
        if ll[3][:2] == "名詞":
            noun.append((ll[1], ind))
    sc = []
    for nst, ind in noun:
        ll = len(nst)
        c = 0
        n_start = ind[0]
        for found in re.finditer(nst, yomi):
            s_start = found.start()

            if s_start != n_start:
                if s_start < n_start:
                    yy = yomi[: s_start] + "\"" + yomi[s_start: s_start + ll] + "\"" + \
                        yomi[s_start + ll: n_start] + "\"" + \
                        yomi[n_start:n_start + ll] + "\"" + yomi[n_start + ll:]
                else:
                    yy = yomi[:n_start] + "\"" + yomi[n_start: n_start + ll] + "\"" + \
                        yomi[n_start + ll:s_start] + "\"" + \
                        yomi[s_start:s_start + ll] + "\"" + yomi[s_start + ll:]
                rep += yy + "\n"
                sc.append(len(nst))

    if len(sc) == 0:
        return 0, None
    else:
        score = 1
        for i in sc:
            score *= i
    prt = ""
    for i, x in enumerate(sc):
        prt += f"{x}"
        if not i == len(sc) - 1:
            prt += "x"
    rep += f"{prt}->{score}pt"
    return score, rep
