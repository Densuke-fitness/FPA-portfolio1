import numpy 
from numpy import nan 
import copy
import sklearn 
from sklearn import linear_model 
import statsmodels.api as smf
import pyautogui as pg 
import pandas as pd
from IPython.display import clear_output
import time 

stock = pd.read_csv("work3_Analytics/stocklist.csv")

"""
参考
https://availability89.com/financial-indicators/
上記のものより「安全性・成長性・収益性・割安性」の指標20個

http://skyrocket777.com/excel_financial_analysis_tool_ver002/
上記のものより「効率性・生産性・株主還元性」の指標6個を作成

"""

#＜＜＜２つの分析の共通項＞＞＞
#＜最初にどちらの分析を行うか選択する関数＞
def first_pattern():
    pattern = pg.confirm(text = "どちらの分析を行いたいですか。",
                        title = "Analytics",
                        buttons =["企業の総合力調査", "重回帰分析によるリターン予測"]
                        )

    return  pattern

#＜加工データの重複部分の除去する関数＞
def data_drop(processed_data):
    del_list = []
    del_code = []
    for i,k in enumerate(processed_data.code):
        if list(processed_data.code).count(k) != 1 and not k in del_code:
            del_list.append(i)
            del_code.append(k)
    #重複してデータを取得した場合のものを除去
    processed_data = processed_data.drop(del_list)
    return processed_data


#＜業種が同じ企業を集める関数＞
def industry_classification(industry,processed_data):
    data_concat = pd.DataFrame()
    for num in industry["銘柄コード"]:
        data_class = processed_data[processed_data["code"] == num]
        data_concat = pd.concat([data_concat,data_class])
    #集めたデータの欠損値を埋める
    ind_data = data_concat.fillna(data_concat.median())
    return    ind_data 



#＜指定企業を記入する関数＞
def typing() :
    type_in = pg.prompt(text = "分析したい証券コードもしくは会社名を入力してください", 
                        title = "入力欄", 
                        default = "(例1)2020,(例2)STUDENT株式会社"
                        )
    return type_in




#＜指定企業の分析範囲の確定させる関数＞
def confirm_enterprise(code,stock,pattern):
    clear_output()
    
    cannot_confirm = True
    while cannot_confirm :
        if pattern == "企業の総合力調査":
            confirm = pg.confirm(
                text = "どちらの順位を確認しますか？",
                title = "分析範囲の選択",
                buttons = ["全体で確認する", "業種内で確認する"]
            )
            if confirm == None :
                
                return None

            else:
                cannot_confirm = False
                return confirm


        else: #重回帰分析を選択したとき
            confirm = pg.confirm(text = "どちらを確認しますか？\n<注意>\n電気機器,卸売業,小売業,サービス業,情報・通信業\n以外の業種は業種内予測を行えません。",
                                            title = "分析範囲の選択",
                                            buttons =["全体で確認する","業種内で確認する"]
            )
            if confirm == None:
                
                return None

            elif confirm == "全体で確認する":
                cannot_confirm = False
                return confirm

            else: #業種内 を選択したとき
                specified = stock[stock["銘柄コード"] == int(code)]  
                ind_c = specified["業種"].values[0]
                if ind_c in ["電気機器","卸売業","小売業","サービス業","情報・通信業"]:
                    cannot_confirm = False
                    return confirm
                else:
                    print(f"業種：{ind_c}\n業種内分析が出来ない企業です、全体分析を行ってください。")
                    time.sleep(3)
    





#＜＜＜企業の総合力調査限定＞＞＞

#＜分析対象を選択する関数＞
def flag_one():
    flag_one = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "企業総合力調査",
                            buttons = ["全体を分析する", "業種内を分析する", "指定企業を分析する"]
    )
    return flag_one

#１０社以下の業種は省いています。
#＜業種⓵を選択する関数＞
def flag_two():
    flag_two = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "業種欄①", 
                            buttons =[
                                    "水産・農林業",
                                    "建設業",
                                    "食料品",
                                    "繊維製品",
                                    "パルプ・紙",
                                    "化学",
                                    "医薬品",
                                    "石油・石炭製品",
                                    "ゴム製品",
                                    "ガラス・土石製品",
                                    "業種欄②へ"
                                    ]
    )
    return flag_two


