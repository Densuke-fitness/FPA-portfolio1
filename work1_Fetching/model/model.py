import datetime 
import json
import pandas as pd
import requests


with open('work1_Fetching/model/acsess_key.txt', 'r') as f:
    file = f.readlines()

decode = list(map(lambda x: x.strip('\n'), file))

APIKEY = decode[0]
FETCHTIMEYEAR = int(decode[1])
FETCHTIMEMONTH = int(decode[2])



#＜＜＜バフェットコードAPI取得＞＞＞
class UseBaffetCodeAPI(object):
    
    def fetch(self, ticker, bc_api_endpoint, APIKEY, fetch_from, fetch_to):
        """バフェットコードのapiを利用し、データを取得する為の関数"""
        #httpのGETメソッド
        response = requests.get(
                                #アクセスしたurlを取得
                                url=bc_api_endpoint,
                                #urlパラメータを指定
                                params={
                                        #銘柄コードを指定
                                        "tickers":ticker,
                                        #期間を指定
                                        "from":fetch_from,
                                        "to":fetch_to,
                                        },
                                        #レスポンスヘッダーを指定
                                        headers={
                                                #apikeyを指定
                                                "x-api-key":APIKEY,
                                                },
                                )
        return response


#＜＜＜バフェットコードAPIをもとに3種類のデータを取得＞＞＞
class DataAcquisition(UseBaffetCodeAPI):

    def __init__(self):
        #＜＜入力した期間をもとに、取得すべきデータをもってくる＞＞
        if FETCHTIMEMONTH == 1 or  FETCHTIMEMONTH == 2 or FETCHTIMEMONTH == 3:
            #四半期の財務数値にて使用
            from_q =f"{FETCHTIMEYEAR - 4}Q4"
            to_q =f"{FETCHTIMEYEAR - 1}Q3"
            #四半期の財務数値にて使用
            from_d_year = FETCHTIMEYEAR - 3
            add_year = 0
            from_d_month = "01" 
            to_d_month = "12"

        elif FETCHTIMEMONTH == 4 or  FETCHTIMEMONTH == 5 or FETCHTIMEMONTH == 6:
            from_q =f"{FETCHTIMEYEAR - 3}Q1"
            to_q =f"{FETCHTIMEYEAR - 1}Q4"
            from_d_year = FETCHTIMEYEAR - 3
            add_year = 1
            from_d_month = "04" 
            to_d_month = "03"

        elif FETCHTIMEMONTH == 7 or  FETCHTIMEMONTH == 8 or FETCHTIMEMONTH == 9:       
            from_q =f"{FETCHTIMEYEAR - 3}Q2"
            to_q =f"{FETCHTIMEYEAR}Q1"
            from_d_year = FETCHTIMEYEAR - 3
            add_year = 1
            from_d_month = "07" 
            to_d_month = "06"

        #FETCHTIMEMONTH == 10 or  FETCHTIMEMONTH == 11  FETCHTIMEMONTH == 12:
        else:
            from_q =f"{FETCHTIMEYEAR-3}Q3"
            to_q = f"{FETCHTIMEYEAR}Q2"
            from_d_year = FETCHTIMEYEAR - 3
            add_year = 1
            from_d_month = "10"
            to_d_month = "09"

        self.from_q = from_q 
        self.to_q = to_q
        self.from_d_year = from_d_year
        self.add_year = add_year
        self.from_d_month  = from_d_month
        self.to_d_month = to_d_month


    def quarter_acquire(self, tickers_str:str):
        """直近3年間の四半期の財務数値を取得する関数 12周期の財務数値データを取得(3年間）"""
        #証券コードのリストの行に入っている３つのコードを分割
        tickers_list = tickers_str.split(",")
        #バフェットコードのURLからエンドポイントを取得
        bc_api_endpoint_q = "https://api.buffett-code.com/api/v2/quarter"

        #apikeyを入れ、api利用を許可してもらい四半期データを取得
        res_q = self.fetch(tickers_str, bc_api_endpoint_q, APIKEY, self.from_q,self.to_q)
        json_data_q = json.loads(res_q.text)
        #バフェットコードの仕様で一回当たり最大3社が取得可能な為対応
        df_q_0 = pd.DataFrame.from_dict(json_data_q[tickers_list[0]]) 
        df_q_1 = pd.DataFrame.from_dict(json_data_q[tickers_list[1]]) 
        df_q_2 = pd.DataFrame.from_dict(json_data_q[tickers_list[2]]) 
        #リスト化をし最終的に一気にCSV化をする
        df_q_list = [df_q_0, df_q_1, df_q_2]

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

        return df_q_list


    def daily_acquire(self,tickers_str:str):
        """直近3年間の日別の株価指標を取得し四半期ごとに平均化する関数"""
        #証券コードのリストの行に入っている３つのコードを分割
        tickers_list = tickers_str.split(",")
        
        bc_api_endpoint_day = "https://api.buffett-code.com/api/v2/daily" 
        #仕様上最大1年間までしかデータを取得できない為、1年ごとにデータを取得しforで3年間取得する形を取っている）
        json_data_day = dict()
        for year in range(self.from_d_year,self.from_d_year+3):  
            from_day = f"{year}-{self.from_d_month}-01" 
            to_day =  f"{year+self.add_year}-{self.to_d_month}-31" 

            #apikeyを入れ、api利用を許可してもらい日別の株価を取得
            res_day = self.fetch(tickers_str, bc_api_endpoint_day, APIKEY, from_day, to_day) 
            textDict_day = json.loads(res_day.text)
        
            #dayをdatetimeに変換(後で比較するため）
            for k in textDict_day.keys():
                json_data_day.setdefault(k, list())
                json_data_day[k].extend(textDict_day[k])

        df_d_0 = pd.DataFrame.from_dict(json_data_day[tickers_list[0]])
        df_d_1 = pd.DataFrame.from_dict(json_data_day[tickers_list[1]])
        df_d_2 = pd.DataFrame.from_dict(json_data_day[tickers_list[2]])
        df_d_list = [df_d_0,df_d_1,df_d_2]

        df_day_list = []
        #四半期ごとに株価の平均を出すために、datetimeで4半期ごとにわけられるようラベル付けする
        for i in range(len(df_d_list)):
            df_d_list[i]['to_datetime'] = pd.to_datetime(df_d_list[i]['day'])
            #mergeのための、空フレームを作成
            df_merge = pd.DataFrame()
            #４半期に分解  
            if self.from_d_month == "10":
                wrapper_month = int(self.from_d_month)
            else :
                wrapper_month = int(self.from_d_month.split('0')[1])

            searchConditionMonth = wrapper_month - 1
            searchConditionMonthIncrement = 3
            searchConditionYear = self.from_d_year

            count = 0
            while True:
                count += 1
                if 4 * 3 + 1  <= count:
                    break

                # 検索条件（From）
                searchConditionDatetimeFrom = datetime.datetime(searchConditionYear, searchConditionMonth + 1, 1, tzinfo=datetime.timezone.utc)

                # 検索期間の月と年を更新する
                searchConditionMonth = (searchConditionMonth + searchConditionMonthIncrement) % 12
                if searchConditionMonth < searchConditionMonthIncrement:
                    searchConditionYear += 1

                # 検索条件（To）
                searchConditionDatetimeTo = datetime.datetime(searchConditionYear, searchConditionMonth + 1, 1, tzinfo=datetime.timezone.utc)    

                df_dq = df_d_list[i][(searchConditionDatetimeFrom <= df_d_list[i]['to_datetime']) & (df_d_list[i]['to_datetime'] < searchConditionDatetimeTo)]

                #四半期ごとのデータを平均化しmergeさせる
                df_dq_mean = df_dq.mean()
                df_DQ = pd.DataFrame(df_dq_mean)
                df_merge = pd.concat([df_merge,df_DQ],axis = 1)

            df_day_list.append(df_merge.T) 
            
        return df_day_list

        
    def current_acquire(self, tickers_str:str):
        """現在の株価指標を取得する関数""" 
        tickers_list = tickers_str.split(",")
        
        bc_api_endpoint_c = "https://api.buffett-code.com/api/v2/indicator"
    
        #apikeyを入れ、api利用を許可してもらい現在の株価を取得
        res_c = self.fetch(tickers_str,bc_api_endpoint_c,APIKEY,None,None)
        json_data_c = json.loads(res_c.text)
        df_c_0 = pd.DataFrame.from_dict(json_data_c[tickers_list[0]])  
        df_c_1 = pd.DataFrame.from_dict(json_data_c[tickers_list[1]]) 
        df_c_2 = pd.DataFrame.from_dict(json_data_c[tickers_list[2]])  
        df_c_list = [df_c_0,df_c_1,df_c_2]
        
        return df_c_list



#＜＜＜データ取得の一連の操作を実行＞＞＞
class Working1(DataAcquisition):
    def work_one(self):   
        """デーバフェットコードの使用上、APIのリクエストが500回のため実質一日300社までしか取得できないです。
            |  500 / (quarter*1 + daily*3 + ingicator*1) = 100回まで取得可能
            |  100*3(一回当たり取得できるのが最大3社) = 300社

            従って約3500社を取得するため、2週間弱に渡り取得をしなければならないです。
            →リストのインデックスを記憶(セーブ)し続きから始められるようにしています。
        """
        try:
            print("データの取得を開始します")
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
                df_q_list =  self.quarter_acquire(ticker_code)
                df_day_list = self.daily_acquire(ticker_code)
                df_c_list =  self.current_acquire(ticker_code)

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


