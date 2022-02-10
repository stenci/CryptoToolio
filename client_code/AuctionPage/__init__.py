from ._anvil_designer import AuctionPageTemplate
from anvil import *
import anvil.server

class AuctionPage(AuctionPageTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.timer_1_tick()
        
    def timer_1_tick(self, **event_args):
        n_tot, price, rows = anvil.server.call_s('get_value')
        self.label_1.text = f'Lowest successful bid: {price}'
        self.label_2.text = f'RBT Number: {n_tot:,f}'
        self.repeating_panel_1.items = rows
        

    def link_1_click(self, **event_args):
      """This method is called when the link is clicked"""

      pass

    def link_2_click(self, **event_args):
      open_form('Form2')
      

    def link_4_click(self, **event_args):
      open_form('AquaReward')
      


