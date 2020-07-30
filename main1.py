from work1_Fetching.model import model

"""
<<1.データを取得>>
バフェットコードのAPIを用いて、現存する東証の上場企業の3種類(4半期の決算データ・日別の株価指標・現在の株価指標）のデータを取得します。
以下のものが取得先です。

3年間の財務数値データ(quarter)， 3年間の株価指標(daily)，現在の株価指標(ingicator)

参考URL 
https://blog.buffett-code.com/entry/how_to_use_api
https://docs.buffett-code.com/#/default/get_api_v2_quarter
"""


#ご自身のバフェットコードAPIkEYを記入してください
APIKEY = "YourApiKey"
#取得年を記入してください（データの取得を一回以上している場合は、カウントをリセットしない限り変えないでください。）
FETCHTIMEYEAR = 2020
#取得月を記入してください（データの取得を一回以上している場合は、カウントをリセットしない限り変えないでください。）
FETCHTIMEMONTH = 7

if __name__== '__main__':
    with open('work1_Fetching/model/acsess_key.txt','w') as f:
        file = f.write(f"{APIKEY}\n{FETCHTIMEYEAR}\n{FETCHTIMEMONTH}")
    
    work1 = model.Working1()
    work1.work_one()


