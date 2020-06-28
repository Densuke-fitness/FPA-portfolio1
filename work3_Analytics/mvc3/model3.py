from copy import deepcopy as cp
import numpy 
from numpy import nan 
import pandas as pd
import pyautogui as pg 
import sklearn 
from sklearn import linear_model 
import statsmodels.api as smf
import time 

from . import view3

STOCK = pd.read_csv("work3_Analytics/stocklist.csv")

#＜＜＜２つの分析の共通項＞＞＞
class TwoAnalyzeCommonnOperation(object):

    def industry_classification(self, industry, processed_data):
        """業種が同じ企業を集める関数"""
        data_concat = pd.DataFrame()
        for num in industry["銘柄コード"]:
            data_class = processed_data[processed_data["code"] == num]
            data_concat = pd.concat([data_concat, data_class])
        #集めたデータの欠損値を埋める
        ind_data = data_concat.fillna(data_concat.median())
        return  ind_data 


#＜＜＜総合力調査(TPS)＞＞＞
class TPSAnalyseRank(object):
    def tps_rank(self, data_mediRE):
        """rankにより、データ群の数値を相対的に評価する関数(TrueとFalseの基準は財務指標の見方に依存"""
        #安全性 
        data_mediRE["current_ratio"] = data_mediRE["current_ratio"].rank(ascending=True)  
        data_mediRE["equity_ratio"] = data_mediRE["equity_ratio"].rank(ascending=True)    
        data_mediRE["interest_coverage_ratio"] = data_mediRE["interest_coverage_ratio"].rank(ascending=True) 
        data_mediRE["margin_of_safety_ratio"] = data_mediRE["margin_of_safety_ratio"].rank(ascending=True) 
        data_mediRE["Interest-bearing debt operating CF magnification"] = data_mediRE["Interest-bearing debt operating CF magnification"].rank(ascending=False)#-

        #成長性
        data_mediRE["Net asset growth rate"] = data_mediRE["Net asset growth rate"].rank(ascending=True)  
        data_mediRE["Sales growth rate"] = data_mediRE["Sales growth rate"].rank(ascending=True)    
        data_mediRE["Net income growth rate"] = data_mediRE["Net income growth rate"].rank(ascending=True) 
        data_mediRE["Operating Cash Flow Growth Rate"] = data_mediRE["Operating Cash Flow Growth Rate"].rank(ascending=True)    
        data_mediRE["roic"] = data_mediRE["roic"].rank(ascending=True)    

        #収益性
        data_mediRE["Cost of sales rate"] = data_mediRE["Cost of sales rate"].rank(ascending=False) 
        data_mediRE["sga ratio"] = data_mediRE["sga ratio"].rank(ascending=False) 
        data_mediRE["roe"] = data_mediRE["roe"].rank(ascending=True)
        data_mediRE["EVA Spread"] = data_mediRE["EVA Spread"].rank(ascending=True) 
        data_mediRE["Operating CF margin ratio"] = data_mediRE["Operating CF margin ratio"].rank(ascending=True)

        #割安性
        data_mediRE["PSR"] = data_mediRE["PSR"].rank(ascending=False) 
        data_mediRE["PCFR"] = data_mediRE["PCFR"].rank(ascending=False) 
        data_mediRE["Mix factor"] = data_mediRE["Mix factor"].rank(ascending=False) 
        data_mediRE["EV_EBITDA"] = data_mediRE["EV_EBITDA"].rank(ascending=False) 
        data_mediRE["FCF theory stock price ratio"] = data_mediRE["FCF theory stock price ratio"].rank(ascending=True) 

        #その他(効率性・労働生産性・株主還元性）
        data_mediRE["Total assets turnover"] = data_mediRE["Total assets turnover"].rank(ascending=True) 
        data_mediRE["ccc"] = data_mediRE["ccc"].rank(ascending=False) 
        data_mediRE["Sales per productivity"] = data_mediRE["Sales per productivity"].rank(ascending=True) 
        data_mediRE["Operating income per person"] = data_mediRE["Operating income per person"].rank(ascending=True) 
        data_mediRE["Dividend payout ratio"] = data_mediRE["Dividend payout ratio"].rank(ascending=True) 
        data_mediRE["DOE"] = data_mediRE["DOE"].rank(ascending=True)
        
        return data_mediRE

