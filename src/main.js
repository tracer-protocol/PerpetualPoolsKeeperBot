// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
//
// When running the script with `npx hardhat run <script>` you'll find the Hardhat
// Runtime Environment's members available in the global scope.
const hre = require("hardhat");
// const { Command } = require("commander")
const { Command } = require("commander");
const fs = require('fs')

const POOL_ABI_FILE = "artifacts/LeveragedPool.json"

fs.readFile('/Users/joe/test.txt', 'utf8' , (err, data) => {
  if (err) {
    console.error(err)
    return
  }
  console.log(data)
})


const program = new Command()

program
    .version("0.0.1")
    .requiredOption("-pk, --privatekey", "private key filename")
    .requiredOption("-p, --poolAddresses", "filename including all pools to upkeep")
    .parse(process.argv)

async function main() {
  const { ethers } = hre 
  const privateKeyFilename = program.args[0]
  const poolAddressFilename = program.args[1]

  // Get private key from pkey2.secret, and trim any newlines
  let pkey = fs.readFileSync(privateKeyFilename, "utf-8")
  pkey = pkey.trim()

  let poolAddresses = fs.readFileSync(privateKeyFilename, "utf-8")
  poolAddresses = poolAddresses.trim()
  const addressArray = poolAddresses.split(",")
  for (let i = 0; i < addressArray.length; i++) {
    addressArray[i] = addressArray[i].trim()
  }
  console.log(addressArray)

  const poolAbi = JSON.parse(
    fs.readFileSync(POOL_ABI_FILE).toString()
  ).abi

  const pools = {}
  for (address of addressArray) {
    pools[address] = new ethers.Contract(address, poolAbi)
    console.log(address)
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });