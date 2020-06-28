from model2 import model2
"""
<<2.データ加工>>
取得したデータを、下記のもの参考にし説明変数となる財務指標(約25個)をします。

参考
https://note.com/naosukenya/n/n2c18dcdc51a8
上記のものより「安全性・成長性・収益性・割安性」の指標20個を作成

http://skyrocket777.com/excel_financial_analysis_tool_ver002/
上記のものより「効率性・生産性・株主還元性」の指標6個を作成

加工時、Ａ・Ｂパターンに分け作成する(重回帰分析の際に目的変数を変えている)

Ａパターン・・・目的変数がリターン(インカムゲイン＋キャピタルゲイン)となっている
Ｂパターン・・・キャピタルゲインとなっている
"""

if __name__== '__main__':
    work2_a = model2.DataProcessPatternA()
    work2_a.data_proprocess_pattern_a()

    work2_b = model2.DataProcessPatternB()
    work2_b.data_proprocess_pattern_b()