#＜＜＜総合力調査(TPS)＞＞＞
class  TotalPowerSurvey(view3.TwoAnalyzeCommonnSelect, view3.TPSAnalyseSelect, TwoAnalyzeCommonnOperation, TPSAnalyseRank):

    def total_power_survey(self, pattern):
        """企業の総合力調査の関数"""
        #企業の総合力調査はリターンを除く財務指標で分析するため、データA群のみで問題ない
        processed_data = pd.read_csv("work2_Processing/ProcessedDataA.csv")
        #pyautguiによる選択操作
        wrapper_tps_as = view3.TPSAnalyseSelect()
        select_tps_target = wrapper_tps_as.select_tps_target()
        if select_tps_target == None :
            
            return None,None,None

        elif select_tps_target == "全体を分析する" :
            data_mediRE = processed_data.fillna(processed_data.median())

        elif select_tps_target == "業種内を分析する":
            industy_one = wrapper_tps_as.select_industy_one()

            if industy_one == None:
                
                return None,None,None

            elif industy_one == "業種欄②へ" :
                industy_two = wrapper_tps_as.select_industy_two()

                if industy_two == None:
                    
                    return None,None,None

                elif industy_two == "業種欄③へ":
                    industy_three = wrapper_tps_as.select_industy_three()

                    if industy_three == None :
                        
                        return None, None, None
                    else :
                        stock_class = STOCK[STOCK["業種"] == industy_three]
                        data_mediRE = self.industry_classification(stock_class, processed_data)
                else :
                    stock_class = STOCK[STOCK["業種"] == industy_two]
                    data_mediRE = self.industry_classification(stock_class, processed_data)
            else :
                stock_class = STOCK[STOCK["業種"] == industy_one]
                data_mediRE = self.industry_classification(stock_class, processed_data)

        else:
            #"指定企業を分析する"を選択したとき
            cannot_analyze = True
            while cannot_analyze:
                
                #企業名(コード)を記入する
                wrapper_tacs = view3.TwoAnalyzeCommonnSelect()
                type_in = wrapper_tacs.type_in_enterprise()
                if type_in == None :
                    
                    return None, None, None
                else :
                    #入力値がコードか会社名か判定
                    if type_in.isdecimal() :
                        #コードを記入したとき
                        #入力値のコードが存在するか判定
                        if len(processed_data[processed_data["code"] == int(type_in)]) == 0 :
                            print("入力した証券コードは存在しません")        
                        else:
                            cannot_analyze = False
                            code = type_in
                            confirm = wrapper_tacs.confirm_scope_analysis(code, STOCK, pattern)
                            if confirm == None:
                                
                                return None, None, None
                            elif confirm  == "全体で確認する":
                                data_mediRE = processed_data.fillna(processed_data.median())
                            else :#"業種内の順位を確認する"
                                #選択したコードの業種を確定させる
                                specified = STOCK[STOCK["銘柄コード"] == int(code)]  
                                ind_c = specified["業種"].values[0]
                                #最終行付近で利用
                                stock_class = STOCK[STOCK["業種"] == ind_c]
                                #同じ業種のコードを抽出する
                                data_mediRE = self.industry_classification(stock_class, processed_data)
                        
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
                                
                                return None, None, None 
                            else :
                                cannot_analyze = False
                                code = processed_data[processed_data["company"]== reference]["code"].values[0]
                                confirm = wrapper_tacs.confirm_scope_analysis(code, STOCK, pattern)
                                if confirm == None:
                                    
                                    return None, None, None
                                elif confirm  == "全体で確認する":
                                    data_mediRE = processed_data.fillna(processed_data.median())
                                else :#"業種内の順位を確認する"
                                    #選択したコードの業種を確定させる
                                    specified = STOCK[STOCK["銘柄コード"] == int(code)]  
                                    ind_c = specified["業種"].values[0]
                                    #最終行付近で利用
                                    stock_class = STOCK[STOCK["業種"] == ind_c]
                                    #同じ業種のコードを抽出する
                                    data_mediRE = self.industry_classification(stock_class, processed_data)                                          
        #指標を相対的に評価する
        data_mediRE = self.tps_rank(data_mediRE)

        #いらないデータを除去し総合順位を出す
        data_point = data_mediRE.drop(["company", "code", "equity_investment_return_rate"], axis = 1)
        data_mediRE["point"] = data_point.sum(axis=1) / 26 / len(data_point) * 100 
        data_mediRE["RANKING"] = data_mediRE["point"].rank(ascending=False)                         
        result = data_mediRE.sort_values(by=["point"], ascending=False)


        #指定企業のランキングを表示
        if select_tps_target == "指定企業を分析する":
            result_sp = pd.concat([result[result["RANKING"] == min(result["RANKING"])], result[result["code"] == int(code)]])
            result_sp = pd.concat([result_sp,result[result["RANKING"] == max(result["RANKING"])]])
            tps_out = result_sp.iloc[:, [0, 1, 29, 30]] 

        #全体or業種内のTOP3の会社と最下位を出力
        else:  
            tps_out = result.iloc[[0, 1, 2, -1], [0 , 1, 29, 30]]

        #インデックスをランキングに置換
        tps_out.set_index("RANKING", inplace=True)
        
        return tps_out , data_mediRE, result