#＜業種⓶を選択する関数＞
def flag_three():
    flag_three = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "業種欄②", 
                            buttons =
                                    [
                                    "鉄鋼",
                                    "非鉄金属",
                                    "金属製品",
                                    "機械",
                                    "電気機器",
                                    "輸送用機器",
                                    "精密機器",
                                    "その他製品",
                                    "電気・ガス業",
                                    "陸運業",
                                    "業種欄③へ"
                                    ]
    )
    return flag_three

#＜業種➂を選択する関数＞
def flag_four():
    flag_four = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "業種欄③", 
                            buttons =
                                    [
                                    "海運業",
                                    "倉庫・運輸関連業",
                                    "卸売業",
                                    "小売業",
                                    "銀行業",
                                    "証券、商品先物取引業",
                                    "保険業",
                                    "その他金融業",
                                    "不動産業",
                                    "サービス業",
                                    "情報・通信業"
                                    ]
    )
    return flag_four


#＜rankにより、データ群の数値を相対的に評価する関数(TrueとFalseの基準は財務指標の見方に依存）＞
def TPS(data_mediRE):
    #安全性 
    data_mediRE["current_ratio"] = data_mediRE["current_ratio"].rank(ascending=True)  #＋
    data_mediRE["equity_ratio"] = data_mediRE["equity_ratio"].rank(ascending=True)    #＋
    data_mediRE["interest_coverage_ratio"] = data_mediRE["interest_coverage_ratio"].rank(ascending=True) # ＋
    data_mediRE["margin_of_safety_ratio"] = data_mediRE["margin_of_safety_ratio"].rank(ascending=True) # ＋
    data_mediRE["Interest-bearing debt operating CF magnification"] = data_mediRE["Interest-bearing debt operating CF magnification"].rank(ascending=False)#-

    #成長性
    data_mediRE["Net asset growth rate"] = data_mediRE["Net asset growth rate"].rank(ascending=True)  #＋
    data_mediRE["Sales growth rate"] = data_mediRE["Sales growth rate"].rank(ascending=True)    #＋
    data_mediRE["Net income growth rate"] = data_mediRE["Net income growth rate"].rank(ascending=True) #＋
    data_mediRE["Operating Cash Flow Growth Rate"] = data_mediRE["Operating Cash Flow Growth Rate"].rank(ascending=True)    #＋
    data_mediRE["roic"] = data_mediRE["roic"].rank(ascending=True)    #＋

    #収益性
    data_mediRE["Cost of sales rate"] = data_mediRE["Cost of sales rate"].rank(ascending=False) # ー
    data_mediRE["sga ratio"] = data_mediRE["sga ratio"].rank(ascending=False) # ー
    data_mediRE["roe"] = data_mediRE["roe"].rank(ascending=True) #＋
    data_mediRE["EVA Spread"] = data_mediRE["EVA Spread"].rank(ascending=True) #＋
    data_mediRE["Operating CF margin ratio"] = data_mediRE["Operating CF margin ratio"].rank(ascending=True) #＋

    #割安性
    data_mediRE["PSR"] = data_mediRE["PSR"].rank(ascending=False) # -
    data_mediRE["PCFR"] = data_mediRE["PCFR"].rank(ascending=False) # -
    data_mediRE["Mix factor"] = data_mediRE["Mix factor"].rank(ascending=False) # -
    data_mediRE["EV_EBITDA"] = data_mediRE["EV_EBITDA"].rank(ascending=False) # -
    data_mediRE["FCF theory stock price ratio"] = data_mediRE["FCF theory stock price ratio"].rank(ascending=True) # ＋

    #その他(効率性・労働生産性・株主還元性）
    data_mediRE["Total assets turnover"] = data_mediRE["Total assets turnover"].rank(ascending=True) # +
    data_mediRE["ccc"] = data_mediRE["ccc"].rank(ascending=False) # -
    data_mediRE["Sales per productivity"] = data_mediRE["Sales per productivity"].rank(ascending=True) # ＋
    data_mediRE["Operating income per person"] = data_mediRE["Operating income per person"].rank(ascending=True) #+
    data_mediRE["Dividend payout ratio"] = data_mediRE["Dividend payout ratio"].rank(ascending=True) #+
    data_mediRE["DOE"] = data_mediRE["DOE"].rank(ascending=True) #+
    
    return data_mediRE


#＜＜＜企業の総合力調査の関数＞＞＞
def total_power_survey(pattern):
    #企業の総合力調査はリターンを除く財務指標で分析するため、データA群のみで問題ない
    processed_data = pd.read_csv("work2_Processing/ProcessedDataA.csv")
    processed_data = data_drop(processed_data)
    #pyautguiによる選択操作
    flag1 = flag_one()
    if flag1== None :
        
        return None,None,None

    elif flag1 == "全体を分析する" :
        data_mediRE = processed_data.fillna(processed_data.median())

    elif flag1 == "業種内を分析する":
        flag2 =flag_two()

        if flag2 == None:
            
            return None,None,None

        elif flag2 == "業種欄②へ" :
            flag3 = flag_three()

            if flag3 == None:
                
                return None,None,None

            elif flag3 == "業種欄③へ":
                flag4 = flag_four()

                if flag4 == None :
                    
                    return None,None,None
                else :
                    stock_class = stock[stock["業種"] == flag4]
                    data_mediRE = industry_classification(stock_class,processed_data)
            else :
                stock_class = stock[stock["業種"] == flag3]
                data_mediRE = industry_classification(stock_class,processed_data)
        else :
            stock_class = stock[stock["業種"] == flag2]
            data_mediRE = industry_classification(stock_class,processed_data)

    else:
        #"指定企業を分析する"を選択したとき
        cannot_analyze = True
        while cannot_analyze:
            clear_output()
            #企業名(コード)を記入する
            type_in = typing()
            if type_in == None :
                
                return None,None,None
            else :
                #入力値がコードか会社名か判定
                if type_in.isdecimal() == True:
                    #コードを記入したとき
                    #入力値のコードが存在するか判定
                    if len(processed_data[processed_data["code"] == int(type_in)]) == 0 :
                        print("入力した証券コードは存在しません")        
                    else:
                        cannot_analyze = False
                        code = type_in
                        confirm = confirm_enterprise(code,stock,pattern)
                        if confirm == None:
                            
                            return None,None,None
                        elif confirm  == "全体で確認する":
                            data_mediRE = processed_data.fillna(processed_data.median())
                        else :#"業種内の順位を確認する"
                            #選択したコードの業種を確定させる
                            specified = stock[stock["銘柄コード"] == int(code)]  
                            ind_c = specified["業種"].values[0]
                            #最終行付近で利用
                            stock_class = stock[stock["業種"] == ind_c]
                            #同じ業種のコードを抽出する
                            data_mediRE = industry_classification(stock_class,processed_data)
                            

                    
                else:
                    #会社名を記入したとき
                    #入力値の会社が存在するか判定
                    contain =  processed_data[processed_data['company'].str.contains(type_in) == True]
                    if len(contain) == 0:
                        print(f"入力したもの:{type_in}\n検索出来ませんでした。(整数値の４桁もしくは正確な会社名に対応しています。)")
                        time.sleep(3)

                    elif 6 <= len(contain):
                        print(f"入力したもの:{type_in}\n検索ヒット数が多すぎます、具体的に記入してください。\n(タイピング出来てない可能性もあります。)")
                        time.sleep(3)
                    else :
                        reference = pg.confirm(text = "検索したい企業はどれですか？", 
                                                title = "確認用", 
                                                buttons =contain["company"].values
                                                )
                        if reference == None:
                            
                            return None,None,None 
                        else :
                            cannot_analyze = False
                            code = processed_data[processed_data["company"]== reference]["code"].values[0]
                            confirm = confirm_enterprise(code,stock,pattern)
                            if confirm == None:
                                
                                return None,None,None
                            elif confirm  == "全体で確認する":
                                data_mediRE = processed_data.fillna(processed_data.median())
                            else :#"業種内の順位を確認する"
                                #選択したコードの業種を確定させる
                                specified = stock[stock["銘柄コード"] == int(code)]  
                                ind_c = specified["業種"].values[0]
                                #最終行付近で利用
                                stock_class = stock[stock["業種"] == ind_c]
                                #同じ業種のコードを抽出する
                                data_mediRE = industry_classification(stock_class,processed_data)

                            
                            
    #指標を相対的に評価する
    data_mediRE = TPS(data_mediRE)

    #いらないデータを除去し総合順位を出す
    data_point = data_mediRE.drop(["company","code","equity_investment_return_rate"],axis = 1)
    data_mediRE["point"] = data_point.sum(axis=1)/26/len(data_point)*100 
    data_mediRE["RANKING"] = data_mediRE["point"].rank(ascending=False)                         
    result = data_mediRE.sort_values(by=["point"], ascending=False)


    #指定企業のランキングを表示
    if flag1 == "指定企業を分析する":
        result_sp = pd.concat([result[result["RANKING"] == min(result["RANKING"])],result[result["code"] == int(code)]])
        result_sp = pd.concat([result_sp,result[result["RANKING"] == max(result["RANKING"])]])
        tps_out = result_sp.iloc[:,[0,1,29,30]] 

    #全体or業種内のTOP3の会社と最下位を出力
    else:  
        tps_out = result.iloc[[0,1,2,-1],[0,1,29,30]]

    #インデックスをランキングに置換
    tps_out.set_index("RANKING",inplace=True)
    
    return tps_out , data_mediRE, result




#＜＜＜重回帰分析限定＞＞＞

#＜"キャピタルゲイン＋インカムゲイン"か""キャピタルゲイン"どちらを分析するか選択する関数＞
def select_one():
    select1 = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                        title = "重回帰分析による予測", 
                        buttons =["株式投資収益率の予測","キャピタルゲインの予測"]
    )
    return select1

#＜分析対象を選択する関数＞
def select_two():
    select2 = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                        title = "重回帰分析による予測", 
                        buttons =["全体を分析する", "業種内で分析する", "指定企業を分析する"]
    )
    return select2

#＜業種を選択する関数＞
def select_three():
    select3 = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                        title = "業種欄", 
                        buttons = ["電気機器","卸売業","小売業","サービス業","情報・通信業"]
    )
    return select3



#＜データクレンジングを行った上で、重回帰分析を行う関数＞
def MRA(data_medi):
    clf = linear_model.LinearRegression()

    # データフレームで分析に使わないcolumnsを除去               
    data_mediRE = data_medi.drop(["code","company"], axis = 1)

    #  データフレームの各列を正規化                                                                   全ての列がnanのものを除去
    data_medi_new = data_mediRE.apply(lambda x: (x - numpy.mean(x)) / (numpy.max(x) - numpy.min(x))).dropna(how='all', axis=1)


    #初期設定の説明変数作成のため要らない指標を削除            目的変数を除去
    data_medi_new_except_criterion = data_medi_new.drop(data_medi_new.iloc[:,[-1]], axis = 1)

    #初期設定の目的変数作成
    Y = data_medi_new.iloc[:,-1].values


    #＜データクレンジングを行い重回帰分析を行う＞
    while True :
        # 初期設定説明変数を作成 （今回ここをforでまわしていく）
        X = data_medi_new_except_criterion.values 
        #重回帰分析モデルの作成
        model = smf.OLS(Y,X) 
        result = model.fit()

        #＜データクレンジング1: p値が0.05以上のものを削除＞
        del_list = []
        count = 0
        for i,k in enumerate(result.pvalues):
            if k >= 0.05 :
                count += 1
                del_list.append(data_medi_new_except_criterion.iloc[:,i].name) 

        #p値で有意水準が全て５％でかつ分散共分散行列でも問題なかったときに出力
        if count == 0 :
            break
        else:
            if len(del_list) == len(result.pvalues):
                print("p値判定で全てクレンジングをした為、分析出来ませんでした。")
                return None,None,None
            else:
                data_medi_new_except_criterion = data_medi_new_except_criterion.drop(del_list,axis = 1)


        #＜データクレンジング2: 多重共線性回避のため、説明変数動詞の相関の強さを確認し削除＞
        while True :
            #分散共分散行列を作成する
            matrix = data_medi_new_except_criterion.astype(float).corr()
            #絶対値を取り、相関の強さを確認する
            cleansing = numpy.abs(matrix)

            fp_dict = {}
            #全ての財務指標を検索し相関性が高いものをみる
            for figure in range(len(cleansing)):
                                    #指標のkey                           1以外の相関性が0.5以上の指標の個数を特定
                Pd ={cleansing[0.5 <= abs(cleansing.iloc[figure,:])].index.values[0] :len(cleansing[0.5 <= abs(cleansing.iloc[figure,:])])-1}
                fp_dict.update(Pd)


            #最大の行が1個以上か確認した上で最大のindexを特定し(複数ある場合は早い方を抽出）、dropで行で削除。その後またcorr()を繰り返す。
            if 1 <= max(fp_dict.values()):
                Pmax = max(fp_dict,key = fp_dict.get)
                data_medi_new_except_criterion = data_medi_new_except_criterion.drop([Pmax], axis = 1)
            else :
                break


    #＜データクレンジング後、予測値や実測値を見比べる＞
    #説明変数の実測値
    measured_valueE = pd.DataFrame()
    for a in data_medi_new_except_criterion.iloc[0,:].index :
        data_merge = data_medi[[a]]
        measured_valueE = pd.concat([measured_valueE,data_merge],axis=1)

    #係数の計算
    clf.fit(X, Y)

    #説明変数の予測値の係数
    predicted_valueE = pd.DataFrame({"Name": data_medi_new_except_criterion.columns,"Coefficients": clf.coef_ })

    #説明変数の予測値の切片
    predicted_valueI = clf.intercept_ 

    

    #＜実測値と予測値の掛け算を行い、回帰式の予測値より現実のデータが低くなっている上位５％のインデックスと、その乖離度を出す。＞
    E = list(map(lambda x: sum(x * predicted_valueE.iloc[:,1].values) + predicted_valueI ,measured_valueE.values))

    return E , result , data_medi_new_except_criterion  



