from ._anvil_designer import AquaRewardTemplate
from anvil import *
import anvil.server

class AquaReward(AquaRewardTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.update_list()
        
    def update_click(self, **event_args):
        self.update_list()
        
    def usd_amount_change(self, **event_args):
        self.update_values()
        
    def update_list(self):
        self.summary.text = 'Loading list...'
        self.repeating_panel_1.items = []
        self.session_id, self.xlmpricing, self.rows = anvil.server.call_s('start_aquarewards')
        self.repeating_panel_1.items = self.rows
        self.start_timer()
#         self.rows =anvil.server.call_s('aquaprice')
#         print(float.aquaprice)
    def start_timer(self):
        self.timer_1.interval = 1
        
    def timer_1_tick(self, **event_args):
        print('Tick')
        new_rows, done = anvil.server.call_s('get_aquarewards_details', self.session_id)
        
        if done:
            print('Done')
            self.timer_1.interval = 0
            return
    
        if not new_rows:
            print('Nothing new')
            return
        
        for new_row in new_rows:
            for i in range(len(self.rows)):
                if self.rows[i]['asset1_code'] == new_row['asset1_code'] and self.rows[i]['asset2_code'] == new_row['asset2_code']:
                    print(f'Update {new_row["asset1_code"]} / {new_row["asset2_code"]}')
                    self.rows[i] = new_row
                    break

        self.update_values()
        
    def update_values(self):
        # check if the input value is valid
        try:
            usd_amount = float(self.usd_amount.text)
        except:
            usd_amount = 0
            
        if usd_amount > 0:
            # update the calculated value in self.rows
            xlmpricing = float(self.xlmpricing)
            
            for row in self.rows:
                if 'price1' not in row or row['price1'] == '-':
                    row['calculated_value'] = 'Calculating...'
                else:     
                    xlminvestment = usd_amount/float(self.xlmpricing) 
#                     print('xlminvestment')
#                     print(xlminvestment)
                    amounts1 = float(row['reserves'][0]['amount'])
                    amounts2 = float(row['reserves'][1]['amount'])
#                     print('invested amount in dollar')
#                     print(amounts1)
#                     print(amounts2)
                    investment1 = (usd_amount/ 2 )/ float(row['price1'])
                    investment2 = (usd_amount/ 2 )/ float(row['price2'])
#                     print(f'pair {row["asset1_code"]} / {row["asset2_code"]}')
#                     print(row["asset1_code"])
#                     print(float(row['price1']))
# #                     print(float(row['price1']))
# #                     print(row["asset2_code"])
#                     print(float(row['price2']))
#                     print(float(row['price2']))
#                     print(float(row['price']))
#                     print('assetqty')
#                     print(investment1)                     
#                     print(investment2)
                    assetprice1 = investment1 / amounts1 * 100
                    assetprice2 = investment2 / amounts2 * 100
#                     print(assetprice1)
#                     print(assetprice2)
                    average = (assetprice1 + assetprice2)/ 2 
#                     print(average)
#                     print(float(row['total_shares']))
                    invested_pool_share = average * float(row['total_shares'])
#                     print(invested_pool_share)
# #                     print('daily')
# #                     print( + float(row['daily_amm_reward']))
#                     print('investedpoolshare')
#                     print(invested_pool_share)
                    row['calculated_value'] = float(row['daily_amm_reward']) * (average/100)
                    row['calculated_value_hourly'] = float(row['daily_amm_reward']) * (average/100) /24
                    self.xlminvestment.text = xlminvestment
#                    aqua_equiv_daily = float(row['daily_amm_reward']) * (average/100) /
  
        else:
            # clear the calculated value in self.rows
            for row in self.rows:
                row['calculated_value'] = ''
        
        self.repeating_panel_1.items = self.rows
        self.summary.text = ''

    def link_3_click(self, **event_args):
        open_form('Home')

    def usd_amount_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        pass

