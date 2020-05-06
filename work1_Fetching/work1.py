"""
<<1.データを取得>>
バフェットコードのAPIを用いて、現存する東証の上場企業の3種類(4半期の決算データ・日別の株価指標・現在の株価指標）のデータを取得します。
以下のものが取得先です。

3年間の財務数値データ(quarter)， 3年間の株価指標(daily)，現在の株価指標(ingicator)

参考URL 
https://blog.buffett-code.com/entry/how_to_use_api
https://docs.buffett-code.com/#/default/get_api_v2_quarter
"""
import requests
import json
import pandas as pd
from datetime import *

#＜バフェットコードのapiを利用し、データを取得する為の関数＞
def fetch(ticker,bc_api_endpoint,apikey,FROM,TO):
    #httpのGETメソッド
    response = requests.get(
                            #アクセスしたurlを取得
                            url=bc_api_endpoint,
                            #urlパラメータを指定
                            params={
                                    #銘柄コードを指定
                                    "tickers":ticker,
                                    #期間を指定
                                    "from":FROM,
                                    "to":TO,
                                    },
                                    #レスポンスヘッダーを指定
                                    headers={
                                            #apikeyを指定
                                            "x-api-key":apikey,
                                            },
                            )
    return response

#＜３種類のデータを取得する為の関数＞
def make_df(TICKER:str):
    #証券コードのリストの行に入っている３つのコードを分割
    ticker = TICKER.split(",")
    #######1-1:12周期の財務数値データを取得(3年間）###################################################
    bc_api_endpoint_q = "https://api.buffett-code.com/api/v2/quarter"
    apikey_q = "YourApiKey" #【自分で調整するもの(購入してください)】 

    START_q ="2017Q1"  #【自分で調整するもの: 2020年5月3日時点の最新の値です】
    END_q ="2019Q4"    #【自分で調整するもの: 2020年5月3日時点の最新の値です】

    #apikeyを入れ、api利用を許可してもらい四半期データを取得
    res_q = fetch(TICKER,bc_api_endpoint_q,apikey_q,START_q,END_q)
    json_data_q = json.loads(res_q.text)
    #バフェットコードの仕様で一回当たり最大3社が取得可能な為対応
    df_q_0 = pd.DataFrame.from_dict(json_data_q[ticker[0]]) #quarter
    df_q_1 = pd.DataFrame.from_dict(json_data_q[ticker[1]]) #quarter
    df_q_2 = pd.DataFrame.from_dict(json_data_q[ticker[2]]) #quarter
    #リスト化をし最終的に一気にCSV化をする
    df_q_list = [df_q_0,df_q_1,df_q_2]

    #古い順にデータをソートする
    for i in range(len(df_q_list)):
        #to_datetimeに変換
        df_q_list[i]['to_datetime'] = pd.to_datetime(df_q_list[i]["edinet_updated_date"])
        #ソートしたリストを作成
        sort_data = sorted(df_q_list[i]['to_datetime'])
        #データを再作成
        concat_data = pd.DataFrame()
        for sort_num in range(len(sort_data)):
            #リストを頼りに組み直す
            datetime_data = df_q_list[i][df_q_list[i]['to_datetime'] == sort_data[sort_num]]
            concat_data = pd.concat([concat_data,datetime_data],axis = 0)
        #データを更新
        df_q_list[i] = concat_data

    #######1-2:2017年～2019年のdailyの株価指標を取得し四半期ごとに平均化###############################
            #(4月〜6月が第1四半期、7月〜 9月が第2四半期となる)  

    bc_api_endpoint_day = "https://api.buffett-code.com/api/v2/daily"
    apikey_day =  apikey_q #上記で入れたapikeyをそのまま使用


    #仕様上最大1年間までしかデータを取得できない為、1年ごとにデータを取得しforで3年間取得する形を取っている）
    start_year = 2017 #【自分で調整するもの:2020年5月3日時点の最新の値です】
    start_month = 4       #【自分で調整するもの:2020年5月3日時点の最新の値です】
    json_data_day = dict()
    for year in range(start_year,start_year+3):  
        START_day = f"{year}-0{start_month}-01" 
        END_day =  f"{year+1}-03-31" #【自分で調整するもの:2020年5月3日時点の最新の値です】
        #apikeyを入れ、api利用を許可してもらい日別の株価を取得
        res_day = fetch(TICKER,bc_api_endpoint_day,apikey_day,START_day,END_day) 
        textDict_day = json.loads(res_day.text)
    
        #dayをdatetimeに変換(後で比較するため）
        for k in textDict_day.keys():
            json_data_day.setdefault(k, list())
            json_data_day[k].extend(textDict_day[k])

    df_d_0 = pd.DataFrame.from_dict(json_data_day[ticker[0]])
    df_d_1 = pd.DataFrame.from_dict(json_data_day[ticker[1]])
    df_d_2 = pd.DataFrame.from_dict(json_data_day[ticker[2]])
    df_d_list = [df_d_0,df_d_1,df_d_2]


    df_day_list = []
    #四半期ごとに株価の平均を出すために、datetimeで4半期ごとにわけられるようラベル付けする
    for i in range(len(df_d_list)):
        df_d_list[i]['to_datetime'] = pd.to_datetime(df_d_list[i]['day'])
        
        #mergeのための、空フレームを作成
        df_merge = pd.DataFrame()

        #４半期に分解
        searchConditionMonth = start_month - 1
        searchConditionMonthIncrement = 3
        searchConditionYear = start_year

        count = 0
        while True:
            count += 1
            if 4 * 3 + 1  <= count:
                break

            # 検索条件（From）
            searchConditionDatetimeFrom = datetime(searchConditionYear, searchConditionMonth + 1, 1, tzinfo=timezone.utc)

            # 検索期間の月と年を更新する
            searchConditionMonth = (searchConditionMonth + searchConditionMonthIncrement) % 12
            if searchConditionMonth < searchConditionMonthIncrement:
                searchConditionYear += 1

            # 検索条件（To）
            searchConditionDatetimeTo = datetime(searchConditionYear, searchConditionMonth + 1, 1, tzinfo=timezone.utc)    

            df_dq = df_d_list[i][(searchConditionDatetimeFrom <= df_d_list[i]['to_datetime']) & (df_d_list[i]['to_datetime'] < searchConditionDatetimeTo)]

            #四半期ごとのデータを平均化しmergeさせる
            df_dq_mean = df_dq.mean()
            df_DQ = pd.DataFrame(df_dq_mean)
            df_merge = pd.concat([df_merge,df_DQ],axis = 1)

        df_day_list.append(df_merge.T) #day
    
    ##############1-3:現在の株価指標を取得  ################################################

    bc_api_endpoint_c = "https://api.buffett-code.com/api/v2/indicator"
    apikey_c =  apikey_q

    #apikeyを入れ、api利用を許可してもらい現在の株価を取得
    res_c = fetch(TICKER,bc_api_endpoint_c,apikey_c,None,None)
    json_data_c = json.loads(res_c.text)
    df_c_0 = pd.DataFrame.from_dict(json_data_c[ticker[0]])  #current
    df_c_1 = pd.DataFrame.from_dict(json_data_c[ticker[1]])  #current
    df_c_2 = pd.DataFrame.from_dict(json_data_c[ticker[2]])  #current
    df_c_list = [df_c_0,df_c_1,df_c_2]
    
    return df_q_list,df_day_list,df_c_list



