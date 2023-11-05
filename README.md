# DeFiDe: Decentralized Financial Derivatives

DeFiDe (Decentralized Financial Derivatives) is an innovative DeFi protocol that introduces a new way to 
create value in the Ethereum ecosystem through DeFiDeTo (Decentralized Financial Derivatives Tokens).
These are ERC-20 tokens minted from a basket of underlying assets, providing a derivative value that is 
directly linked to the collaterals.

This project was developed as a part of EthLisbon 23’ hackathon.

## Introduction

The DeFi ecosystem is an combination of open finance instruments and protocols that aim to replicate and 
innovate on traditional financial services. DeFiDe provides a means to mint ERC-20 derivative tokens backed by a 
diversified collection of assets. This mechanism introduces a scalable and flexible approach to asset-backed tokens, 
enabling users to create and trade complex financial instruments in a trustless environment.

## Value Proposition

DeFiDe empowers users to:

- **Mint DeFiDeTo Tokens**: Representing a basket of underlying ERC-20 tokens held in collateral.
- **Retain Value**: Each DeFiDeTo token’s value is pegged to the collective value of underlying assets.
- **Burn and Recover Assets**: Users can burn DeFiDeTo tokens to recover the underlying assets, ensuring liquidity and ownership rights.
- **Enhance Liquidity**: By providing a protocol for creating derivative tokens, DeFiDe enhances the liquidity and accessibility of various ERC-20 tokens within the DeFi ecosystem.
- **Create Diversified Portfolios**: Users can diversify their cryptocurrency holdings by minting DeFiDeTo tokens that are backed by multiple assets.
- **Hedging Against Volatility**: Users can hedge against the volatility of a single cryptocurrency by holding a DeFiDeTo token that represents a basket of various tokens, thus spreading out their risk.
- **Customized Index Funds**: Create personalized index funds that represent a custom selection of tokens based on user's preferences or investment strategies.

## How It Empowers the DeFi Ecosystem

- **Innovation in Financial Products**: By leveraging DeFiDe, the creation of sophisticated financial products becomes more accessible, promoting financial innovation on the blockchain.
- **Decentralization and Autonomy**: Operating in a permissionless and decentralized manner, DeFiDe adheres to the ethos of the DeFi movement, providing autonomy to users.
- **Interoperability**: The system is built on Ethereum, allowing seamless interaction with other DeFi protocols and services.
- **Transparency and Security**: Open-source and auditable smart contracts underpin DeFiDe, ensuring transparency and security for its users.

## Contracts

### DeFiDeTo

#### Description

The `DeFiDeTo` contract allows the creation of ERC-20 tokens (DeFiDeTo tokens) that are valued based on a collection of underlying tokens. These tokens can be burned, with the underlying assets returned to the token holder.

#### Inheritance

- `ERC20Burnable`: Provides functionality to burn tokens, reducing the total supply.
- `Ownable`: Introduces ownership over the contract, giving special privileges to the owner account.

#### Structs

- `CollateralToken`: Defines a token and its amount to be used as collateral.

#### Constructor

- `constructor(CollateralToken[] memory tokens)`: Initializes the contract with a list of `CollateralToken`, setting up the underlying basket.

#### Functions

- `getCollateralTokensCount()`: Returns the count of collateral tokens.
- `burn(uint256 amount)`: Burns `amount` of DeFiDeTo and returns the corresponding underlying tokens to the caller.
- `mint(uint256 amount)`: Mints `amount` of DeFiDeTo tokens to the caller in exchange for a proportional amount of underlying tokens.

#### State Variables

- `collateralTokens`: Array of addresses representing the tokens used as collateral.
- `tokenAmountMultiplier`: A mapping from an address to a multiplier, used to calculate the amount of each token required for minting.
- `baseToken`: The token with the smallest amount among collateral tokens.

---

### DeFiDe

#### Description

The `DeFiDe` contract manages the creation of `DeFiDeTo` instances. It ensures that each unique combination of underlying tokens and proportions has a single corresponding DeFiDeTo token.

#### Functions

- `getOrCreateDerivativeTokenForTokenAddressesAndProportions(CollateralToken[] calldata tokens)`: Retrieves or creates a `DeFiDeTo` token for a given combination of underlying tokens.
- `computeIndexForUnderlyingTokens(CollateralToken[] memory tokens)`: Computes a unique index for a given set of underlying tokens based on their addresses and amounts.
- `createDerivativeTokenForTokenAddressesAndProportions(CollateralToken[] memory tokens)`: Creates a `DeFiDeTo` instance for a specific set of tokens and proportions.

#### State Variables

- `deployedDeFiDeToInstance`: A mapping from a unique index to an address of a deployed `DeFiDeTo` instance.

### Usage

To use the DeFiDe system:

1. Deploy the `DeFiDe` contract.
2. Call `getOrCreateDerivativeTokenForTokenAddressesAndProportions` with the desired underlying tokens to retrieve or create a `DeFiDeTo` instance.
3. Interact with the `DeFiDeTo` instance to mint or burn derivative tokens.
