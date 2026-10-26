// Q2 word search on an N x N torus (8 dirs). Submission: lookup of offline grids, else live annealer (~1.7 s).
// Offline build: g++ -O3 -DOFFLINE q2.cpp ; ./a.out <input> <N> <secs> <seed> [T A B]  (N=0: descend from easy N)
#include <bits/stdc++.h>
#ifndef OFFLINE
#pragma GCC optimize("O3,unroll-loops")
#endif
using namespace std;

static const int DR[8] = {0, 1, 1, 1, 0, -1, -1, -1}, DC[8] = {1, 0, 1, -1, -1, 0, -1, 1};
static mt19937_64 rng(12345);
static inline double rnd() { return (rng() >> 11) * (1.0 / 9007199254740992.0); }
static inline int rndi(int n) { return (int)(rnd() * n); }
typedef chrono::steady_clock Clk;
static Clk::time_point T0;
static double elapsed() { return chrono::duration<double>(Clk::now() - T0).count(); }

static vector<string> REQ, FORB;
static vector<vector<int>> words;  // reduced required words
static int W, maxL, maxf = 1;
static double TEMP = 1.0;
static int A = 4, B = 2, L2 = 0, BK = 0;  // L2: forbidden-bigram scan penalty, BK: breakout interval
static bool bad2[26][26];
static vector<int> bad2list[26];
struct Node { int nxt[26]; int term; };
static vector<Node> trie;

static void addPat(const string &p) {
    int u = 0;
    for (char ch : p) {
        int x = ch - 'A';
        if (!trie[u].nxt[x]) { trie[u].nxt[x] = trie.size(); Node z; memset(&z, 0, sizeof z); trie.push_back(z); }
        u = trie[u].nxt[x];
    }
    trie[u].term = 1;
}

struct Solver {
    int N, N2;
    vector<int> nb, pen2, wc, cellAt, cnt, cover, mx, let, Ed, confList, confPos, posOf, stepF, backF, stampArr, en, starts, cand;
    vector<vector<int>> cw;
    vector<double> wt;
    int stampId = 0, F = 0;

