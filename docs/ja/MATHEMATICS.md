# 数学的導出と実装の範囲

[English](../en/MATHEMATICS.md) · [한국어](../ko/MATHEMATICS.md) · [简体中文](../zh-CN/MATHEMATICS.md) · [日本語](../ja/MATHEMATICS.md)

[Dexted DSP](../../README.ja.md)

## 1. ランタイムが判定する命題

固定された実係数と正の上限について、

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}},\quad \gamma>0,$$

の分母が厳密に安定で、`sup |H| < gamma` であることを判定します。実係数の共役対称性により `[0,pi]` で十分です。不安定分母が形式的に約分される非最小の表現でも拒否します。

厳密に扱う値は、明示した配備変換後の有限な 2 進有理数です。理想 10 進数、未知の係数誤差区間、各サンプル処理中の全丸めを証明するものではありません。

## 2. 分母の安定性

実モニック 2 次式 `z²+a1 z+a2` の根が単位円内部に厳密に入る必要十分条件は、

$$|a_2|<1,\qquad 1+a_1+a_2>0,\qquad 1-a_1+a_2>0.$$

十分性は `z=(1+s)/(1-s)` を代入し、`(1-s)²` を掛けます。

$$(1-a_1+a_2)s^2+2(1-a_2)s+(1+a_1+a_2).$$

3 係数が正なので根は開左半平面にあり、元の根は円内です。必要性は根の積と `z=±1` の正値から従います。厳密不等号が境界極を除きます。古典的な 2 次 Schur/Jury の議論であり、OpenAI 定理ではありません。

## 3. ゲインを 2 次式の符号へ変換

実数 `x,y,z`、`c=cos(omega)` について、

$$|x+ye^{-i\omega}+ze^{-2i\omega}|^2=(x-z)^2+y^2+2y(x+z)c+4xz c^2.$$

分子・分母に適用したものを `N(c)`、`D(c)` とします。分母安定性より `D(c)>0` なので、ゲイン条件は

$$Q(c)=\gamma^2D(c)-N(c)>0\quad\text{for all }c\in[-1,1]$$

と同値です。連続性とコンパクトな区間により、この場合は点ごとの厳密正値性が上限の厳密制約と同値になります。`Q(c)=Ac²+Bc+C` とし、端点 `A-B+C>0`、`A+B+C>0` を検査します。`A>0` かつ `-2A<B<2A` の場合だけ内部頂点が必要で、条件は

$$4AC-B^2>0$$

へ還元されます。有限の 2 進浮動小数点値は整数を 2 のべきで割った値です。**正の**共通分母を掛けて符号を保持します。Python 整数と Boost `cpp_int` は桁落ちの丸め誤差なしに判定します。ただし入力ビット長に依存しない定時間ではありません。

完全な導出は [biquad.md](../math/biquad.md)、実装は `biquad.py` とネイティブヘッダー、別表現の参照は `reference.py` です。

## 4. カスケードと UNKNOWN の必要性

安定節の全体ゲイン条件は、

$$Q(c)=\gamma^2\prod_j D_j(c)-\prod_j N_j(c)>0,\quad c\in[-1,1]$$

と同値です。周波数補償を保持し、各節の最大値の積より緩い評価が可能です。同じ周波数で応答を掛けるグリッドも補償は保持しますが、依然として点の検査です。

`t=(c+1)/2` とし、Bernstein 形式で表します。

$$Q(2t-1)=\sum_{i=0}^n\beta_i {n\choose i}t^i(1-t)^{n-i}.$$

基底は非負で総和が 1 のため、すべての `beta_i>0` は区間上の正値性の十分条件です。一つの非正係数だけでは不成立の証明にならず、中点で厳密に分割します。端点の非正値なら厳密正値性の反例です。予算が尽きたら `unknown` とします。

成功証明書は 2 進有理区間の被覆です。`verify_cascade()` が有理数多項式を再構成し、元入力と上限、隙間・重複のない被覆、各区間の Bernstein 係数正値性を確認します。生成器の合格フラグだけは信用しません。資源制限付きの十分条件手続きであり、任意次数の実根完全判定器ではありません。[cascade.md](../math/cascade.md)に詳細があります。

## 5. OpenAI との条件付き接続

OpenAI 原文 [OAI-325] は行列値多項式について

$$\|P[A]\|_2\le2\sup_{z\in W(A)}\|P(z)\|_2$$

という完全型不等式を示しています。一般定理を仮定すると、独立テンソル軸の非正規軸 `r` 個には `2^r`、正規軸には 1 が得られます。共通基底を固定し、各時刻のチャネル多項式が同じ数値域上で `q<1` に抑えられていれば `||H_(T-1)...H_0|| <= 2 q^T` です。

相対状態摂動 `||e_t(x)||<=epsilon||x||` には定数変化法と帰納法から

$$\|x_T\|\le2(q+2\epsilon)^T\|x_0\|$$

が従います。既存の完全型定数 `1+sqrt(2)` [CP-2017] を 2 に置き換えることで、十分条件の摂動半径が約 20.71% 広がります。真の最大半径や一般的な音質・画質向上を証明したわけではありません。任意に基底が変わる系や任意フィードバックグラフが共通基底条件を自動的に満たすわけではありません。

一般 OpenAI 定理は外部仮定のままです。厳密 biquad/カスケードの実装とすべての公開ベンチマーク棒グラフは**この定理を使いません**。参照版と一般認証器の未実装課題は[出典](PROVENANCE.md)と[条件付き全文](../math/crouzeix.md)を参照してください。

## 6. このリポジトリでの「検証」

厳密演算は指定された有限入力モデルの符号を確認し、テスト一致は実装間の整合性を確認します。有理数検査器は期待入力に対して証明書を再確認します。これらは証明支援系による形式検証、外部セキュリティ監査、すべての実行算術の正しさ、物理的安全認証とは異なり、その完了を意味しません。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
