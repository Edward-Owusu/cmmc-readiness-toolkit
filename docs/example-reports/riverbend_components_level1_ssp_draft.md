# System Security Plan (draft): Riverbend business network

> Draft generated from questionnaire answers. Review, complete, and approve it before use. A System Security Plan is a formal requirement at CMMC Level 2; at Level 1 it is good practice and supports the self-assessment.

## 1. System identification

- **Organization:** Riverbend Components (fictional)
- **CAGE code:** 0XXX0
- **Employees:** 85
- **System name:** Riverbend business network
- **Point of contact:** Jim Miller, IT Manager
- **Senior official responsible for affirmation:** Dana Reyes, President
- **Prepared:** 2026-10-05 22:43 UTC

### Business description

Machines brackets and housings for a defense prime contractor under a subcontract that includes FAR 52.204-21.

### System boundary

Office and shop-floor Windows computers, one on-premises file server, Microsoft 365 email and file storage, and the office firewall.

### Federal Contract Information handled

Purchase orders, drawings marked for contract use, delivery schedules, and contract correspondence.

## 2. Requirement implementation (5 of 15 met)

### AC.L1-B.1.I Authorized Access Control

*Requirement (52.204-21(b)(1)(i); NIST SP 800-171 3.1.1):* Limit information system access to authorized users, processes acting on behalf of authorized users, or devices (including other information systems).

- **Status:** NOT MET
- **Implementation:** User accounts are managed in Microsoft 365 and on the domain controller; the IT manager keeps the list. All computers require Windows sign-in; Microsoft 365 requires sign-in.
- **Evidence:** Microsoft 365 user export
- **Gaps:** Only partly in place. (AC1-2) Office computers are listed; shop-floor PCs and personal phones are not.
- **Planned action:** Create and maintain a list of authorized users and devices, turn off guest and anonymous access, and require a sign-in on every system that holds FCI.

### AC.L1-B.1.II Transaction and Function Control

*Requirement (52.204-21(b)(1)(ii); NIST SP 800-171 3.1.2):* Limit information system access to the types of transactions and functions that authorized users are permitted to execute.

- **Status:** NOT MET
- **Implementation:** Implementation description to be completed.
- **Gaps:** Not in place. (AC2-1) No written roles. | Not in place. (AC2-2) Several office users have local administrator rights.
- **Planned action:** Define user roles, remove administrator rights from everyday accounts, and give administrators a separate account for admin work.

### AC.L1-B.1.III External Connections

*Requirement (52.204-21(b)(1)(iii); NIST SP 800-171 3.1.20):* Verify and control/limit connections to and use of external information systems.

- **Status:** NOT MET
- **Implementation:** Implementation description to be completed.
- **Gaps:** Not in place. (AC3-1) | Not in place. (AC3-2) Employees use personal phones and home PCs for email without restriction.
- **Planned action:** List the external systems and services in use, approve the ones that are needed, and block or restrict company data on everything else.

### AC.L1-B.1.IV Control Public Information

*Requirement (52.204-21(b)(1)(iv); NIST SP 800-171 3.1.22):* Control information posted or processed on publicly accessible information systems.

- **Status:** NOT MET
- **Implementation:** The office manager approves website and social posts.
- **Gaps:** Only partly in place. (AC4-2) Reviewed before posting, but no periodic review.
- **Planned action:** Name who may post public content, require review for FCI before anything is published, and check existing public content periodically.

### IA.L1-B.1.V Identification

*Requirement (52.204-21(b)(1)(v); NIST SP 800-171 3.5.1):* Identify information system users, processes acting on behalf of users, or devices.

- **Status:** NOT MET
- **Implementation:** Devices are named by location.
- **Gaps:** Not in place. (IA1-1) Shop floor uses a shared 'floor.kiosk' login.
- **Planned action:** Replace shared logins with individual accounts and record every device and service account with a unique name.

### IA.L1-B.1.VI Authentication

*Requirement (52.204-21(b)(1)(vi); NIST SP 800-171 3.5.2):* Authenticate (or verify) the identities of those users, processes, or devices, as a prerequisite to allowing access to organizational information systems.

- **Status:** NOT MET
- **Implementation:** Passwords required for all accounts.
- **Gaps:** Only partly in place. (IA2-2) Changed on computers but not on the shop printer and two network switches.
- **Planned action:** Require authentication on every system and change all default passwords; adding multi-factor authentication is strongly recommended and is required at Level 2.

