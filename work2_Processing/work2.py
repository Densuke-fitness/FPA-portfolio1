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

import pandas as pd
import time
from IPython.display import clear_output
from numpy import nan

#取得したCSVデータを読み込む際に、もとの証券コードのリストを頼りにしている
with open("work1_Fetching/ticker.txt" ,mode = "r") as f:
    file = f.read()
ticker_list_three = file.split("\n")
with open("work1_Fetching/ticker_count.txt" , mode = "r") as f:
    count_int = int(f.read())
count = count_int
ticker_data = ",".join(ticker_list_three[:count])
ticker_data = ticker_data.split(",")


#＜加重平均関数(各指標を求める際、加重平均を用いて時系列ごとにウエイトを置いて出力している)＞
def w_ave(x):
    x = x.dropna()
    sum_wa = 0
    count=0
    
    for a in x.values:
        count += 1
        weight = a * count
        sum_wa += weight 

    if count == 0:
        return nan
    else :
        result = sum_wa / ((1/2)*count*(count+1))
        if result == float('inf') :
            return nan
        else :
            return result


#＜成長率算出関数(成長性の指標の際に利用)＞
def slide(a):
    #nanを除去
    b = a.dropna()
    #0を除去  
    c = b[b == 0]
    d = b.drop(c.index,axis = 0)
    #ずらす
    e = d.shift(-1)
    #成長率を出す
    return  (d - e)/e *100


#＜日別の株価指標と現在の株価指標をmergeさせる関数＞
def dc_merge(daily,current):
    if current[0] is None:
        return daily
    else : 
        dcm = pd.concat([daily,current],axis = 0)
        return dcm



#＜説明変数群1【安全性指標 safety】＞
def safety(df_q):
    #<1:流動比率 current_ratio>
    s1 = df_q["current_ratio"]
    s1_cr =w_ave(s1)
    
    #<2:自己資本比率 equity_ratio>
    s2 = df_q["equity_ratio"]
    s2_er = w_ave(s2)
    
    #<3:インタレストカバレッジレシオ interest_coverage_ratio>
    s3 = df_q["interest_coverage_ratio"]
    s3_icr = w_ave(s3)/1000
    
    #<4:安全余裕率 margin_of_safety_ratio> 
    #安全余裕率 ＝ （売上高 net_sales - 損益分岐点売上高)/売上高 ＊100)
    s4= df_q[["net_sales","sga","gross_margin"]] 

    #s4_bp 損益分岐点 Breakeven point ＝  販管費 sga /(売上高総利益率 gross_margin /100)
    s4_bp = w_ave(s4["sga"]) / w_ave(s4["gross_margin"] )* 100

    #<安全余裕率>
    s4_msr = (w_ave(s4["net_sales"])- s4_bp)/w_ave(s4["net_sales"]) *100
    
    #<5:有利子負債営業CF倍率 Interest-bearing debt operating CF magnification>
    s5 = df_q["operating_cash_flow_debt_ratio"]
    s5_ocfr= w_ave(s5)/100
    
    return s1_cr,s2_er,s3_icr,s4_msr,s5_ocfr




#＜説明変数群2【成長性指標 growth_potential】＞
def growth_potential(df_q):
    #<1:純資産成長率 Net asset growth rate = (後equity - 前equity)/前equity * 100>
    gp1 = df_q["equity"]   
    gp1_s = slide(gp1)
    gp1_nsar = w_ave(gp1_s)
    
    #<2:売上高成長率 Sales growth rate = (後net_sales-前net_sales )/前net_sales*100>
    gp2 = df_q["net_sales"]
    gp2_s = slide(gp2)
    gp2_sgr = w_ave(gp2_s)
    
    #<3:当期純利益成長率 Net income growth rate = (後net_income-前net_income)/前net_income *100>
    gp3 = df_q["net_income"]
    gp3_s = slide(gp3)
    gp3_nigr = w_ave(gp3_s)
    
    #<4:営業ＣＦ成長率 Operating Cash Flow Growth Rate = (後operating_cash_flow-前operating_cash_flow)/前operating_cash_flow *100>
    gp4 = df_q["operating_cash_flow"]
    gp4_s = slide(gp4)
    gp4_ocfgr = w_ave(gp4_s)
    
    #<5:roic>
    gp5 = df_q["roic"]
    gp5_roic = w_ave(gp5)
    
    return gp1_nsar,gp2_sgr,gp3_nigr,gp4_ocfgr,gp5_roic