    void setup(int n) {
        N = n; N2 = N * N;
        cellAt.assign((size_t)8 * N2 * maxL, 0);
        for (int d = 0; d < 8; d++) for (int s = 0; s < N2; s++) for (int k = 0; k < maxL; k++) {
            int r = ((s / N + k * DR[d]) % N + N) % N, c = ((s % N + k * DC[d]) % N + N) % N;
            cellAt[((size_t)d * N2 + s) * maxL + k] = r * N + c;
        }
        stepF.assign(4 * N2, 0); backF.assign(4 * N2, 0); stampArr.assign(4 * N2, 0);
        for (int f = 0; f < 4; f++) for (int s = 0; s < N2; s++) {
            int r = s / N, c = s % N;
            stepF[f * N2 + s] = ((r + DR[f] + N) % N) * N + (c + DC[f] + N) % N;
            backF[f * N2 + s] = ((r - DR[f] + N) % N) * N + (c - DC[f] + N) % N;
        }
        nb.assign(8 * N2, 0);
        for (int s = 0; s < N2; s++) for (int d = 0; d < 8; d++)
            nb[s * 8 + d] = ((s / N + DR[d] + N) % N) * N + (s % N + DC[d] + N) % N;
        pen2.assign(N2 * 26, 0); wc.assign(N2, 1);
        cnt.assign(N2 * 26, 0); cover.assign(N2, 0); mx.assign(N2, 0); let.assign(N2, -1); Ed.assign(26 * N * 2 * N, 0);
        confList.clear(); confPos.assign(N2, -1); cw.assign(N2, {}); posOf.assign(W, -1); en.assign(8 * N2, 0);
        wt.clear();
        for (int d = 0; d < 64; d++) { double v = exp(-d / TEMP); if (v < 1e-9) break; wt.push_back(v); }
        F = 0;
    }
    inline void writeE(int c, int x) {
        int ct = cnt[c * 26 + x];
        int v = (ct < mx[c] ? A * wc[c] : 0) - (ct > 0 ? B : 0) + L2 * pen2[c * 26 + x];
        int *row = &Ed[(x * N + c / N) * 2 * N];
        row[c % N] = v; row[c % N + N] = v;
    }
    void updCell(int c) {
        int *ct = &cnt[c * 26];
        int m = 0, arg = -1;
        for (int x = 0; x < 26; x++) if (ct[x] > m) { m = ct[x]; arg = x; }
        int oldl = let[c];
        mx[c] = m; let[c] = arg;
        for (int x = 0; x < 26; x++) writeE(c, x);
        if (L2 && oldl != arg) for (int d = 0; d < 8; d++) {
            int n = nb[c * 8 + d];
            if (oldl >= 0) for (int x : bad2list[oldl]) { pen2[n * 26 + x]--; writeE(n, x); }
            if (arg >= 0) for (int x : bad2list[arg]) { pen2[n * 26 + x]++; writeE(n, x); }
        }
        bool bad = cover[c] > m;
        if (bad && confPos[c] < 0) { confPos[c] = confList.size(); confList.push_back(c); }
        else if (!bad && confPos[c] >= 0) {
            int last = confList.back(); confList.pop_back();
            if (last != c) { confList[confPos[c]] = last; confPos[last] = confPos[c]; }
            confPos[c] = -1;
        }
    }
    void addW(int w, int p) {
        posOf[w] = p;
        const int *ca = &cellAt[(size_t)p * maxL];
        for (size_t k = 0; k < words[w].size(); k++) {
            int c = ca[k];
            cnt[c * 26 + words[w][k]]++; cover[c]++; cw[c].push_back(w); updCell(c);
        }
    }
    void remW(int w) {
        int p = posOf[w];
        const int *ca = &cellAt[(size_t)p * maxL];
        for (size_t k = 0; k < words[w].size(); k++) {
            int c = ca[k];
            cnt[c * 26 + words[w][k]]--; cover[c]--;
            auto &v = cw[c]; v.erase(find(v.begin(), v.end(), w)); updCell(c);
        }
        posOf[w] = -1;
    }
    int heat(int w) {
        const vector<int> &a = words[w];
        int L = a.size(), P = 8 * N2, N2x = 2 * N;
        int *E = en.data();
        for (int d = 0; d < 8; d++) {
            int *out = E + d * N2;
            for (int k = 0; k < L; k++) {
                int rs = ((k * DR[d]) % N + N) % N, co = ((k * DC[d]) % N + N) % N;
                const int *base = &Ed[(a[k] * N) * N2x] + co;
                for (int r = 0; r < N; r++) {
                    const int *src = base + ((r + rs) % N) * N2x;
                    int *dst = out + r * N;
                    if (k == 0) for (int c = 0; c < N; c++) dst[c] = src[c];
                    else for (int c = 0; c < N; c++) dst[c] += src[c];
                }
            }
        }
        int mn = INT_MAX;
        for (int p = 0; p < P; p++) mn = min(mn, E[p]);
        double tot = 0;
        int lim = mn + (int)wt.size();
        cand.clear();
        for (int p = 0; p < P; p++) if (E[p] < lim) { cand.push_back(p); tot += wt[E[p] - mn]; }
        double r = rnd() * tot;
        for (int p : cand) { r -= wt[E[p] - mn]; if (r <= 0) return p; }
        return cand.back();
    }
    inline int countAt(int f, int s) {
        int u = 0, c = s, tot = 0;
        for (int k = 0; k < maxf; k++) {
            int x = let[c];
            if (x < 0) break;
            u = trie[u].nxt[x];
            if (!u) break;
            tot += trie[u].term;
            c = stepF[f * N2 + c];
        }
        return tot;
    }
    void collect(int w, int p) {
        const int *ca = &cellAt[(size_t)p * maxL];
        for (size_t k = 0; k < words[w].size(); k++) {
            for (int f = 0; f < 4; f++) {
                int c = ca[k];
                for (int j = 0; j < maxf; j++) {
                    int id = f * N2 + c;
                    if (stampArr[id] != stampId) { stampArr[id] = stampId; starts.push_back(id); }
                    c = backF[f * N2 + c];
                }
            }
        }
    }
    int countStarts() { int t = 0; for (int id : starts) t += countAt(id / N2, id % N2); return t; }
    int fullForb(vector<int> *cellsOut) {
        int t = 0;
        for (int f = 0; f < 4; f++) for (int s = 0; s < N2; s++) {
            int k = countAt(f, s);
            if (k) { t += k; if (cellsOut) { cellsOut->push_back(s); cellsOut->push_back(stepF[f * N2 + s]); } }
        }
        return t;
    }
    void initGreedy() {
        vector<int> order(W);
        iota(order.begin(), order.end(), 0);
        stable_sort(order.begin(), order.end(), [](int a, int b) { return words[a].size() > words[b].size(); });
        for (int w : order) addW(w, heat(w));
        F = fullForb(nullptr);
    }
    void initFrom(const vector<int> &pos) { for (int w = 0; w < W; w++) addW(w, pos[w]); F = fullForb(nullptr); }
    vector<int> remap(int n2) const {
        vector<int> out(W);
        for (int w = 0; w < W; w++) {
            int d = posOf[w] / N2, s = posOf[w] % N2, r = s / N % n2, c = s % N % n2;
            out[w] = d * n2 * n2 + r * n2 + c;
        }
        return out;
    }
    // anneal until conflicts and forbidden hits are both zero, or time limit (seconds since T0)
    bool anneal(double tlim, long *itOut = nullptr) {
        long it = 0;
        double lam = A;
        bool ok = false;
        while (true) {
            int conf = confList.size();
            if (conf == 0 && F == 0) { ok = true; break; }
            if ((it & 63) == 0 && elapsed() > tlim) break;
            it++;
            if (BK && it % BK == 0) for (int c : confList) { wc[c]++; for (int x = 0; x < 26; x++) writeE(c, x); }
            int w;
            if (rnd() < 0.02) w = rndi(W);
            else if (conf > 0 && (F == 0 || rnd() < 0.8)) { int c = confList[rndi(conf)]; w = cw[c][rndi(cw[c].size())]; }
            else {
                vector<int> cells; fullForb(&cells);
                if (cells.empty()) { F = 0; continue; }
                int c = cells[rndi(cells.size())];
                if (cw[c].empty()) continue;
                w = cw[c][rndi(cw[c].size())];
            }
            int old = posOf[w];
            remW(w);
            int np = heat(w);
            if (np == old) { addW(w, old); continue; }
            stampId++; starts.clear();
            collect(w, old); collect(w, np);
            addW(w, old);
            int before = countStarts();
            remW(w); addW(w, np);
            int dF = countStarts() - before;
            if (dF > 0 && rnd() >= exp(-lam * dF / TEMP)) { remW(w); addW(w, old); }
            else F += dF;
        }
        if (itOut) *itOut = it;
        return ok;
    }
    // fill free cells; safe letter if one exists, else greedy per-cell; returns empty on failure
    vector<string> emit() {
        vector<int> g = let;
        set<char> used;
        for (auto &f : FORB) for (char ch : f) used.insert(ch);
        int safe = -1;
        for (int x = 25; x >= 0; x--) if (!used.count('A' + x)) { safe = x; break; }
        vector<int> freeCells;
        for (int c = 0; c < N2; c++) if (g[c] < 0) freeCells.push_back(c);
        if (safe >= 0) for (int c : freeCells) g[c] = safe;
        else {
            vector<int> fr(26, 0);
            for (auto &f : FORB) for (char ch : f) fr[ch - 'A']++;
            vector<int> ord(26);
            iota(ord.begin(), ord.end(), 0);
            sort(ord.begin(), ord.end(), [&](int a, int b) { return fr[a] < fr[b]; });
            vector<int> saved = let;
            let = g;
            for (int c : freeCells) {
                bool done = false;
                for (int x : ord) {
                    let[c] = x;
                    int bad = 0;
                    for (int f = 0; f < 4 && !bad; f++) {
                        int s = c;
                        for (int j = 0; j < maxf && !bad; j++) { bad += countAt(f, s); s = backF[f * N2 + s]; }
                    }
                    if (!bad) { done = true; break; }
                }
                if (!done) { let = saved; return {}; }
            }
            g = let; let = saved;
        }
        vector<string> rows(N, string(N, 'A'));
        for (int c = 0; c < N2; c++) rows[c / N][c % N] = 'A' + g[c];
        return rows;
    }
};

