import { network } from "hardhat";

async function main() {
  const { viem } = await network.connect();

  const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
  const mediVault = await viem.getContractAt("MediVaultAccess", contractAddress);

  const range = { fromBlock: 0n, toBlock: "latest" as const };

  console.log("\n--- Fetching all AccessGranted events ---");
  const grantedEvents = await mediVault.getEvents.AccessGranted(undefined, range);
  grantedEvents.forEach((e) => {
    console.log("Patient:", e.args.patient, "→ granted access to Doctor:", e.args.doctor);
  });

  console.log("\n--- Fetching all AccessRevoked events ---");
  const revokedEvents = await mediVault.getEvents.AccessRevoked(undefined, range);
  revokedEvents.forEach((e) => {
    console.log("Patient:", e.args.patient, "→ revoked access from Doctor:", e.args.doctor);
  });

  console.log("\n--- Fetching all BreakGlassTriggered events ---");
  const breakGlassEvents = await mediVault.getEvents.BreakGlassTriggered(undefined, range);
  breakGlassEvents.forEach((e) => {
    console.log(
      "EMERGENCY: Admin", e.args.admin,
      "granted Doctor", e.args.doctor,
      "access to Patient", e.args.patient, "records"
    );
  });

  console.log("\n--- Fetching all RecordUploaded events ---");
  const uploadEvents = await mediVault.getEvents.RecordUploaded(undefined, range);
  uploadEvents.forEach((e) => {
    console.log("Patient:", e.args.patient, "uploaded record with CID:", e.args.cid);
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});