#＜説明変数群3【収益性指標 profitability】＞
def profitability(df_q,df_day,df_c):
    #<1:売上原価率 Cost of sales rate = cost_of_sales/net_sales>
    p1 = df_q[["cost_of_sales","net_sales"]]
    p1_cosr = w_ave(p1["cost_of_sales"])/w_ave(p1["net_sales"])*100  
    
    #<2:売上高販管費率 sga_ratio>
    p2= df_q[ "sga_ratio"]
    p2_sr = w_ave(p2)
    
    #<3:roe>
    p3= df_q["roe"]       
    p3_roe = w_ave(p3)

    #<4:EVAスプレッド eva Spread  = roic - wacc>
    #4-1:roicの加重平均 
    p4_1= df_q["roic"]
    p4_1_roic = w_ave(p4_1)

    #4-2:waccの加重平均  wacc =  ＦＣＦ / 企業価値  (企業価値 ＝ FCF / WACC(割引キャッシュフロー法 より算定)

    #4-2-1:フリーCFの加重平均    
    p4_2_1 = df_q["free_cash_flow"]
    p4_2_1fcf = w_ave(p4_2_1)

    #4-2-2:企業価値の加重平均
    p4_2_2_1 = df_day["enterprise_value"]
    p4_2_2_2 = df_c["enterprise_value"]
    p4_2_2merge= dc_merge(p4_2_2_1, p4_2_2_2)
    p4_2_2ep = w_ave(p4_2_2merge)

    #<EVAスプレッド>
    p4_eva = p4_1_roic - (p4_2_1fcf/p4_2_2ep)
    
    #<5:営業CFマージン比率 Operating CF margin ratio>
    p5= df_q["net_sales_operating_cash_flow_ratio"] 
    p5_ocfmr = w_ave(p5)
    
    return p1_cosr,p2_sr,p3_roe,p4_eva,p5_ocfmr



#＜説明変数群4【割安性指標 Inexpensive】＞
def inexpensive(df_q,df_day,df_c):
    #<1:PSR  = 時価総額 Market capitalization/売上高 net sales>
    #1-1:時価総額の加重平均
    i1_1_1 = df_day["market_capital"]
    i1_1_2 = df_c["market_capital"]
    i1_1merge= dc_merge(i1_1_1,i1_1_2)
    i1_1mc=w_ave(i1_1merge)

    #1-2:売上高の加重平均
    i1_2= df_q["net_sales"]
    i1_2ns=w_ave(i1_2)

    #PSR  = 時価総額/売上高  
    i1_psr = i1_1mc/i1_2ns
    
    #<2:PCFR  = 時価総額/営業ＣＦ>
    #2-1:時価総額の加重平均
    i2_1mc = i1_1mc

    #1-2:営業ＣＦの加重平均
    i2_2 = df_q["operating_cash_flow"]
    i2_2ocf=w_ave(i2_2)

    #PCFR  = 時価総額/営業CF
    i2_pcfr = i2_1mc/i2_2ocf
    
    #<3:ミックス係数 ＝ PER＊PBR>  
    i3_1 = df_day["per_pbr"]
    i3_2 = df_c["per_pbr"]
    i3 = dc_merge(i3_1,i3_2)
    i3_mix = w_ave(i3)
    
    #<4:EV/EBITDA倍率  会社予想>
    i4_1 = df_day["ev_ebitda_forecast"]
    i4_2 = df_c["ev_ebitda_forecast"]
    i4 = dc_merge(i4_1,i4_2)
    i4_ev_ebitda = w_ave(i4)

    #<5:FCF理論株価との乖離割合 = (1+(FCF理論株価-株価)/株価)*100 >

    #FCF理論株価 =(企業価値 enterprise_value -有利子負債 debt)/発行株式数  "issued_share_num")
    #5-1:企業価値の加重平均 enterprise_value
    i5_1_1 = df_day["enterprise_value"]
    i5_1_2 = df_c["enterprise_value"]
    i5_1_merge= dc_merge(i5_1_1, i5_1_2)
    i4_2_2ep = w_ave(i5_1_merge)
    i5_1ep = i4_2_2ep 

    #5-2:有利子負債 debt
    i5_2 = df_q["debt"]
    i5_2_debt = w_ave(i5_2)

    #5-3:株式数  "issued_share_num"
    i5_3 = df_q["issued_share_num"]
    i5_3_isn = w_ave(i5_3)

    #FCF理論株価 fcf stock price
    i5_fcfstock = (i5_1ep - i5_2_debt)/i5_3_isn

    #5-4:株価 stock price 株価 = 時価総額/発行株式数
    i5_4_1sp = w_ave(df_day["market_capital"])/w_ave(df_q["issued_share_num"])
    i5_4_2sp = w_ave(df_c["stockprice"])
    i5_stock = (i5_4_1sp+i5_4_2sp)/2


    #<FCF理論株価との乖離割合 FCF theory stock price ratio>
    i5_FCFtspr = (1+(i5_fcfstock - i5_stock)/i5_stock)*100
    
    return i1_psr,i2_pcfr,i3_mix,i4_ev_ebitda,i5_FCFtspr



