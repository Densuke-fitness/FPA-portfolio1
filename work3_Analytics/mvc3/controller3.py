from . import model3
from . import view3

def work3_analytics():
    while True:
        wrapper_tacs = view3.TwoAnalyzeCommonnSelect()
        pattern = wrapper_tacs.select_analytical_method()
        print(f"あなたが選択したもの:{pattern}")

        if pattern == None:
            print("操作を終了します")
            break
        wrapper_fpa = model3.FinancialPointerAnalyzer()
        mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion = wrapper_fpa.financial_pointer_analyzer(pattern)
        if  mra_out is None or tps_out is None:
            print("操作を終了します")
            break
        if type(mra_out) == int:
            print(tps_out)
        if type(tps_out) == int:
            print(mra_out)

        while True :
            wrapper_crd = view3.CheckResultDetails()
            check_flag = wrapper_crd.check_enterprize(pattern, mra_out , data_mediRE, tps_out , data_medi , result , data_medi_new_except_criterion) 
            if type(check_flag) == bool:
                break
            print(check_flag)
        
            

