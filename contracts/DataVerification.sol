// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataVerification {
    mapping(bytes32 => bool) public whitelist;
    mapping(bytes32 => bool) public verifiedDataHashes;
    mapping(bytes32 => bool) public verifiedModelHashes;

    event DataHashVerified(bytes32 indexed dataHash);
    event ModelHashVerified(bytes32 indexed modelHash);
    event AggregateModelHashRecorded(bytes32 indexed aggHash);

    function dataExists(bytes32 dataHash) public view returns (bool) {
        return verifiedDataHashes[dataHash];
    }

    function addToWhitelist(bytes32 hash) public {
        require(!whitelist[hash], "Already whitelisted");
        whitelist[hash] = true;
    }

    function verifyDataHash(bytes32 dataHash) public view returns (bool) {
        return whitelist[dataHash];
    }

    function markDataHashVerified(bytes32 dataHash) public returns (bool) {
        require(whitelist[dataHash], "Not whitelisted");
        verifiedDataHashes[dataHash] = true;
        emit DataHashVerified(dataHash);
        return true;
    }

    function verifyModelHash(bytes32 modelHash) public view returns (bool) {
        return verifiedModelHashes[modelHash];
    }

    function submitModelHash(bytes32 modelHash) public returns (bool) {
        verifiedModelHashes[modelHash] = true;
        emit ModelHashVerified(modelHash);
        return true;
    }

    function recordAggregateModelHash(bytes32 aggHash) public returns (bool) {
        emit AggregateModelHashRecorded(aggHash);
        return true;
    }
}