#＜説明変数群5【効率性指標 Efficiency】＞
def efficiency(df_q):
    #<1:総資産回転率 Total assets turnover>
    e1 = df_q["total_asset_turnover"]
    e1_tat = w_ave(e1)
    
    #<2:CCC(キャッシュコンバージョンサイクル) = 売上債権回転期間 + 棚卸資産回転期間 – 支払債務回転期間)>
    e2_df = df_q[["accounts_receivable_turnover","inventory_turnover","trade_payable_turnover"]]
    e2_ccc = w_ave(e2_df["trade_payable_turnover"])+w_ave(e2_df["inventory_turnover"])-w_ave(e2_df["accounts_receivable_turnover"])
    
    return e1_tat,e2_ccc



#＜説明変数群6【生産性指標 Labor Productivity】＞
def labor_productivity(df_q):
    #<1:1人当たり売上高 Sales per productivity>
    lp1 = df_q["net_sales_per_employee"]
    lp1_nspe = w_ave(lp1)

    #<2:1人当たり営業利益 Operating income per person>
    lp2 = df_q["operating_income_per_employee"]
    lp2_oipe = w_ave(lp2)

    return lp1_nspe,lp2_oipe



#＜説明変数群7 Aパターン【株主還元性指標 Shareholder returnability】＞
def shareholder_returnabilityA(df_q):
    #<1:配当性向 Dividend payout ratio (%）＝ 1株あたり配当金 Dividends per share ÷1株あたり純利益（EPS）×100>
    sr1 = df_q["dividend"] /df_q["eps_actual"] * 100
    sr1A_dpr= w_ave(sr1)
                                        
    #<2:株主資本配当率 DOE(株主資本配当率）＝ 年間総配当額 ÷ 自己資本>
    sr2 = df_q["doe"]
    sr2A_doe = w_ave(sr2)
    
    return sr1A_dpr,sr2A_doe



#＜目的変数Aパターン【4半期株式投資収益率(4倍で年間)】＞
def eirrA(df_day,df_c):
    #<インカムゲインの率  income gain  年間配当利回り "dividend_yield_forecast">
    ig_d=df_day["dividend_yield_forecast"]
    ig_c=df_c["dividend_yield_forecast"]
    ig_merge= dc_merge(ig_d,ig_c)
    ig = w_ave(ig_merge)/4

    #<キャピタルゲインの率 capital gain  (後４周期の平均値(売却時) - 前4周期の平均値(購入時）)/前4周期の平均値(購入時)>
    df_cg = df_day[["market_capital","num_of_shares"]]
    cg_d = df_cg["market_capital"]/df_cg["num_of_shares"]
    cg_c = df_c["stockprice"]
    cg_merge = dc_merge(cg_d,cg_c)
    cg_before = cg_merge
    cg_after = cg_merge.shift(-1)
    cg_ab = (cg_after - cg_before)/cg_before
    cg = w_ave(cg_ab)

    #<キャピタルゲイン ＋ インカムゲイン  4半期株式投資収益率 4-quarter equity investment return rate>
    equity_investment_return_rateA= ig+cg 
    
    return equity_investment_return_rateA


