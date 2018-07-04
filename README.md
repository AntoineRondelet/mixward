# Mixward: The community mixer that rewards its users

**WARNING: ** This work is "heavy" WIP, and should NOT be used for any serious purpose

## Idea:
- Sender deposits on mixer contract the amount to send to recipient + reward to anyone who "unlocks" the payment
- The mixer keeps tracks of every reward on a mapping((address=>uint256) where the address is the stealth address of the recipient, and the uint256 is the amount of the reward. Or even better, we have a struct:
```
struct StuckPayment {
   address: stealthAddress of secret recipient
   uint256: reward to whoever unlocks the payment
}
```
and we have an array:
```
stuckPayments[StuckPayments]
```
If we implement the array as being a queue (FIFO), we can "simulate" a lottery, where:
1. Sender compute stealth address of recipient (this needs for a shared secret between the 2 of them)
2. Sender calls `deposit(address stealthAddress, uint256 reward)` (which is a payable function) --> Btw we need to ensure the fees are above a threshold; otherwise senders will be incentivized to set super low fees. Btw2 --> Threshold might not be required if we think about the fact that recipients have a view on the array of stuck payments on the smart contract. So if they see small rewards they might not want to withdraw and then the sender's payment can be stuck for a very long time.... Thus senders might be incentivized to set high fees.
Actually they are multiple ways we can consider the array of stuck payments:
    - 1) We could implement the array of stuck payments as a priority queue ordered according to the reward: That way senders are "forced" to put high fees if they want to see their payments unlocked asap. However, it could lead to some payments being stuck "forever" in the mixer, because always overtook in the "stuck payment array/pool"
    - 2) A way to circumvent the problem raised in 1), we could implement the array as a queue (FIFO) such that at each call of the "unlock" function, the first payment is unlocked and the corresponding reward is atributed to the account who "unlocked" the payment. The only problem I see with this is: People can track all Tx depositing to the mixer, and basically get the state of the array of stcuk Tx. Then, in case where the rewards a too small, they could decide not to unlock payments (this is why in such case we need to make sure that the rewards are above a certain threshold, to make sure it is always interesting for someone (ie: they make money out of it) to unlock a payment), or target a special payment that comes to the front of the queue => Then we could have a bunch of people waiting for a specific stuck payment (with a really good reward) to be at the head of the queue to fire an "unlock" => Which would lead to a massive peak of tx being fired. The good aspect of it is that if a stuck payment with a massive reward is in the middle of the queue, this could incentivize people to unlock the preceding stuck payments to have a chance to unlock this appealing one and get the reward + in case where N Tx where fired (from different addresses) to unlock this stuck payment, only one would effectively unlcok the payment in question and get the reward, and the N-1 other tx would unlock the n-1 (or less, in which case some tx would be reverted) next payments in the queue. This approach does not seem so bad after all!!!
    - 3) Try and make the unlocking of stuck payment "random". Each time the "unlock" function is called, it's like a lottery to determine which payment gets popped out of the stuck payment array, and which reward (associated to this payment) the caller gets. While, randomness is not possible on-chain, we can think of a way to leverage entropy of the calling client something like: `indexOfNextPaymentToUnlock = sha256(shq256(previousCaller) || callerAddress) % sizeOfArray`, where `sizeOfArray` is the number of stuck payments waiting to be unlocked, `sha256(previousCaller)` would be a variable of the contract that stores the sha256 of the previous caller of the contract (either a deposit or unlock function --> it is updated at every call), and `callerAddress` is the address calling the contract. This is not trully random, but in the case where many users interact with the contract, it could probaby provide a sufficient solution --> Although many edge cases would need to be considered, where one guy (address) unlocks multiple payments in a row, then the `previousCaller` is perfectly predictable, and the "random" effect of the solution does not work anymore. TODO: Try to think more about it...
3. Anyone one the network can unlock payments from the stuck payment pool of the mixer
4. When a stuck payment gets selected to be unlocked, the stealth address associated with it gets rewarded.

## Notes:

- I thought about having a mapping like: `mapping((address=>uint256)=>uint256)` in which the inmost `uint256` indicates the value of the payment (the mixer would be able to mix for different denominations), and the outmost `uint256` would be the reward associated to the payment. However, I am afraid, having payments of different denoms would enable network analysis and leak valuable information about the recipient of a payment... Probably better to keep the mixer bounded to a standard denomination (although network/timing analysis could leak info if users are not careful enough when using the mixer for odd denominations that need to be spit into multiple deposits).

## Pros

- Anonymity set: All the network
- Very cheap: The only expensive operation is the computation of the stealth address which is done off-chain, the logic of the mixer on-chain is pretty simple and does not make use of any expensive operations (no call to expensive EC operations on precompiled and so on)
- It circumvent the "stealth address funding problem", where people can just create stealth addresses to hide their identities, and leverage the network effect to wait for others on the network to "unlock" for them the payment they are expecting + Imagine I am the recipient of a private TX (one stuck TX containing my stealth address is in the pool of stuck TX on the mixer contract), I am the only one (along with the sender who obviously sent me the money in a previous transaction) who knows the "ownership" of the stealth address (ie: the identity of the recipient, who is me in this case). Then I could just "unlock" my stuck payment in the pool of the mixer --> The other members of the network will just believe I am unlocking funds to get their reward.

## Cons

- In case where very good rewards are set, there could be a "rush" a people trying to withdraw/unlock the payment, which means that this could create congestions on the blockchain (think about 1000 payments being deposited, with a reward of 1ether each ==> Everyone would try to unlock them !), which could lead to many transactions being reverted, and thus, many "trash" transactions being included into blocks...
- The sender of a payment can see when his recipient does another payment (because he is the only one to know the mapping between the recipient's stealth address and the "identity" behind it). So in case where the sender wanted to be malicious, he could reveal the identity of his recipient to everyone after the payment is done, or, he could track when the recipient of his previous payment does another payment (although this does not leak a loot of information...)
