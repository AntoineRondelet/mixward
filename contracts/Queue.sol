pragma solidity ^0.4.22;

// Implementation of the queue, taken from:
// https://github.com/chriseth/solidity-examples/blob/master/queue.sol
contract Queue {
    struct StuckPayment {
        address recipient;
        uint256 reward;
    }

    struct Queue {
        StuckPayment[] data;
        uint front;
        uint back;
    }

    function length(Queue storage q) constant internal returns (uint) {
        return q.back - q.front;
    }

    function capacity(Queue storage q) constant internal returns (uint) {
        return q.data.length - 1;
    }
    
    function push(Queue storage q, StuckPayment data) internal {
        if ((q.back + 1) % q.data.length == q.front) {
            return; // throw;
        }
        q.data[q.back] = data;
        q.back = (q.back + 1) % q.data.length;
    }

    function pop(Queue storage q) internal returns (StuckPayment r) {
        if (q.back == q.front) {
            return; // throw;
        }
        r = q.data[q.front];
        delete q.data[q.front];
        q.front = (q.front + 1) % q.data.length;
    }
}