#上記の関数を寄せ集め、データを株価指標に加工する(Aパターン)
df_listA = []

for i in range(len(ticker_data)):
    ticker = ticker_data[i]
    df_q = pd.read_csv(f"work1_Fetching/df_q/{ticker_data[i]}.csv")
    df_day = pd.read_csv(f"work1_Fetching/df_day/{ticker_data[i]}.csv")
    df_c = pd.read_csv(f"work1_Fetching/df_c/{ticker_data[i]}.csv")

    s1_cr,s2_er,s3_icr,s4_msr,s5_ocfr = safety(df_q)
    gp1_nsar,gp2_sgr,gp3_nigr,gp4_ocfgr,gp5_roic = growth_potential(df_q)
    p1_cosr,p2_sr,p3_roe,p4_eva,p5_ocfmr = profitability(df_q,df_day,df_c)
    i1_psr,i2_pcfr,i3_mix,i4_ev_ebitda,i5_FCFtspr = inexpensive(df_q,df_day,df_c)
    e1_tat,e2_ccc = efficiency(df_q)
    lp1_nspe,lp2_oipe = labor_productivity(df_q)
    sr1A_dpr,sr2A_doe = shareholder_returnabilityA(df_q)
    equity_investment_return_rateA = eirrA(df_day,df_c)

    company = df_q.loc[ :,"company_name"]
    df_q.index.name = company[0]

    df_A =pd.DataFrame({"company":[df_q.index.name],
                        "code":[ticker],
                        "current_ratio":[s1_cr],
                        "equity_ratio":[s2_er],
                        "interest_coverage_ratio":[s3_icr],
                        "margin_of_safety_ratio":[s4_msr],
                        "Interest-bearing debt operating CF magnification":[s5_ocfr],
                        "Net asset growth rate":[gp1_nsar],
                        "Sales growth rate":[gp2_sgr], 
                        "Net income growth rate":[gp3_nigr],
                        "Operating Cash Flow Growth Rate":[gp4_ocfgr],
                        "roic":[gp5_roic],
                        "Cost of sales rate":[p1_cosr],
                        "sga ratio":[p2_sr],
                        "roe":[p3_roe],
                        "EVA Spread":[p4_eva],
                        "Operating CF margin ratio":[p5_ocfmr],
                        "PSR":[i1_psr],
                        "PCFR":[i2_pcfr],
                        "Mix factor":[i3_mix],
                        "EV_EBITDA":[i4_ev_ebitda],
                        "FCF theory stock price ratio":[i5_FCFtspr],
                        "Total assets turnover":[e1_tat],
                        "ccc":[e2_ccc],
                        "Sales per productivity":[lp1_nspe],
                        "Operating income per person":[lp2_oipe],
                        "Dividend payout ratio":[sr1A_dpr],
                        "DOE":[sr2A_doe],
                        "equity_investment_return_rate":[equity_investment_return_rateA]
                        })
    
    df_listA.append(df_A)
    clear_output()
    print(f"{i + 1}/{len(ticker_data)}",flush = True)
    
ProcessedDataA = pd.concat([df_listA[i] for i in range(len(ticker_data))])
#分析につかうデータAを作成
ProcessedDataA.to_csv("work2_Processing/ProcessedDataA.csv",index = False,encoding = "utf_8_sig")




#＜説明変数群7 Bパターン【株主還元性指標 Shareholder returnability】＞
def shareholder_returnabilityB(df_q):
    #<1:配当性向 Dividend payout ratio (%）＝ 1株あたり配当金 Dividends per share ÷1株あたり純利益（EPS）×100>
    sr1 = (df_q["dividend"]) /(df_q["eps_actual"]) * 100
    sr1B_dpr= w_ave(sr1)
    
    #<2:株主資本配当率 DOE(株主資本配当率)>
    sr2 = df_q["doe"]
    sr2B_doe = w_ave(sr2)

    #<3:インカムゲインの率  年間配当利回り "dividend_yield_forecast">
    sr3_1=df_day["dividend_yield_forecast"]
    sr3_2=df_c["dividend_yield_forecast"]
    sr3_merge= dc_merge(sr3_1,sr3_2)
    sr3B_ig = w_ave(sr3_merge)/4     
    
    return sr1B_dpr,sr2B_doe,sr3B_ig   