#＜＜＜重回帰分析によるリターン予測(MRA)＞＞＞
class MRADataAnalyzeCleansing(object):

    def mra_cleansing(self, data_medi):
        """データクレンジングを行った上で、重回帰分析を行う関数＞"""
        print("しばらくお待ちください。（3分）")
        clf = linear_model.LinearRegression()
        # データフレームで分析に使わないcolumnsを除去               
        data_mediRE = data_medi.drop(["code","company"], axis = 1)
        #  データフレームの各列を正規化                                                                   全ての列がnanのものを除去
        data_medi_new = data_mediRE.apply(lambda x: (x - numpy.mean(x)) / (numpy.max(x) - numpy.min(x))).dropna(how='all', axis=1)
        #初期設定の説明変数作成のため要らない指標を削除            目的変数を除去
        data_medi_new_except_criterion = data_medi_new.drop(data_medi_new.iloc[:, [-1]], axis = 1)
        #初期設定の目的変数作成
        Y = data_medi_new.iloc[:, -1].values
        #＜データクレンジングを行い重回帰分析を行う＞
        while True :
            # 初期設定説明変数を作成 （今回ここをforでまわしていく）
            X = data_medi_new_except_criterion.values 
            #重回帰分析モデルの作成
            model = smf.OLS(Y, X) 
            result = model.fit()
            #＜データクレンジング1: p値が0.05以上のものを削除＞
            del_list = []
            count = 0
            for i,k in enumerate(result.pvalues):
                if k >= 0.05 :
                    count += 1
                    del_list.append(data_medi_new_except_criterion.iloc[:, i].name) 
            #p値で有意水準が全て５％でかつ分散共分散行列でも問題なかったときに出力
            if count == 0 :
                break
            else:
                if len(del_list) == len(result.pvalues):
                    print("p値判定で全てクレンジングをした為、分析出来ませんでした。")
                    return None, None, None
                else:
                    data_medi_new_except_criterion = data_medi_new_except_criterion.drop(del_list, axis = 1)
            #＜データクレンジング2: 多重共線性回避のため、説明変数動詞の相関の強さを確認し削除＞
            while True :
                #分散共分散行列を作成する
                matrix = data_medi_new_except_criterion.astype(float).corr()
                #絶対値を取り、相関の強さを確認する
                cleansing = numpy.abs(matrix)

                financital_pointer_dict = {}
                #全ての財務指標を検索し相関性が高いものをみる
                for figure in range(len(cleansing)):
                                        #指標のkey                           1以外の相関性が0.5以上の指標の個数を特定
                    high_corr ={cleansing[0.5 <= abs(cleansing.iloc[figure, :])].index.values[0] :len(cleansing[0.5 <= abs(cleansing.iloc[figure, :])])-1}
                    financital_pointer_dict.update(high_corr)
                #最大の行が1個以上か確認した上で最大のindexを特定し(複数ある場合は早い方を抽出）、dropで行で削除。その後またcorr()を繰り返す。
                if 1 <= max(financital_pointer_dict.values()):
                    p_max = max(financital_pointer_dict,key = financital_pointer_dict.get)
                    data_medi_new_except_criterion = data_medi_new_except_criterion.drop([p_max], axis = 1)
                else :
                    break
        #＜データクレンジング後、予測値や実測値を見比べる＞
        #説明変数の実測値
        measured_valueE = pd.DataFrame()
        for i in data_medi_new_except_criterion.iloc[0, :].index :
            data_merge = data_medi[[i]]
            measured_valueE = pd.concat([measured_valueE, data_merge], axis=1)
        #係数の計算
        clf.fit(X, Y)
        #説明変数の予測値の係数
        predicted_valueE = pd.DataFrame({"Name": data_medi_new_except_criterion.columns, "Coefficients": clf.coef_ })
        #説明変数の予測値の切片
        predicted_valueI = clf.intercept_ 
        #＜実測値と予測値の掛け算を行い、回帰式の予測値より現実のデータが低くなっている上位５％のインデックスと、その乖離度を出す。＞
        E = list(map(lambda x: sum(x * predicted_valueE.iloc[:, 1].values) + predicted_valueI, measured_valueE.values))

        return E , result , data_medi_new_except_criterion  


