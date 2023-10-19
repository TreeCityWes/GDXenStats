import json
from web3 import Web3
import time

# Initialize web3
w3 = Web3(Web3.HTTPProvider('https://polygon.llamarpc.com'))

# Load contract ABIs
with open('gdxen_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)
with open('xec_abi.json', 'r') as abi_file:
    xec_contract_abi = json.load(abi_file)
with open('xec_erc20_abi.json', 'r') as abi_file:
    xec_erc20_contract_abi = json.load(abi_file)
with open('gdxen_views_abi.json', 'r') as abi_file:
    gd_xen_views_abi = json.load(abi_file)

# Contract addresses
contract_address = "0xC16FF25860E87afFe92BcdD81D1eA498726F2dDf"  # GDXen contract address
xec_contract_address = "0x9b38b7212083EAD287C1FCDD0827d9648fF19a0e"  # Xec contract address
xec_erc20_contract_address = "0x78BE30F2a60d63244425AA2466B90CA677d5Aa77"  # XecERC20 contract address
gdxen_views_address = "0xE85677b4C7Fc8B394Eab1a8505bEbb38569F8313"  # GDXenViews contract address

# Set up contract instances
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
xec_contract = w3.eth.contract(address=xec_contract_address, abi=xec_contract_abi)
xec_erc20_contract = w3.eth.contract(address=xec_erc20_contract_address, abi=xec_erc20_contract_abi)
gdxen_views_contract = w3.eth.contract(address=gdxen_views_address, abi=gd_xen_views_abi)

def print_banner():
    banner = r"""
   ____   ____   __  __                   ____    _             _         
  / ___| |  _ \  \ \/ /   ___   _ __     / ___|  | |_    __ _  | |_   ___ 
 | |  _  | | | |  \  /   / _ \ | '_ \    \___ \  | __|  / _` | | __| / __|
 | |_| | | |_| |  /  \  |  __/ | | | |    ___) | | |_  | (_| | | |_  \__ \
  \____| |____/  /_/\_\  \___| |_| |_|   |____/   \__|  \__,_|  \__| |___/                                                                                                                                                                                                                                                                                     
By TreeCityWes.eth - visit TreeCityTrading.us for more info!                                                                                                                                           
    """
    print(banner)
def format_token_amount(amount, decimals=18, ticker=""):
    decimals = int(decimals)
    formatted_amount = amount / (10 ** decimals)
    # Change formatting to display as a whole number
    return "{:,.0f} {}".format(formatted_amount, ticker)  # 0 decimal places

def calculate_total_xen_from_batches(batches):
    XEN_PER_BATCH = 2000000
    total = batches * XEN_PER_BATCH
    return total

def get_current_cycle_stats():
    current_cycle = contract.functions.getCurrentCycle().call()
    current_cycle_reward = contract.functions.currentCycleReward().call()
    current_cycle_fees = contract.functions.cycleAccruedFees(current_cycle).call()
    total_batches_burned = contract.functions.cycleTotalBatchesBurned(current_cycle).call()
    total_xen_burned = calculate_total_xen_from_batches(total_batches_burned)
    time_remaining = get_time_remaining()

    return {
        "Current Cycle": current_cycle,
        "Time Remaining in Current Cycle": time_remaining,
        "Total Batches Burned": total_batches_burned,
        "Total XEN Burned": format_token_amount(total_xen_burned, decimals=0),
        "Current Cycle Reward": format_token_amount(current_cycle_reward, ticker="GDXEN"),
        "Current Cycle Fees": format_token_amount(current_cycle_fees, ticker="MATIC"),
    }

def get_time_remaining():
    current_time = time.time()
    period_duration = contract.functions.i_periodDuration().call()
    initial_timestamp = contract.functions.i_initialTimestamp().call()
    current_cycle = contract.functions.getCurrentCycle().call()
    current_cycle_start_time = initial_timestamp + (current_cycle * period_duration)
    current_cycle_end_time = current_cycle_start_time + period_duration
    time_remaining = current_cycle_end_time - current_time
    time_remaining_formatted = time.strftime("%H hours, %M minutes, %S seconds", time.gmtime(time_remaining))
    return time_remaining_formatted

def get_account_stats(user_address):
    current_cycle = contract.functions.getCurrentCycle().call()
    rewards_claimed = contract.functions.accRewards(user_address).call()
    total_staked = contract.functions.accStakeCycle(user_address, current_cycle).call()
    health_score = contract.functions.getHealth(user_address).call()
    pending_stake = contract.functions.pendingStake().call()
    accrued_fees = contract.functions.accAccruedFees(user_address).call()
    first_burn_cycle = contract.functions.firstBurnCycle(user_address).call()
    xen_batches_burned = contract.functions.accBurnedBatches(user_address, current_cycle).call()
    total_xen_burned = calculate_total_xen_from_batches(xen_batches_burned)

    # Combine the formatted "Total Staked" and "Pending Stake" into one string
    stake_information = "Current: {} // Pending: {}".format(
        format_token_amount(total_staked, ticker="GDXEN"),
        format_token_amount(pending_stake, ticker="GDXEN")
    )

    return {
        "Health Score": health_score,
        "XEN Batches Burned": xen_batches_burned,
        "Rewards Claimed": format_token_amount(rewards_claimed, ticker="GDXEN"),
        "Stake Information": stake_information,  # This is the combined string
        "Accrued Fees": format_token_amount(accrued_fees, ticker="MATIC"),
        "Your Total XEN Burned": format_token_amount(total_xen_burned, decimals=0),
    }

def get_xec_total_supply():
    total_supply = xec_erc20_contract.functions.totalSupply().call()
    return format_token_amount(total_supply)

def get_user_xec_balance(user_address):
    balance = xec_erc20_contract.functions.balanceOf(user_address).call()
    return format_token_amount(balance)

def get_claimable_xec(user_address):
    claimable = xec_contract.functions.accClaimableXec(user_address).call()
    return format_token_amount(claimable)

def get_total_burned_garbage():
    total_burned = xec_contract.functions.totalBurnedGarbage().call()
    return format_token_amount(total_burned)

def main():
    print_banner()

    while True:
        address_input = input("\nPlease enter your wallet address (or 'exit' to leave): ").strip()
        if address_input.lower() == 'exit':
            print("Goodbye!")
            break
        if not w3.is_address(address_input):
            print("This doesn't look like a valid Ethereum address. Please try again.")
            continue
        current_cycle_stats = get_current_cycle_stats()
        total_xec_supply = get_xec_total_supply()
        total_burned_garbage = get_total_burned_garbage()

        print("\n================ Cycle Statistics ================")
        for key, value in current_cycle_stats.items():
            print(f"{key}: {value}")
        account_stats = get_account_stats(address_input)
        user_xec_balance = get_user_xec_balance(address_input)
        claimable_xec = get_claimable_xec(address_input)

        print("\n================ Account Statistics  ================")
        print(f"Account Address: {address_input}")
        for key, value in account_stats.items():
            print(f"{key}: {value}")
        print(f"Your XEC Balance: {user_xec_balance}")
        print(f"Your Claimable XEC: {claimable_xec}")
        continue_response = input("\nWould you like to check another address? (yes/no): ").strip()
        if continue_response.lower() != 'yes':
            print("Goodbye!")
            break
if __name__ == "__main__":
    main()