"""
バフェットコードの使用上、APIのリクエストが500回のため実質一日300社までしか取得できないです。
    |  500 / (quarter*1 + daily*3 + ingicator*1) = 100回まで取得可能
    |  100*3(一回当たり取得できるのが最大3社) = 300社

従って約3500社を取得するため、2週間弱に渡り取得をしなければならないです。
    →リストのインデックスを記憶(セーブ)し続きから始められるようにしています。
"""


try:
    #あらかじめバフェットコードから抽出できる証券コードのリストを用意(下記のURLのcsvデータを参考）
    # https://kabusapo.com/stock-data/stock-list/
    with open("work1_Fetching/ticker.txt" ,mode = "r") as f:
        file = f.read()
    ticker_list_three = file.split("\n")
    #取得終了時にセーブポイントが上書きされる、初期化する(初めから行いたい）場合はカウントを0にする。
    with open("work1_Fetching/ticker_count.txt" , mode = "r") as f:
        count_int = int(f.read())
    count = count_int
    memory = count
    for ticker_code in ticker_list_three[count:] :
        df_q_list,df_day_list,df_c_list = make_df(ticker_code)
        for i in range(3):
            ticker_l = ticker_code.split(",")
            #上記で書いた3種類のデータ取得の関数をもとに集めたデータを、それぞれcsvへ保存
            df_q_list[i].to_csv(f"work1_Fetching/df_q/{ticker_l[i]}.csv")
            df_day_list[i].to_csv(f"work1_Fetching/df_day/{ticker_l[i]}.csv")
            df_c_list[i].to_csv(f"work1_Fetching/df_c/{ticker_l[i]}.csv")
        count += 1
except :
    #リクエスト制限が掛かり一日で取得出来るデータ数が達したらセーブポイントを作成
    with open("work1_Fetching/ticker_count.txt" , mode = "w") as f:
        f.write(str(count))
    print(f"{count}行で処理が終了しました。")
    print(f"{memory}から始まって{count}まで{count - memory}行読み込まれました。")
