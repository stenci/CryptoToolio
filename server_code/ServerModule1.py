import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import json
import datetime
import uuid

#Auction Calc
@anvil.server.callable
def get_value():
    response = requests.get('https://horizon.stellar.org/order_book?selling_asset_type=credit_alphanum4&selling_asset_code=RBT&selling_asset_issuer=GCMSCRWZ3QBOI6AF75B5ZWDBXOSMIRW4FSBZH5OI65Y4H4GVH7LPSOYS&buying_asset_type=native&limit=200')
    data = response.json()
    counter = data['counter']
    bids = data['bids']
    asks = data['asks']
    base = data['base']
    n_tot = 0
    previous_bid = None
    rows = []
    for bid in bids:
        n = float(bid['amount']) / float(bid['price'])
        n_tot += n
        rows.append({'price': bid['price'], 'rtb': n,'amount': bid['amount'], 'n_tot': n_tot})
        if n_tot > 8000000:
            break
        previous_bid = bid
    return n_tot, previous_bid['price'], rows

@anvil.server.callable
def start_aquarewards():
    session_id = str(uuid.uuid4())

    response = requests.get('https://reward-api.aqua.network/api/rewards/?page=1&page_size=100&ordering=-daily_total_reward')
    data = response.json()
    rows = [
        {
            'asset1_code': result['market_key']['asset1_code'],
            'asset1_issuer': result['market_key']['asset1_issuer'],
            'asset2_code': result['market_key']['asset2_code'],
            'asset2_issuer': result['market_key']['asset2_issuer'],
            'daily_sdex_reward': result['daily_sdex_reward'],
            'daily_amm_reward': result['daily_amm_reward'],
        }
        for result in data['results']
    ]
    
    task_id = anvil.server.launch_background_task('start_aquarewards_background_tasks', rows, session_id).get_id()
    app_tables.taskids.add_row(session_id=session_id, task_id=task_id, rows=rows)
    
    response = requests.get('https://horizon.stellar.org/order_book?selling_asset_type=native&buying_asset_type=credit_alphanum4&buying_asset_code=USDC&buying_asset_issuer=GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
    xlmpricing = response.json()
    
    return session_id, xlmpricing['bids'][0]['price'], rows

@anvil.server.background_task
def start_aquarewards_background_tasks(rows, session_id, start_from_row=0):
    for n in range(start_from_row, len(rows)):
        row = rows[n]
        asset1 = row['asset1_code']
        address1 = row['asset1_issuer']
        asset2 = row['asset2_code']
        address2 = row['asset2_issuer']
        print(f'{n} getting {asset1} / {asset2}')
        
        if asset1 == 'XLM':
            url = f'https://horizon.stellar.org/liquidity_pools?reserves=native%2C{asset2}%3A{address2}'
        else:
            url = f'https://horizon.stellar.org/liquidity_pools?reserves={asset1}%3A{address1}%2C{asset2}%3A{address2}'   
        response = requests.get(url)
        reserves = response.json()
        
        
        row['total_trustlines'] = reserves['_embedded']['records'][0]['total_trustlines']
        row['total_shares'] = reserves['_embedded']['records'][0]['total_shares']
        row['reserves'] = reserves['_embedded']['records'][0]['reserves']

        if asset1 == 'XLM':
            url = 'https://horizon.stellar.org/paths/strict-send?destination_assets=USDC%3AGA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN&source_asset_type=native&source_amount=1'
        else:
            url = f'https://horizon.stellar.org/paths/strict-send?destination_assets=USDC%3AGA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN&source_asset_type=credit_alphanum4&source_asset_issuer={address1}&source_asset_code={asset1}&source_amount=1'
        response = requests.get(url)
        pricing1 = response.json()
        row['price1'] = pricing1['_embedded']['records'][0]['destination_amount']
        
        alphanum = 4 if len(asset2) <= 4 else 12
        url = f'https://horizon.stellar.org/paths/strict-send?destination_assets=USDC%3AGA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN&source_asset_type=credit_alphanum{alphanum}&source_asset_issuer={address2}&source_asset_code={asset2}&source_amount=1'
        response = requests.get(url)
        pricing2 = response.json()
        row['price2'] = pricing2['_embedded']['records'][0]['destination_amount']
        
        app_tables.rows.add_row(
            session_id=session_id,
            details=row,
        )

        app_tables.taskids.get(session_id=session_id)['n_last_row'] = n

    app_tables.taskids.get(session_id=session_id)['n_last_row'] = -999 # this means the job is done

@anvil.server.callable
def get_aquarewards_details(session_id):
    new_rows = []
    done = False
    
    for row in app_tables.rows.search(session_id=session_id):
        new_rows.append(row['details'])
        row.delete()
    
    if not new_rows:
        task_row = app_tables.taskids.get(session_id=session_id)
        
        if task_row['n_last_row'] == -999:
            task_row.delete()
            done = True
        else:        
            task_id = task_row['task_id']
            task = anvil.server.get_background_task(task_id)
            print(f'Termination status: {task.get_termination_status()}')
            if task.get_termination_status() == 'failed':
                print('background task restarted')
                new_task = anvil.server.launch_background_task('start_aquarewards_background_tasks', task_row['rows'], session_id, task_row['n_last_row'] + 1)
                new_task_id = new_task.get_id()
                task_row['task_id'] = new_task_id

    return new_rows, done

@anvil.server.callable
def asset_inquiry(address):
    url = f'https://horizon.stellar.org/accounts/{address}'
    print(url)
    response = requests.get(url) 
    if response.status_code != 200:
        return False, []
    data = response.json()
    balances = data['balances']
    rows = [
        {
                'balance': item['balance'],
                'asset_code': item['asset_code'],
        }
            for item in balances
        if 'asset_code' in item and float(item['balance']) > 0
        ]

    print(data['balances'])

    return True, rows
