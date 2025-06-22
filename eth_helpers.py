import json
from web3 import Web3
from web3.middleware import geth_poa_middleware  # ВАЖНО: для web3>=6

# Адрес смарт-контракта ABM
ABM_CONTRACT_ADDRESS = "0xA417AF4bAaCb61914a51bEDF194171d6acDB14F5"

# Минимальный ABI для токена ERC20 (только нужные функции)
ERC20_ABI = json.loads("""[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":
    [{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
]""")

# Поддерживаемые сети
NETWORKS = {
    "sepolia": {
        "rpc": "https://sepolia.infura.io/v3/b0cbd2dfc84c4e7e8f6c07aaa84718b3",
        "chain_id": 11155111,
        "use_poa": True
    },
    "mainnet": {
        "rpc": "https://mainnet.infura.io/v3/b0cbd2dfc84c4e7e8f6c07aaa84718b3",
        "chain_id": 1,
        "use_poa": False
    }
}


def get_web3(network: str) -> Web3:
    if network not in NETWORKS:
        raise ValueError(f"Unknown network: {network}")

    rpc = NETWORKS[network]["rpc"]
    w3 = Web3(Web3.HTTPProvider(rpc))

    if NETWORKS[network]["use_poa"]:
        # ⚠️ ВАЖНО: В новой версии передаём Web3 в geth_poa_middleware()
        w3.middleware_onion.add(geth_poa_middleware(w3))

    return w3


def is_valid_eth_address(address: str) -> bool:
    return Web3.is_address(address)


def checksum_address(address: str) -> str:
    return Web3.to_checksum_address(address)


def get_token_balance(address: str, network: str):
    w3 = get_web3(network)

    if not is_valid_eth_address(address):
        raise ValueError("Invalid Ethereum address")

    address = checksum_address(address)

    contract = w3.eth.contract(address=Web3.to_checksum_address(ABM_CONTRACT_ADDRESS), abi=ERC20_ABI)

    balance_raw = contract.functions.balanceOf(address).call()
    decimals = contract.functions.decimals().call()
    symbol = contract.functions.symbol().call()

    balance = balance_raw / (10 ** decimals)
    return balance, symbol