#＜＜重回帰分析の関数＞＞＞
#説明変数が26個のため、業種内分析において会社数が260社(少なくとも234＝260＊0.9）以下の業種は分析しない。 
#バーニーおじさんのルールを準拠(重回帰のときに必要なデータの数はパラメータの数の10倍）
def multiple_regression_analysis(pattern):
    #pyautoguiによる選択
    select1 = select_one()
    if select1 ==  "株式投資収益率の予測":
        processed_data = pd.read_csv("work2_Processing/ProcessedDataA.csv")
        processed_data = data_drop(processed_data)

    elif select1 ==  "キャピタルゲインの予測":
        processed_data = pd.read_csv("work2_Processing/ProcessedDataB.csv")
        processed_data = data_drop(processed_data)

    else:
        
        return None,None,None,None


    select2 = select_two()
    if select2 == None:
        
        return None,None,None,None

    elif select2 == "全体を分析する" :
        data_medi = processed_data.fillna(processed_data.median())


    elif select2 == "業種内で分析する":
        select3 = select_three()

        if select3 == None:
            
            return None,None,None,None  
        else :
            stock_class = stock[stock["業種"] == select3]
            data_medi = industry_classification(stock_class,processed_data)


    else:
        #"指定企業を分析する"
        cannot_analyze = True
        while cannot_analyze:
            clear_output()
            type_in = typing()
            if type_in == None :
                
                return None,None,None,None
            else :
                #入力値がコードか会社名か判定
                if type_in.isdecimal() :
                    #コード
                    #入力値のコードが存在するか判定
                    if len(processed_data[processed_data["code"] == int(type_in)]) == 0 :
                        print("入力した証券コードは存在しません")        
                    else:
                        cannot_analyze = False
                        code = type_in
                        confirm = confirm_enterprise(code,stock,pattern)
                        if confirm == None:
                            
                            return None,None,None,None
                        elif confirm  == "全体で確認する":
                            data_medi = processed_data.fillna(processed_data.median())
                        else :#"業種内の順位を確認する"
                            #選択したコードの業種を確定させる
                            specified = stock[stock["銘柄コード"] == int(code)]  
                            ind_c = specified["業種"].values[0]
                            #最終行付近で利用
                            stock_class = stock[stock["業種"] == ind_c]
                            #同じ業種のコードを抽出する
                            data_medi = industry_classification(stock_class,processed_data)
                            
                        
                    
                else:
                    #会社名
                    #入力値の会社が存在するか判定
                    contain =  processed_data[processed_data['company'].str.contains(type_in) == True]
                    if len(contain) == 0:
                        print(f"入力したもの:{type_in}\n検索出来ませんでした。(整数値の４桁もしくは正確な会社名に対応しています。)")
                        time.sleep(3)

                    elif 6 <= len(contain):
                        print(f"入力したもの:{type_in}\n検索ヒット数が多すぎます、具体的に記入してください。\n(タイピング出来てない可能性もあります。)")
                        time.sleep(3)
                    else :
                        reference = pg.confirm(text = "検索したい企業はどれですか？", title = "確認用", buttons = contain["company"].values )
                        if reference == None:
                            
                            return None,None,None,None  
                        else :
                            cannot_analyze = False
                            code = processed_data[processed_data["company"]== reference]["code"].values[0]
                            confirm = confirm_enterprise(code,stock,pattern)
                            if confirm == None:
                                
                                return None,None,None,None
                            elif confirm  == "全体で確認する":
                                data_medi = processed_data.fillna(processed_data.median())
                            else :#"業種内の順位を確認する"
                                #選択したコードの業種を確定させる
                                specified = stock[stock["銘柄コード"] == int(code)]  
                                ind_c = specified["業種"].values[0]
                                #最終行付近で利用
                                stock_class = stock[stock["業種"] == ind_c]
                                #同じ業種のコードを抽出する
                                data_medi = industry_classification(stock_class,processed_data)
                            
                            
                            

    #データをクレンジングし分析する
    E , result , data_medi_new_except_criterion   = MRA(data_medi)
    if E is None:
        return None, None,None,None

    #＜指定企業を選択したとき＞
    if select2 == "指定企業を分析する":
        count = 0
        for c in  data_medi["code"].values:
            if c == int(code):
                break
            count += 1

        df_code = data_medi.iloc[[count]]
        df_code["expect_rate"] = E[count]
        out_put = df_code


    #＜指定企業以外を選択したとき＞
    else:#乖離度上位の予測データを出力
        #実測値
        Y= data_medi.iloc[:,-1]
        Y=[ y for y in Y]
        mra_list = []
        for i in range(len(E)):
            #予測値が実測値より大きいか判定

            #値が違うため検証   
            if E[i] >= Y[i]:
                mra_list.append([i,E[i] - Y[i]])

        from copy import deepcopy as cp

        can_add = True
        while can_add :
            f = 0
            for i in range(len(mra_list) - 1):
                if mra_list[i][1] < mra_list[i + 1][1]:
                    save = cp(mra_list[i])
                    mra_list[i] = cp(mra_list[i + 1])
                    mra_list[i + 1] = cp(save)
                    f = 1
            if f == 0 :
                can_add = False


        #乖離度上位10％を抽出 
        sampling = mra_list[:round(len(mra_list)*0.1)]
        if len(sampling) == 0:
            print("期待利益を見込める企業が見つかりませんでした")
            return None,None,None,None
        #上位10％の銘柄が確認されたとき
        else:
            out_put = pd.DataFrame()

            times = 0
            #上位10％からtop有望銘柄を最大5つ出力 
            for i in [sampling[rank][0] for rank in range(len(sampling))]:
                times +=1
                Relay =  data_medi.iloc[[i]]
                Relay["expect_rate"] = E[i]
                out_put = pd.concat([out_put,Relay])
                if times == 5:break


    mra_out = out_put.iloc[:,[0,1,-2,-1]]
    mra_out.set_index("code",inplace=True)
    return mra_out , data_medi , result , data_medi_new_except_criterion