static bool occurs(const vector<string> &g, const string &w) {
    int N = g.size(), L = w.size();
    for (int r = 0; r < N; r++) for (int c = 0; c < N; c++) {
        if (g[r][c] != w[0]) continue;
        for (int d = 0; d < 8; d++) {
            int k = 1;
            while (k < L && g[((r + k * DR[d]) % N + N) % N][((c + k * DC[d]) % N + N) % N] == w[k]) k++;
            if (k == L) return true;
        }
    }
    return false;
}
static bool valid(const vector<string> &g) {
    int N = g.size();
    if (!N) return false;
    for (auto &r : g) { if ((int)r.size() != N) return false; for (char ch : r) if (ch < 'A' || ch > 'Z') return false; }
    for (auto &w : REQ) if ((int)w.size() > N || !occurs(g, w)) return false;
    for (auto &f : FORB) if (occurs(g, f)) return false;
    return true;
}

static void prepare() {
    vector<string> u = REQ;
    sort(u.begin(), u.end()); u.erase(unique(u.begin(), u.end()), u.end());
    sort(u.begin(), u.end(), [](const string &a, const string &b) { return a.size() != b.size() ? a.size() > b.size() : a < b; });
    vector<string> keep;
    for (auto &w : u) {
        string rw(w.rbegin(), w.rend());
        bool in2 = false;
        for (auto &k : keep) if (k.find(w) != string::npos || k.find(rw) != string::npos) { in2 = true; break; }
        if (!in2) keep.push_back(w);
    }
    W = keep.size(); maxL = 0; words.clear();
    for (auto &w : keep) { vector<int> v; for (char ch : w) v.push_back(ch - 'A'); words.push_back(v); maxL = max(maxL, (int)w.size()); }
    trie.assign(1, Node()); memset(&trie[0], 0, sizeof(Node));
    for (auto &f : FORB) { addPat(f); addPat(string(f.rbegin(), f.rend())); maxf = max(maxf, (int)f.size()); }
    for (auto &f : FORB) if (f.size() == 2) { int a = f[0] - 'A', b = f[1] - 'A'; bad2[a][b] = bad2[b][a] = true; }
    for (int a = 0; a < 26; a++) { bad2list[a].clear(); for (int b = 0; b < 26; b++) if (bad2[a][b]) bad2list[a].push_back(b); }
}

// descend from an easy N until tlim; returns best valid grid (empty if none)
static vector<string> descend(double tlim, int startN = 0) {
    int S = 0;
    for (auto &w : REQ) S += w.size();
    int N = startN ? startN : max(maxL, (int)ceil(sqrt(S / 1.0)));
    Solver sv;
    vector<string> best;
    while (best.empty() && elapsed() < tlim) {
        sv.setup(N);
        sv.initGreedy();
        if (sv.anneal(min(tlim, elapsed() + 0.25 * tlim))) {
            vector<string> g = sv.emit();
            if (!g.empty() && valid(g)) { best = g; break; }
        }
        N += max(1, N / 12);
    }
    while (!best.empty() && N - 1 >= maxL && elapsed() < tlim) {
        vector<int> pos = sv.remap(N - 1);
        sv.setup(N - 1);
        sv.initFrom(pos);
        if (!sv.anneal(tlim)) break;
        vector<string> g = sv.emit();
        if (g.empty() || !valid(g)) break;
        best = g; N--;
    }
    return best;
}

static vector<string> fallbackRows() {
    if (REQ.empty()) {
        for (char ch = 'A'; ch <= 'Z'; ++ch) {
            vector<string> g(1, string(1, ch));
            if (valid(g)) return g;
        }
        return {};
    }
    bool used[26] = {};
    for (const auto &f : FORB) for (char ch : f) used[ch - 'A'] = true;
    int filler = 0;
    while (filler < 26 && used[filler]) ++filler;
    if (filler == 26) return {};  // This construction requires a safe separator.
    int letters = 0;
    for (const auto &w : words) letters += int(w.size()) + 1;
    int N = max(maxL + 1, (int)ceil(sqrt(2.0 * letters)));
    vector<int> rowOf(W), colOf(W);
    for (;; ++N) {
        vector<int> used(N / 2, 0);
        bool fit = true;
        for (int w = 0; w < W; ++w) {
            int r = 0, len = int(words[w].size()) + 1;
            while (r < (int)used.size() && used[r] + len > N) ++r;
            if (r == (int)used.size()) { fit = false; break; }
            rowOf[w] = 2 * r; colOf[w] = used[r]; used[r] += len;
        }
        if (fit) break;
    }
    vector<string> g(N, string(N, 'A' + filler));
    for (int i = 0; i < W; ++i)
        for (int k = 0; k < (int)words[i].size(); ++k)
            g[rowOf[i]][colOf[i] + k] = 'A' + words[i][k];
    // Every nonhorizontal multi-cell path crosses a safe row; horizontal
    // wraparound crosses safe padding. Internal forbidden words are unsatisfiable.
    return valid(g) ? g : vector<string>{};
}

#ifdef OFFLINE
int main(int argc, char **argv) {
    T0 = Clk::now();
    ifstream in(argv[1]);
    int N = atoi(argv[2]);
    double secs = atof(argv[3]);
    rng.seed(atoll(argv[4]));
    if (argc > 5) TEMP = atof(argv[5]);
    if (argc > 6) A = atoi(argv[6]);
    if (argc > 7) B = atoi(argv[7]);
    if (argc > 8) L2 = atoi(argv[8]);
    if (argc > 9) BK = atoi(argv[9]);
    int n, m;
    in >> n; REQ.resize(n); for (auto &s : REQ) in >> s;
    in >> m; FORB.resize(m); for (auto &s : FORB) in >> s;
    prepare();
    vector<string> g;
    if (N == 0) g = descend(secs);
    else if (N < 0) g = descend(secs, -N);  // warm-start descent from -N
    else if (N >= maxL) {
        Solver sv; sv.setup(N); sv.initGreedy();
        long it = 0;
        bool ok = sv.anneal(secs, &it);
        fprintf(stderr, "N=%d %s it=%ld t=%.1f conf=%d F=%d\n", N, ok ? "OK" : "FAIL", it, elapsed(), (int)sv.confList.size(), sv.F);
        if (ok) { g = sv.emit(); if (!g.empty() && !valid(g)) { fprintf(stderr, "INVALID\n"); g.clear(); } }
    }
    for (auto &r : g) puts(r.c_str());
    return g.empty();
}
#else
// BEGIN LOOKUP
static const char *LOOKUP[][2] = {
{"81ccabeb97978607", "CNMAMCRMWAFBCIHHWAHNMAGHAWIEABAALHUMRWCHHGCWAWYCWRTBWLLNETLIIWRTGSYWCWIMFAAWIWPSNLHWCOANNNWFWBOKGRKVMEOIOAANDEIOIADLROCDKREWOTPOBWMERTEIPIDARALIARLCNAINEUPTORLLPABGLANWPAIBUGCQLISOFFBWMWABWGHOMLAWMHCNYTTOXWRALTKMSTOBMRWHEGACRREWOWHMEAECULEINOTGNIDDAPARKKWHWDROFTPEDIWVTHILMWDICNYAIOSEHDSOMBNROBLOHWPEHEEMSUTUTUOSVAUXHALLWUPSMSSSHLRLOLRWEYIKEDYHTRWBOTDWAEEHRECSLSWIWWTNGUAONINAMGEEMHLWLWWLOWERANACDLOBNMTMAEKIWATBTYEKKHWINHMAIAARHCNBRTTUYEWMWNOOOWRLWHICIGEOAEERNREGENTSDSEHPNWWTNBRNRNWWNSLOXSSESBAGWSOWEKOSWIWTRPTITMNLULMNINMCDIUY"},
{"5f8d42e7a85e98fa", "ELLAUEATAACOFPCLSTIRUNTMRTUTGAMMAIYENVGXYEUIUNCEVIUNVVFANOBSRRTTAANEQEDIMNTIQSSMOAFFIDAVITCULUAUAUPFSYBNATRAELONSMQTTSUMIXAMSYCINIMODUINYGLADIUSGOCORDLCMREXADCOTIRMHPXYISURAVEIERRNEEDDOVYVSPSCIENTIAQIPSAPIALIUQASTSVCUDPMYDUEASLMVLUPUSUEEAIROLGSUEDVRMAQSPRGSIYAUTRMFIIMILMRSNFRNPASLEGIOLRRPAEAEOORUSSNVRDOLYMCMYVMRSATETCETERA"},
{"cbd6b47dc0fdcf15", "RTXEUEOMOXTXXHUCXBTAUEGXURSAMAJORKAXPUSUSLPSBEYLIASHTRAERLTNESPILCETERURDLGAUAEUCVTXUIIHDCIRTASPSADTEYXGRTREXTRASARNDAENATGAASBAOUIUUAAELBSGRRHNNLLNYRSQSRMEXEAUXIIYUOAHAUMEAOCIRBVMTAGMSSCXWSZBRNBANEOBNEREIDKLYEEDEXTOPONRIXLDLXHYKDNXXNYXHHRICOMETEORLAINACIPSPEEBANXSRLAIITXONIUQEPLIOPXCCEXMEHRCOOVENUSIOPEIAOTULPXHIMICASSMRNXLXLPIPOLARISLDRDKEEXNLELEPXXREMAKEMAIORETSARIEUROPAXPNHDRNPCUSSASSXJNYSIOEXI"},
{"e999c988aec4b78e", "DEETIROULFMARBLERBELODTXJEDGAEGROGXAONBCLIIFAHIRTKXNMXULOBXROMCESCAASAYEEQITEOEAMELLPXMVYURTRRSPBXCTINADEOOERQAITDESLXXETTCSRCNLCHUTNOISOREREXCPLIDLNTTAXDSGEODENGHAASIGPRSPIXMTSSIEJIYRLSRUIAEAGCISSARUCLOVSAMFXENVLTCFXONAAMMONITETIHPARGAELTNOCFICRESYEGMCCMUDNURXITECTONICENIVILOBAULECHALKEEHRMENOTSEMIDMAGNETITECUROCLATLERIANELAGIIESSXUGCAMBEDLUOBAMMXRPHTNSILTRTLASABXVGNOYNACIMPZTESTRATUMAACGPFLINTIX"},
{"3e5e0e28ee4326d5", "SSOFCISSAIRTUXUOSIGOAHLIARUASAIAMBERYSJRNRINPEUAACEOUSSUHCYNONIEDAVMCRETARIVOVCOELOPHYSISPEVROTPVHREHTAEFYVEXTINCTIONPTVBTROODONROHCVBONEOVADOETYCCAPVWALCEOAKBOVRLIRDCRSRAHPLBVAERRNERVTBLSMEAIGTAMATAVMNRYKNOVEOPORCSCVAENASOTBTETYTNRPINAHUAEFSLGNRMRERRHLRTHNTTIMCRRVRTLOOAOOOAOOOOOOOOIVOCAPOIYISSSSSSSSSSSSSMVVMHTRTVLRMAAAAAAAAAAAONHVPAOOPIHLAIUUUUUUUUUHOGYYSEPTAMVAUCMRRRRRRRCDVGPGOOSORNVADKOUUUUUUUOIVESOGPECOIVVLRSSSSSSSSSPVNILNTLERMVVVLOVAVVVACHLOOLOAEARCVAPATOSAURUSIEOVDOTTRCAIVSALTASAURUSSRDEOPNHYSTMVCARNOTAURUSSBOLNHOUXVOVINRACVVSURVSAICOAOESERPVMEGALOSAURUSRVUCUDLTVL"},
{"9f24483f4af52444", "ZSLAFGHANLDALMATIANVVIAVDETUMALAMPVNBEKFVVBUAUHIHCVURIPBEVVVAFBAUHCREDROBVEPRSEEVVNEILLOCHOWCHOWSSELRAHCGNIKOVUVIERVVCEDHIVEGSUPAKBODDYKSUHEGNCTRVKLVIVMUREHNVVNAINAREMOPCENVBRLATOUAVVKILUPKVTNOSVEAEBSNUOVVRKDLPEITTOCSVNSSOZINHEOENVILDGVWHRVCADEDVODFYPUVHPNNBVECHVVRTTPAPILLONWIVUUXRIIVJAVALIERVOFVLELDOOPOLBCNCEEVVVVVWDVLVBDPHVDEVRVKBRIARDEDDRVNEFVXNAREEDREGREBNOELORFDNUOHRBZVIUSOEUGIYMKIGROCHFVTATPHSVHTRVOETJEVVVSRVSSLIPLSVRTKMSDNUOHYERGESHAPHEEGVEAVAEMALTESEHTAVCSTILOMSRVSVTRVKVW"},
{"44e19f5b8213ff4a", "CHROMIUMUINELESNNNXYTXXHLNIUMUIPORUEIGAXDLXROXNITMUINARUXUSMSRAXHCELETMUIROHTXMTXTOBNHHELMHRXNHATXMKEARGOLTHLOTEIOPITBUXRNXOECUEULUVSRSGXTIXLYZSNNOBRYMLOOOCXERALXPICTRRIBSIDBHNXUUNXLXTNAIXRDISIDPMBXCRREPPOCNUOUBUUNLRAENEGYXOPNEDMMEYMXXOUGRXCDXTOTOEIMNRHTOIGBNYSACALHDXNUUXZIETSNIELEESOUYYEIMUINVRNRMDSLRSNLMCNBRADONTACIIIIIIIIIAOONOENXXCINOUUUUUUUDCIMGUSLEKOITANMMMMMMINGIELENIDACRADIUMUILLAHTRFNOBRLUMINIUMUICLACNMTANTAALLADIUMSULFURAAUGEHP"},
{"3d56db8eb0530187", "DGMKYEIELFCJRGTJSPDSGAGPCEECALLAWEZSOHAVOORSENLLCNEEVDMNOUNURNBANRALSVNBMEAIINLCLMOEFNELALAIOINRELPEKIRBGAVNPHRELNNDWHKCIRCNNOLHVIIWDWKGIINNNAMEIRLIDTSNIAVXLSNEAVESKLWEPSTYRGNTOAHGPRGIWHAADAOTAPOGVTNMOPFEAITVZATHCESVENIKGDOHHLSIOTTRVCMRLMEITNERKBNTVINLVEOPASTEURELUEETVCSEOVHHCVSBOHRUVRGILUEIRVTYEVNAMNYEFTYVVRYVEOVMHVILAPLACEUHTIVUORLOHTEONAMARCHIMEDESOBREDUFREGNIDORHCSRAVAFLLCNBESSUAGOODALLFBBOEIYHEBRCHSANVVAAWBOTVDLAIAMLMHUXLEYMLALPREIA"},
{"fe221a2e7ce1cb07", "RMLEYRIVERADTRCVMOSGORRXLDONATELLOGRCAOHUUCOLLOPXXPSIXSAOMBGKEKOTTICELLIXCXIUIIRMGABXHNMRELTSIHWRGXCEEOIPOKEEFFEXSXTBOUXHLXMOOXOGZEUQZALEVMIXEBXXBREXRNOCABRTNNVNBLAKERRAVANEYCKRYSKNABATXIELKNSHTRAGOHTXXANNSOYGMARDLOHRAWPEXMHZGNNRSUXTUTMODIGLIANIOEOEXSCHXIBSCDAVINCIYRLCGAXSIIHSEKITTASSACDOBMHXIRXETSNREIDEGASHXAEXXASTPLSESRTSTUBBSAXUILLTRWBEYDXIUKAHLOOGQENLXXOMUNCHAXRCXRDRDALIIMRRDOYKSNIDNAKEXHRLRMOETMILKMANETERLPIBGLHVBHTENOMXGSEURATPAXCU"},
{"edf6ccb87dba7be3", "RCRIESPADEVJWSCAXCNGHVCLSSEGROFHHNXVNCHEASWPNNXTHMXVWIXCLDTREPAPDNASAIPCRTDEEENILBMULPXLXESEHNUVLIPSQUAREDLORCCXRIEBSMICROMETETHYESRVXRHACKSAWRXMNUTSDEUXAOLKCOTTABLXXHWLEWODECLATHEGYTXTEKCARBABTELMIEXRWRREGNIHLWDRILLYXOPICKAXESWOLLEBLSRWVCSXRFRABWORCLTKREKAAEIESXCEFTUTHETLNSDLGGHOKGFPUEBKUDRNEUILMSCDAPAEMAEEISAJRPEXAECRNMX"},
{"b4cc17fc70332fe7", "LPKIXBXPTLNBUXPXKARRINERTEAXUORGRATEWBXRCOLSNSSIREBSTECEPANLAIIRTLYPVSAULIRGILDLRSARXVAANLXASBMILEAEFTYBAEEGXTAGINEMMLMXRRVRULCTPXSGLAEASISOEJGATEAIXPTRKCPTTIMCNZPREMMISAISOTDLOFIEMVLRXNECNCOLANDERPEELERSPCKSNXPKDXEPNEADOOAPIHWONRORMKUETUASORXDHISMEXAFXXFCSTWOKCFGEAXTETSFHETHENNEILUJEHTXLURHIFLAMBEHXOCSSALOCSKILLETTOCSDSIE"},
{"faaa12213474224e", "DWHZMGILGAMESHTSTSTWWWAPNUMAQSRMFRIGGEIIMVULCANWUSPEKDDNMWPRIIKOLEFREYATAOOOXUUWNSWWSNEPTUNEKARKCWJHEHOHABHYZBDRNPHAENSYRNATROGPAAOWIOPVNOWKVUHENGESLCREDLABTGWUAECEDGUUCCAWOLEAAAADNEFRANSEOHWJHOWIURIRUWASESWHAUWAASGARDEABSUVDMEPTSLSPIRGSYWMISACSIPRLLUONRITIHKRSHORUSOOATLNAEFEMWOLADCOEHRNSCATTNFTEHWEYVWNSTUEYEHIISISTXLASUSUROACWSIITCNARCISSUESEHTMIWUDLSABAWSNESDUPTOMARSSOLERHERMWOAEWONUJWWDPNEHUYEH"},
{"2307e913486f5f6b", "TXBLOODBROTHERSLIEXBXSMOXDEKCIWWXXLERNCRXIAFXSLRIGMAERDSLEHITVSESOOLTOOFRSEMAYIGXEEMYMMOTNAHPETIDTCAOMRMXMARYPOPPINSYOADLITAMOHLIONKINGTIDGORTIMBXHANAVENUEQXDOOHGAISATSXDULXXFROZENEAWAPXCGHTSEFMEMPHISARKINKYBOODSASPAMALOTYNAPMOCFHWUSNOTLIMAHOXXNIDDALABSXPSYOBYESREJNICMJTIOSHREKXWRXXYXXNIEAOORAREVILOSNAZRATIXPLTASTCIUJELTEEBXOXMSEPCSPEPXGYPSYBXETAKEMSSIKRXOHALKOXSIHFXXAXXNXPAMXNCINDERELLACNSSEHCYSXXCSEISWENLRIGYNNUFWXXAHELLODOLLYNINESAERG"},
{"d6ddd156a1eddf1e", "AINEMRACBTGIATPRATAQNEZILARGENTINAAAIPYLGLWEDZLATLAMZAAALZNAIRABUCCELANDAOZIZEMKZAUNAEUIZAWNMKNNRNUUUIRODBEGZLGPZSEOATDZIRAQBAMRBSNWEAINOTSEEGTGZMIIMROOZUHNRRSUHNLPZRELZBANPJTRGAEIAZEEYZZXOREZMOERUSWMKAAVBGRAUGZDICLAODNAAAZICUERBLNZZLAANPZZPAPZNNZIKOOOAISINUTADOICDAGASCARMCLNHDAZCZRNMABKJUDPZMAEIIDCHZOEAFANECRHCNAZAICXVSGGLMZYLLIPHTIAAIZJNEEIGEORGIANYAAIZNNWNZZEEMARMZZTYUGAHLLSDARPZTZROMBZVASCUUWTEESODCHHSCGAIIZLIWIZRRDZVENARICADNAGUYASFTBUOAAINEVOLSDYEKRUTSRIZZZNHMEESPAIDNALERII"},
{"d63ef244ad80ee61", "OOETVTLFIEODEACOCKATHRTVVUILLWDRVVHTOKYRTAILGNCGLRNIKSISRWAGVRPNCWACAMOBUZZARDVSITIHVENLPACKCALBLUETDWPDGOLDFINCHOUGHKCUPVLRGAJACKDAWRENVSVUCUOTMEVVGNILRATSICNAQUVHMARTINCBMVTBOLLVSYERPSOVEUIAKNIOISRUHPRUEVGHRSGTAWTNASAEMLNSKPRLEPORHVANCIDVGIWHNOEGIPOOVGDHLNOEFAVVOWBERMVSGPINSVVVLRNMTVEVREHSIFGNIKEFLFINCHNOACKPFVIEYBULIDERECCEHCECTPBTBPOEBLERUTLUVRHEEAVIBWARNWORRAPSWANTRPTKOVKRRNVLEHELFNRNGTDRHPJO"},
{"56b24765b0ad7ce3", "RTNVIQQNLLTOHMANGOOEUBEVRCPIPHTIQABKNAJASHEEAMQTAMARACKAAMQUATDELWTAMARINDKURPQSBLOADSECKHLPHQBDILEZAHGPEARCBOXWOOGNFQYQNEWJMQOPNGOWLLERUCRNYQOPALMGRAQILYTOCIRPAQOAMEANENQDLRIHCEEBNRDELMCKDYNKOAQTCQHCAAHZSGYEWOCEWDHKSHCSQQZOPWSPMONTEEUCALYPTUSQRLELCDSAMCCAYAPAPPLEUAAOTUADIBELDERYNOBECENECTARINEBCCEQQBGHUUIODEODARQADKSNANQYTTLPWALNUTNBNRSYATRABIRCHEIAIQROOQDRR"},
{"3438f71cfbabb244", "QOCONIKUNLVJRMDRLREIMUCIWONSGOEFRESFACPJNCABCJPASHMOLNUDTBYSORCLRLRLLRTUHAILWHJCIETILLETASGJJCSOJHARSTMZRESWTEZAHILCJJIWSENZTRSSJRJFORECASTTEMJASMURDLODHRCLIMATROSRJDRSCLOUDUUUIJJRPRUDTRETNIWJGHMSRGGYEGNTHONOOHPYTHUIJEHJDYSEUNRJSCJFNJLODPWTNHHLNIMBUSNHOFUNEIEOHIIADNMUTUAMSGSZJMTKESNGELCJARHOARFROSTYZLEGREHBREEZEELMDRIZNDVANEIJTMATSTRADEWIROBIDONWSMTJEEGTRADAOODANROTUUWZHMNNSTFLSIGJNBOSGSATJOOOITSS"},
{"9eff1355eef99cac", "BMSCEEUEDRMMSTNDRURPEBLFYRNEDEIEEPPEGEFHRURXDMSRERHESRBOTOOITRAVAHTEHCWXOLRSGNRLXGJTLYEOCABVOGEESOTLDEUUERRAXROCOCHMBTRYDRXILTSEULHNUCOOULEGENAXHIJNOOZONKCURICOTTABALONNOLAEWBLRTNCRRCGGSENLGMDYHEDASPOKFONTINAETLMDECTTMFMUOGJETOSETANGYRAAUDTENNERLPRMENHLXULALEERDAMMEIARLCAAEMERVEHCUXXWECCACALTPBGDEGAAEGYBNESPASLNOLGRIRCMLRELSSAARHOEIYIIROAELIBOLTMNAIUMSHONBQEM"}};
// END LOOKUP
static unsigned long long keyOf() {
    vector<string> a = REQ, b = FORB;
    sort(a.begin(), a.end()); sort(b.begin(), b.end());
    unsigned long long h = 1469598103934665603ULL;
    auto mix = [&](const string &s) { for (char ch : s) { h ^= (unsigned char)ch; h *= 1099511628211ULL; } h ^= '|'; h *= 1099511628211ULL; };
    for (auto &s : a) mix(s);
    h ^= '#'; h *= 1099511628211ULL;
    for (auto &s : b) mix(s);
    return h;
}
int main() {
    T0 = Clk::now();
    int n, m = 0;
    if (!(cin >> n)) return 0;
    REQ.resize(n);
    for (auto &s : REQ) cin >> s;
    if (!(cin >> m)) m = 0;
    FORB.resize(m);
    for (auto &s : FORB) cin >> s;
    for (auto *v : {&REQ, &FORB}) for (auto &s : *v) { string t; for (char ch : s) if (isalpha((unsigned char)ch)) t += toupper(ch); s = t; }
    REQ.erase(remove(REQ.begin(), REQ.end(), string()), REQ.end());
    FORB.erase(remove(FORB.begin(), FORB.end(), string()), FORB.end());
    vector<string> g;
    if (!REQ.empty()) {
        prepare();
        char key[32];
        snprintf(key, sizeof key, "%016llx", keyOf());
        for (auto &e : LOOKUP) if (!strcmp(e[0], key)) {
            string s = e[1];
            int N = (int)llround(sqrt((double)s.size()));
            for (int r = 0; r < N; r++) g.push_back(s.substr(r * N, N));
            if (!valid(g)) g.clear();
        }
        if (g.empty()) {
            vector<string> backup = fallbackRows();
            g = descend(1.7);
            if (g.empty()) g = move(backup);
        }
    } else g = fallbackRows();
    const char *op = getenv("OUTPUT_PATH");
    FILE *out = op ? fopen(op, "w") : stdout;
    for (auto &r : g) {
        for (int i = 0; i < (int)r.size(); i++) { if (i) fputc(' ', out); fputc(r[i], out); }
        fputc('\n', out);
    }
    if (op) fclose(out);
    return 0;
}
#endif
