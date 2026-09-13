// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MediVaultAccess {

    address public admin; // the person who deployed this contract = hospital admin

    // ---- DATA STRUCTURES ----

    struct Patient {
        bool registered;
        string ipfsCID;       // pointer to encrypted record on IPFS
        bool breakGlassAllowed; // did patient pre-authorize emergency access?
    }

    struct Doctor {
        bool registered;
        bool approved; // admin has to approve before doctor can do anything
    }

    // wallet address => Patient info
    mapping(address => Patient) public patients;

    // wallet address => Doctor info
    mapping(address => Doctor) public doctors;

    // patientAddress => doctorAddress => access granted?
    mapping(address => mapping(address => bool)) public accessGranted;

    // ---- EVENTS (this becomes your audit trail) ----

    event PatientRegistered(address patient);
    event DoctorRegistered(address doctor);
    event DoctorApproved(address doctor);
    event RecordUploaded(address patient, string cid);
    event AccessGranted(address patient, address doctor);
    event AccessRevoked(address patient, address doctor);
    event BreakGlassTriggered(address patient, address doctor, address admin);

    // ---- SETUP ----

    constructor() {
        admin = msg.sender; // whoever deploys the contract becomes admin
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can do this");
        _;
    }

    // ---- PATIENT FUNCTIONS ----

    function registerPatient(bool allowBreakGlass) external {
        patients[msg.sender].registered = true;
        patients[msg.sender].breakGlassAllowed = allowBreakGlass;
        emit PatientRegistered(msg.sender);
    }

    function uploadRecord(string calldata cid) external {
        require(patients[msg.sender].registered, "Register first");
        patients[msg.sender].ipfsCID = cid;
        emit RecordUploaded(msg.sender, cid);
    }

    function grantAccess(address doctor) external {
        require(patients[msg.sender].registered, "Register first");
        require(doctors[doctor].approved, "Doctor not approved yet");
        accessGranted[msg.sender][doctor] = true;
        emit AccessGranted(msg.sender, doctor);
    }

    function revokeAccess(address doctor) external {
        accessGranted[msg.sender][doctor] = false;
        emit AccessRevoked(msg.sender, doctor);
    }

    // ---- DOCTOR FUNCTIONS ----

    function registerDoctor() external {
        doctors[msg.sender].registered = true;
        doctors[msg.sender].approved = false; // waits for admin
        emit DoctorRegistered(msg.sender);
    }

    function getPatientRecord(address patient) external view returns (string memory) {
        require(
            accessGranted[patient][msg.sender],
            "Access not granted"
        );
        return patients[patient].ipfsCID;
    }

    // ---- ADMIN FUNCTIONS ----

    function approveDoctor(address doctor) external onlyAdmin {
        require(doctors[doctor].registered, "Doctor not registered");
        doctors[doctor].approved = true;
        emit DoctorApproved(doctor);
    }

    // ---- BREAK-GLASS EMERGENCY ACCESS ----
    // Requires: patient pre-authorized it + admin co-signs at the moment of emergency

    function breakGlassAccess(address patient) external onlyAdmin returns (string memory) {
        require(patients[patient].breakGlassAllowed, "Patient did not authorize break-glass");
        emit BreakGlassTriggered(patient, msg.sender, admin);
        return patients[patient].ipfsCID;
    }
}