#分析結果出力後、確認のため元データや統計量を出力する確認
def check_enterprize(pattern, mra_out , data_mediRE, tps_out , data_medi , result , data_medi_new_except_criterion):
    if pattern == "企業の総合力調査":  
        check = pg.confirm(text = "確認したいものはどれですか？",
                            title = "確認用", 
                            buttons = ["元のデータを確認する"]
        )

        if check == "元のデータを確認する":
            #確認用1：加工用データ
            return data_mediRE

        else :
            
            return True

    else:#"重回帰分析"
        check = pg.confirm(text = "確認したいものはどれですか？", 
                            title = "確認用", 
                            buttons =["分析する元データ","分析後の統計量"]
        )

        if check == "分析する元データ":
            #確認用１: 加工データ
            return data_medi

        elif check == "分析後の統計量":
            #確認用2: 統計量
            return result.summary()
        else :
            
            return True


#＜patternの選択により、企業の総合力かリターン予測かを決める関数＞
def financial_pointer_analyzer(pattern,total_power_survey,multiple_regression_analysis):
    #初期値を0に設定し、企業の総合力調査と重回帰分析の出力結果の返り値の個数が異なる問題を回避
    mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion = 0,0,0,0,0,0,0
    if pattern == "企業の総合力調査":
        tps_out , data_mediRE, result = total_power_survey(pattern)
        return mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion
    else:
        mra_out , data_medi , result , data_medi_new_except_criterion = multiple_regression_analysis(pattern)
        return mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion



