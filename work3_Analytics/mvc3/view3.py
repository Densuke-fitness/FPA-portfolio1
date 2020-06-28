from copy import deepcopy as cp
import numpy 
from numpy import nan 
import pandas as pd
import pyautogui as pg 
import sklearn 
from sklearn import linear_model 
import statsmodels.api as smf
import time 

#＜＜＜２つの分析の共通項＞＞＞
class TwoAnalyzeCommonnSelect(object):
    
    def select_analytical_method(self):
        """最初にどちらの分析を行うか選択する関数"""

        pattern = pg.confirm(text = "どちらの分析を行いたいですか。",
                            title = "Analytics",
                            buttons =["企業の総合力調査", "重回帰分析によるリターン予測"]
                            )
        return  pattern


    def type_in_enterprise(self) :
        """指定企業を記入する関数"""

        type_in = pg.prompt(text = "分析したい証券コードもしくは会社名を入力してください", 
                            title = "入力欄", 
                            default = "(例1)2020,(例2)STUDENT株式会社"
                            )
        return type_in


    def confirm_scope_analysis(self, code, STOCK, pattern):    
        """指定企業の分析範囲の確定させる関数"""

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
                    specified = STOCK[STOCK["銘柄コード"] == int(code)]  
                    ind_c = specified["業種"].values[0]
                    if ind_c in ["電気機器","卸売業","小売業","サービス業","情報・通信業"]:
                        cannot_confirm = False
                        return confirm
                    else:
                        print(f"業種：{ind_c}\n業種内分析が出来ない企業です、全体分析を行ってください。")
                        time.sleep(3)


#＜＜＜総合力調査(TPS)＞＞＞
class TPSAnalyseSelect(object):
    #＜分析対象を選択する関数＞
    def select_tps_target(self):
        """"分析対象を選択する関数"""
        #１０社以下の業種は省いています。
        select_tps_target = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                                title = "企業総合力調査",
                                buttons = ["全体を分析する", "業種内を分析する", "指定企業を分析する"]
        )
        return select_tps_target
    

    def select_industy_one(self):
        """業種⓵を選択する関数"""
        industy_one = pg.confirm(text = "操作を終了したい場合は×を押してください", 
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
        return  industy_one


    def select_industy_two(self):
        """業種⓶を選択する関数"""
        industy_two = pg.confirm(text = "操作を終了したい場合は×を押してください", 
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
        return  industy_two


    def select_industy_three(self):
        """業種➂を選択する関数"""
        industy_three = pg.confirm(text = "操作を終了したい場合は×を押してください", 
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
        return industy_three


#＜＜＜重回帰分析によるリターン予測(MRA)＞＞＞
class MRAAnalyseSelect(object):

    def select_forecast(self):
        """どちらのリターン予測をおこなうか選択する関数"""

        select_forecast = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "重回帰分析による予測", 
                            buttons =["株式投資収益率の予測","キャピタルゲインの予測"]
        )
        return select_forecast


    def select_mra_target(self):
        """分析対象を選択する関数"""

        select_mra_target = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "重回帰分析による予測", 
                            buttons =["全体を分析する", "業種内で分析する", "指定企業を分析する"]
        )
        return select_mra_target


    def select_industy_limited(self):
        """業種を選択する関数"""

        select_industy_limited = pg.confirm(text = "操作を終了したい場合は×を押してください", 
                            title = "業種欄", 
                            buttons = ["電気機器", "卸売業", "小売業", "サービス業", "情報・通信業"]
        )
        return select_industy_limited



#＜＜＜分析結果の詳細を確認するクラス()＞＞＞
class CheckResultDetails(object):

    def check_enterprize(self,pattern, mra_out , data_mediRE, tps_out , data_medi , result , data_medi_new_except_criterion):
        """#分析結果出力後、確認のため元データや統計量を確認する関数"""

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
                                buttons =["分析する元データ", "分析後の統計量"]
            )

            if check == "分析する元データ":
                #確認用１: 加工データ
                return data_medi

            elif check == "分析後の統計量":
                #確認用2: 統計量
                return result.summary()
            else :
                
                return True