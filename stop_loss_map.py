from risk_management.static_stop_loss import static_stop_loss
from risk_management.trailing_stop_loss import trailing_stop_loss
from risk_management.atr_stop_loss import atr_stop_loss
from risk_management.trailing_atr_stop_loss import trailing_atr_stop_loss


stop_loss_map = {

    'static': static_stop_loss,
    'trailing': trailing_stop_loss,
    'atr': atr_stop_loss,
    'trailing_atr': trailing_atr_stop_loss,  
  
}