### MP.L1-B.1.VII Media Disposal

*Requirement (52.204-21(b)(1)(vii); NIST SP 800-171 3.8.3):* Sanitize or destroy information system media containing Federal Contract Information before disposal or release for reuse.

- **Status:** MET
- **Implementation:** Old drives are drilled before disposal; paper goes to a shredding vendor. Computers are reimaged before reassignment.
- **Evidence:** Shredding vendor certificates

### PE.L1-B.1.VIII Limit Physical Access

*Requirement (52.204-21(b)(1)(viii); NIST SP 800-171 3.10.1):* Limit physical access to organizational information systems, equipment, and the respective operating environments to authorized individuals.

- **Status:** MET
- **Implementation:** Office and server closet access limited to staff. Server closet is locked; office has keycard entry.

### PE.L1-B.1.IX Manage Visitors and Physical Access

*Requirement (52.204-21(b)(1)(ix); NIST SP 800-171 3.10.3, 3.10.4, 3.10.5):* Escort visitors and monitor visitor activity; maintain audit logs of physical access; and control and manage physical access devices.

- **Status:** NOT MET
- **Implementation:** Visitors are escorted. Front desk sign-in sheet.
- **Evidence:** Visitor log binder
- **Gaps:** Only partly in place. (PE2-3) Keycards are issued but not always collected from departing staff.
- **Planned action:** Escort visitors, keep a sign-in log, and track who holds keys and badges, collecting them at departure.

### SC.L1-B.1.X Boundary Protection

*Requirement (52.204-21(b)(1)(x); NIST SP 800-171 3.13.1):* Monitor, control, and protect organizational communications (i.e., information transmitted or received by organizational information systems) at the external boundaries and key internal boundaries of the information systems.

- **Status:** NOT MET
- **Implementation:** Office firewall at the internet edge.
- **Gaps:** Not in place. (SC1-2) Default rules; nobody reviews logs.
- **Planned action:** Put a business-grade firewall at the internet edge, block all inbound traffic that is not needed, and review its rules and alerts regularly.

### SC.L1-B.1.XI Public-Access System Separation

*Requirement (52.204-21(b)(1)(xi); NIST SP 800-171 3.13.5):* Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks.

- **Status:** MET
- **Implementation:** Website is hosted by an external provider; guest Wi-Fi is a separate network.

### SI.L1-B.1.XII Flaw Remediation

*Requirement (52.204-21(b)(1)(xii); NIST SP 800-171 3.14.1):* Identify, report, and correct information and information system flaws in a timely manner.

- **Status:** NOT MET
- **Implementation:** Windows Update notifications are on.
- **Gaps:** Only partly in place. (SI1-2) Office PCs update automatically; the file server and shop PCs are patched irregularly.
- **Planned action:** Turn on automatic updates where possible, subscribe to vendor security alerts, and set a time frame for installing critical updates.

### SI.L1-B.1.XIII Malicious Code Protection

*Requirement (52.204-21(b)(1)(xiii); NIST SP 800-171 3.14.2):* Provide protection from malicious code at appropriate locations within organizational information systems.

- **Status:** NOT MET
- **Implementation:** Microsoft 365 email filtering is on.
- **Gaps:** Only partly in place. (SI2-1) Two shop-floor PCs have no antivirus.
- **Planned action:** Deploy endpoint protection on every computer and server, and turn on malware and phishing filtering for email.

### SI.L1-B.1.XIV Update Malicious Code Protection

*Requirement (52.204-21(b)(1)(xiv); NIST SP 800-171 3.14.4):* Update malicious code protection mechanisms when new releases are available.

- **Status:** MET
- **Implementation:** Microsoft Defender updates automatically.

### SI.L1-B.1.XV System and File Scanning

*Requirement (52.204-21(b)(1)(xv); NIST SP 800-171 3.14.5):* Perform periodic scans of the information system and real-time scans of files from external sources as files are downloaded, opened, or executed.

- **Status:** MET
- **Implementation:** Weekly full scan scheduled. Real-time protection on.

## 3. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Senior official | Dana Reyes, President | | |
| Point of contact | Jim Miller, IT Manager | | |

_This report was produced by a self-assessment aid from the answers supplied. It is not a CMMC assessment, certification, or legal advice. Level 1 self-assessment results and the annual affirmation by a senior company official are submitted through the Supplier Performance Risk System (SPRS). Confirm current requirements in 32 CFR Part 170, your contract, and official DoD CMMC guidance._
