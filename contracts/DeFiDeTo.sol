pragma solidity ^0.8.20;

// https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v4.8.3/contracts
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./DTO.sol";

/*
    DeFiDeTo is a token that is backed by a basket of other tokens.  The value of DeFiDeTo is pegged to the value of the
    basket of tokens.
*/
contract DeFiDeTo is ERC20Burnable, Ownable {
    using SafeERC20 for IERC20;

    address[] public collateralTokens;
    mapping(address => uint256) public tokenAmountMultiplier;
    address public baseToken; // The token with the smallest amount. Present soley for readability, it's identical to collateralTokens[0]

    function getCollateralTokensCount() public view returns (uint256) {
        return collateralTokens.length;
    }

    constructor(CollateralToken[] memory tokens) ERC20("Decentralized Financial Derivatives Token", "DeFiDeTo") {
        require(tokens.length > 1, "Must have at least two collateral token");

        // Ensure that duplicate tokens are not present
        for (uint256 i = 0; i < tokens.length; i++) {
            for (uint256 j = i + 1; j < tokens.length; j++) {
                require(tokens[i].token != tokens[j].token, "Duplicate collateral token");
            }
        }


        // Sort CollaterlToken by amount, smallest to largest
        for (uint256 i = 0; i < tokens.length; i++) {
            for (uint256 j = i + 1; j < tokens.length; j++) {
                if (tokens[i].amount > tokens[j].amount || (tokens[i].amount == tokens[j].amount && tokens[i].token > tokens[j].token)) {
                    CollateralToken memory temp = tokens[i];
                    tokens[i] = tokens[j];
                    tokens[j] = temp;
                }
            }
        }
        
        uint256 baseTokenAmount = tokens[0].amount;
        for (uint256 i = 0; i < tokens.length; i++) {
            require(tokens[i].amount > 0, "Amount of collateral token must be greater than 0");
            require(tokens[i].token != address(0), "Collateral token address must be valid");

            uint256 baseTokenAmountMultiplier = tokens[i].amount / baseTokenAmount;
            tokenAmountMultiplier[tokens[i].token] = baseTokenAmountMultiplier;
            collateralTokens.push(tokens[i].token);
        }

        baseToken = collateralTokens[0];
    }

    function burn(uint256 amount) public override {
        super.burn(amount);
        uint256 amountOfbaseTokenToReturn = amount;
        IERC20(baseToken).safeTransfer(msg.sender, amountOfbaseTokenToReturn);

        for (uint256 i = 1; i < collateralTokens.length; i++) {
            address token = collateralTokens[i];
            uint256 multiplier = tokenAmountMultiplier[token];
            uint256 tokenAmountToReturn = amount * multiplier;
            IERC20(token).safeTransfer(msg.sender, tokenAmountToReturn);
        }
    }

    function mint(uint256 amount) public {
        IERC20(baseToken).safeTransferFrom(msg.sender, address(this), amount);

        for (uint256 i = 1; i < collateralTokens.length; i++) {
            address token = collateralTokens[i];
            uint256 multiplier = tokenAmountMultiplier[token];
            uint256 tokenAmount = amount * multiplier;
            IERC20(token).safeTransferFrom(msg.sender, address(this), tokenAmount);
        }
        _mint(msg.sender, amount);
    }
}

