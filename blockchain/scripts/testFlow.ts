import { network } from "hardhat";

async function main() {
  const { viem } = await network.connect();

  // Get test accounts - think of these as Admin, Patient, Doctor
  const [admin, patient, doctor] = await viem.getWalletClients();

  console.log("Admin address:  ", admin.account.address);
  console.log("Patient address:", patient.account.address);
  console.log("Doctor address: ", doctor.account.address);

  // Connect to the already-deployed contract
  const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
  const mediVault = await viem.getContractAt("MediVaultAccess", contractAddress);

  // ---- STEP 1: Patient registers (and allows break-glass) ----
  console.log("\n--- Patient registering ---");
  await mediVault.write.registerPatient([true], { account: patient.account });
  console.log("Patient registered ✅");

  // ---- STEP 2: Doctor registers ----
  console.log("\n--- Doctor registering ---");
  await mediVault.write.registerDoctor([], { account: doctor.account });
  console.log("Doctor registered (pending approval) ✅");

  // ---- STEP 3: Admin approves doctor ----
  console.log("\n--- Admin approving doctor ---");
  await mediVault.write.approveDoctor([doctor.account.address], { account: admin.account });
  console.log("Doctor approved ✅");

  // ---- STEP 4: Patient uploads record (fake CID for now) ----
  console.log("\n--- Patient uploading record ---");
  const fakeCID = "QmFakeHashForTestingPurposesOnly123";
  await mediVault.write.uploadRecord([fakeCID], { account: patient.account });
  console.log("Record uploaded with CID:", fakeCID);

  // ---- STEP 5: Patient grants doctor access ----
  console.log("\n--- Patient granting access to doctor ---");
  await mediVault.write.grantAccess([doctor.account.address], { account: patient.account });
  console.log("Access granted ✅");

  // ---- STEP 6: Doctor reads the record ----
  console.log("\n--- Doctor fetching record ---");
  const record = await mediVault.read.getPatientRecord([patient.account.address], {
    account: doctor.account,
  });
  console.log("Doctor retrieved CID:", record);

  // ---- STEP 7: Patient revokes access ----
  console.log("\n--- Patient revoking access ---");
  await mediVault.write.revokeAccess([doctor.account.address], { account: patient.account });
  console.log("Access revoked ✅");

  // ---- STEP 8: Doctor tries again (should fail) ----
  console.log("\n--- Doctor trying to access after revoke (should fail) ---");
  try {
    await mediVault.read.getPatientRecord([patient.account.address], {
      account: doctor.account,
    });
  } catch (err) {
    console.log("Access correctly denied ❌ (this is expected!)");
  }

  // ---- STEP 9: Break-Glass emergency access by admin ----
  // ---- STEP 9: Break-Glass emergency access by admin ----
  console.log("\n--- Admin triggering Break-Glass emergency access ---");
  const emergencyTx = await mediVault.write.breakGlassAccess([patient.account.address], {
    account: admin.account,
  });
  console.log("Break-Glass transaction sent:", emergencyTx);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});