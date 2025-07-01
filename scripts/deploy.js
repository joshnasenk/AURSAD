const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with account:", deployer.address);

  const DataVerification = await ethers.getContractFactory("DataVerification");
  const dataVerification = await DataVerification.deploy();

  // Wait for deployment to be mined (optional but good practice)
  await dataVerification.waitForDeployment();

  console.log("DataVerification deployed to:", dataVerification.target);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

