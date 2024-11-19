from .two_stage import TwoStageMethod
from .pitch_distribution import PitchDistributionMethod

def create_judgment_method(method_name):
    """
    指定された名前の判定方式のインスタンスを作成
    """
    methods = {
        'two_stage': TwoStageMethod,
        'pitch_distribution': PitchDistributionMethod,
    }
    
    if method_name not in methods:
        raise ValueError(f"Unknown judgment method: {method_name}")
        
    return methods[method_name]() 