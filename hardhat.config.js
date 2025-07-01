require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.18",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",
      accounts: ["0xdf86027d778b7494d70e59b90a477c0fb77301c8138662878e213514e17315ba"]
    }
  }
};

