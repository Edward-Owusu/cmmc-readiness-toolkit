# System Security Plan (draft): Keystone corporate network

> Draft generated from questionnaire answers. Review, complete, and approve it before use. A System Security Plan is a formal requirement at CMMC Level 2; at Level 1 it is good practice and supports the self-assessment.

## 1. System identification

- **Organization:** Keystone Precision Machining (fictional)
- **CAGE code:** 0YYY0
- **Employees:** 40
- **System name:** Keystone corporate network
- **Point of contact:** Priya Nair, Operations Manager
- **Senior official responsible for affirmation:** Marcus Bell, Owner
- **Prepared:** 2026-10-05 22:43 UTC

### Business description

Precision machining subcontractor supporting two defense prime contractors.

### System boundary

Managed Windows laptops and desktops, Microsoft 365 tenant, and a managed firewall. No on-premises servers.

### Federal Contract Information handled

Purchase orders, contract correspondence, and delivery schedules.

## 2. Requirement implementation (15 of 15 met)

### AC.L1-B.1.I Authorized Access Control

*Requirement (52.204-21(b)(1)(i); NIST SP 800-171 3.1.1):* Limit information system access to authorized users, processes acting on behalf of authorized users, or devices (including other information systems).

- **Status:** MET
- **Implementation:** Authorized users are managed in Microsoft Entra ID; access is reviewed quarterly. All devices are enrolled in Intune; unenrolled devices are blocked. Conditional access requires sign-in with MFA from compliant devices.

### AC.L1-B.1.II Transaction and Function Control

*Requirement (52.204-21(b)(1)(ii); NIST SP 800-171 3.1.2):* Limit information system access to the types of transactions and functions that authorized users are permitted to execute.

- **Status:** MET
- **Implementation:** Roles are defined for staff, managers, and IT administrators. Standard users have no local administrator rights; IT uses separate admin accounts.

### AC.L1-B.1.III External Connections

*Requirement (52.204-21(b)(1)(iii); NIST SP 800-171 3.1.20):* Verify and control/limit connections to and use of external information systems.

- **Status:** MET
- **Implementation:** Approved external systems are listed in the IT policy. Company data is accessible only from managed devices; personal devices are blocked.

### AC.L1-B.1.IV Control Public Information

*Requirement (52.204-21(b)(1)(iv); NIST SP 800-171 3.1.22):* Control information posted or processed on publicly accessible information systems.

- **Status:** MET
- **Implementation:** The owner approves all public posts. Public content is reviewed before posting and every quarter.

### IA.L1-B.1.V Identification

*Requirement (52.204-21(b)(1)(v); NIST SP 800-171 3.5.1):* Identify information system users, processes acting on behalf of users, or devices.

- **Status:** MET
- **Implementation:** Every employee has an individual account; shared accounts are prohibited. Devices and service accounts are named and recorded in Intune and Entra ID.

### IA.L1-B.1.VI Authentication

*Requirement (52.204-21(b)(1)(vi); NIST SP 800-171 3.5.2):* Authenticate (or verify) the identities of those users, processes, or devices, as a prerequisite to allowing access to organizational information systems.

- **Status:** MET
- **Implementation:** Passwords plus MFA are required for every account. Default passwords are changed as part of the device setup checklist.

### MP.L1-B.1.VII Media Disposal

*Requirement (52.204-21(b)(1)(vii); NIST SP 800-171 3.8.3):* Sanitize or destroy information system media containing Federal Contract Information before disposal or release for reuse.

- **Status:** MET
- **Implementation:** Drives are destroyed by a certified vendor; certificates are kept. Devices are wiped through Intune before reassignment.

### PE.L1-B.1.VIII Limit Physical Access

*Requirement (52.204-21(b)(1)(viii); NIST SP 800-171 3.10.1):* Limit physical access to organizational information systems, equipment, and the respective operating environments to authorized individuals.

- **Status:** MET
- **Implementation:** Only staff may enter the office; the network closet is limited to IT. Badge access to the office; the network closet is locked.

### PE.L1-B.1.IX Manage Visitors and Physical Access

*Requirement (52.204-21(b)(1)(ix); NIST SP 800-171 3.10.3, 3.10.4, 3.10.5):* Escort visitors and monitor visitor activity; maintain audit logs of physical access; and control and manage physical access devices.

- **Status:** MET
- **Implementation:** Visitors are escorted at all times. Visitors sign in electronically at reception. Badges are tracked and collected at departure.

### SC.L1-B.1.X Boundary Protection

*Requirement (52.204-21(b)(1)(x); NIST SP 800-171 3.13.1):* Monitor, control, and protect organizational communications (i.e., information transmitted or received by organizational information systems) at the external boundaries and key internal boundaries of the information systems.

- **Status:** MET
- **Implementation:** A managed firewall sits at the internet edge. Inbound traffic is denied by default; the managed service provider reviews alerts daily.

### SC.L1-B.1.XI Public-Access System Separation

*Requirement (52.204-21(b)(1)(xi); NIST SP 800-171 3.13.5):* Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks.

- **Status:** MET
- **Implementation:** Website is hosted externally; guest Wi-Fi is isolated.

### SI.L1-B.1.XII Flaw Remediation

*Requirement (52.204-21(b)(1)(xii); NIST SP 800-171 3.14.1):* Identify, report, and correct information and information system flaws in a timely manner.

- **Status:** MET
- **Implementation:** Vendor security alerts are subscribed; Intune reports missing updates. Critical updates are installed within 14 days through Intune.

### SI.L1-B.1.XIII Malicious Code Protection

*Requirement (52.204-21(b)(1)(xiii); NIST SP 800-171 3.14.2):* Provide protection from malicious code at appropriate locations within organizational information systems.

- **Status:** MET
- **Implementation:** Microsoft Defender for Endpoint on all devices. Microsoft Defender for Office 365 filters email.

### SI.L1-B.1.XIV Update Malicious Code Protection

*Requirement (52.204-21(b)(1)(xiv); NIST SP 800-171 3.14.4):* Update malicious code protection mechanisms when new releases are available.

- **Status:** MET
- **Implementation:** Defender updates automatically.

### SI.L1-B.1.XV System and File Scanning

*Requirement (52.204-21(b)(1)(xv); NIST SP 800-171 3.14.5):* Perform periodic scans of the information system and real-time scans of files from external sources as files are downloaded, opened, or executed.

- **Status:** MET
- **Implementation:** Weekly full scans are scheduled. Real-time protection is enforced by policy.

## 3. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Senior official | Marcus Bell, Owner | | |
| Point of contact | Priya Nair, Operations Manager | | |

_This report was produced by a self-assessment aid from the answers supplied. It is not a CMMC assessment, certification, or legal advice. Level 1 self-assessment results and the annual affirmation by a senior company official are submitted through the Supplier Performance Risk System (SPRS). Confirm current requirements in 32 CFR Part 170, your contract, and official DoD CMMC guidance._
