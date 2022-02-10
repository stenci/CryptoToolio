from ._anvil_designer import WalletFilterTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class WalletFilter(WalletFilterTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
 

    def reload_asset(self, **event_args):
        print('1')
        if len(self.address_one.text) != 56 or self.address_one.text[0] != 'G':
            self.repeating_panel_1.items = []
            return
        
        print('2')
        print(self.info_type.selected_value)
        if self.info_type.selected_value == 'Asset Balances':
            print('3')
            self.address_two.visible = False
            found, rows = anvil.server.call('asset_inquiry', self.address_one.text)
            if found:
                self.repeating_panel_1.items = rows
            else:
                self.repeating_panel_1.items = []
                Notification('Oops...').show()
                
        elif self.info_type.selected_value == 'Compare Addresses':
            print('4')
            self.address_two.visible = True
            if len(self.address_two.text) != 56 or self.address_two.text[0] != 'G':
                self.repeating_panel_1.items = []
                return           
        
        elif self.info_type.selected_value == 'Transactions':
            print('5')
            self.address_two.visible = False
            
        elif self.info_type.selected_value == 'Created Accounts':
            pass   
        

    def link_4_click(self, **event_args):
        open_form('AquaReward')

    def link_2_click(self, **event_args):
        open_form('AuctionPage')

    def link_1_click(self, **event_args):
        """This method is called when the link is clicked"""
        pass

    def text_box_1_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        pass

