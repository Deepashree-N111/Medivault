import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("MediVaultAccessModule", (m) => {
  const mediVaultAccess = m.contract("MediVaultAccess");

  return { mediVaultAccess };
});