
import os
import json
from dotenv import load_dotenv
from api_connecter_service import APIConnectorService

load_dotenv()
DAO_KEY = os.getenv('DAO_KEY')

# Organized for accessing the DAO API
class CookieDaoAPI:
    def __init__(self, api_key, mode='json'):
        '''
        mode - determine the type of response returned by the dao api where 'json' is the complete original response
        '''
        self.api_key = api_key
        self.base_url = 'https://api.cookie.fun'
        self.options = ['authorization', 'search', 'twitterUserName', 'contractAddress', 'agentsPaged', 'agentsFiltered']
        self.endpoints = {
            self.options[0] : 'authorization',
            self.options[1] : 'v1/hackathon/search',
            self.options[2] : 'v2/agents/twitterUsername',
            self.options[3] : 'v2/agents/contractAddress',
            self.options[4] : 'v2/agents/agentsPaged'
        }
        self.mode = mode
        self.connector = APIConnectorService(self.api_key, self.base_url)
    
    def get_response_for(self, endpoint, params):
        if self.mode == 'json':
            return self.connector.get_json_response(endpoint, params)
        # Return the only other alternate response
        return self.connector.get_typed_response_cookiemaps_01(endpoint, params)

    def get_authorization(self):
        auth_endpoint = self.endpoints['authorization']
        response = self.get_response_for(auth_endpoint)
        return response

    def get_hackathon_search(self, search_term="cookie%20token%20utility", from_date='2025-01-01', to_date='2025-01-20'):
        search_endpoint = self.endpoints['search'] +'/' + search_term
        params = {
            'from_date': from_date,
            'to_date'  : to_date
        }
        response = self.get_response_for(search_endpoint, params)
        return response

    def get_twitter_username(self, user_name='cookiedotfun', interval=7):
        twitter_endpoint = self.endpoints['twitterUserName'] + '/' + user_name
        params = { 'interval': f'_{interval}days'}
        response = self.get_response_for(twitter_endpoint, params)
        return response

    def get_contract_address(self, address='0xc0041ef357b183448b235a8ea73ce4e4ec8c265f', interval=7):
        ca_endpoint = self.endpoints['contractAddress'] + '/' + address
        params = { 'interval': f'_{interval}days'}
        response = self.get_response_for(ca_endpoint, params)
        return response

    def get_agents_paged(self, interval=7, page=1, page_size=25):
        agents_endpoint = self.endpoints['agentsPaged']
        params = { 'interval': f'_{interval}days', 'page': page, 'pageSize': page_size}
        response = self.get_response_for(agents_endpoint, params)
        return response

    def get_agents_filtered(self, interval=7, start_page=1, page_size=25, limit=5):
        agents_endpoint = self.endpoints['agentsPaged']
        limit=int(limit)
        if(limit <=25):
            page_size = limit
        params = { 'interval': f'_{interval}days', 'page': start_page, 'pageSize': page_size}
        response = self.get_response_for(agents_endpoint, params)
        totalPages = 0
        if(len(response) < limit):
            res = self.connector.get_json_response(agents_endpoint, params)
            totalPages = int(res['ok']['totalPages'])
        while(len(response) < limit and start_page < totalPages):
            start_page += 1
            remaining = limit - len(response)
            if(remaining <=25 ):
                page_size = remaining
            params = { 'interval': f'_{interval}days', 'page': start_page, 'pageSize': page_size}
            currentPage = self.get_response_for(agents_endpoint, params)
            response += currentPage
        return response

# Interactive console to explore the DAO API
class CookieDaoConsole:
    def __init__(self, api_key, mode='json'):
        self.dao_api = CookieDaoAPI(api_key, mode)
        self.options = self.dao_api.options
        self.set_choice_string()

    def set_choice_string(self):
        choice_string = ''
        for (idx, option) in list(zip(range(len(self.options)), self.options)):
            choice_string += f'{idx+1}) {option}\n'
        choice_string += f'{len(self.options)+1}) Exit this prompt\n'
        choice_string += f'Select an option {1} - {len(self.options)+1} : '
        self.choice_string = choice_string
        self.choice_string = choice_string

    def get_endpoint_params(self, option_idx):
        '''
        Get the parameters for the endpoint selected from the user
        '''
        # Start out with default params across endpoints, then modify
        params = {
            'search_term'   : "cookie%20token%20utility",
            'from_date'     : "2025-01-01",
            'to_date'       : "2025-01-20",
            'user_name'     :'cookiedotfun',
            'interval'      : 7,
            'address'       : '0xc0041ef357b183448b235a8ea73ce4e4ec8c265f',
            'page'          : 1,
            'page_size'     : 25,
            'limit'         : 5
        }
        all_options = [
            'search_term', 'from_date', 'to_date', 
            'user_name', 'interval', 'address', 'page', 'page_size',
            'limit'
        ]
        toContinue      = True
        curr_options    = []
        if option_idx == 2: # Get search parameters
            while toContinue:
                curr_options = [all_options[0], all_options[1], all_options[2]]
                input_prompt = ""
                input_prompt += f"1) search_term={params['search_term']}\n"
                input_prompt += f"2) from_date={params['from_date']}\n"
                input_prompt += f"3) to_date={params['to_date']}\n"
                input_prompt += f"4) to accept above\n"
                input_prompt += 'Enter the choice (1-4) : '
                option = int(input(input_prompt))
                toContinue = option < 4
                if toContinue:
                    selected_option = curr_options[option-1]
                    params[selected_option] = input(f"Enter new value for {selected_option} : ")
        elif option_idx == 3: # twitter user name
            while toContinue:                
                curr_options = [all_options[3], all_options[4]]
                input_prompt = ""
                input_prompt += f'1) twitter_user_name : {params["user_name"]}\n'
                input_prompt += f'2) interval : {params["interval"]} \n'
                input_prompt += f"3) to accept above\n"                
                input_prompt += 'Enter the choice (1-3) : '
                option = int(input(input_prompt))
                toContinue = option < 3
                if toContinue:
                    selected_option = curr_options[option-1]
                    params[selected_option] = input(f"Enter new value for {selected_option} : ")
        elif option_idx == 4: # contract address
            while toContinue:
                curr_options = [all_options[5], all_options[4]]
                input_prompt = ""
                input_prompt += f'1) contract address : {params["address"]}\n'
                input_prompt += f'2) interval : {params["interval"]}\n'
                input_prompt += f"3) to accept above\n"
                input_prompt += 'Enter the choice (1-3) : '
                option = int(input(input_prompt))
                toContinue = option < 3
                if toContinue:
                    selected_option = curr_options[option-1]
                    params[selected_option] = input(f"Enter new value for {selected_option} : ")
        elif option_idx == 5: # agentsPaged
            while toContinue:
                curr_options = [all_options[4], all_options[6], all_options[7]]
                input_prompt = ""
                input_prompt += f'1) interval : {params["interval"]}\n'
                input_prompt += f'2) page : {params["page"]}\n'
                input_prompt += f'3) pageSize : {params["page_size"]}\n'
                input_prompt += f"4) to accept above\n"
                input_prompt += 'Enter the choice (1-4) : '
                option = int(input(input_prompt))
                toContinue = option < 4
                if toContinue:
                    selected_option = curr_options[option-1]
                    params[selected_option] = input(f"Enter new value for {selected_option} : ")
        elif option_idx == 6: # filter agentsPaged
            while toContinue:
                curr_options = [all_options[4], all_options[6], all_options[7], all_options[8]]
                input_prompt = ""
                input_prompt += f'1) interval : {params["interval"]}\n'
                input_prompt += f'2) start page : {params["page"]}\n'
                input_prompt += f'3) pageSize : {params["page_size"]}\n'
                input_prompt += f'4) limit : {params["limit"]}\n'
                input_prompt += f"5) to accept above\n"
                input_prompt += 'Enter the choice (1-5) : '
                option = int(input(input_prompt))
                toContinue = option < 5
                if toContinue:
                    selected_option = curr_options[option-1]
                    params[selected_option] = input(f"Enter new value for {selected_option} : ")
        return params

    def interactive(self):
        command_choice = ''
        while True:
            if(command_choice != ""):
                print()
            command_choice = int(input(self.choice_string))
            if command_choice > len(self.options):
                break

            params = self.get_endpoint_params(command_choice)            
            if command_choice == 1: # No parameters to select
                response = self.dao_api.get_authorization()
            elif command_choice == 2: # For search
                response = self.dao_api.get_hackathon_search(
                    params['search_term'], params['from_date'], params['to_date']
                )
            elif command_choice == 3:
                response = self.dao_api.get_twitter_username(
                    params['user_name'], params['interval']
                )
            elif command_choice == 4:
                response = self.dao_api.get_contract_address(
                    params['address'], params['interval']
                )
            elif command_choice == 5:
                response = self.dao_api.get_agents_paged(
                    params['interval'], params['page'], params['page_size']
                )
            elif command_choice == 6:
                response = self.dao_api.get_agents_filtered(
                    params['interval'], params['page'], params['page_size'], params['limit']
                )
            if response:
                json_response = json.dumps(response, indent=2)
                print(json_response)

if __name__ == '__main__':
    mode_choice = int(input("1) Complete JSON \n2) Minimal json for cookiemaps\nTo get started, enter the mode (1-2) : "))
    mode = 'json'
    if mode_choice != 1:
        mode = "cookie_maps"
    cdc  = CookieDaoConsole(DAO_KEY, mode)
    cdc.interactive()
