pragma solidity ^0.4.22;

import './Queue.sol';
import './SafeMath.sol';

contract Mixward is Queue {
    using SafeMath for uint;

    Queue  internal payments;
    // minReward = 1 finney; // Idea: We could have a setter (ownerOnly function) that would enable to adjust the minReward in periods where the gasPrice skyrockets on ethereum, to maintain the fees to use this mixer affordable.

    function Mixward () {
        payments.data.length = 100;
    }

    function addPayment(StuckPayment p) {
        push(payments, p);
    }
    
    function deposit(address recipient) payable {
        // Assuming the denomination supported by the contract is 1ether
        // Note we can refine this by making sure the reward is > to a minimum reward
        // By doing something like: require(msg.value > 1 + minReward ether);
        require(msg.value > 1001 finney); // Here we define a minimum reward of 1 finney <=> 0.001 ether
        // See solidity doc --> msg.value (uint): number of wei sent with the message
        uint depositedValue = msg.value;
        uint OneEtherInWei = 1000000000000000000;
        uint reward = SafeMath.sub(depositedValue, OneEtherInWei); // 1 being the denomination supported by the mixer

        StuckPayment memory newPayment = StuckPayment({recipient: recipient, reward: reward});
        addPayment(newPayment);
    }
    
    function popPayment() returns (StuckPayment) {
        return pop(payments);
    }

    function unlock() {
        StuckPayment memory p = popPayment();
        uint reward = p.reward;
        address recipient = p.recipient;
        msg.sender.transfer(reward * 1 wei);
        recipient.transfer(1 ether); // Which is the denomination supported by the mixer
    }
}
