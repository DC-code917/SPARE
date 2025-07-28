from uer.targets.mlm_target import MlmTarget
from uer.targets.sp_target import SpTarget
from uer.targets.lm_target import LmTarget
from uer.targets.cls_target import ClsTarget
from uer.targets.bilm_target import BilmTarget
from uer.targets.csmmsm_target import CsmMsmTarget
from uer.targets.target import Target


str2target = {"sp": SpTarget, "csmmsm":CsmMsmTarget, "mlm": MlmTarget, "lm": LmTarget,
              "bilm": BilmTarget, "cls": ClsTarget}

__all__ = ["Target", "SpTarget","CsmMsmTarget", "MlmTarget", "LmTarget", "BilmTarget", "ClsTarget", "str2target"]
