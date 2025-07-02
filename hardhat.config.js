require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.18",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",
      accounts: ["0xYOUR_PRIVATE_KEY_HERE"], // Replace with your private key
    }
  }
};