#＜＜＜重回帰分析によるリターン予測(MRA)＞＞＞
class  MultipleRegressionAnalysis(view3.TwoAnalyzeCommonnSelect, view3.MRAAnalyseSelect, MRADataAnalyzeCleansing, TwoAnalyzeCommonnOperation):

    def multiple_regression_analysis(self, pattern):
        """
        ＜＜重回帰分析の関数＞＞＞
        説明変数が26個のため、業種内分析において会社数が260社(少なくとも234＝260＊0.9）以下の業種は分析しない。 
        バーニーおじさんのルールを準拠(重回帰のときに必要なデータの数はパラメータの数の10倍）       
        """
        #pyautoguiによる選択
        wrapper_mra_as = view3.MRAAnalyseSelect()
        select_forecast =  wrapper_mra_as.select_forecast()
        if select_forecast ==  "株式投資収益率の予測":
            processed_data = pd.read_csv("work2_Processing/ProcessedDataA.csv")

        elif  select_forecast ==  "キャピタルゲインの予測":
            processed_data = pd.read_csv("work2_Processing/ProcessedDataB.csv")

        else:
            return None, None, None, None

        select_mra_target = wrapper_mra_as.select_mra_target()
        if select_mra_target == None:
            
            return None, None, None, None

        elif select_mra_target == "全体を分析する" :
            data_medi = processed_data.fillna(processed_data.median())

        elif select_mra_target == "業種内で分析する":
            select_industy_limited = wrapper_mra_as.select_industy_limited()

            if select_industy_limited == None:
                
                return None, None, None, None  
            else :
                stock_class = STOCK[STOCK["業種"] == select_industy_limited]
                data_medi = self.industry_classification(stock_class,processed_data)
        else:
            #"指定企業を分析する"
            cannot_analyze = True
            while cannot_analyze:
                wrapper_tacs = view3.TwoAnalyzeCommonnSelect()
                type_in = wrapper_tacs.type_in_enterprise()
                if type_in == None :
                    
                    return None, None, None, None
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
                            confirm = wrapper_tacs.confirm_scope_analysis(code, STOCK, pattern)
                            if confirm == None:
                                
                                return None, None, None, None
                            elif confirm  == "全体で確認する":
                                data_medi = processed_data.fillna(processed_data.median())
                            else :#"業種内の順位を確認する"
                                #選択したコードの業種を確定させる
                                specified = STOCK[STOCK["銘柄コード"] == int(code)]  
                                ind_c = specified["業種"].values[0]
                                #最終行付近で利用
                                stock_class = STOCK[STOCK["業種"] == ind_c]
                                #同じ業種のコードを抽出する
                                data_medi = self.industry_classification(stock_class, processed_data)                 
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
                                
                                return None, None, None, None  
                            else :
                                cannot_analyze = False
                                code = processed_data[processed_data["company"]== reference]["code"].values[0]
                                # wrapper_tacs = view3.TwoAnalyzeCommonnSelect() 
                                confirm = wrapper_tacs.confirm_scope_analysis(code, STOCK, pattern)
                                if confirm == None:
                                    
                                    return None, None, None, None
                                elif confirm  == "全体で確認する":
                                    data_medi = processed_data.fillna(processed_data.median())
                                else :#"業種内の順位を確認する"
                                    #選択したコードの業種を確定させる
                                    specified = STOCK[STOCK["銘柄コード"] == int(code)]  
                                    ind_c = specified["業種"].values[0]
                                    #最終行付近で利用
                                    stock_class = STOCK[STOCK["業種"] == ind_c]
                                    #同じ業種のコードを抽出する
                                    data_medi = self.industry_classification(stock_class, processed_data)

        #データをクレンジングし分析する
        E , result, data_medi_new_except_criterion   = self.mra_cleansing(data_medi)
        if E is None:
            return None, None,None,None

        #＜指定企業を選択したとき＞
        if select_mra_target == "指定企業を分析する":
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
            Y= data_medi.iloc[:, -1]
            Y=[ y for y in Y]
            mra_list = []
            for i in range(len(E)):
                #予測値が実測値より大きいか判定
                #値が違うため検証   
                if E[i] >= Y[i]:
                    mra_list.append([i,E[i] - Y[i]])

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
            sampling = mra_list[:round(len(mra_list) * 0.1)]
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
                    relay =  data_medi.iloc[[i]]
                    relay["expect_rate"] = E[i]
                    out_put = pd.concat([out_put, relay])
                    if times == 5:
                        break

        mra_out = out_put.iloc[:, [0 , 1, -2, -1]]
        mra_out.set_index("code",inplace=True)
        return mra_out , data_medi , result , data_medi_new_except_criterion


#＜＜＜財務指標の分析(FPA)＞＞＞
class FinancialPointerAnalyzer(TotalPowerSurvey, MultipleRegressionAnalysis):

    def financial_pointer_analyzer(self, pattern):
        """財務指標を分析する関数"""
        #初期値を0に設定し、企業の総合力調査と重回帰分析の出力結果の返り値の個数が異なる問題を回避
        mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion = 0, 0, 0, 0, 0, 0, 0
        if pattern == "企業の総合力調査":
            tps_out , data_mediRE, result = self.total_power_survey(pattern)
            return mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion
        else:
            mra_out , data_medi , result , data_medi_new_except_criterion = self.multiple_regression_analysis(pattern)
            return mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion



