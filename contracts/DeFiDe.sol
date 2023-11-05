pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./DTO.sol";
import "./DeFiDeTo.sol";


contract DeFiDe {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    mapping(uint256 => address) public deployedDeFiDeToInstance;

    function getOrCreateDerivativeTokenForTokenAddressesAndProportions(CollateralToken[] calldata tokens) external returns (address) {
        // Calculate token proportions and create a hash index
        uint256 index = computeIndexForUnderlyingTokens(tokens);

        // Check if a DeFiDeTo instance already exists, if not create one
        if (deployedDeFiDeToInstance[index] == address(0)) {
            deployedDeFiDeToInstance[index] = createDerivativeTokenForTokenAddressesAndProportions(tokens);
        }
        return deployedDeFiDeToInstance[index];
    }

    function computeIndexForUnderlyingTokens(CollateralToken[] memory tokens) public pure returns (uint256) {
        bytes memory packedValues;
        for (uint256 i = 0; i < tokens.length; i++) {
            packedValues = abi.encodePacked(packedValues, tokens[i].token);
            packedValues = abi.encodePacked(packedValues, tokens[i].amount);
        }
        bytes32 hash = keccak256(packedValues);
        return uint256(hash);
    }

    function createDerivativeTokenForTokenAddressesAndProportions(CollateralToken[] memory tokens) internal returns (address) {
        DeFiDeTo deFiDeToInstance = new DeFiDeTo(tokens);
        uint256 index = computeIndexForUnderlyingTokens(tokens);
        deployedDeFiDeToInstance[index] = address(deFiDeToInstance);
        return address(deFiDeToInstance);
    }
}