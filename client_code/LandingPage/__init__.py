from ._anvil_designer import LandingPageTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class LandingPage(LandingPageTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def link_4_click(self, **event_args):
        open_form('AquaReward')
       
    def link_2_click(self, **event_args):
        open_form('AuctionPage')

    def link_1_click(self, **event_args):
        """This method is called when the link is clicked"""
        pass

    def link_5_click(self, **event_args):
        open_form('WalletFilter')