#＜目的変数Bパターン【4半期のキャピタルゲイン(4倍で年間)】＞
def capital_gainB(df_day,df_c):
    #<キャピタルゲインの率 capital gain ((後４周期の平均値(売却時) - 前4周期の平均値(購入時))/前4周期の平均値(購入時）>
    df_cg = df_day[["market_capital","num_of_shares"]]
    cg_d = df_cg["market_capital"]/df_cg["num_of_shares"]
    cg_c = df_c["stockprice"]
    cg_merge = dc_merge(cg_d,cg_c)
    cg_before = cg_merge
    cg_after = cg_merge.shift(-1)
    cg_ab = (cg_after - cg_before)/cg_before
    cg = w_ave(cg_ab)
    
    return cg


#＜データを株価指標に加工する Bパターン＞
df_listB = []

for i in range(len(ticker_data)):
    ticker = ticker_data[i]
    df_q = pd.read_csv(f"work1_Fetching/df_q/{ticker_data[i]}.csv")
    df_day = pd.read_csv(f"work1_Fetching/df_day/{ticker_data[i]}.csv")
    df_c = pd.read_csv(f"work1_Fetching/df_c/{ticker_data[i]}.csv")

    s1_cr,s2_er,s3_icr,s4_msr,s5_ocfr = safety(df_q)
    gp1_nsar,gp2_sgr,gp3_nigr,gp4_ocfgr,gp5_roic = growth_potential(df_q)
    p1_cosr,p2_sr,p3_roe,p4_eva,p5_ocfmr = profitability(df_q,df_day,df_c)
    i1_psr,i2_pcfr,i3_mix,i4_ev_ebitda,i5_FCFtspr = inexpensive(df_q,df_day,df_c)
    e1_tat,e2_ccc = efficiency(df_q)
    lp1_nspe,lp2_oipe = labor_productivity(df_q)
    sr1B_dpr,sr2B_doe,sr3B_ig  = shareholder_returnabilityB(df_q)
    cg = capital_gainB(df_day,df_c)

    company = df_q.loc[ :,"company_name"]
    df_q.index.name = company[0]

    df_B =pd.DataFrame({"company":[df_q.index.name],
                        "code":[ticker],
                        "current_ratio":[s1_cr],
                        "equity_ratio":[s2_er],
                        "interest_coverage_ratio":[s3_icr],
                        "margin_of_safety_ratio":[s4_msr],
                        "Interest-bearing debt operating CF magnification":[s5_ocfr],
                        "Net asset growth rate":[gp1_nsar],
                        "Sales growth rate":[gp2_sgr], 
                        "Net income growth rate":[gp3_nigr],
                        "Operating Cash Flow Growth Rate":[gp4_ocfgr],
                        "roic":[gp5_roic],
                        "Cost of sales rate":[p1_cosr],
                        "sga ratio":[p2_sr],
                        "roe":[p3_roe],
                        "EVA Spread":[p4_eva],
                        "Operating CF margin ratio":[p5_ocfmr],
                        "PSR":[i1_psr],
                        "PCFR":[i2_pcfr],
                        "Mix factor":[i3_mix],
                        "EV_EBITDA":[i4_ev_ebitda],
                        "FCF theory stock price ratio":[i5_FCFtspr],
                        "Total assets turnover":[e1_tat],
                        "ccc":[e2_ccc],
                        "Sales per productivity":[lp1_nspe],
                        "Operating income per person":[lp2_oipe],
                        "Dividend payout ratio":[sr1B_dpr],
                        "DOE":[sr2B_doe],
                        "income gain":[sr3B_ig],
                        "capital gain":[cg] 
                        })
    
    df_listB.append(df_B)
    clear_output()
    print(f"{i + 1}/{len(ticker_data)}",flush = True)

ProcessedDataB = pd.concat([df_listB[i] for i in range(len(ticker_data))])
#分析につかうデータBを作成
ProcessedDataB.to_csv("work2_Processing/ProcessedDataB.csv",index = False,encoding = "utf_8_sig")


"""
加工参考URL
https://blog.buffett-code.com/entry/how_to_use_api

https://docs.buffett-code.com/#/default/get_api_v2_quarter
"""